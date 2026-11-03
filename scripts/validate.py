#!/usr/bin/env python3
"""Validate the marketplace: .devin-plugin/plugin.json and the plugins/ we author.

    python3 scripts/validate.py          # structural checks
    python3 scripts/validate.py --fix    # also rewrite plugin.json in canonical form
    python3 scripts/validate.py --fetch  # also confirm every pinned sha exists upstream
"""

from __future__ import annotations

import argparse
import json
import os
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
    "shortDescription",
    "setup",
    "homepage",
    "repository",
    "logo",
    "keywords",
    "mcpServers",
}
STDIO_KEYS = {"command", "args", "env"}
HTTP_KEYS = {"url", "headers", "transport", "oauthClientId", "oauthScopes"}
# Other manifest/MCP locations the plugin loader would also read; authored
# plugins declare everything in .devin-plugin/plugin.json so this validator sees it.
SHADOW_FILES = ("plugin.json", ".mcp.json", "mcp.json")
HOOK_FILES = ("hooks.json", "hooks/hooks.json")
# Commands that download and run a package at session start. Their package
# argument must name an exact version so the code that runs is fixed by this
# repo, not by whatever the registry serves today.
FETCHERS = {"npx", "bunx", "pnpx", "uvx", "pipx"}
FETCHER_SUBCOMMANDS = {("npm", "exec"), ("npm", "x"), ("pnpm", "dlx"), ("yarn", "dlx"), ("uv", "tool"), ("uvx", "run")}
EXACT_VERSION_RE = re.compile(r"(?<!^)@\d+\.\d+\.\d+[A-Za-z0-9.+-]*$|==\d+(\.\d+)*([A-Za-z0-9.+-]*)$|[#@][0-9a-f]{40}$")
# docker run flags that take no operand; every other flag consumes the next word.
DOCKER_BOOL_FLAGS = {"-i", "-t", "-it", "-ti", "-d", "--rm", "--init", "--privileged", "--interactive", "--tty", "--detach", "--no-healthcheck", "--read-only", "--sig-proxy", "-P", "--publish-all", "-q", "--quiet"}
IMAGE_DIGEST_RE = re.compile(r"@sha256:[0-9a-f]{64}$")
PIPED_INSTALLER_RE = re.compile(
    r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+(-\S+\s+)*)?(\S*/)?(ba|z|da|fi)?sh\b|\b(irm|iwr|Invoke-(RestMethod|WebRequest))\b[^\n|]*\|\s*(iex|Invoke-Expression)\b",
    re.I,
)
LINE_CONTINUATION_RE = re.compile(r"\\\r?\n\s*")
TEXT_SUFFIXES = (".md", ".txt", ".json", ".sh", ".bash", ".zsh", ".py", ".js", ".mjs", ".cjs", ".ts", ".yaml", ".yml", ".toml")
# "<slug>/<server>" entries that predate the pin rules. Do not add to these
# lists: pin the version (or image digest) instead, and remove the entry here
# once it is pinned. A new server in a listed plugin is still checked.
GRANDFATHERED_UNPINNED = {
    "aws-agent-toolkit", "aws-aurora-dsql", "aws-aurora-postgresql", "aws-documentdb", "aws-dynamodb",
    "aws-elasticache", "aws-iam", "aws-lambda", "aws-neptune", "aws-redshift", "aws-sns-sqs", "azure",
    "cognition-alloydb", "cognition-bigquery", "cognition-cloud-sql-mssql", "cognition-cloud-sql-mysql",
    "cognition-cloud-sql-postgres", "cognition-dataplex", "cognition-firestore", "cognition-looker",
    "cognition-mssql", "cognition-mysql", "cognition-postgres", "cognition-redshift", "cognition-snowflake",
    "cognition-spanner", "cortex", "dbt", "dockerhub", "elasticsearch", "firecrawl", "google-analytics",
    "google-maps", "grafana", "heroku", "hubspot", "metabase", "mongodb", "netlify", "pinecone", "playwright",
    "pulumi", "redis", "ref-tools", "replicate", "slack", "sonarqube", "sqlite", "supabase", "unleash",
}
GRANDFATHERED_UNPINNED = {f"{slug}/{slug}" for slug in GRANDFATHERED_UNPINNED}
GRANDFATHERED_INSTALLERS = {"graphos-tools", "hex", "slack-remote", "tavily"}


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


def placeholder_name(reference: str) -> str:
    # `${NAME:-default}` falls back to `default` when NAME has no saved value.
    return reference.split(":-", 1)[0]


def check_placeholders(where: str, value: str, errors: list[str]) -> None:
    for reference in PLACEHOLDER_RE.findall(value):
        name = placeholder_name(reference)
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
        for reference in PLACEHOLDER_RE.findall(value):
            name = placeholder_name(reference)
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


def check_pinned_command(where: str, slug: str, name: str, config: dict, errors: list[str]) -> None:
    command = config.get("command")
    args = config.get("args", [])
    if not isinstance(command, str) or not isinstance(args, list) or not all(isinstance(a, str) for a in args):
        return
    words = [command, *args]
    base = Path(command).name
    if base == "docker" and "run" in args:
        image = docker_image(args[args.index("run") + 1 :])
        if image and not IMAGE_DIGEST_RE.search(image):
            errors.append(f"{where}: server '{name}' runs docker image '{image}' by tag; pin it with @sha256:<digest>")
        return
    fetched = base in FETCHERS or (len(args) > 0 and (base, args[0]) in FETCHER_SUBCOMMANDS)
    if not fetched:
        return
    packages = [a for a in args if not a.startswith("-") and a not in {"exec", "x", "dlx", "tool", "run"}]
    specs = [a.split("=", 1)[1] for a in args if a.startswith(("--package=", "--spec=", "--from="))]
    candidates = specs or packages[:1]
    if not candidates or not any(EXACT_VERSION_RE.search(c) for c in candidates):
        errors.append(
            f"{where}: server '{name}' runs {' '.join(words)[:80]} without an exact version; "
            "pin it (name@1.2.3 for npm, name==1.2.3 for PyPI, or a 40-hex git ref) so the executed code cannot change under the pin"
        )


def docker_image(words: list[str]) -> str | None:
    skip = False
    for word in words:
        if skip:
            skip = False
        elif word.startswith("-"):
            skip = "=" not in word and word not in DOCKER_BOOL_FLAGS
        else:
            return word
    return None


def walk_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from walk_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from walk_strings(v)


def check_hooks(where: str, slug: str, root: Path, errors: list[str]) -> None:
    for rel in HOOK_FILES:
        path = root / rel
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: {rel} is not valid JSON ({exc.msg})")
            continue
        for text in walk_strings(data):
            text = LINE_CONTINUATION_RE.sub(" ", text)
            if PIPED_INSTALLER_RE.search(text):
                errors.append(f"{where}: {rel} pipes a download into a shell; hooks may only run files shipped in the plugin")
            words = text.split()
            if words:
                check_pinned_command(f"{where} ({rel})", slug, "hook", {"command": words[0], "args": words[1:]}, errors)


def check_piped_installers(where: str, root: Path, errors: list[str]) -> None:
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if PIPED_INSTALLER_RE.search(LINE_CONTINUATION_RE.sub(" ", text)):
            errors.append(
                f"{where}: {path.relative_to(root)} pipes a download into a shell (curl ... | sh); "
                "point users at the vendor's release page or a version-pinned package instead"
            )


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


def check_symlinks(where: str, root: Path, errors: list[str]) -> None:
    for parent, dirs, files in os.walk(root):
        for name in dirs + files:
            link = Path(parent) / name
            if link.is_symlink() and not link.resolve().is_relative_to(root.resolve()):
                errors.append(f"{where}: symlink {link.relative_to(root)} must point inside the plugin")


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
    short_description = data.get("shortDescription")
    if not isinstance(short_description, str) or not short_description.strip():
        errors.append(f"{where}: shortDescription must be a non-empty string")
    elif len(short_description) > 40:
        errors.append(f"{where}: shortDescription must be 40 characters or fewer")
    if "setup" in data:
        setup = data["setup"]
        if not isinstance(setup, dict):
            errors.append(f"{where}: setup must be an object")
        else:
            extra = set(setup) - {"notice", "steps"}
            if extra:
                errors.append(f"{where}: setup has unexpected keys {sorted(extra)}")
            if not {"notice", "steps"} & set(setup):
                errors.append(f"{where}: setup needs notice or steps")
            if "notice" in setup and (
                not isinstance(setup["notice"], str) or not setup["notice"].strip()
            ):
                errors.append(f"{where}: setup notice must be a non-empty string")
            if "steps" in setup and (
                not isinstance(setup["steps"], list)
                or not setup["steps"]
                or any(not isinstance(step, str) or not step.strip() for step in setup["steps"])
            ):
                errors.append(f"{where}: setup steps must be a non-empty list of non-empty strings")
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
    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict):
        errors.append(f"{where}: mcpServers must be an object")
        return
    root = PLUGINS / slug
    for name, config in servers.items():
        check_server(where, name, config, errors)
        if isinstance(config, dict) and "command" in config and f"{slug}/{name}" not in GRANDFATHERED_UNPINNED:
            check_pinned_command(where, slug, name, config, errors)
    check_hooks(where, slug, root, errors)
    if slug not in GRANDFATHERED_INSTALLERS:
        check_piped_installers(where, root, errors)
    if not servers and not any(f.is_file() for f in (root / "skills").glob("*/SKILL.md")):
        errors.append(f"{where}: a plugin needs mcpServers or at least one skills/*/SKILL.md")
    for shadow in SHADOW_FILES:
        if (root / shadow).exists():
            errors.append(f"{where}: {shadow} is not allowed; declare everything in .devin-plugin/plugin.json")
    check_symlinks(where, root, errors)


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
