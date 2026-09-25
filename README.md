# Nikhil's Agent Plugins

Public plugin marketplace for Nikhil Yadav's macOS apps. Add this repository
once, then install Moody, LocalEditor, and future plugins independently.

Each plugin contains the integration metadata, MCP configuration, skills, and
artwork needed by supported agent clients. The signed MCP executable itself is
distributed inside the corresponding macOS app; this repository does not ship
or download application binaries.

## Available plugins

| Plugin | What it does | Required app |
| --- | --- | --- |
| `moody` | Search, review, import, organize, and annotate a local visual-inspiration library. | [Moody](https://usemoody.com) |
| `localeditor` | Read and update approved Projects and Scratchpads with LocalEditor's Agent Access controls. | [LocalEditor](https://localeditor.app) |

## ChatGPT desktop and Codex

Add the marketplace once:

```sh
codex plugin marketplace add nikhildesigns/agent-plugins
```

Install either plugin independently:

```sh
codex plugin add moody@nikhildesigns-agent-plugins
codex plugin add localeditor@nikhildesigns-agent-plugins
```

## Claude Code

Add the marketplace once:

```sh
claude plugin marketplace add nikhildesigns/agent-plugins
```

Install either plugin independently:

```sh
claude plugin install moody@nikhildesigns-agent-plugins
claude plugin install localeditor@nikhildesigns-agent-plugins
```

## Requirements

- macOS with the corresponding app installed in `/Applications`.
- Agent Access enabled in the app.
- A supported agent client running on the same Mac.

These are local `stdio` integrations. They do not make local app data available
to ChatGPT web or claude.ai. If an app was previously registered manually as an
MCP server, remove that old registration before installing its plugin to avoid
duplicate tools.

## Repository structure

```text
.agents/plugins/marketplace.json       Codex and ChatGPT catalog
.claude-plugin/marketplace.json        Claude catalog
plugins/moody/                         Moody plugin package
plugins/localeditor/                   LocalEditor plugin package
```

Each plugin owns its version, client manifests, MCP configuration, skill,
artwork, requirements, and documentation. No npm package is required because
the signed helper is part of the installed macOS app.

For compatibility with the current Codex plugin loader, each package includes
`.codex-plugin/plugin.json` in addition to the portable root `plugin.json`.

## License

The integration packages in this repository are available under the MIT
License. The Moody and LocalEditor applications are distributed separately
under their own terms.
