# Recover LocalEditor MCP tools

Use this when a skill is available but the client has not exposed LocalEditor
tools. A missing session tool does not prove that the installed helper is old.

1. Try the client's tool search/discovery facility when available. Search for
   LocalEditor and the needed tool; full names may have a client-specific prefix.
   In Claude Code, use `ToolSearch` if exposed and inspect `/mcp` for connection
   status. In Codex, use the available tool registry/search; do not invent a
   discovery command when the host exposes none.
2. If discovery cannot expose the tools, use the bundled helper through
   [scripts/localeditor_mcp.py](../scripts/localeditor_mcp.py). Resolve the script
   relative to this plugin package, not the project or an installed cache path
   remembered from another session. It uses Python 3 standard library only.
3. Run `python3 <absolute-plugin-path>/scripts/localeditor_mcp.py discover`.
   Read the returned server instructions and tool schemas. This establishes
   actual helper availability before recommending an app update.
4. If the sandbox blocks helper startup or its local entitlement check, retry
   the same helper operation once with the host's approved elevated execution.
   In Codex, request `sandbox_permissions: "require_escalated"` on the shell
   tool, with a short justification that the bundled helper needs its normal
   macOS access. Elevation means running outside that sandbox, not `sudo` or
   root. Respect approval denial; explain it and stop dependent work.
5. Call only tools authorized by the user's task. Supply tool arguments as a
   JSON object on stdin; the script preserves MCP text metadata and errors,
   omits image base64, and exits unsuccessfully for tool errors. Preserve
   successful writes across failures.

For example, after discovering the schema:

```sh
python3 /absolute/plugin/path/scripts/localeditor_mcp.py call list_scratchpads <<'JSON'
{}
JSON
```

For document bodies, use a quoted heredoc for JSON stdin, or another structured
stdin mechanism. Never interpolate document text into executable shell code.
No temporary files are required. Read the tool result; success of the process
alone is not proof that a document was created or opened.

The script always invokes
`/Applications/LocalEditor.app/Contents/Helpers/localeditor-mcp`, performs MCP
initialization and tool discovery, then sends the requested MCP call. It does
not read or write source documents itself. The optional PNG output below writes
only the image returned by an authorized MCP call. LocalEditor still enforces entitlement,
the master toggle, approved scopes, revisions, secret-file protections, and
cloud/symlink/size guards. A persistent `licenseRequired` or permission error is
a real block: report it. Do not change configuration, Keychain, environment
gates, or permissions to force access; do not replace MCP with filesystem reads.

If the connected helper's tool list lacks a needed tool, then explain that an
app/helper update is required. Plugin updates and app/helper updates are
separate. Reconnect or restart the client through its supported controls after
updating; do not claim that a source checkout has updated the installed client.


## Inspect a rendered PNG

Prefer native MCP image blocks when the host can display them. Recovery output
always omits image base64 from printed JSON. To inspect `render_canvas` through
recovery, save its single PNG to a new, independently authorized absolute path:

```sh
python3 /absolute/plugin/path/scripts/localeditor_mcp.py call render_canvas --image-output /approved/project/review.png <<'JSON'
{"path":"/approved/project/Drawing.lcv","expectedRevision":"<saved revision>"}
JSON
```

Use an existing project folder authorized for the output; follow the user's
Scratchpad/temporary-file rules for temporary destinations. MCP read permission
does not itself grant arbitrary filesystem output permission. The caller never
creates parent folders or overwrites existing files/symlinks. Choose a fresh
filename if the destination exists. It saves only after a successful result
with exactly one `image/png` block, strict base64, at most 8 MiB decoded bytes,
and a PNG header with dimensions from 1 to 4096. Header validation is a transport
check; the host's image viewer performs actual image decoding/inspection.

The JSON retains render metadata (saved revision, world bounds, pixel size)
and adds `imageOutput` with the absolute path, MIME type and byte count. Inspect
that file with the host's image viewer before claiming visual verification.
Do not read/reprint its base64. A tool error creates no PNG; preserve the reported
error rather than substituting direct source-file access. A disk-write failure
can leave a partial new file: report that path and choose a fresh destination
for a retry, following the user's cleanup rules.

The existing 16 MiB transport-line limit accommodates the renderer's 8 MiB PNG
cap (about 10.7 MiB base64) plus its bounded metadata. No larger transport limit
is needed. The recovery caller identifies as `localeditor-plugin-recovery`, so
its generic activity badge is expected; do not impersonate Claude, Codex or Cursor.

## Newer Canvas features

Discovery also establishes whether `get_canvas_appearance` and the render
`theme` parameter are available. Do not infer them from a helper version number.
When supported, include `"theme":"light"` or `"theme":"dark"` in the render
JSON above and use a fresh output filename for each image. The caller passes
these arguments unchanged and retains theme/background metadata. When absent,
omit the argument and report the unavailable theme check. Follow the shared
[update guidance](document-workflows.md#update-while-keeping-older-helpers-usable)
to update the app and plugin separately, reconnect and rediscover; keep working
older document/drawing tools usable.
