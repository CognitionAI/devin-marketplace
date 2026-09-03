#!/usr/bin/env python3
"""Validate the marketplace: .devin-plugin/plugin.json and the plugins/ we author.

    python3 scripts/validate.py          # structural checks
    python3 scripts/validate.py --fix    # also rewrite plugin.json in canonical form
    python3 scripts/validate.py --fetch  # also confirm every pinned sha exists upstream
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / ".devin-plugin" / "plugin.json"
PLUGINS = ROOT / "plugins"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
NAME_RE = re.compile(r"^[a-z0-9]+([.-][a-z0-9]+)*$")
URL_RE = re.compile(r"^https://[^\s/]+/[^\s]+\.git$")
LOCAL_RE = re.compile(r"^\./plugins/([a-z0-9]+([.-][a-z0-9]+)*)$")
PLACEHOLDER_RE = re.compile(r"\$\{([^}]*)\}")
CREDENTIAL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
RUNTIME_PLACEHOLDERS = {"CLAUDE_PLUGIN_ROOT", "PLUGIN_ROOT"}
LOGO_RE = re.compile(r"^[A-Za-z0-9_-]+(/[A-Za-z0-9_-]+)*\.(svg|png|jpg|jpeg|webp)$")
TOP_LEVEL_KEYS = {"name", "description", "homepage", "repository", "skills", "optionalPlugins"}
UPSTREAM_KEYS = {"source", "url", "path", "sha"}
PLUGIN_KEYS = {
    "name",
    "displayName",
    "description",
    "homepage",
    "repository",
    "logo",
    "keywords",
    "mcpServers",
}
STDIO_KEYS = {"command", "args", "env"}
HTTP_KEYS = {"url", "headers", "transport", "oauthClientId", "oauthScopes"}


def identity(plugin: object) -> tuple[str, str]:
    if isinstance(plugin, str):
        return (plugin, "")
    return (plugin["url"], plugin.get("path", ""))


def check_upstream(where: str, plugin: dict, errors: list[str]) -> None:
    extra = set(plugin) - UPSTREAM_KEYS
    if extra:
        errors.append(f"{where}: unexpected keys {sorted(extra)}")
    kind = plugin.get("source")
    if kind not in ("url", "git-subdir"):
        errors.append(f"{where}: source must be 'url' or 'git-subdir'")
    url = plugin.get("url")
    if not isinstance(url, str) or not URL_RE.match(url):
        errors.append(f"{where}: url must be an https git URL ending in .git")
    sha = plugin.get("sha")
    if not isinstance(sha, str) or not SHA_RE.match(sha):
        errors.append(f"{where}: sha must be a full 40-character lowercase commit sha")
    path = plugin.get("path")
    if kind == "git-subdir":
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
            errors.append(f"{where}: git-subdir needs a relative 'path' inside the repository")
    elif path is not None:
        errors.append(f"{where}: 'path' is only valid for git-subdir sources")


def check_entry(index: int, plugin: object, errors: list[str]) -> None:
    where = f"optionalPlugins[{index}]"
    if isinstance(plugin, str):
        match = LOCAL_RE.match(plugin)
        if not match:
            errors.append(f"{where}: a local reference must look like './plugins/<slug>'")
        elif not (PLUGINS / match.group(1) / ".devin-plugin" / "plugin.json").is_file():
            errors.append(f"{where}: {plugin} has no .devin-plugin/plugin.json")
        return
    if isinstance(plugin, dict):
        check_upstream(where, plugin, errors)
        return
    errors.append(f"{where}: must be a './plugins/<slug>' string or a pinned upstream object")


def check_placeholders(where: str, value: str, errors: list[str]) -> None:
    for name in PLACEHOLDER_RE.findall(value):
        if name in RUNTIME_PLACEHOLDERS:
            continue
        if not CREDENTIAL_NAME_RE.match(name):
            errors.append(f"{where}: placeholder ${{{name}}} is not a credential name the runtime can resolve")
        elif name.startswith("MCP_"):
            errors.append(f"{where}: placeholder ${{{name}}} uses the retired MCP_ prefix; name the credential ${{{name[4:]}}}")


def check_env_placeholders(where: str, env: dict[str, object], errors: list[str]) -> None:
    for key, value in env.items():
        if not isinstance(value, str):
            continue
        for name in PLACEHOLDER_RE.findall(value):
            if name not in RUNTIME_PLACEHOLDERS and name != key:
                errors.append(f"{where}: env {key} references ${{{name}}}; a saved credential is matched by the env key, so it must be ${{{key}}}")


def check_server(where: str, slug: str, config: object, errors: list[str]) -> None:
    if not isinstance(config, dict):
        errors.append(f"{where}: server '{slug}' must be an object")
        return
    stdio = "command" in config
    allowed = STDIO_KEYS if stdio else HTTP_KEYS
    extra = set(config) - allowed - {"description"}
    if extra:
        errors.append(f"{where}: server '{slug}' has unexpected keys {sorted(extra)}")
    if stdio:
        args = config.get("args", [])
        env = config.get("env", {})
        if not isinstance(args, list):
            errors.append(f"{where}: server '{slug}' args must be a list")
            return
        if not isinstance(env, dict):
            errors.append(f"{where}: server '{slug}' env must be an object")
            return
        strings = [config["command"], *args, *env.values()]
        check_env_placeholders(f"{where} ({slug})", env, errors)
    else:
        url = config.get("url")
        headers = config.get("headers", {})
        if not isinstance(url, str) or not url.startswith("https://"):
            errors.append(f"{where}: server '{slug}' needs an https url or a command")
            return
        if not isinstance(headers, dict):
            errors.append(f"{where}: server '{slug}' headers must be an object")
            return
        strings = [url, *headers.values()]
    for value in strings:
        if not isinstance(value, str):
            errors.append(f"{where}: server '{slug}' has a non-string value")
            continue
        check_placeholders(f"{where} ({slug})", value, errors)


def check_logo(where: str, slug: str, logo: object, errors: list[str]) -> None:
    if not isinstance(logo, str) or not logo:
        errors.append(f"{where}: logo must be a string")
        return
    if logo.startswith("https://"):
        return
    if not LOGO_RE.match(logo):
        errors.append(f"{where}: logo must be an https url or a plain repo-relative file path")
        return
    if not (PLUGINS / slug / logo).is_file():
        errors.append(f"{where}: logo '{logo}' does not exist in the plugin directory")


def check_local_plugin(slug: str, errors: list[str]) -> None:
    where = f"plugins/{slug}"
    path = PLUGINS / slug / ".devin-plugin" / "plugin.json"
    if not path.is_file():
        errors.append(f"{where}: missing .devin-plugin/plugin.json")
        return
    data = json.loads(path.read_text())
    extra = set(data) - PLUGIN_KEYS
    if extra:
        errors.append(f"{where}: unexpected keys {sorted(extra)}")
    if data.get("name") != slug:
        errors.append(f"{where}: name must match the directory ({slug})")
    display_name = data.get("displayName")
    if display_name is not None and (
        not isinstance(display_name, str)
        or display_name != display_name.strip()
        or not display_name
        or any(ch.isspace() and ch != " " for ch in display_name)
    ):
        errors.append(f"{where}: displayName must be one non-empty line without surrounding whitespace")
    logo = data.get("logo")
    if logo is not None:
        check_logo(where, slug, logo, errors)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or len(servers) != 1 or slug not in servers:
        errors.append(f"{where}: mcpServers must declare exactly one server named '{slug}'")
        return
    check_server(where, slug, servers[slug], errors)


def canonical(data: dict) -> str:
    ordered: list[object] = []
    for plugin in sorted(data["optionalPlugins"], key=identity):
        if isinstance(plugin, str):
            ordered.append(plugin)
            continue
        entry = {"source": plugin["source"], "url": plugin["url"]}
        if "path" in plugin:
            entry["path"] = plugin["path"]
        entry["sha"] = plugin["sha"]
        ordered.append(entry)
    out = {key: data[key] for key in data if key != "optionalPlugins"}
    out["optionalPlugins"] = ordered
    return json.dumps(out, indent=2) + "\n"


def fetch_ok(plugin: dict) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        cmds = (
            ["git", "init", "-q"],
            ["git", "fetch", "-q", "--depth", "1", plugin["url"], plugin["sha"]],
        )
        return all(
            subprocess.run(cmd, cwd=tmp, capture_output=True).returncode == 0 for cmd in cmds
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()

    text = MANIFEST.read_text()
    data = json.loads(text)
    errors: list[str] = []

    if not isinstance(data, dict):
        print("plugin.json: top level must be an object")
        return 1
    extra = set(data) - TOP_LEVEL_KEYS
    if extra:
        errors.append(f"unexpected top-level keys {sorted(extra)}")
    if "requiredPlugins" in data:
        errors.append("marketplace plugins are optional; use optionalPlugins")
    if not isinstance(data.get("name"), str) or not NAME_RE.match(data["name"]):
        errors.append("name must be lowercase alphanumeric with '-' or '.' separators")
    plugins = data.get("optionalPlugins")
    if not isinstance(plugins, list):
        errors.append("optionalPlugins must be a list")
        plugins = []
    for i, plugin in enumerate(plugins):
        check_entry(i, plugin, errors)
    if errors:
        print("\n".join(errors))
        return 1

    seen: dict[tuple[str, str], int] = {}
    for i, plugin in enumerate(plugins):
        key = identity(plugin)
        if key in seen:
            errors.append(f"optionalPlugins[{i}] duplicates optionalPlugins[{seen[key]}]: {key}")
        seen[key] = i

    listed = {identity(p)[0] for p in plugins if isinstance(p, str)}
    authored = sorted(d.name for d in PLUGINS.iterdir() if d.is_dir()) if PLUGINS.is_dir() else []
    for slug in authored:
        if f"./plugins/{slug}" not in listed:
            errors.append(f"plugins/{slug}: not listed in optionalPlugins")
        check_local_plugin(slug, errors)

    want = canonical(data)
    if text != want:
        if args.fix:
            MANIFEST.write_text(want)
            print("rewrote .devin-plugin/plugin.json")
        else:
            errors.append("plugin.json is not canonical; run scripts/validate.py --fix")

    if args.fetch:
        for plugin in plugins:
            if isinstance(plugin, dict) and not fetch_ok(plugin):
                errors.append(f"{plugin['url']}: sha {plugin['sha']} not found upstream")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"ok: {len(plugins)} entries ({len(authored)} authored, {len(plugins) - len(authored)} upstream)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
