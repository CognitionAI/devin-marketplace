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
