# Canvas image composition

Use this after discovering the destination and before composing its image
placements. The installed helper's schemas are authoritative; source edits or
a plugin version alone do not establish app capabilities.

## Capability and access checks

Discover `import_image` / `import_image_url`, Canvas destinations in their
instructions, and `apply_canvas_batch` with `addAssets` and `type:"image"`.
If unsupported, explain that the app/helper needs those capabilities. Keep
supported drawing usable; do not bypass scope with shell copies/downloads or
inject unsupported content through full-document writes. Updating a plugin
alone cannot add native tools.

A local source must be in an approved read scope. The existing Canvas needs
Read & write access; a user-supplied path alone grants no permission. Imports
accept local `.lcv`/`.gcv` destinations and explicitly requested public HTTPS
images or public X-post photos. Respect secret, cloud, symlink, size and URL
blocks. Do not store remote hotlinks or base64 payloads as Canvas assets.

## Import, register and place

1. Begin destination activity before preparation. Read its summary/revision and
   relevant elements; use `read_document` when existing asset records are needed.
   Read appearance for new drawn content. Preserve
   existing IDs, groups, layers and assets; renew the lease every 60 seconds.
2. Import all requested images first. For a local image, call `import_image`
   with the Canvas `documentPath` and approved `sourcePath`. For a requested
   public link, call `import_image_url` with `documentPath` and `sourceUrl`;
   it may return several images. Imports copy/reuse local assets and return
   `markdownPath`; they do not insert an image into the document.
3. Reread the latest Canvas revision after imports. For each unregistered image,
   choose a fresh asset ID and register `{id,type:"image",path}` in `addAssets`,
   using its returned `markdownPath` verbatim. Optional intrinsic asset width,
   height and MIME type need known values; omit them when unknown. Reuse an
   existing matching asset ID instead of replacing shared resources.
4. In the same coherent batch, add image elements with fresh IDs, the registered
   `assetId`, finite x/y and positive placed width/height. Choose intended layout
   bounds; preserve the known source aspect ratio unless a crop is requested.
   Keep annotations editable with Text, native shape labels, arrows and groups.
   Place backgrounds before images and annotations above them in paint order.
5. Use returned revisions for later batches. Adjust crop, corner radius,
   rotation or opacity only through fields exposed by the helper. See
   [image geometry](canvas-format.md#image-resources-in-supporting-helpers).
6. Render the saved Canvas, inspect actual pixels and adjust the composition.
   Check supported light/dark previews for annotation contrast; imported image
   colors stay original. Report unreadable assets or unavailable rendering
   honestly. Finish activity on success/failure and follow shared review handoff
   guidance. Saved rendering does not verify live app behavior or Finder.

For example, after importing a reference image into an existing approved Canvas:

```json
{"documentPath":"/approved/Board.lcv","sourcePath":"/approved/reference.png"}
```

Use the actual returned path, latest revision, lease and fresh IDs in the batch;
the example below assumes the returned path was `assets/reference.png`:

```json
{
  "path": "/approved/Board.lcv",
  "expectedRevision": "<latest revision>",
  "leaseId": "<your token>",
  "addAssets": [{"id":"asset-reference","type":"image","path":"assets/reference.png"}],
  "add": [{"id":"reference-image","type":"image","assetId":"asset-reference","x":80,"y":80,"width":640,"height":360}]
}
```

A crop update uses normalized source coordinates, not Canvas pixels:

```json
{
  "path": "/approved/Board.lcv",
  "expectedRevision": "<revision returned by the batch>",
  "leaseId": "<your token>",
  "update": [{"id":"reference-image","set":{"crop":{"x":0.1,"y":0.1,"width":0.8,"height":0.8},"cornerRadius":12}}]
}
```

The crop and rounding retain the imported original. The placed size in the
example is a layout choice, not a claim about the source's intrinsic dimensions.

## Recovery and resource limits

Imports are capped at 20 MiB per image. Saved rendering also bounds total/decoded
image input, pixels, output and document complexity; respect the helper's actual
limits and errors. `read_document` returns Canvas JSON, not source image pixels.

If import succeeds but insertion fails, retain that asset, reread the document
and reconcile the authorized insertion. Do not blindly reimport or replay a
batch after a lost response. A stale revision requires rereading and preserving
intervening user edits. Removing an image retains asset records/files for shared
references and Undo; do not delete them as cleanup. Follow the same rule when
replacing a placement's `assetId`; unrelated users of the original remain intact.

With an older helper, preserve existing image resources and explain missing
import, batch or render capabilities separately. Keep supported document/drawing
operations usable; do not strip images to force a render or promise that an
unpublished app update is available. Canvas images missing from Finder Quick Look
or thumbnails are a known deferred limitation of the 0.17.0 candidate; app/MCP
image composition and saved rendering do not establish Finder parity.
