# Document activity, navigation and review

Use the connected helper's discovered schemas and initialize instructions. The
plugin supplies workflows; LocalEditor.app supplies capabilities and permissions.

## Declare work before preparing it

For creation/editing, call `begin_document_activity` as soon as the approved
existing target path is known, before reading for an edit, drafting content,
drawing elements or preparing a generator. Pass `paths` from discovery or a
successful creation. Creating a new document returns its path before a lease
can begin; begin immediately if you will populate or revise it. Guidance in a
read/create response is a suggested next call, not an already-started lease.

Preserve the returned opaque `leaseId`. Renew with `renew_document_activity`
every 60 seconds during preparation, including between helper connections.
Each lease lasts two minutes. Split long preparation into chunks so renewal
happens on time. Finish with `finish_document_activity` on success or failure,
including failed writes and interrupted work when cleanup is possible. Never
invent another caller's token. Saved content remains after finish or expiry.

Activity does not save, open, read document bytes or grant permissions. Read-only
lookups need no write-intent lease; ordinary reads pulse briefly after returning.
If the helper lacks an activity capability, explain that limitation, keep
supported tools usable and do not fabricate activity or bypass access. Canvas
regions are an optional extension: only send them when the discovered schema
supports them. Older helpers can still use path-only document activity.

## Local navigation

For a Markdown link within the same owning Project or Scratchpad scope, use the
returned `wikiLink`: literal spaces and Unicode, `.md` omitted for Markdown,
other supported extensions retained. A label is `[[Target|Label]]`. Do not
URL-encode WikiLink targets or substitute encoded Markdown navigation links.
Duplicate filenames may require the app's chooser. External URLs and images
keep standard Markdown syntax; embedded Pages/Canvases keep their tool-returned
marked links. A reference never establishes content permission.

## Finish and hand off

Finish activity before handing off completed work. For an explicit user request
to show a file, use `open_in_localeditor` with `activate:true` when supported.
For routine completion, default `activate:false` preserves the user's current
selection and focus if the exact path is already open in any tab/window;
`alreadyOpen:true` means no new handoff occurred. An unopened target can still
open for review. Let the watcher update an attached open document.

New Scratchpad creation normally already opens its result; do not open it again
without a reason. An `opened:false`/`openWarning` result preserves a successful
creation: report it and retry only the handoff, not creation. Respect older
schemas; do not send unsupported activation arguments or promise focus behavior
that the connected helper does not expose.

## App and plugin updates

Discover missing session tools before recommending updates. A missing tool in
connected `tools/list` may need an app/helper update; a plugin update cannot add
native tools. The helper reports its own version, not the installed plugin
version. Do not claim to detect an old plugin from that number or promise an
unpublished release. Explain skill installation/update through the client's
supported plugin manager when needed. Reload/reconnect after updates and keep
working older capabilities usable. A source edit does not update installed clients.
