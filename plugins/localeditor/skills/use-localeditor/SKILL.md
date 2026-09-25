---
name: use-localeditor
description: Discover, read, create, update, or open documents in the user's approved LocalEditor Projects and Scratchpads through LocalEditor Agent Access.
---

# Use LocalEditor

Use LocalEditor as a permission-scoped local document workspace. Keep Projects
and Scratchpads distinct, preserve the application's security boundaries, and
use revision-checked writes for existing documents.

## Prerequisites and recovery

- LocalEditor must be installed at `/Applications/LocalEditor.app` with a valid
  license or account-backed trial that includes Agent Access.
- **Settings → Agent Access → Allow MCP access** must be on. LocalEditor does
  not need to remain open after setup.
- **Full access** permits all Projects and Scratchpads. **Custom Access** grants
  each Project and the combined Scratchpads scope No access, Read only, or Read
  & write.
- If a tool reports that access is disabled or unavailable, name the exact
  requirement and ask the user to update LocalEditor. Do not bypass Agent
  Access with direct filesystem reads or writes.
- Retry once when an app handoff or helper connection may have failed
  transiently. Preserve successful file creation even if an open request fails.

## Discover before reading

- Call `list_projects` to discover Projects currently allowed by Agent Access.
- Call `list_project_files` with the exact returned Project path to discover
  files. Respect pagination instead of assuming the first page is complete.
- Call `list_scratchpads` to discover persistent Scratchpads when that scope is
  allowed.
- Do not infer access from a remembered path. Use the current tool results.
- Listings may expose filenames, including secret filenames, but never secret
  contents. Do not claim that a listed file is readable until `read_document`
  succeeds.

## Read and inspect documents

- Call `read_document` only with an absolute path inside an approved Project or
  Scratchpad scope.
- Treat the returned `revision` as the version of the bytes you read. Retain it
  for any proposed update to that document.
- Secret files, unsupported or oversized documents, symlink escapes, and files
  unavailable locally must remain unread. Do not work around these blocks.
- Use `resolve_local_path` only for an explicit handoff to another separately
  authorized local capability. It never authorizes access or returns content.

## Create and update documents

Before a write, state the exact destination and proposed change, and obtain the
user's approval when the client does not already provide an equivalent write
approval.

- Use `create_scratchpad` for every new Scratchpad. Supply a useful title when
  the user provided one; LocalEditor creates persistent Markdown and normally
  opens its compact review window.
- Use `write_document` to create an ordinary supported text document only when
  its parent directory already exists inside a writable Project.
- To update an existing Project or Scratchpad document, first call
  `read_document`, then pass its latest `revision` as `expectedRevision` with
  the full replacement content.
- If a revision is stale, read the latest document, reconcile the changes with
  the user's intent, and ask for approval again before retrying. Never overwrite
  an intervening edit blindly.
- Never use `write_document` to create a new Scratchpad.

## Open for review

- Use `open_in_localeditor` when the user asks to see a document or when review
  is a useful final step. This is an app handoff and does not return content.
- A successful `create_scratchpad` may report `opened: false` with an
  `openWarning`. Report that the file was created and separately explain that
  LocalEditor could not be opened.
- Do not describe an open request as proof that a write persisted; rely on the
  write result and, when needed, a subsequent read.

## Safety boundaries

- Never read or write `.env` files, credentials, private keys, certificates, or
  other paths LocalEditor classifies as secret.
- Do not create folders, move, rename, or delete files. Those operations are
  outside the current MCP contract.
- Do not run shell commands through LocalEditor or imply it provides general
  filesystem access.
- Do not upload document content to a LocalEditor service. LocalEditor MCP is a
  local `stdio` capability and LocalEditor remains the owner of its local state.
