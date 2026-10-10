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
| Rounded rectangle | Prefer `type: "rectangle"` + `cornerRadius` when supported; legacy `rounded-rectangle` remains readable |
| Ellipse | `type: "ellipse"` |
| Diamond | `type: "diamond"` |
| Text | `type: "text"`, with `text` |
| Arrow | `type: "arrow"`; unrotated endpoint is `(x + width, y + height)` |
| Frame | `type: "frame"`; children refer to it with `parentId` |
| Group | `type: "group"`; member elements refer to it with `parentId` |
| Pencil | `type: "stroke"`, with nonempty `points: [{"x": 0, "y": 0}, ...]` |
| Eraser/delete | Remove requested elements and bindings that reference them |
| Move/resize/rotate | Change element geometry and all intended descendants; rotation is absolute clockwise degrees |
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
Group bounds refit in their rotated axes. Batch removal cascades through all
descendants. To keep children when removing a container, reparent them in a
prior revision-checked batch before removing it; removal happens before updates.
Remove empty groups and stale bindings. Group each editable component, icon or
repeated motif; use labeled Frames for screens/concepts. Filled shapes must
precede the elements they contain in paint order.

Layers have `id`, `name`, and optional `visible`/`locked`. Membership uses
`layerId`; array order controls layer stacking. Preserve hidden/locked state
and avoid editing locked content unless the user requests it. Element array
order also affects drawing order within a layer.

There is no supported `image` element. Preserve existing asset records, but do
not invent rendering support by adding one. Importing an image into a Markdown
Page is handled by
`compose-localeditor-page`.

To revert your own saved edit, reread the latest document and apply the inverse
change with its current revision, preserving intervening user edits. Do not
restore an entire old snapshot over newer work or claim to invoke UI Undo.

## Optional styles in supporting helpers

Discover the connected helper's instructions and schema before adding these
fields. Older helpers may ignore them or reject a batch; a full-document write
is not a substitute for rendering support. Preserve existing unknown values.
Defaults are omitted; use update `unset` to reset a field rather than injecting
defaults throughout an existing document.

| Field | Values and behavior |
| --- | --- |
| `strokeColor`, `fillColor` | `ink`, `gray`, `red`, `orange`, `yellow`, `green`, `blue`, `purple`, or exact `#rrggbb`. Names adapt to themes; custom hex does not. Text/labels use stroke color. Unset fill color follows stroke color; custom-stroke fills use a theme-relative pale mix. |
| `fillStyle` | `none` (default) or `solid` on shapes, Frames and enclosed Pencil regions. Frame fill is a backdrop behind its children; its border remains. |
| `strokeStyle` | `solid` (default), `dashed`, or `none` to remove the outline of a fillable shape/stroke. Keep the Frame border. |
| `strokeWidth` | `thin`, `regular` (default), `thick`. |
| `opacity` | `0.1–1`; default `1`. Keep wireframe text at full opacity. |
| `cornerRadius` | Canvas units, `0–10000`, clamped to the shape; rectangles, Frames and diamonds. Legacy rounded rectangles use radius 12 until edited. |
| `smoothing` | Pencil only, `0–1`; zero restores the original polyline. |
| `arrowShape` | `straight` (absent default) or `curved`; new GUI arrows are curved, so set it explicitly for a curved MCP connector. |
| `fontFamily` | Text/shape labels: `freehand` (default), `sans`, `serif`, `mono`. Frame titles retain their fixed presentation. |
| `textAlign` | `left`, `center`, `right`; default left for Text and center for fitted shape labels. |

Wireframes default to `ink`/`gray`, with no fill or adaptive neutral fills.
Use colors/custom hex only when requested; do not copy resolved palette hex into
saved JSON. Avoid fixed white cards with theme-following text. Styling a group
means updating its eligible visible members; styling a container shape affects
that shape only. Preserve existing composition for styling-only requests.

### Pencil fill and smoothing

Solid fill uses the bounded regions of the smoothed Pencil path, including
self-crossing loops with open tails. Distant endpoints are not implicitly
joined; open tails stay unfilled. Repeating the first point closes an outline.
Near-start hand-drawn closure is allowed within 20% of the point-bounds diagonal
(minimum 12 units), for a diagonal of at least 24 units.

Increasing smoothing progressively rounds joints through arc-length sampling,
independent of recording density. Overall shape and exact endpoints remain;
derived curves stay inside source-point bounds. Original editable points are
unchanged, so do not replace them with derived samples or repeatedly smooth
already-derived points. Fill, ink selection and rendering follow this geometry.

### Rotation and connectors

`rotation` is a finite clockwise angle in degrees around each element's own
unrotated box center; absent/zero means no rotation. Coordinates and angles are
absolute, never inherited from `parentId`. To rotate a selection, transform each
selected root and every descendant exactly once: rotate its center around the
selection center, update x/y to retain its size, and add the angle to its own
rotation in the same batch. Keep Pencil points local and unchanged. Group bounds
refit in the group's rotated axes.

Bound arrow endpoints derive from the target's rotated attachment ports. Remove
an endpoint binding explicitly to rotate that endpoint away from its target.
Curved arrows leave/enter perpendicular to bound sides; free ends follow a
derived direction, and the arrowhead follows the curve's final tangent. Do not
invent control-point fields. Shift snapping and rotation cursors are GUI
behavior; MCP writes the intended numeric angle rather than keyboard gestures.
