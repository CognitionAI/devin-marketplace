#!/usr/bin/env python3
"""Smoke-test the playwright plugin's stdio server exactly as the manifest declares it.

    python3 plugins/playwright/tests/smoke_test.py

Needs a Docker daemon. Starts the server command from .devin-plugin/plugin.json
(with ${CLAUDE_PLUGIN_ROOT} resolved to the plugin directory), completes the MCP
handshake, drives a page, and checks that the pinned image's browser meets the
minimum version and that Chromium reports its own sandbox as active.
"""

from __future__ import annotations

import json
import queue
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
MANIFEST = PLUGIN / ".devin-plugin" / "plugin.json"
MIN_BROWSER_VERSION = (152, 0, 7977, 82)
TIMEOUT = 120


class StdioClient:
    def __init__(self, command: list[str]):
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )
        self.lines: queue.Queue[str] = queue.Queue()
        self.stderr: list[str] = []
        threading.Thread(target=self._pump, args=(self.proc.stdout, self.lines.put), daemon=True).start()
        threading.Thread(target=self._pump, args=(self.proc.stderr, self.stderr.append), daemon=True).start()
        self.next_id = 0

    @staticmethod
    def _pump(stream, sink):
        for line in stream:
            sink(line)

    def notify(self, method: str, params: dict | None = None) -> None:
        self._write({"jsonrpc": "2.0", "method": method, **({"params": params} if params else {})})

    def request(self, method: str, params: dict | None = None) -> dict:
        self.next_id += 1
        self._write({"jsonrpc": "2.0", "id": self.next_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + TIMEOUT
        while time.monotonic() < deadline:
            try:
                line = self.lines.get(timeout=1)
            except queue.Empty:
                if self.proc.poll() is not None:
                    raise AssertionError(f"server exited with {self.proc.returncode}\n{''.join(self.stderr)}")
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                continue
            if message.get("id") == self.next_id:
                if "error" in message:
                    raise AssertionError(f"{method} failed: {message['error']}")
                return message["result"]
        raise AssertionError(f"timed out waiting for {method}\n{''.join(self.stderr)}")

    def call_tool(self, name: str, arguments: dict) -> str:
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        text = "\n".join(block.get("text", "") for block in result.get("content", []))
        if result.get("isError"):
            raise AssertionError(f"tool {name} returned an error:\n{text}")
        return text

    def _write(self, message: dict) -> None:
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def close(self) -> int:
        self.proc.stdin.close()
        try:
            return self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            return self.proc.wait()


def server_command() -> list[str]:
    server = json.loads(MANIFEST.read_text())["mcpServers"]["playwright"]
    args = [arg.replace("${CLAUDE_PLUGIN_ROOT}", str(PLUGIN)) for arg in server["args"]]
    return [server["command"], *args]


def image_reference(command: list[str]) -> str:
    for arg in command:
        if arg.startswith("mcr.microsoft.com/playwright/mcp@sha256:"):
            return arg
    raise AssertionError("manifest does not pin the mcr.microsoft.com/playwright/mcp image by digest")


def browser_version(image: str) -> tuple[int, ...]:
    out = subprocess.run(
        ["docker", "run", "--rm", "--entrypoint", "sh", image, "-c", "exec /ms-playwright/chromium-*/chrome-linux*/chrome --version"],
        check=True, capture_output=True, text=True, timeout=TIMEOUT,
    ).stdout
    match = re.search(r"(\d+)\.(\d+)\.(\d+)\.(\d+)", out)
    if not match:
        raise AssertionError(f"could not read browser version from: {out!r}")
    return tuple(int(part) for part in match.groups())


def main() -> int:
    command = server_command()
    print("server command:", " ".join(command))

    version = browser_version(image_reference(command))
    print("browser version:", ".".join(map(str, version)))
    assert version >= MIN_BROWSER_VERSION, f"browser {version} is older than {MIN_BROWSER_VERSION}"

    client = StdioClient(command)
    try:
        info = client.request(
            "initialize",
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "smoke-test", "version": "0"}},
        )
        print("server:", info.get("serverInfo"))
        client.notify("notifications/initialized")

        tools = {tool["name"] for tool in client.request("tools/list")["tools"]}
        for required in ("browser_navigate", "browser_snapshot", "browser_evaluate", "browser_close"):
            assert required in tools, f"missing tool {required}"

        page = client.call_tool("browser_navigate", {"url": "data:text/html,<title>smoke-ok</title><h1>hello</h1>"})
        assert "smoke-ok" in page, page

        client.call_tool("browser_navigate", {"url": "chrome://sandbox"})
        status = client.call_tool("browser_evaluate", {"function": "() => document.body.innerText"})
        print(status)
        assert "You are adequately sandboxed." in status, "Chromium is not running sandboxed"
        assert "Seccomp-BPF sandbox\\tYes" in status, "Chromium seccomp-bpf layer is not active"

        client.call_tool("browser_close", {})
    finally:
        code = client.close()
        if client.stderr:
            print("server stderr:", "".join(client.stderr)[:2000], file=sys.stderr)
    assert code == 0, f"server exited with {code}"
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
