---
name: use-moody
description: Search, inspect, show, import, organize, annotate, or comment on media, saved posts and page previews in the user's local Moody library through Moody Agent Access.
---

# Use Moody

Use Moody as a local inspiration workspace for media, complete available social
posts, text-only posts and page previews. Keep Library items, temporary Agent
Results and Collections distinct. Use the smallest relevant response.

## Prerequisites and recovery

- Moody must be open with **Settings → Agent Access → Allow agent access** on
  and an active or offline-grace license.
- Search/view is on by default. Import, Organize, Annotate items and **Edit
  personal comments** are separate off-by-default permissions.
- Discover the connected helper's tool schemas before calling tools, including
  deferred definitions in clients such as Claude Code. Never omit required
  arguments to discover a tool's shape.
- If Moody is unavailable, retry once if transient; otherwise report the exact
  app, license or Settings requirement. Wait for missing permission to be enabled.
- The installed app supplies tools; this plugin supplies guidance. An older
  helper may not expose reference fields or `set_inspiration_comment`. Keep its
  supported workflows usable and explain the capability gap. Do not invent tools
  or bypass it by opening SwiftData or scanning Application Support.

## Search and show results

1. For exploratory requests, call `search_inspiration` with the user's concepts.
2. For “show me” requests, call `show_results_in_moody` with its `resultSetID`.
3. Do not list all tags or Collections first.

Omit query for newest-first or capture-date requests; use `capturedFrom`,
`capturedBefore` and `sortBy: "capturedAt"` as needed. Link captures use import
time; Photos imports retain the original photo date.

For exact Collection/tag membership, pass names directly to `query_library_items`.
Use `list_collections` or bounded, filtered `list_tags` only for discovery or
ambiguity. Result-set IDs cover all matches, not just the text page. An optional
member `itemID` opens its viewer while keeping the full Agent Results gallery.

After the user curates Agent Results, call `get_current_agent_results` and use
that revision's `resultSetID` for follow-up or saving. Removing a result does
not delete its Library item. Never call Agent Results a Collection.

## Understand references and attachment IDs

- A social post is one reference with saved source text and ordered attachments;
  a text-only post is still a sourced reference. General web pages save a preview
  title, description and optional image, not an article archive. A plain-link
  fallback may contain only its address.
- `type: "link"` can have media attachments. `referenceKind: "page"` identifies
  general-page previews; `"link"` identifies other sourced references/posts.
  `mediaCount` counts currently accessible media. Legacy media can lack these fields.
- Each attachment is also an Item. Search/Collections can return an attachment
  independently; `parentID` identifies its post.
- `get_inspiration_assets` returns ordered paths. Its `id` is the requested
  item; `assetID` is the actual media Item ID. Use **assetID** to read or edit
  that attachment's caption, comment, tags or Collections. Use the **post ID**
  for post organisation/commentary. Changes affect only the exact target.

## Inspect selected items

- For known IDs, fetch details/assets directly without repeating search.
- Request only needed detail fields: `title`, `sourceText`, `sourceURL`,
  `comment`, `captureState`, `captureIssue`, `mediaCount`, `parentID` and
  `referenceKind` support reference inspection. `layout` is readable only.
- Use saved title/sourceText for text-only posts and previews. An empty asset
  list is valid for a link without media; it is not a failed media read.
- Inspect returned media using a permitted local-file or visual capability.
  Metadata does not prove visual facts. An asset path is for inspection;
  `moody://` links and `show_results_in_moody` are for navigation.
- Keep captured source words, the user's personal comment and descriptive media
  captions separate. Do not substitute one for another or fetch a retained URL
  merely because it appears in a result.

## Import media and links

State the exact paths/URLs before import and obtain approval for the write.
Authorization already given for that exact action is sufficient; respect any
MCP client approval as well.

- `import_media` accepts explicit absolute image, GIF or video file paths.
  Never pass a folder or scan siblings.
- `import_links` accepts explicit public HTTP(S) URLs, preserving query
  parameters. It uses the shared capture flow: one reference per page with
  available text/ordered attachments, page preview or plain-link fallback.
  Direct-media URLs retain media-import behavior; legacy saves remain distinct.
- Report each input's item IDs, duplicate/unsupported/failed status, partial
  asset failures and `contentStatus` when returned: `complete`, `partial` or
  `linkOnly`. An imported partial/link-only social post is not a complete archive.
  A complete general-page preview still does not archive the article body.
- Imports leave new items unfiled. Use `save_to_collection` as a separate write
  if the user also requested organisation.

## Organize and annotate

Show exact targets, values and destinations before writes; obtain approval.

- `save_to_collection` accepts exactly one source (`itemIDs` or `resultSetID`)
  and one destination (`collectionID`, `collectionName` or `newCollectionName`).
  Report added, already-present and skipped counts.
- `add_tags` is additive and case-insensitively deduplicated. Both operations
  require **Organize tags and Collections**. Filing/tagging a post does not
  automatically file/tag its attachments, or vice versa.
- For `annotate_inspiration`, inspect the selected media, draft a factual caption
  and relevant tags, then show the exact item ID and values for user approval.
  For an attachment, target its assetID. Captions require **Annotate items**.
- Text-only posts and page references accept tags from their retained text;
  omit caption. Never write a caption onto the parent post on behalf of an
  attachment. Tags require Organize; a combined edit requires both permissions.
- If inspection is unavailable, explain the limitation and avoid invented
  visual details. Existing tags remain; intentional captions are protected from
  background replacement. Annotation never edits source words or comments.

## Write personal comments

Use `set_inspiration_comment(itemID, comment)` for the one personal comment on
an existing post, page, attachment or standalone media Item. It requires the
separate **Edit personal comments** permission, not Annotate items or Organize.

1. Resolve the exact target: the post's comment and every attachment's comment
   are independent. Clarify the target if the user's request is ambiguous.
2. Read its current `comment` when Search/view is allowed, so replacement is
   explicit. If reading is disabled, explain that the write replaces the entire
   comment and use only the user's approved target and replacement/clear action.
3. Show the exact replacement text or clear action for approval. A direct user
   request with the exact target and text/action already authorizes it. Draft
   personal commentary only when requested and grounded in the user's stated
   intent; do not invent why they saved something.
4. Send the full replacement string. Empty/whitespace-only text **clears** it;
   this is not append. Report the normalized saved comment (null after clear)
   and `changed`; repeating the same write is unchanged.

Comment writes preserve captured text, captions, tags, Collections and layout.
They refresh only the separate comment search index. They do not create a card.

## Safety boundaries

- Reads need no action approval; respect client write approvals.
- Clearing/replacing the explicitly targeted personal comment is supported.
  Delete, Trash, metadata removal, Collection deletion and other subtractive
  operations remain outside this MCP contract.
- Refresh Link and layout editing are not available through MCP.
- Read only approved explicit returned/user-supplied files; fetch only approved
  explicit public links. Local paths/source URLs do not grant broader access.
