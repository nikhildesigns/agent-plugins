---
name: compose-localeditor-page
description: Compose a LocalEditor Markdown Page or Scratchpad with imported local images and embedded child Pages or Canvases, or inspect the contents of those children. Use for inserting an image into a LocalEditor note, creating a linked subpage/subcanvas, or reading a parent's embedded documents. Plain document edits and drawing the Canvas itself have separate skills.
---

# Compose a LocalEditor Page

Use the client's LocalEditor MCP tools, regardless of their client-specific
prefix. A Page is a Markdown `.md` file; embedded children are ordinary relative
links with a standard Markdown title marker. Images use ordinary image syntax.

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

Every call needs an eligible entitlement and the app's Agent Access toggle.
Discover current scope; parent and child edits require Read & write. Respect
secret-file, size, symlink, and unavailable cloud-file blocks. If
`create_embedded_document` or `import_image` is absent, explain that the installed
LocalEditor app/helper needs a version exposing it; never bypass with shell or
filesystem writes. These tools create their own `subpages/` or `assets/` folders,
not arbitrary folders.

On `revisionMismatch`, reread and reconcile with the existing authorization;
ask only if the changes conflict with the intended result. Retry transient
connection/open failures once. Preserve successful file creation when opening
fails and report any rollback failure with the returned remaining child path.
