# Devin marketplace

Plugins for Devin's marketplace.

## Using a plugin

In Devin: Settings → Marketplace, pick a plugin, install it. Credentials a
server needs are supplied in Devin; nothing in this repo holds one.

Or reference a plugin from your own plugin manifest, pinned to a commit of
this repo:

```json
{
  "requiredPlugins": [
    {
      "source": "git-subdir",
      "url": "https://github.com/CognitionAI/devin-marketplace.git",
      "path": "plugins/notion",
      "sha": "<commit>"
    }
  ]
}
```

## Contributing

See [`.agents/skills/adding-a-plugin/SKILL.md`](.agents/skills/adding-a-plugin/SKILL.md).

Write plugin `description` copy as one concise, action-oriented sentence about
what users can do and the value they get. Aim for 60–130 characters (about 200
maximum), without a trailing period, and expand on `shortDescription` rather
than repeating it. Avoid filler such as "integration" or "MCP server".

Put requirements outside the install form and connection caveats in optional
`setup`, immediately after `shortDescription`:
`{"notice": "...", "steps": ["..."]}`. Use a one- or two-sentence notice and
ordered steps without environment-specific URLs. At least one key is required;
`notice` must be a non-empty string and `steps` a non-empty list of non-empty
strings. No other keys are allowed. Do not repeat credential fields, placeholder
names, OAuth sign-in instructions, or default domains already handled by the
install form. Only add `setup` for external steps or meaningful connection caveats.

Contributions are accepted under the [Contributor License Agreement](CLA.md);
opening a pull request means you agree to it.

## License

[MIT](LICENSE)
