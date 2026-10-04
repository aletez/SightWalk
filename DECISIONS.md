# Decisions and status

Newest first within each section. "J" = decided by Jakub, "C" = proposed by Claude and accepted.

## Status

Verified in Sublime:
- Plugin loads; the setup command writes the token once and keeps it.
- `show` and `say` through the bridge.
- Headers and strip use the code view's font; headers are not selected on creation.
- Per-file hues: code tint 2%, header band 25%; schemes applied only after indexing (no error dialogs).

Changed, not yet verified in Sublime:
- Header cells overlap their code pane by `OVERLAP` = 2 px, which hides the border below the header (1 px still showed it; pixel-checked by Claude). Header gutter takes the band colour (the header scheme's line highlight is the band).
- Headers have a gutter without line numbers; the eye can sit on a header when it is the first or last line on screen.
- Gutter icons (tools/draw_icons.py → icons/), eyes for off-screen marks, strip without marks. Old emoji marks map to icons until the point format changes. Seen in a screenshot by Claude.
- Gutter background in the header's tint (pixel-checked by Claude: gutter = header colour).
- Send shortcut: primary+enter (Cmd+Enter on macOS).
- Range outline removed.
- `follow_resize` (panels, window resize).
- Squared marks in the agent manual (needs the setup command again and a fresh Claude Code session).
- Scroll limit (`plan.max_offset`) and the filler view below the last pane.
- Tint amounts read from settings (`tint`, `header_tint`).
- Conversation pane: transcript guard, prompt kept at the bottom by a filler phantom, conversation syntax.
- Repo-relative header paths, `~` in specs, suffix matching at path separators.

Open:
- Lower half of the conversation pane, ideas Jakub liked: (1) vetting ledger, one row per walked function with a verdict (OK, question, concern) and a note, kept by the agent and corrected by the user, ending as the review summary; (2) route map, the current pane sequence with the centred pane highlighted and click-to-jump, earlier routes kept dimmed; (3) legend of the marks on screen, one line per icon saying what it means now. Possibly route map above the ledger.
- Scrolling a single view (not the reader) hides its icons and no eye appears. Deal with it after the current changes.
- Long paths in narrow windows: shorten from the left (`…/sw/reader.py:1-30`) if repo-relative is not enough.
- HTML header pane with a copy link; key binding to copy the spec of the focused or centred pane.
- Header-jump artefact when a sliver merges into a neighbour.
- Dependency-free MCP server (standard library only) for shipping; `.gitattributes` export-ignore for dev files before Package Control.
- Self-vetting walk-through: Jakub reads the plugin's own code through the reader.
- Shipping defaults for `tint` / `header_tint` (Jakub is tuning).
- Possible VS Code port; open question: one scroll for the whole layout or per-pane scrolling.

## Decisions

Conversation pane
- J (agreed, not built): The bottom of the transcript sits at the vertical centre of the pane, with the prompt right under it. The upper half is the conversation's; the lower half is for something else (open).
- J: One conversation pane, not a transcript plus input box, so the transcript can be copied with the keyboard without switching panes. The prompt stays at the bottom: an invisible block phantom fills the space above the transcript (below a blank first line), measured and corrected on each poll.
- J: The transcript is protected with `TextChangeListener.on_text_changed` (criteria: resilience, KISS, execution time). Claude had wrongly argued that any listener would leak; `on_text_command` would need a list of editing commands and cannot see what undo does. Fast path: changes after the protected length are ignored without reading the buffer.
- C: The draft boundary is the recorded length of the protected text, set before each of the plugin's own edits. The syntax is for colour only, because agent text could fake a prompt.

Marks
- J (agreed, not built): The outlines of marked lines take over the role of the code tint, so the code background loses its tint. Files are still told apart by the header band and the gutter.
- J (agreed, not built): Marks move into Sublime's gutter as icons, and every marked line gets an outline around its text in the file's strong hue. The gutter takes the header's tint. Icons use Inter (OFL; SF Pro's licence forbids shipping work drawn with it). Icons are squares with corner radius 1/16, digit glyphs 12.5/16, letter glyphs 11/16, drawn by a script: green arrows for control (original size, stroke 1.7/16; pale lime #E4F7B5 glyphs), amber squares with semibold dark plum (#3A1838) digits 1-9 for ordered relations, blue squares with regular-weight pale butter (#FFEFB0) letters A-Z for lines without order (A alone = "this line"). No asterisk. A control jump is a pair (from, to): the sender's arrow leaves the right edge and bends up or down towards the target; the receiver's arrow arrives at the right edge from above (↳) or below (↱). There and back are always two separate point calls, so one line never needs two icons. Off-screen marks: an eye looking up in the gutter of the topmost visible code line when a mark is above, an eye looking down on the bottom visible line when one is below; the eye replaces any other icon on that line, whose outline stays. The strip shows no marks any more (it stays for wheel scrolling). Eyes: graphite (#3A3B40) on a pale butter (#FFEFB0) square; eyebrow style open.
- J: Only emoji on their own coloured square, visible on any theme. *️⃣ this line ("the missing part of what is being said"); ➡️ passes control, ⬅️ takes control (call/callee, return/call site, raise/handler); 1️⃣ 2️⃣ 3️⃣ other ordered relations; 🅰️ 🅱️ compare. The agent names the relation in the conversation. ⬆️/⬇️ for marks off screen.

Panes and scrolling
- J (agreed, not built): No scroll strip. The mouse wheel over code panes and headers scrolls the reader. A code view never scrolls on its own by the wheel; its content moves only with focus changes, such as the caret moving with the arrow keys.
- J (agreed, not built): The caret stops at the first and last line of a pane's range. Following the caret into the next pane at the last line may come later.
- J: Every pane, the last one included, is exactly as tall as its range. An empty filler view takes the rest of the column.
- J: If the last pane fits on screen with its header, scrolling stops when its header reaches the top; otherwise when the end of its range reaches the bottom.
- C: The strip spans the whole column; wheel movement over it is read by polling an anchored buffer (the API has no wheel events).

Headers and colour
- J: Headers in a separate pane, not phantoms (phantom text cannot be copied). Header path relative to the repository root by default, `~/…` outside a repository; no setting until needed.
- J: No outline around the range. An `add_regions` outline was tried (it follows the text, not a rectangle) and removed: it looked bad.
- J: Header band clearly stronger than the code tint; a strong header makes different files' code tints harder to tell apart (simultaneous contrast), so the two are tuned together, in settings.

Name
- J: SightWalk: sightseeing with a guide, and a sidewalk (the conversation) running alongside the street of code. Chosen over RunWalk, RuntimeWalk, TraceWalk ("trace" suggests errors) and CodeSightWalk (the prefix hides the sidewalk). No software project or Package Control package uses the name (checked 2026-10-04); a 2024 accessibility campaign in Lima is called "SightWalks".

Process
- J: Whole files only when anything is pasted; checkpoints by hash (`shasum -a 256 -c`), now replaced by git commits.
- J: Development moves to a local Claude Code session in this repository, symlinked into Sublime.
