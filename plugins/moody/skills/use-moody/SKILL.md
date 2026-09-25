---
name: use-moody
description: Search, inspect, show, import, organize, or annotate visual inspiration in the user's local Moody library through Moody Agent Access.
---

# Use Moody

Use Moody as a local visual-inspiration workspace. Keep media and metadata on
the user's Mac, use the smallest relevant MCP response, and preserve the
distinction between Library items, temporary Agent Results, and Collections.

## Prerequisites and recovery

- Moody must be open with **Settings → Agent Access → Allow agent access** on
  and an active or offline-grace license.
- Read access is available whenever Agent Access is ready. Imports,
  organization, and caption edits each have separate off-by-default permissions.
- If a tool reports that Moody is unavailable, retry once when the failure may
  be transient. Otherwise tell the user to open Moody or enable Agent Access.
- If a write reports a missing capability, name the exact Settings permission
  it requires and wait for the user to enable it.
- Never bypass Moody by opening its SwiftData store or scanning its Application
  Support folder.
- If the client defers MCP tool definitions (for example Claude Code's tool
  search), load the Moody tool schemas before the first call. Never call a
  Moody tool without its required arguments to discover its shape.

## Search and show results

For exploratory requests such as "show inspiration like X":

1. Call `search_inspiration` with the user's concepts.
2. Call `show_results_in_moody` with the returned `resultSetID` so the user sees
   the complete visual gallery.
3. Do not list all tags or Collections first.

Omit the search query for newest-first items or capture-date requests. Use
`capturedFrom`, `capturedBefore`, and `sortBy: "capturedAt"` when appropriate.
Link imports use import time as `capturedAt`; Photos imports retain the photo's
original capture date.

Use `query_library_items` only for exact Collection or tag membership, passing
the user's Collection or tag names directly. Use `list_collections` or the
bounded, filtered `list_tags` only when discovery or disambiguation is needed.

Every search or exact query returns a `resultSetID` for its full ordered match
set, not just the current text page. Pass an optional member `itemID` to
`show_results_in_moody` to focus that item while retaining the full gallery.

The user may remove tiles from Agent Results without deleting Library items.
After they curate the gallery, call `get_current_agent_results` and use the
returned revision's `resultSetID` for follow-up work or saving.

## Inspect selected items

- Use `get_inspiration_details` only for selected item IDs and requested fields.
- Use `get_inspiration_assets` directly when item IDs are already known; do not
  repeat a search. It returns explicit local paths, not media bytes.
- Inspect returned media with an available local-file or visual capability.
  Do not claim visual facts based only on metadata.
- Moody deep links and `show_results_in_moody` are for navigation. Local asset
  paths are for inspection and must not be substituted as navigation links.

## Import media and links

Before calling `import_media` or `import_links`, state the exact paths or URLs
and obtain the user's approval. The client may also present its normal write
approval.

- `import_media` accepts explicit absolute image, GIF, or video file paths.
  Never pass a directory or scan sibling files.
- `import_links` accepts explicit public HTTP or HTTPS URLs. Preserve the full
  supplied URL, including query parameters.
- Report each input's result, including imported item IDs, duplicates,
  unsupported inputs, failures, and partial asset failures.
- Imports add items to the Library but leave them unfiled. If the user also
  requested organization, make the Collection save a separate approved action.

## Organize with Collections and tags

Before `save_to_collection` or `add_tags`, show the exact proposed change and
obtain approval.

- `save_to_collection` accepts exactly one source: explicit `itemIDs` or a
  `resultSetID` for the full cached set.
- It accepts exactly one destination: `collectionID`, `collectionName`, or
  `newCollectionName`.
- Collection membership is additive. Report added, already-present, and skipped
  counts.
- `add_tags` is additive and case-insensitively deduplicated. State the exact
  item IDs and tag names before calling it.
- Both operations require **Organize tags and Collections** in Moody Settings.

## Annotate inspiration

For a caption or tag request:

1. Resolve the exact live item ID.
2. Fetch its asset path and inspect the media. Fetch existing details if useful.
3. Draft a concise factual caption and a few relevant tags yourself.
4. Show the exact item ID, caption, and tags to the user and wait for approval
   or revision. Do not ask the user to author the initial wording.
5. After approval, call `annotate_inspiration` with only the approved values.

If inspection is unavailable, explain the limitation and do not invent visual
details. Caption changes require **Edit captions**; tag additions require
**Organize tags and Collections**; a combined edit requires both. Existing
tags remain, and an intentional caption is protected from background AI
replacement.

## Safety boundaries

- Reads may run without action approval; respect every client approval shown
  for writes.
- Do not delete, trash, permanently remove, rename, or subtract metadata. Those
  mutations are outside the supported MCP contract.
- Do not infer permission from a local path or retained source URL. Read only
  explicit returned or user-supplied files, and fetch only explicit approved
  public links.
- Never describe temporary Agent Results as a Collection or imply that import
  automatically filed an item.
