# Adding a plugin

The repo is itself a Devin plugin: `.devin-plugin/plugin.json` lists every
offering under `optionalPlugins`, and that file is the only thing consumers
read. Two kinds of entry: `"./plugins/<slug>"` for a plugin authored here (every
MCP server Devin hosts has one), and a `{ "source", "url", ["path",] "sha" }`
object for a third-party plugin pinned to an exact commit. Entries are sorted
and each identity appears once; `python3 scripts/validate.py` enforces all of
this and CI runs it.

## An MCP server we host

1. Create `plugins/<slug>/.devin-plugin/plugin.json`, where `<slug>` is the
   marketplace server slug:
   * `name` is the slug; `displayName` is the server definition's `name`
     (the human title, e.g. `"MySQL"`); `description`, `homepage`,
     `repository`, `keywords` come from the server definition too.
   * Check the brand mark in as `plugins/<slug>/logo.svg` (or `.png`/`.jpg`)
     and set `"logo": "logo.svg"` — a path relative to the plugin directory,
     as in Cursor's plugin format. Prefer this over an absolute `https` URL so
     cards never load images from a third-party host.
   * `mcpServers` declares exactly one server, keyed by the slug: `command` +
     `args` + `env` for stdio, or `url` (+ `headers`) for HTTP.
   * Never check in a credential. Anything a user supplies is a plain
     `${<NAME>}` placeholder, resolved from the credentials saved on the
     user's installation (no `MCP_` prefix). A stdio `env` value must
     reference its own key (`"AWS_PROFILE": "${AWS_PROFILE}"`) because a saved
     credential replaces the env entry with the same key; in `args` and
     `headers` the placeholder is the credential's only name.
2. Add `"./plugins/<slug>"` to `optionalPlugins` in `.devin-plugin/plugin.json`.

## A third-party plugin

1. Review the vendor and the exact upstream commit you are endorsing.
2. Add an object to `optionalPlugins`:
   * whole repository: `{ "source": "url", "url": "https://github.com/<owner>/<repo>.git", "sha": "<40-hex>" }`
   * plugin inside a repository: `{ "source": "git-subdir", "url": "...", "path": "<dir>", "sha": "<40-hex>" }`

   Always pin a full 40-hex commit sha, never a branch or tag. Do not add
   display metadata; the plugin's own manifest at that sha supplies it. If we
   host the same integration ourselves, author it under `plugins/` instead of
   pointing upstream.

## Both

1. Run `python3 scripts/validate.py --fix` to sort and format the manifest,
   then `python3 scripts/validate.py --fetch` to confirm upstream pins resolve.
2. To bump an upstream plugin, change its `sha`. To remove one, delete its
   entry (and its `plugins/<slug>` directory if it was authored here).
3. Consumers pin this repo by commit; after the change lands on `main`, bump
   their pin to the new sha.
