---
name: draw-localeditor-canvas
description: Create or edit a LocalEditor .lcv Canvas in an approved Project or Scratchpad. Use when the user wants shapes, a diagram, text, connected arrows, frames, groups, or Pencil/freehand artwork on a LocalEditor Canvas, or wants to move, resize, organize, or erase its elements. Ordinary Markdown notes and raster image generation are separate workflows.
---

# Draw a LocalEditor Canvas

Use the client's LocalEditor MCP tools, regardless of their client-specific
prefix. Drawing edits the saved `.lcv` JSON through `write_document`.

## Choose the destination

- Discover the named approved Project with `list_projects` and
  `list_project_files`, or find a Canvas with `list_scratchpads`.
- Create a new Canvas Scratchpad with `create_canvas_scratchpad` (`title`),
  then use its returned path. This normally opens the empty Canvas.
- For a new Canvas file in an existing writable Project folder, use
  `write_document` with `create: true` and the empty document from the format
  reference. Never create a new Scratchpad with `write_document`.
- A child Canvas inside a Markdown Page uses `create_embedded_document`;
  use `compose-localeditor-page` for that composition when available.

If the connected helper’s tool list lacks a needed tool after recovery, explain
that the installed LocalEditor app/helper needs a version exposing it. Do not substitute shell writes or a
Markdown Scratchpad for a requested Canvas.

## Draw or edit

Read [references/canvas-format.md](references/canvas-format.md) before writing
Canvas JSON. It covers every supported element type and editing operation.

1. Call `read_document` for an existing or newly created Canvas. Retain its
   revision and parse its JSON without discarding unrelated fields.
2. Apply the requested drawing or edit. Use stable unique IDs, finite
   coordinates, valid bindings and membership, and preserve existing elements,
   assets, layers, and metadata outside the requested change.
3. Call `write_document` with the full JSON and `expectedRevision` from that
   read. On a revision conflict, reread and merge; ask only if the intervening
   edit conflicts with the requested result.
4. Open the Canvas with `open_in_localeditor` for requested review. Report the
   saved path and what changed. An open result is not proof that the visual
   result is correct; obtain the user's visual feedback when needed.

For a Pencil request such as a clover icon, use `stroke` elements with sampled
local points. Do not silently replace freehand ink with ellipses or a bitmap.
For ordinary diagrams, choose shapes/text/arrows suitable for the user's goal.

## Access and recovery

If tools are missing from the session or helper startup is sandbox-blocked,
follow [the shared tool recovery guide](../../references/tool-recovery.md) first.
It covers discovery and approved elevated MCP access, including Codex.

Every call requires an eligible entitlement and the app's Agent Access toggle.
Discover the current approved scope; content writes need Read & write. Respect
secret-file, size, symlink, and cloud-file blocks without filesystem bypasses.
Keep existing user authorization; do not impose another approval for each
stroke. Retry a transient connection/open failure once and preserve a Canvas
that was created successfully even when opening fails.
