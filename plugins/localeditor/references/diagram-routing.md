# Choose Mermaid or Canvas

Preserve an explicit format choice and the format of an existing target. A
request to revise a `.lcv` Canvas stays Canvas even if Mermaid could express it;
an existing Mermaid fence stays Markdown unless conversion is requested.

| Intent when no format was specified | Default | Workflow |
| --- | --- | --- |
| Structured flow, sequence, state/class/ER diagram, Git graph, timeline or other supported relationship diagram | Mermaid | An ordinary `.md` document with a `mermaid` fence; `create-localeditor-diagram` when available. |
| Wireframe, sketch, spatial idea board, precise/custom composition, manually positioned diagram or visual shape editing | Canvas | `.lcv` artwork through `draw-localeditor-canvas` when available. |
| Specification containing both flows and UI sketches | Markdown Page | Inline Mermaid for the flows and embedded Canvas for the spatial work; use `compose-localeditor-page` when available. |

Choose from the requested outcome, not the mere word “diagram.” A sign-in flow
with success/error branches defaults to Mermaid; a sign-in screen wireframe
defaults to Canvas. “Draw that flow on a Canvas” explicitly selects Canvas.
“Add an architecture diagram to this Page” does not by itself request a child
Canvas or a separate file. A request to move individual diagram shapes visually
selects Canvas for new work; ask about conversion before changing an existing
Mermaid file. Ask only when a meaningful ambiguity remains or neither format
can represent the request faithfully.

## Tools and capability boundaries

- Mermaid is plain Markdown source. New Scratchpads use `create_scratchpad`
  with content; existing Pages use `read_document` and revision-checked
  `write_document`. Project creates use `write_document` with `create:true` in
  an existing writable folder. No dedicated Mermaid creation tool is needed.
- Canvas uses its creation, summary, element, batch and render tools when
  advertised. A `.lcv` edit never becomes a Markdown write implicitly.
- `render_canvas` handles Canvas only. A successful Mermaid write/read confirms
  saved source, not syntax validity or visual quality. Do not invent a Mermaid
  render/validation tool or silently substitute Canvas to obtain a PNG.
- This Mermaid preview feature is advertised in the updated helper's initialize
  instructions. An older helper may still save portable Markdown fences without
  offering a diagram preview. If support is unadvertised, describe preview as
  unconfirmed and explain the app/helper requirement when it matters. Do not
  infer support from a plugin/helper version or claim an unpublished app release
  is available. Keep requested source work usable; switch formats only with the
  user's agreement.
- Standalone `.mmd`/`.mermaid` preview and Mermaid-to-Canvas conversion are not
  part of this integration. Preserve such existing source files when reading;
  do not create them as the diagram-preview destination.

Follow the shared document guidance for activity, revisions, permissions and
handoffs. Routing grants no additional access and does not change the user's
chosen destination.
