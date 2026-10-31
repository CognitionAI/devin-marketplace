# Playwright

Runs Microsoft's published Playwright MCP image
(`mcr.microsoft.com/playwright/mcp`), pinned by digest, over stdio.

`seccomp.json` is the Docker seccomp profile that Playwright ships for its own
container images (`utils/docker/seccomp_profile.json` in
[microsoft/playwright](https://github.com/microsoft/playwright)). It extends
Docker's default profile with the user-namespace calls Chromium's sandbox needs,
so the browser runs with its sandbox enabled instead of `--no-sandbox`.

To bump the image, pick a release tag of
[microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp), resolve
its digest on `mcr.microsoft.com`, update `plugin.json`, and run
`python3 plugins/playwright/tests/smoke_test.py` (needs Docker).
