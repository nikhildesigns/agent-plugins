# LocalEditor plugin

Version **0.4.0** adds theme-aware monochrome wireframes, Canvas styling and
rotation guidance, Pencil fill/smoothing, and coherent Page/document saves.
New features require a supporting native helper; older workflows remain usable.

This plugin lets an external agent read and edit your local documents, draw
editable Canvas wireframes and diagrams, and compose Markdown Pages with images
and linked subpages in approved LocalEditor Projects and Scratchpads.

The workflows cover coherent saves, Canvas styling/rotation, monochrome
wireframes, Pencil fill/smoothing, current/light/dark saved rendering and
fixed/adaptive activity fields when the connected helper supports them. Older
helpers remain usable through supported document and full-Canvas workflows.
Discover capabilities rather than inferring them from a version number.

This plugin connects local agent clients on macOS to the LocalEditor Agent
Access MCP helper installed at:

`/Applications/LocalEditor.app/Contents/Helpers/localeditor-mcp`

One package serves Claude Code and Codex with the same three skills in
`skills/`:

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

## What to ask

| Skill | When to use it | Example |
| --- | --- | --- |
| `use-localeditor` | Find, read, revise, or open documents; exchange Markdown Scratchpad checklists and notes. | “Read the design brief in my LocalEditor Project.” |
| `draw-localeditor-canvas` | Create/edit/style/rotate `.lcv` Canvases with shapes, text, arrows, frames, groups and Pencil strokes when supported. | “Draw a simple clover with Pencil on a LocalEditor Canvas Scratchpad.” |
| `compose-localeditor-page` | Import an image, create a child Page/Canvas, or read embedded documents. | “Add these reference images and a child Canvas to my LocalEditor note.” |

Both clients can select the same skills from these requests. Claude Code also
exposes explicit names such as `/localeditor:draw-localeditor-canvas`; Codex
exposes the installed skills for explicit invocation through its skill picker.
Mixed tasks can use more than one skill.

For Canvas work, prefer summary + bounded reads + coherent revision-checked
batches. Declare a fixed planned agent field by default; explicitly choose
adaptive growth at activity begin when needed. Inspect meaningful saved stages
with `render_canvas` before claiming visual quality. The
[Canvas workflow](skills/draw-localeditor-canvas/references/canvas-mcp-workflow.md)
covers batching, field semantics, visual checks and older-helper fallbacks.
Shared [document guidance](references/document-workflows.md) covers activity
renewal, coherent saves, WikiLinks, completion handoffs and upgrading while
keeping older helpers usable. Read current appearance before drawing and use
monochrome wireframes by default; inspect both themes when supported.
Composition also supports explicit
public HTTPS/X-photo import when `import_image_url` is exposed.

Discover actual helper schemas before using newer tools. These skills do not
replace the native helper; keep supported full-document workflows usable when
batching/rendering is absent. If session tools are unavailable, first follow the
[tool recovery guide](references/tool-recovery.md), including approved elevated
access and optional safe PNG output. A missing tool in the connected helper's
list establishes a capability gap. The helper version does not identify the
installed plugin version. Coordinate publication with matching app/helper
availability; source edits alone do not update installed clients. For missing
capabilities, update LocalEditor through its sidebar update control or the
[official download](https://localeditor.app), update the plugin separately using
the client instructions below, then reconnect/start a fresh chat and rediscover.
Do not promise that an unpublished feature is available in the latest release.

More document examples are on
[localeditor.app/agents](https://localeditor.app/agents.html).

## ChatGPT desktop and Codex

```sh
codex plugin marketplace add nikhildesigns/agent-plugins
codex plugin add localeditor@nikhildesigns-agent-plugins
```

The Codex compatibility manifest points to `./skills/`, while the portable
package uses the conventional root `skills/` directory. Both discover all
three workflows from the same files.

To update an existing installation:

```sh
codex plugin marketplace upgrade nikhildesigns-agent-plugins
codex plugin add localeditor@nikhildesigns-agent-plugins
```

Start a fresh chat after updating so it loads the new skills and helper schemas.

## Claude Code

Add the repository marketplace and install the plugin:

```sh
claude plugin marketplace add nikhildesigns/agent-plugins
claude plugin install localeditor@nikhildesigns-agent-plugins
```

To update an existing installation:

```sh
claude plugin marketplace update nikhildesigns-agent-plugins
claude plugin update localeditor@nikhildesigns-agent-plugins
```

Restart Claude Code after updating.

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
