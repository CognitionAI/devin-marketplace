#!/usr/bin/env python3
"""A stdio MCP server over the App Store Connect API, for TestFlight releases.

Authentication is an App Store Connect API key (Issuer ID, Key ID, and the
`.p8` private key) taken from the environment the plugin installation fills
in: ASC_ISSUER_ID, ASC_KEY_ID, ASC_PRIVATE_KEY. The private key never leaves
this process except through `prepare_signing_key`, which materializes it as a
0600 file for `xcodebuild`/`xcrun altool` and returns only its path.

Standard library only; ES256 signing goes through the openssl CLI.
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

API = "https://api.appstoreconnect.apple.com"
JWT_TTL_SECONDS = 15 * 60
POLL_SECONDS = 30
PROTOCOL_VERSION = "2024-11-05"


class AscError(Exception):
    """A failure to surface to the model as a tool error."""


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def der_ecdsa_to_raw(der: bytes) -> bytes:
    # SEQUENCE { INTEGER r, INTEGER s } -> r || s, each left-padded to 32 bytes.
    if not der or der[0] != 0x30:
        raise AscError("openssl produced a signature that is not a DER sequence")
    pos = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)
    parts = []
    for _ in range(2):
        if der[pos] != 0x02:
            raise AscError("openssl produced a malformed DER signature")
        length = der[pos + 1]
        value = der[pos + 2 : pos + 2 + length].lstrip(b"\x00")
        parts.append(value.rjust(32, b"\x00"))
        pos += 2 + length
    return b"".join(parts)


def private_key_pem() -> str:
    """The `.p8` contents, accepted either verbatim or base64-encoded."""
    raw = os.environ.get("ASC_PRIVATE_KEY", "").strip()
    if not raw:
        raise AscError(
            "ASC_PRIVATE_KEY is not set: install the TestFlight plugin with the "
            "contents of your App Store Connect .p8 key"
        )
    if "BEGIN" in raw:
        return raw if raw.endswith("\n") else raw + "\n"
    try:
        decoded = base64.b64decode(raw, validate=True).decode()
    except Exception:
        raise AscError(
            "ASC_PRIVATE_KEY is neither a PEM private key nor base64-encoded one"
        ) from None
    if "BEGIN" not in decoded:
        raise AscError("ASC_PRIVATE_KEY decodes to something that is not a PEM key")
    return decoded if decoded.endswith("\n") else decoded + "\n"


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise AscError(
            f"{name} is not set: reinstall the TestFlight plugin with your "
            "App Store Connect API key credentials"
        )
    return value


class Client:
    """App Store Connect REST client with a cached bearer token."""

    def __init__(self) -> None:
        self._token = ""
        self._token_expires = 0.0
        self._key_file: Path | None = None

    @property
    def key_id(self) -> str:
        return required_env("ASC_KEY_ID")

    @property
    def issuer_id(self) -> str:
        return required_env("ASC_ISSUER_ID")

    def key_path(self, directory: Path | None = None) -> Path:
        """Write the private key to a 0600 file and return its path."""
        if directory is None and self._key_file is not None:
            return self._key_file
        target_dir = directory or Path(tempfile.mkdtemp(prefix="asc-key-"))
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"AuthKey_{self.key_id}.p8"
        path.write_text(private_key_pem())
        path.chmod(0o600)
        if directory is None:
            self._key_file = path
        return path

    def token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expires - 60:
            return self._token
        header = {"alg": "ES256", "kid": self.key_id, "typ": "JWT"}
        payload = {
            "iss": self.issuer_id,
            "iat": int(now),
            "exp": int(now) + JWT_TTL_SECONDS,
            "aud": "appstoreconnect-v1",
        }
        signing_input = (
            b64url(json.dumps(header, separators=(",", ":")).encode())
            + "."
            + b64url(json.dumps(payload, separators=(",", ":")).encode())
        )
        with tempfile.NamedTemporaryFile() as data_file:
            data_file.write(signing_input.encode())
            data_file.flush()
            signed = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", str(self.key_path()), data_file.name],
                capture_output=True,
            )
        if signed.returncode != 0:
            raise AscError("could not sign the App Store Connect token; the .p8 key looks invalid")
        self._token = signing_input + "." + b64url(der_ecdsa_to_raw(signed.stdout))
        self._token_expires = now + JWT_TTL_SECONDS
        return self._token

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.token()}")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")
            raise AscError(f"{method} {path} -> HTTP {err.code}: {detail}") from None
        except urllib.error.URLError as err:
            raise AscError(f"{method} {path} failed: {err.reason}") from None
        return json.loads(raw) if raw else {}


CLIENT = Client()


def app_for(bundle_id: str) -> dict[str, Any]:
    apps = CLIENT.request(
        "GET", "/v1/apps", params={"filter[bundleId]": bundle_id, "limit": 200}
    )["data"]
    exact = [app for app in apps if app["attributes"].get("bundleId") == bundle_id]
    if not exact:
        raise AscError(f"no App Store Connect app with bundle id {bundle_id}")
    return exact[0]


def tool_prepare_signing_key(arguments: dict[str, Any]) -> dict[str, Any]:
    directory = arguments.get("directory")
    path = CLIENT.key_path(Path(directory).expanduser() if directory else None)
    return {
        "key_id": CLIENT.key_id,
        "issuer_id": CLIENT.issuer_id,
        "key_path": str(path),
        "xcodebuild_args": [
            "-allowProvisioningUpdates",
            "-authenticationKeyID",
            CLIENT.key_id,
            "-authenticationKeyIssuerID",
            CLIENT.issuer_id,
            "-authenticationKeyPath",
            str(path),
        ],
        "note": "The key file is mode 0600. Pass its path to xcodebuild or altool; never print its contents.",
    }


def tool_list_apps(arguments: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {"limit": int(arguments.get("limit", 100))}
    if arguments.get("bundle_id"):
        params["filter[bundleId]"] = arguments["bundle_id"]
    apps = CLIENT.request("GET", "/v1/apps", params=params)["data"]
    return {
        "apps": [
            {
                "id": app["id"],
                "name": app["attributes"].get("name"),
                "bundle_id": app["attributes"].get("bundleId"),
                "sku": app["attributes"].get("sku"),
            }
            for app in apps
        ]
    }


def tool_list_beta_groups(arguments: dict[str, Any]) -> dict[str, Any]:
    app = app_for(arguments["bundle_id"])
    groups = CLIENT.request(
        "GET", f"/v1/apps/{app['id']}/betaGroups", params={"limit": 200}
    )["data"]
    return {
        "app_id": app["id"],
        "beta_groups": [
            {
                "id": group["id"],
                "name": group["attributes"].get("name"),
                "internal": group["attributes"].get("isInternalGroup", False),
                "public_link_enabled": group["attributes"].get("publicLinkEnabled", False),
                "public_link": group["attributes"].get("publicLink"),
            }
            for group in groups
        ],
    }


def tool_list_builds(arguments: dict[str, Any]) -> dict[str, Any]:
    app = app_for(arguments["bundle_id"])
    builds = CLIENT.request(
        "GET",
        "/v1/builds",
        params={
            "filter[app]": app["id"],
            "sort": "-uploadedDate",
            "limit": int(arguments.get("limit", 10)),
        },
    )["data"]
    return {
        "builds": [
            {
                "id": build["id"],
                "build_number": build["attributes"].get("version"),
                "processing_state": build["attributes"].get("processingState"),
                "uploaded_date": build["attributes"].get("uploadedDate"),
                "expired": build["attributes"].get("expired"),
            }
            for build in builds
        ]
    }


def tool_wait_for_build(arguments: dict[str, Any]) -> dict[str, Any]:
    app = app_for(arguments["bundle_id"])
    build_number = str(arguments["build_number"])
    deadline = time.time() + float(arguments.get("wait_minutes", 45)) * 60
    params = {
        "filter[app]": app["id"],
        "filter[version]": build_number,
        "filter[preReleaseVersion.platform]": arguments.get("platform", "IOS"),
        "sort": "-uploadedDate",
        "limit": 1,
    }
    while True:
        builds = CLIENT.request("GET", "/v1/builds", params=params)["data"]
        state = builds[0]["attributes"]["processingState"] if builds else "NOT_FOUND"
        if state == "VALID":
            return {
                "build_id": builds[0]["id"],
                "build_number": build_number,
                "processing_state": state,
            }
        if state in ("FAILED", "INVALID"):
            raise AscError(f"build {build_number} finished processing in state {state}")
        if time.time() >= deadline:
            raise AscError(
                f"build {build_number} is still {state} after wait_minutes; check App Store Connect"
            )
        time.sleep(POLL_SECONDS)


def tool_set_whats_new(arguments: dict[str, Any]) -> dict[str, Any]:
    build_id = arguments["build_id"]
    whats_new = arguments["whats_new"]
    locale = arguments.get("locale", "en-US")
    localizations = CLIENT.request("GET", f"/v1/builds/{build_id}/betaBuildLocalizations")["data"]
    existing = [loc for loc in localizations if loc["attributes"].get("locale") == locale]
    if existing:
        CLIENT.request(
            "PATCH",
            f"/v1/betaBuildLocalizations/{existing[0]['id']}",
            {
                "data": {
                    "type": "betaBuildLocalizations",
                    "id": existing[0]["id"],
                    "attributes": {"whatsNew": whats_new},
                }
            },
        )
    else:
        CLIENT.request(
            "POST",
            "/v1/betaBuildLocalizations",
            {
                "data": {
                    "type": "betaBuildLocalizations",
                    "attributes": {"locale": locale, "whatsNew": whats_new},
                    "relationships": {"build": {"data": {"type": "builds", "id": build_id}}},
                }
            },
        )
    return {"build_id": build_id, "locale": locale, "whats_new": whats_new}


def tool_add_build_to_group(arguments: dict[str, Any]) -> dict[str, Any]:
    build_id = arguments["build_id"]
    group_id = arguments["group_id"]
    group = CLIENT.request("GET", f"/v1/betaGroups/{group_id}")["data"]
    CLIENT.request(
        "POST",
        f"/v1/betaGroups/{group_id}/relationships/builds",
        {"data": [{"type": "builds", "id": build_id}]},
    )
    result = {
        "build_id": build_id,
        "group_id": group_id,
        "group_name": group["attributes"].get("name"),
        "internal": group["attributes"].get("isInternalGroup", False),
        "beta_review": "not required for an internal group",
    }
    if group["attributes"].get("isInternalGroup", False):
        return result
    try:
        CLIENT.request(
            "POST",
            "/v1/betaAppReviewSubmissions",
            {
                "data": {
                    "type": "betaAppReviewSubmissions",
                    "relationships": {"build": {"data": {"type": "builds", "id": build_id}}},
                }
            },
        )
        result["beta_review"] = "submitted"
    except AscError as err:
        if "HTTP 409" not in str(err):
            raise
        existing = CLIENT.request("GET", f"/v1/builds/{build_id}/betaAppReviewSubmission").get("data")
        if not existing:
            raise
        result["beta_review"] = existing["attributes"].get("betaReviewState", "already submitted")
    return result


def tool_public_link(arguments: dict[str, Any]) -> dict[str, Any]:
    group_id = arguments["group_id"]
    if arguments.get("enable"):
        CLIENT.request(
            "PATCH",
            f"/v1/betaGroups/{group_id}",
            {
                "data": {
                    "type": "betaGroups",
                    "id": group_id,
                    "attributes": {"publicLinkEnabled": True},
                }
            },
        )
    group = CLIENT.request("GET", f"/v1/betaGroups/{group_id}")["data"]
    link = group["attributes"].get("publicLink")
    if not link:
        raise AscError(
            "this beta group has no public link; call testflight_public_link with enable=true, "
            "or invite testers by email in App Store Connect"
        )
    return {
        "group_id": group_id,
        "group_name": group["attributes"].get("name"),
        "public_link": link,
        "public_link_limit": group["attributes"].get("publicLinkLimit"),
    }


TOOLS: list[dict[str, Any]] = [
    {
        "name": "prepare_signing_key",
        "description": (
            "Materialize the installed App Store Connect API key as a 0600 .p8 file and return "
            "the path plus the xcodebuild authentication flags. Call this before archiving or "
            "uploading; the key contents are never returned."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Where to write the key. Defaults to a private temp directory.",
                }
            },
        },
    },
    {
        "name": "list_apps",
        "description": "List the apps this API key can see, with their bundle ids.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_id": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "list_beta_groups",
        "description": "List an app's TestFlight beta groups, including their public links.",
        "inputSchema": {
            "type": "object",
            "properties": {"bundle_id": {"type": "string"}},
            "required": ["bundle_id"],
        },
    },
    {
        "name": "list_builds",
        "description": "List an app's most recent TestFlight builds and their processing state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_id": {"type": "string"},
                "limit": {"type": "integer"},
            },
            "required": ["bundle_id"],
        },
    },
    {
        "name": "wait_for_build",
        "description": (
            "Poll until an uploaded build finishes processing, then return its build id. "
            "Fails if processing ends in FAILED/INVALID or wait_minutes elapses."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "bundle_id": {"type": "string"},
                "build_number": {"type": "string"},
                "wait_minutes": {"type": "number"},
                "platform": {"type": "string", "description": "IOS (default), MAC_OS or TV_OS."},
            },
            "required": ["bundle_id", "build_number"],
        },
    },
    {
        "name": "set_whats_new",
        "description": "Set a processed build's 'What to Test' text.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "build_id": {"type": "string"},
                "whats_new": {"type": "string"},
                "locale": {"type": "string"},
            },
            "required": ["build_id", "whats_new"],
        },
    },
    {
        "name": "add_build_to_group",
        "description": (
            "Add a processed build to a beta group, submitting it for beta app review when the "
            "group is external."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "build_id": {"type": "string"},
                "group_id": {"type": "string"},
            },
            "required": ["build_id", "group_id"],
        },
    },
    {
        "name": "testflight_public_link",
        "description": "Return a beta group's public TestFlight link, optionally enabling it first.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "group_id": {"type": "string"},
                "enable": {"type": "boolean"},
            },
            "required": ["group_id"],
        },
    },
]

HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "prepare_signing_key": tool_prepare_signing_key,
    "list_apps": tool_list_apps,
    "list_beta_groups": tool_list_beta_groups,
    "list_builds": tool_list_builds,
    "wait_for_build": tool_wait_for_build,
    "set_whats_new": tool_set_whats_new,
    "add_build_to_group": tool_add_build_to_group,
    "testflight_public_link": tool_public_link,
}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handler = HANDLERS.get(name)
    if handler is None:
        return {
            "content": [{"type": "text", "text": f"unknown tool {name}"}],
            "isError": True,
        }
    try:
        result = handler(arguments)
    except AscError as err:
        return {"content": [{"type": "text", "text": str(err)}], "isError": True}
    except KeyError as err:
        return {
            "content": [{"type": "text", "text": f"missing required argument {err}"}],
            "isError": True,
        }
    return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    if method == "initialize":
        return {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "testflight", "version": "1.0.0"},
        }
    if method == "ping":
        return {}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        params = message.get("params") or {}
        return call_tool(params.get("name", ""), params.get("arguments") or {})
    raise AscError(f"unsupported method {method}")


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError:
            continue
        message_id = message.get("id")
        if message_id is None:  # A notification; nothing to answer.
            continue
        try:
            result = handle(message)
        except AscError as err:
            response = {
                "jsonrpc": "2.0",
                "id": message_id,
                "error": {"code": -32601, "message": str(err)},
            }
        else:
            response = {"jsonrpc": "2.0", "id": message_id, "result": result}
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
