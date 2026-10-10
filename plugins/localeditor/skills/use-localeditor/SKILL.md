---
name: use-localeditor
description: Find, read, create, revise, or open ordinary documents in approved LocalEditor Projects and Markdown Scratchpads. Use for LocalEditor project briefs, specs, notes, document review, or Scratchpad checklists and user feedback. Canvas drawing and Markdown composition with images or embedded Pages/Canvases have separate skills; a generic mention of a project alone does not call for LocalEditor.
---

# Use LocalEditor

Use the LocalEditor MCP tools available in the client; their full names may
have a client-specific prefix. LocalEditor owns permissions and local files.
Read the shared [activity, navigation and review guidance](../../references/document-workflows.md)
for editing leases, WikiLinks, focus-preserving handoffs and helper/plugin updates.

## Example workflows

| Use case | Example request | Workflow |
| --- | --- | --- |
| Project brief | “Read the approved project notes and draft a feature brief.” | Discover the named Project, read relevant documents, then create the brief in the requested Project folder or a Markdown Scratchpad. |
| Document review | “Review this spec and update its acceptance criteria.” | Read the spec and its revision, apply the requested changes, preserve unrelated content, and open the saved document for review. |
| Testing and feedback | “Make a checklist for this change, then read my findings.” | Create one Scratchpad with checkbox checks and nested notes; later read it and summarize the user's marks and comments. |

For a visual exploration or a brief with linked sketches/images, combine this
skill with the Canvas or composition skill below.

## Discover and read

- Discover approved Projects with `list_projects`, then use the exact returned
  Project path with `list_project_files`. Follow pagination. Use
  `list_scratchpads` for persistent Scratchpads.
- Match the user's named Project and document; ask if several candidates fit.
  Read likely matches with `read_document`, not the entire Project by default.
  Name the documents used when summarizing or acting on their contents.
- A listed filename is not proof of content access. Retain the returned
  `revision` for edits. A remembered path does not establish current permission.

## Create or revise a document

- Follow the user's requested destination and existing authorization. If the
  destination or intended change is ambiguous, resolve that before writing.
- Create a Markdown Scratchpad with `create_scratchpad` (`title`, `content`).
  Supply the body without duplicating the title heading: the tool adds it.
- Create an ordinary supported Project text file with `write_document` using
  `create: true` only when its parent directory already exists in a writable
  Project. Never create a new Scratchpad using `write_document`.
- For existing-target edits, begin activity before preparation, then
  read with `read_document`, then use `write_document` with
  its absolute `path`, complete `content`, and `expectedRevision`. Preserve
  frontmatter, unrelated content, and the user's notes and check marks. Combine
  related changes into one revision-checked write; avoid a separate save for
  each paragraph or checklist item.
- On `revisionMismatch`, reread and reconcile the requested edit with the
  intervening changes. Retry under the existing authorization; ask only when
  reconciliation changes the intended result or creates a conflict.

Renew activity every 60 seconds while preparing and finish on success/failure.
A new Scratchpad returns its path before you can begin a lease to populate it.

For Canvas drawing, use `draw-localeditor-canvas` when available; it prefers
batches. For image imports or child Pages/Canvases in Markdown, use `compose-localeditor-page`.

## Scratchpad handoffs and feedback

When asked to hand over checks or tasks, create one descriptive Markdown
Scratchpad for that work item. Use `- [ ]` items with short steps and expected
behavior, and a nested line for the user's notes. Do not mix unrelated runs.

When the user asks you to read their findings, locate and read that Scratchpad.
Interpret checked items with their notes: an unchecked item alone may mean it
has not been tested. Summarize the findings and continue the authorized work.
Preserve the user's marks and notes when updating the document.

## Open for review

Finish activity before review. Use `open_in_localeditor` with an existing absolute
path and `activate:true` for an explicit show request. Routine completion may
omit activation, preserving an exact already-open target’s tab/window/focus.
It can hand off a file outside an approved content scope without authorizing reads or writes there. A new Scratchpad
normally opens automatically. If its result has `opened: false`, report the
created path and `openWarning`; do not recreate the successful file.

## Access and recovery

If tools are missing from the session or helper startup is sandbox-blocked,
follow [the shared tool recovery guide](../../references/tool-recovery.md) first.
It covers discovery and approved elevated MCP access, including Codex.
If an older helper lacks a requested capability, follow the shared app/plugin
update guidance and continue the document operations it supports. Do not infer
feature support from a version number or send unsupported arguments.

LocalEditor must be installed in `/Applications`, have an eligible license or
trial, and have **Settings → Agent Access → Allow MCP access** enabled.
Full access or Custom Access must grant the relevant Project/Scratchpads scope;
content edits need Read & write. The app need not remain open after setup.

Respect disabled access, secret-file, size, symlink, and unavailable cloud-file
errors. State the reported requirement; never bypass a block with filesystem
or shell access. `resolve_local_path` is a path-only handoff to a separately
authorized capability, not permission to read content. The MCP bridge does not
provide general folder creation, move, rename, delete, or shell operations.
Retry a transient connection/app handoff once; preserve successful writes if
opening fails. Do not upload content to a LocalEditor service.
