# LocalEditor Canvas JSON

Use this reference when creating or editing `.lcv` content. The available MCP
tool schema and the installed app remain the authority if versions differ.
Prefer batches as described in [canvas-mcp-workflow.md](canvas-mcp-workflow.md),
including fixed/adaptive fields and saved PNG inspection. This file describes
saved drawing geometry; activity overlays never become Canvas elements.

## Document

A new Canvas is:

```json
{
  "format": "localeditor-canvas",
  "version": 1,
  "elements": [],
  "bindings": [],
  "assets": [],
  "layers": []
}
```

Keep an existing `format` (including legacy `grove-canvas`), version, unrelated
top-level keys, assets and layers. Unknown top-level keys stay at the top level;
do not wrap them in an invented `extra` property. Preserve optional element
fields when changing geometry. All coordinates must be finite numbers.

## Elements and controls

Every element has `id`, `type`, `x`, `y`, `width`, and `height`.

| Canvas capability | Saved representation |
| --- | --- |
| Rectangle | `type: "rectangle"` |
| Rounded rectangle | `type: "rounded-rectangle"` |
| Ellipse | `type: "ellipse"` |
| Diamond | `type: "diamond"` |
| Text | `type: "text"`, with `text` |
| Arrow | `type: "arrow"`; endpoint is `(x + width, y + height)` |
| Frame | `type: "frame"`; children refer to it with `parentId` |
| Group | `type: "group"`; member elements refer to it with `parentId` |
| Pencil | `type: "stroke"`, with nonempty `points: [{"x": 0, "y": 0}, ...]` |
| Eraser/delete | Remove requested elements and bindings that reference them |
| Move/resize | Change element geometry and affected descendants/bindings |
| Duplicate | Copy elements with new IDs, translating geometry and remapping copied membership/bindings |
| Layers | `layers` entries and element `layerId` membership |
| Hand/Select, pan/zoom | UI controls; no saved drawing element or MCP gesture tool |
| Undo/Redo | UI history controls; MCP exposes document reads/writes, not history commands |

Use positive bounds for ordinary shapes. Arrow width and height are signed
endpoint deltas, allowing any direction. Shapes may have a `text` label.
Standalone text supports `fontSize`, `textWrap`, `textAutoSize`, and
`textMinHeight`; shape labels support `fontSize` and `labelAutoFit`. Preserve
existing text behavior unless the requested edit changes it. Positive font
sizes and nonnegative minimum heights are required.

## Pencil geometry

Stroke points are in Canvas units relative to the element's `x/y`; moving ink
changes that origin. Width/height describe its bounds. For new ink, calculate
the points' bounding box, put its top-left in `x/y`, subtract that origin from
all points, and use the box size for width/height. To resize ink, scale its
points along with its bounds; changing bounds alone does not redraw the points.
A closed outline repeats the first point at the end. Sample enough points for
smooth curves while keeping the complete document within the MCP size limit.

Example stroke element:

```json
{
  "id": "ink-1",
  "type": "stroke",
  "x": 100,
  "y": 100,
  "width": 40,
  "height": 30,
  "points": [{"x": 0, "y": 30}, {"x": 20, "y": 0}, {"x": 40, "y": 30}]
}
```

## Connections, containers, and layers

A connected arrow uses document-level bindings:

```json
{"arrowId": "arrow-1", "end": "end", "elementId": "shape-2", "side": "left"}
```

`end` is `start` or `end`; `side` is `top`, `right`, `bottom`, or `left`.
The arrow and target IDs must exist; `arrowId` must identify an arrow. Keep one
binding per endpoint. Set the arrow geometry consistently with its targets.

Container membership uses `parentId`, but child coordinates remain absolute
Canvas coordinates. Moving a container together with its contents requires
translating its descendants too. Do not create cyclic or dangling membership.
Keep group bounds consistent with the member bounds. When deleting a container,
either remove the requested descendants or clear their membership according
to the user's intended result; remove empty groups and stale bindings.

Layers have `id`, `name`, and optional `visible`/`locked`. Membership uses
`layerId`; array order controls layer stacking. Preserve hidden/locked state
and avoid editing locked content unless the user requests it. Element array
order also affects drawing order within a layer.

There is no supported `image` element or per-element color/style property in
this schema. Preserve existing asset records, but do not invent rendering
support by adding one. Importing an image into a Markdown Page is handled by
`compose-localeditor-page`.

To revert your own saved edit, reread the latest document and apply the inverse
change with its current revision, preserving intervening user edits. Do not
restore an entire old snapshot over newer work or claim to invoke UI Undo.
