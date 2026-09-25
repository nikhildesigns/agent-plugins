# Moody plugin

This plugin connects local agent clients on macOS to the Moody Agent
Access MCP helper installed at:

`/Applications/Moody.app/Contents/Helpers/moody-mcp`

One directory serves two plugin formats and shares the same `use-moody` skill:

| Client               | Manifest                     | MCP config  |
| -------------------- | ---------------------------- | ----------- |
| Claude Code          | `.claude-plugin/plugin.json` | `.mcp.json` |
| ChatGPT desktop/Codex | `.codex-plugin/plugin.json` | `.mcp.json` |

A portable root `plugin.json` and `mcp.json` are included for compatible
clients and tooling.

Before using it:

1. Open Moody.
2. In **Settings → Agent Access**, enable **Allow agent access**.
3. Enable the separate Import, Organize, or Annotate items permissions only
   when those capabilities are needed.

## Claude Code

The repository root holds marketplaces that point at this directory. From a
clone of the repository:

```sh
claude plugin marketplace add /path/to/agent-plugins
claude plugin install moody@nikhildesigns-agent-plugins
```

Or, with access to the GitHub repository:

```sh
claude plugin marketplace add nikhildesigns/agent-plugins
claude plugin install moody@nikhildesigns-agent-plugins
```

For local development without installing, run
`claude --plugin-dir /path/to/agent-plugins/plugins/moody`.

The plugin registers the helper as its own MCP server, so its tools appear as
`mcp__plugin_moody_moody__*`. If you previously added Moody with the
`claude mcp add` command from Moody's Setup card, remove that entry
(`claude mcp remove moody -s user`) to avoid two copies of every tool.

The skill is available as `/moody:use-moody` and also loads automatically for
Moody requests.

## Library ownership

Moody remains the sole owner of its local SwiftData library. The helper talks
to the running app over a user-only local socket; it does not open the data
store itself. This local `stdio` integration is for desktop clients on the Mac
and does not make the library available to ChatGPT web or claude.ai.
