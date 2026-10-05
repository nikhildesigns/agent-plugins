---
name: compose-localeditor-page
description: Compose a LocalEditor Markdown Page or Scratchpad with imported local images and embedded child Pages or Canvases, or inspect the contents of those children. Use for LocalEditor code-context hubs, component references, linked flow documentation, image insertion, child Pages/Canvases, or reading embedded documents. Plain document edits and drawing the Canvas itself have separate skills.
---

# Compose a LocalEditor Page

Use the client's LocalEditor MCP tools, regardless of their client-specific
prefix. A Page is a Markdown `.md` file; embedded children are ordinary relative
links with a standard Markdown title marker. Images use ordinary image syntax.

## Example workflows

| Use case | Example request | Workflow |
| --- | --- | --- |
| Feature proposal | “Create a proposal with a wireframe Canvas and a detailed notes Page.” | Create the Markdown parent, add child Canvas/Page links with `create_embedded_document`, then populate each child; use the Canvas skill to draw the wireframe. |
| Reference collection | “Add these local reference images to my design brief.” | Import images from an approved read scope, insert the returned relative image paths with revision-checked writes, and open the brief for review. |
| System explainer | “Add an architecture diagram and a child Page explaining each component.” | Embed a Canvas for the diagram and a Markdown Page for the explanation; keep the parent's returned links intact. |
| Component references | “Create a LocalEditor reference Page for the Button component, with subpages for props, variants, and accessibility.” | Inspect the relevant source, create the parent reference Page, and add child Pages with source-backed details and code-file links. |
| Flow documentation | “Document sign-in, recovery, and sign-out with an index and a subpage for each flow.” | Read the implementation, create the flow index, then populate each child Page with entry points, steps, states, and edge cases; link related flows. |
| Code-context hub | “Create a context Page for this feature linking its components, flows, and implementation notes.” | Build a concise parent overview and linked detail Pages so users and agents can read the overview first and open only the relevant details. |
| Linked-document review | “Read this proposal and its linked Pages/Canvases, then summarize the open questions.” | Read the parent, resolve relevant marked links, read each child separately, and name the documents used in the summary. |

Use child Canvases for editable drawings and Markdown image references for
imported images. A child link does not include its contents in the parent read;
inspect the relevant children explicitly.

## Context around code

Ground component and flow references in source inspected through an authorized
code-reading capability. Include relevant source paths/symbols, component
responsibilities and public APIs, flow entry points and states, edge cases, and
confirmed decisions. Mark unresolved questions explicitly; filenames alone do
not establish implementation behavior.

Use a parent Page as the index and child Pages for focused details. Create and
link them through `create_embedded_document`, then fill or revise their Markdown
through revision-checked `write_document`. Link actual source files with ordinary
Markdown links using paths relative to the reference file where practical.
When asked to refresh references, reread the affected source and documents and
update the relevant children while preserving unrelated notes and parent links.

## Locate the parent

Discover the named approved Project and files with `list_projects` and
`list_project_files`, or use `list_scratchpads`. Follow pagination and resolve
ambiguous names before writing. Read the Markdown parent with `read_document`.
For a new Markdown Scratchpad, use `create_scratchpad` and its returned path;
for a Project file, use `write_document` with `create: true` in an existing
writable folder.

## Create a child Page or Canvas

1. Read the parent and retain its latest `revision`.
2. Call `create_embedded_document` with `parentPath`, `expectedRevision`, a
   nonempty single-line `title`, and `kind: "page"` or `kind: "canvas"`.
3. The tool creates the child and appends its link to the parent. Use the
   returned `path` and `link`; do not append a duplicate link or guess the
   filename. The result's `parentRevision` describes the changed parent.
4. Read the child, then populate it with revision-checked `write_document`.
   For Canvas drawing, use `draw-localeditor-canvas` when available.
5. Reread the parent before later edits, preserving the inserted link and any
   intervening user changes. Open the parent or child for requested review.

Children live in a shared `subpages/` folder. Creating a child of an existing
child reuses that folder, so a link may be a sibling filename. Treat the tool's
returned link as authoritative, including encoding and collision suffixes.

## Read an embedded child

Read the parent first. Find marked links such as:

```markdown
[Notes](subpages/Notes.md "localeditor:page")
[Diagram](subpages/Diagram.lcv "localeditor:canvas")
```

Resolve the relative, percent-encoded target against the parent's folder and
call `read_document` on the resulting absolute path in the approved scope.
The parent's content does not recursively contain its child bytes. A Canvas
read returns JSON, not a screenshot. Inspect relevant children only and name
which documents informed the answer. Report missing or blocked targets; do
not claim access merely because the parent contains a link.

## Import and insert a local image

1. Identify an existing local source image in an approved read scope and an
   existing Markdown destination in a Read & write scope. A path supplied by
   the user alone does not grant MCP access to another folder.
2. Call `import_image` with `documentPath` and `sourcePath`. The helper copies
   or reuses the image in `assets/` and returns `markdownPath`.
3. Reread the destination, then insert `![descriptive alt text](markdownPath)`
   using the returned path verbatim and `write_document` with the latest
   `expectedRevision`. Preserve frontmatter and unrelated Markdown.
4. Report the saved document and image. If the document write fails after the
   import, retain the successful asset, reconcile the document, and retry the
   authorized insertion; do not repeatedly import or claim the image is linked.

Imports accept local images up to 20 MB. The helper does not return image pixels
through `read_document`, which reads supported text documents. Removing a
Markdown image reference does not automatically trash an MCP-imported asset.

## Access and recovery

If tools are missing from the session or helper startup is sandbox-blocked,
follow [the shared tool recovery guide](../../references/tool-recovery.md) first.
It covers discovery and approved elevated MCP access, including Codex.

Every call needs an eligible entitlement and the app's Agent Access toggle.
Discover current scope; parent and child edits require Read & write. Respect
secret-file, size, symlink, and unavailable cloud-file blocks. If the connected
helper’s tool list lacks `create_embedded_document` or `import_image` after
recovery, explain that an app/helper update is required; never bypass with
shell or filesystem writes. These tools create their own `subpages/` or `assets/` folders,
not arbitrary folders.

On `revisionMismatch`, reread and reconcile with the existing authorization;
ask only if the changes conflict with the intended result. Retry transient
connection/open failures once. Preserve successful file creation when opening
fails and report any rollback failure with the returned remaining child path.
