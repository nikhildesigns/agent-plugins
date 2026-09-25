# LocalEditor plugin

This plugin connects local agent clients on macOS to the LocalEditor Agent
Access MCP helper installed at:

`/Applications/LocalEditor.app/Contents/Helpers/localeditor-mcp`

One directory serves two plugin formats and shares the same `use-localeditor`
skill:

| Client | Manifest | MCP config |
| --- | --- | --- |
| Claude Code | `.claude-plugin/plugin.json` | `.mcp.json` |
| ChatGPT desktop/Codex | `.codex-plugin/plugin.json` | `.mcp.json` |

A portable root `plugin.json` and `mcp.json` are included for compatible
clients and tooling.

Before using it:

1. Install LocalEditor in `/Applications`.
2. Open **Settings → Agent Access**.
3. Turn on **Allow MCP access**.
4. Choose **Full access** or grant the required Project and Scratchpad access.

The plugin requires a LocalEditor license or account-backed trial that includes
Agent Access. LocalEditor remains the authority for every permission check.

## Claude Code

Add the repository marketplace and install the plugin:

```sh
claude plugin marketplace add nikhildesigns/agent-plugins
claude plugin install localeditor@nikhildesigns-agent-plugins
```

For local development without installing, run
`claude --plugin-dir /path/to/agent-plugins/plugins/localeditor`.

The plugin registers the helper as its own MCP server, so its tools appear as
`mcp__plugin_localeditor_localeditor__*`. If LocalEditor was previously added
with `claude mcp add`, remove that entry with
`claude mcp remove localeditor -s user` to avoid duplicate tools.

## Local ownership and security

The helper reads LocalEditor's existing local configuration on every tool call.
It only exposes Projects and Scratchpads approved in Agent Access. Secret-file
contents are blocked, document writes require read/write permission, and edits
to existing documents require the latest content revision.

The helper runs over local `stdio`; it does not upload document content to a
LocalEditor service and does not make local files available to ChatGPT web or
claude.ai.
