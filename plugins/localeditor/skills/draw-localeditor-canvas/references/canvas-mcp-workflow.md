# Incremental Canvas workflow, agent field and visual inspection

The connected helper's schemas are authoritative. Prefer bounded reads and
`apply_canvas_batch` over rewriting the full Canvas on every step. If those
tools are absent after discovery/recovery, use the revision-checked full-document
workflow the helper supports; updating the plugin alone does not add tools.

## Preferred drawing loop

1. Create or discover the approved Canvas. Begin activity immediately when its
   existing path is known, before preparing drawing data or a script. Declare
   a planned region if known; see the field choices below.
2. `get_canvas_summary({path})` supplies the saved revision, counts and stored
   geometry bounds without all drawing bytes. For an edit, inspect only the
   necessary pages or exact IDs with `read_canvas_elements`.
3. Submit coherent `apply_canvas_batch` operations using `path`, the latest
   `expectedRevision` and your `leaseId`. Start with meaningful structure (a
   screen frame or central motif), then related sections/rings/details. Do not
   make one call per primitive or delay saves just to animate the cursor.
4. Use each returned revision for the next batch. Renew every 60 seconds while
   preparing; successful batches with the token renew expiry, but do not change
   declared workspace bounds. Inspect saved stages visually when useful.
5. Finish activity on success or failure, then use the shared handoff guidance.

Batch ceilings are 100 requested items total and 64 KiB of compact request JSON;
the resulting Canvas remains capped at 1 MiB. These are ceilings, not a target
batch size. Large Pencil paths may need fewer elements or lower sampling.
Generated JSON can go to the configured helper caller's stdin without being
read/retyped through model context. This is transport, not a shell-execution tool.

Bounded reads default to 25 elements, at most 100 and 24 KiB including bindings.
`read_canvas_elements` returns `nextOffset`; continue with that and the same
`expectedRevision` and selection. Do not mix pages from different revisions.
Exact-ID selections fail atomically when any ID is absent; use bounded
`details.missingIds`, `missingCount`, and `missingIdsTruncated` to reconcile.
If a single element exceeds the bounded-read budget, the supported
`read_document` escape hatch can inspect the complete document.

For an existing pair of inspected labels, one coherent batch can update both:

```json
{"path":"/approved/Canvas.lcv","expectedRevision":"<saved revision>","leaseId":"<your token>","update":[{"id":"<first label ID>","set":{"text":"Sign in"}},{"id":"<second label ID>","set":{"text":"Create account"}}]}
```

Batches support `add`, `update` (`id`, `set`, `unset`), `remove`, `setBindings`,
`removeBindings` and optional `order`. Preserve unknown fields and stable IDs.
Moving/resizing a container does not implicitly transform children or Pencil
points: submit the intended descendant changes. Removing a container cascades
through descendants. Removing a target detaches surviving arrow endpoints at
their saved positions; explicitly remove the connector if it should disappear.
Use current tool schemas for fields, binding targets and ordering anchors.

On `revisionMismatch`, reread the summary/relevant elements and reconcile. A lost
response or I/O error has an uncertain save outcome: check saved IDs/revision
before retrying. Never blindly replay additions. If a save returns
`activityUpdated:false`, preserve that successful save and repair/rebegin
activity separately; do not replay drawing just to repair its indicator.

## Choose the agent field

The field declares intended work, not saved artwork, a progress percentage or a
simulated cursor. It is an app-only overlay; never add fields/badges to Canvas JSON.

| Situation | Choice | Expected behavior |
| --- | --- | --- |
| Planned wireframe, diagram, icon or illustration with known bounds | Fixed, the default; prefer this | The complete planned workspace is visible before the first save and holds still across both fast and slow batches. |
| Exploratory work whose affected area should grow/move with saved changes | Explicit `fixed:false` at begin | Adaptive presentation follows the caller's changed artwork, excluding unrelated existing content; growth can shift as batches arrive. |
| Workspace not yet known | Begin with paths only | Show document activity without inventing a Canvas field; declare fixed bounds on renewal when known. |

Example fixed declaration (omitting `fixed` also means true):

```json
{"paths":["/approved/Canvas.lcv"],"regions":[{"path":"/approved/Canvas.lcv","bounds":{"x":40,"y":40,"width":720,"height":480},"fixed":true}]}
```

For adaptive growth, use the same declaration with `"fixed":false` explicitly
at begin; omitting the flag chooses fixed.

Choose bounds in Canvas/world coordinates covering the intended work plus a
reasonable margin, not viewport pixels. Coordinates must be finite and extents
positive. Read guidance may suggest existing-artwork bounds; adjust them to the
new plan. An empty Canvas has no honest inferred workspace until you choose one.

The mode is selected at begin and retained through finish. Renew can replace or
correct bounds; omitted/null `regions` keeps them and `regions:[]` clears them
without changing mode. Repeat `fixed:false` whenever renewing adaptive bounds.
Renew cannot add paths or switch modes; finish and begin a new lease for that.
Do not change fixed/adaptive mode because writes become faster or slower: cadence
controls cursor versus pulse feedback independently. Use one lease per Canvas
when independent latest batch receipts matter. Do not invent another agent's
identity/token or make brand marks part of the drawing.

## When to use render_canvas

Use `render_canvas` to inspect an existing Canvas when the user's question is
visual, after the first meaningful layout, after a substantial geometry/text
change, and before reporting a final drawing as visually checked. Rendering
after every batch is unnecessary. Check composition, overlaps, arrow endpoints,
labels, margins and cropping; revise through batches and render again if needed.
JSON validity and element counts alone do not establish visual quality.

Render the saved revision you intend to inspect:

```json
{"path":"/approved/Canvas.lcv","expectedRevision":"<latest saved revision>"}
```

For a crowded label, connector or local detail, use a crop in Canvas coordinates:

```json
{"path":"/approved/Canvas.lcv","expectedRevision":"<latest saved revision>","crop":{"x":-20,"y":40,"width":240,"height":180},"maxDimension":2048}
```

The tool returns PNG pixels and metadata for the same saved snapshot: revision,
rendered bounds and pixel dimensions. Whole-image output fits artwork with
padding; crops are exact, including negative origins and blank space. Use
returned bounds/dimensions to map pixels to world coordinates; summary bounds
are stored geometry and need not include label overflow. Crop extents are at
least one Canvas unit. `maxDimension` is the longest pixel edge, default 2048,
allowed 64–4096; a small crop is not guaranteed to fill that size (upscaling is
capped). Stale `expectedRevision` fails rather than inspecting another version.

Rendering is read-only and headless: it does not open/switch the app or include
selection, activity fields, cursors or unsaved GUI edits. It uses a white
background and the bundled Canvas font; it does not verify live progress,
theme, viewport, gestures or Finder packaging. Those remain separate user checks.
Nonempty assets/layers and excessive complexity are rejected. Preserve user
data; do not strip unsupported content merely to force a successful render.

Inspect the native image block with the host's image capability. For recovery,
use the caller's PNG-output option and an independently authorized destination
as described in the shared recovery guide; inspect the returned file through
the host's image viewer. Do not print base64 into model context. If image
inspection or `render_canvas` is unavailable, report visual verification as
pending and request user review; keep supported drawing tools usable. A rendered
PNG never replaces the requested editable `.lcv` file.
