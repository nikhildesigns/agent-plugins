---
name: draw-localeditor-canvas
description: Create or edit a LocalEditor .lcv Canvas in an approved Project or Scratchpad. Use for wireframes, diagrams, icons, illustration concepts, idea boards, or Pencil/freehand artwork on a LocalEditor Canvas, and for styling, rotating, moving, resizing, organizing, or erasing its shapes, text, arrows, frames, groups, and strokes, including theme-aware colors, curved connectors, Pencil fill and smoothing when supported. Ordinary Markdown notes and raster image generation are separate workflows.
---

# Draw a LocalEditor Canvas

Use the client's LocalEditor MCP tools, regardless of their client-specific
prefix. Prefer incremental drawing with `apply_canvas_batch`; use revision-checked
`write_document` only for the full-document fallback. Read the shared
[activity, navigation and review guidance](../../references/document-workflows.md).

## Example workflows

| Use case | Example request | Workflow |
| --- | --- | --- |
| Wireframes | “Sketch two dashboard layout ideas in a LocalEditor Canvas.” | Use frames for screens, rectangles for UI regions, and readable text. Default to monochrome ink/gray and adaptive neutral fills or no fill; check both themes when supported. |
| Diagrams | “Map the sign-in flow with success and error branches.” | Draw labeled shapes and connected arrows; organize related steps in frames or groups. Read an approved existing spec when the user asks to base the diagram on it. |
| Icons | “Draw a simple clover icon with Pencil.” | Create sampled `stroke` paths in a Canvas; preserve editable ink and revise the requested details. |
| Illustration ideas | “Sketch three simple plant illustration concepts.” | Combine Pencil strokes and supported shapes; place each concept in its own frame for comparison. |
| Idea boards | “Explore three onboarding approaches side by side.” | Arrange short text notes and rough sketches in frames, then update the chosen direction while preserving alternatives. |

Use `create_canvas_scratchpad` for a quick standalone Canvas, or
`create_embedded_document` with the composition skill for a Canvas inside a
Markdown Page. Inspect bounded Canvas data, save coherent batches, render useful
saved stages for visual inspection, and hand off for review. These are editable vector sketches; follow the format
reference for supported elements and styles.

## Choose the destination

- Discover the named approved Project with `list_projects` and
  `list_project_files`, or find a Canvas with `list_scratchpads`.
- Create a new Canvas Scratchpad with `create_canvas_scratchpad` (`title`),
  then use its returned path. This normally opens the empty Canvas in compact review; MCP handoffs preserve an existing main window and keep it hidden on cold launch.
- For a new Canvas file in an existing writable Project folder, use
  `write_document` with `create: true` and the empty document from the format
  reference. Never create a new Scratchpad with `write_document`.
- A child Canvas inside a Markdown Page uses `create_embedded_document`;
  use `compose-localeditor-page` for that composition when available.

If the connected helper’s tool list lacks a needed tool after recovery, explain
that the installed LocalEditor app/helper needs a version exposing it. Do not substitute shell writes or a
Markdown Scratchpad for a requested Canvas.

## Draw or edit — batching preferred

Read [references/canvas-format.md](references/canvas-format.md) for element
geometry and [references/canvas-mcp-workflow.md](references/canvas-mcp-workflow.md)
for the drawing loop, fixed/adaptive agent fields, limits/retries and when to use
`render_canvas` for visual inspection.

1. Begin activity as soon as the existing approved Canvas path is known, before
   preparing drawing data or a generator. Prefer a declared fixed workspace for
   a planned drawing; explicitly choose adaptive only for exploratory growth.
2. Discover supported fields and read current appearance with
   `get_canvas_appearance` when exposed, or the `appearance` in a Canvas
   summary/full read when present.
   Use `get_canvas_summary` for the revision and `read_canvas_elements` for the
   needed pages/IDs. Preserve unrelated data and use stable unique element IDs.
3. Prefer coherent `apply_canvas_batch` calls with the latest `expectedRevision`
   and your `leaseId`. Save an early meaningful structure, then related details;
   avoid one call per shape. Use returned revisions for subsequent batches.
4. Renew every 60 seconds while preparing. Keep field mode stable across save
   speeds; correct bounds with renewal, or finish/begin to change modes.
5. Use `render_canvas` after meaningful saved stages and for final visual
   inspection; use a crop for local problems. When the render schema supports
   `theme`, inspect light and dark for contrast. Inspect actual pixels before
   claiming the drawing was visually checked. It does not test live app overlays.
6. Finish activity on success/failure. Follow shared review guidance: explicit
   show uses `activate:true`; ordinary completion preserves an already-open target.

If bounded/batch tools are absent after discovery/recovery, use `read_document`
and revision-checked `write_document` with the complete preserved JSON. Do not
send newer arguments to an older schema or add unsupported style/rotation
fields through full-document writes. Follow shared update guidance; keep basic
drawing usable and report any requested newer feature as pending. On a stale
revision or lost response, reread/reconcile saved data before retrying; never
blindly replay a batch.

Group each component, icon or repeated motif and frame each screen/concept,
with meaningful labels. Preserve the existing composition for styling-only
requests. Store palette names rather than copied hex; use color/custom hex only
when explicitly requested. Keep text at full opacity. Apply group styles to
eligible visible members; changing only the group does not style its children.
Move/resize/rotate all intended descendants explicitly in the same batch.

For Pencil, use `stroke` elements with sampled local points; do not replace
requested freehand ink with ellipses or a bitmap. For diagrams, use suitable
shapes/text/arrows. Preserve assets, layers and metadata outside the requested
change. If a successful Canvas cannot open or render, retain it and report the
remaining review limitation rather than recreating or replacing it.

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
