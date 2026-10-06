# Decisions and status

Newest first within each section. "J" = decided by Jakub, "C" = proposed by Claude and accepted.

## Status

Verified in Sublime:
- Code street (Jakub, 2026-10-06): panes overlap by `OVERLAP` = 2 px, each neighbour taking half the border; the wheel works over every pane, header, the strip and the invisible filler below the last pane; a pane at line 1 is three cells (line 1's gutter in the real view reaching down to line 10, line 1's code in a twin with no margin, the rest in a second view); a gap phantom of `GAP_PX` = 16 px at each line's start between gutter and code. Known and accepted: the caret cannot reach line 1 of a pane at line 1, and trying looks bad.
- Plugin loads; the setup command writes the token once and keeps it.
- `show` and `say` through the bridge.
- Headers and strip use the code view's font; headers are not selected on creation.
- Per-file hues: code tint 2%, header band 25%; schemes applied only after indexing (no error dialogs).

Changed, not yet verified in Sublime:
- The guide no longer fills silence ("Czekam na Twoją kolejną wiadomość."): a timeout of wait_for_user tells it to say nothing and wait again; manual and prompt say so too (Jakub).
- A message carries selected, the text the user selected (at the moment of asking: in the strip, in the view it was asked from or another view the window shows; in a trip, in any sight; Jakub), and the guide's manual says "this" then means exactly that text, not the whole function (Jakub asked about an expression and got the function).
- Typing or pasting into the transcript goes on in the draft instead of being lost (Jakub found the first letter vanished); edits that delete transcript text are still only undone.
- While an answer is on its way, the bench's header says so ("the guide is coming…" when a guide is being started, "the guide is thinking…" otherwise), in the strip and in a trip; sending in a trip also starts a guide if none listens. The first background guide called say with message instead of text and its answer was lost: say now accepts both, and the guide's prompt names text.
- The whole code is covered by trips (Jakub): 25 trips, 7 to 11 sights each, all 229 functions; `tools/trips.py` warns about any function no trip covers. The overlay-bench geometry (`plan.bench_rect`) is gone with the overlay.
- The bench in a trip is 35% of the width (was 45%; Jakub). A proportional font for the conversation (`bench_font_face`, default Helvetica Neue on macOS, Segoe UI on Windows); headers keep the font of code. Asking the guide on a selection starts a Claude Code session in the background (`claude -p`, allowed only the sight-walk tools and reading) when no agent is listening; its output goes to ~/.sight_walk/guide.log; "SightWalk: Stop the Vetting Guide" ends it.
- pane → sight everywhere (Jakub): code (`plan.Sight`, `reader.sights`), the agent's interface (`show(sights=…)`, marks `{"sight": i, …}`, `state` returns `sights`) and the manual; an old server sending `panes` gets told to rerun setup. The bench's header names whom you talk to: "Vetting Guide". The Vetting strip sits at the heights of a trip's bench (header, conversation to 0.6, an empty view below); a trip opening over it takes its status and hides it: the strip vanishes a second later under the trip's window, which is then brought back to the front. Needs setup and a new guide session.
- Vetting strip (`sw/strip.py`, eased glide of 180 ms in 12 ms frames): opened by Claude through `subl --command` on both sides, with the conversation carried over and scroll bars hidden; the glide itself only Jakub can judge. One shared inbox for the agent (`state.INBOX`); `say` goes to the strip while it is open. Needs setup and a new guide session for the manual.
- Header over the Sights ("Sights · trip name", from `show(trip=...)`), level with the bench's; sights scroll under it (checked by Claude on screen). Needs setup and a new guide session for the `trip` argument.
- Marks on the Vetting Bench (Jakub): variables between single asterisks (*name*) instead of tildes; short strings of code between single quotes ('key'), in the string colour. Both count only with no white space inside; quotes not after a letter, so apostrophes stay prose. A string with spaces cannot be marked. Needs setup and a new guide session for the manual.
- Icons drawn with a clear strip on their right (`MARGIN` = 2 of 16 units), so they no longer touch the line number (Jakub). No stippled underline under names on the Vetting Bench any more: it darkened the text (Jakub).
- Setting `bench_side` ("left" or "right"): the Vetting Bench on either side of the Sights, applied at once; the agent can change it through `settings`. A dragged bench width is kept (read from the bench's own cell, which also fixes keeping it since the strip went). `tools/trips.py` writes `docs/trips.md` and prints a trip's views for `show`.
- No scroll strip; the code column starts at the conversation's edge.
- Code audit (2026-10-06, Claude): the line-1 pane's logic in one class (`line_one.LineOne`) instead of checks spread over the reader; the vetting pane without the L machinery; dead code removed (old cell merging, caret keeping, `lift`, unused settings and constants); one window height instead of two equal ones; `places` shared by the wheel and by putting views back; editor regions held and read back through two helpers; tint's two scheme paths merged; names that clashed (`header_text` in two modules) made distinct; unit tests for the pure modules. Checked by Claude on screen: show, point (icons on line 1 and line 3 of a line-1 pane, a jump), say with status, the wheel both ways, the editor opening from the header button. Not checked: Esc closing the editor, saving from it.
- The wheel over a pane scrolls the reader again (the pane is put back on its first line); the strip stays as a fallback for panes at line 1 and headers. Edge fixes (line 1, last line, headers) to return later if this holds (Jakub). Checked by Claude: down and up over the code.
- Cells at their virtual places, rows beyond the screen; hidden scroll bars; borders; narrower gutter; 104 px strip (checked by Claude on screen; smoothness on a trackpad is Jakub's to judge). The gutter is narrower but not quite half (fold buttons off, margin 1).
- One scroll strip between conversation and code; no twins (checked by Claude: wheel over the strip moves the column, over a pane only that pane).
- Smoother wheel: while the wheel keeps the same views in the same groups, a render only resizes the cells (no group moves, no focus). Carets go onto lines wholly inside a cell, which stops an endless slow crawl (focus scrolled a partly visible caret line into view, which read as the wheel). 
- L-shaped vetting pane and wheel scrolling over the code panes without the strip (seen by Claude: opens at the top, the wheel scrolls to the end, a long line runs full width under the code).
- Read-only panes and the editor: opening by the header button (clicked by Claude) and through the bridge; inserting lines moved the range 9-18 to 9-20 and the marks 12, 16 to 14, 18, and the agent note read "sw/header.py:9-18, now 9-20" (tested by Claude through a temporary bridge call, file left unchanged). Enter, Esc, Save and the button checked by Jakub; Don't Save and Save checked by Claude on a scratch file (one dialog each, range 5-6 moved to 6-7 after a line was added above); the editor's position checked by Claude (its gutter starts 15 px right of the panes' gutters).
- Two-line conversation header with status and help mark, text-coloured band, no border below; conversation pane at 0.6 with an empty pane below; prompt `>>> `; blank lines instead of the filler phantom above the transcript; header rewraps when the column is resized and dragged column widths are kept; help on hovering the right end of the header's first line or clicking the `?`; Preferences: SightWalk Settings, with settings applied at once (seen in a screenshot by Claude). Not tested: the help tooltip on hover and the explain next/previous keys (Claude cannot hover or press keys in Sublime).
- Reader windows close themselves before a plugin reload (`plugin_unloaded` → `state.close_all`), so reloads leave no orphans (checked by Claude: the window list loses the reader on reload).
- Conversation on the left (columns: conversation 34%, code, strip 4% at the right edge).
- Conversation syntax colours `functions` (as calls), **classes** (defined and built-in apart) and ~variables~, all with a stippled underline (seen in a screenshot by Claude). Agent manual tells the agent to mark names; needs setup and a new session.
- `show` without `center`; the reader opens at the top.
- Error audit: malformed pane specs, missing files (with the root hint), ranges past the end of a file, a bad center, lines outside a pane, malformed marks, nothing to close, Sublime too slow, unknown op, and (MCP side, needs setup and a new session) Sublime not answering. Bridge-side errors checked live by Claude.
- Outlines around the text of marked lines (scope `sight_walk.outline`, the file's hue at 0.7).
- No code tint: code panes keep the scheme's background; the gutter keeps the band.
- New point format (jumps as from/to, marks 1-9 and A-Z) and agent manual. Needs "SightWalk: Set Up Agent Bridge" and a new Claude Code session.
- Header cells overlap their code pane by `OVERLAP` = 2 px, which hides the border below the header (1 px still showed it; pixel-checked by Claude). Header gutter takes the band colour (the header scheme's line highlight is the band).
- Headers have a gutter without line numbers; the eye can sit on a header when it is the first or last line on screen.
- Gutter icons (tools/draw_icons.py → icons/), eyes for off-screen marks, strip without marks. Seen in a screenshot by Claude.
- Gutter background in the header's tint (pixel-checked by Claude: gutter = header colour).
- Send shortcut: primary+enter (Cmd+Enter on macOS).
- Range outline removed.
- `follow_resize` (panels, window resize).
- Squared marks in the agent manual (needs the setup command again and a fresh Claude Code session).
- Scroll limit (`plan.max_offset`) and the filler view below the last pane.
- Tint amount read from settings (`tint`, the header band and gutter).
- Conversation pane: transcript guard, prompt kept at the bottom by a filler phantom, conversation syntax.
- Repo-relative header paths, `~` in specs, suffix matching at path separators.

Open:
- Question (Jakub): with centring gone, is scrolling past the point where the last pane is fully visible still useful? Kept for now.
- Later: make sure an unusual base text colour in a colour scheme does not blend with an unluckily drawn header hue (e.g. check the contrast between the band and the text and shift the hue or the amount when it is too low).
- The pane below the conversation becomes a tabbed space: its header is a row of a few small horizontal panes acting as tabs (Jakub's "editable tab" idea, the origin of the headers), over the ledger, route map and legend. Route comes first. The tabs are real text (selectable, copyable), not renamable. A diagram tab (a UML-like picture of the code in an image pane) is Jakub's favourite candidate.
- A reader window with an unsaved buffer stops at Sublime's save question when a reload closes it; that is Sublime's usual behaviour and is kept.
- Later, hue settings: a command that draws a new random set of hues and applies it at once to the open reader (the user may not like the first set drawn), and a setting to keep each file's hue constant for the session (default: yes). Today the starting hue is random per plugin load and a file keeps its hue until the next reload.
- Lower half of the conversation pane, ideas Jakub liked: (1) vetting ledger, one row per walked function with a verdict (OK, question, concern) and a note, kept by the agent and corrected by the user, ending as the review summary; (2) route map, the current pane sequence with the centred pane highlighted and click-to-jump, earlier routes kept dimmed; (3) legend of the marks on screen, one line per icon saying what it means now. Possibly route map above the ledger.
- Scrolling a single view (not the reader) hides its icons and no eye appears. Deal with it after the current changes.
- Long paths in narrow windows: shorten from the left (`…/sw/reader.py:1-30`) if repo-relative is not enough.
- HTML header pane with a copy link; key binding to copy the spec of the focused or centred pane.
- Header-jump artefact when a sliver merges into a neighbour.
- Dependency-free MCP server (standard library only) for shipping; `.gitattributes` export-ignore for dev files before Package Control.
- Self-vetting walk-through: Jakub reads the plugin's own code through the reader.
- Shipping default for `tint` (Jakub is tuning).
- Possible VS Code port; open question: one scroll for the whole layout or per-pane scrolling.

## Plans (Jakub)

- README: the English README links to a Polish one, written in the Polish metaphor (panorama, widok, wycieczka, marszruta, mapa, ławka).
- Far future, only after SightWalk has been used in recruitment: a Polish-language version of the tool.
- If this approach to vetting catches on: promote writing code for it. Tell the coding assistant to write with trips in mind: each trip from one branch point to the next (not necessarily at most six sights), so that at the end of a trip the user can decide on the values of the new variables.
- Assistant personalities, two or three to choose from in later versions: a senior who explains hard code well; a junior who presents their code to a senior and states their doubts clearly.

## Decisions

Names (Jakub, 2026-10-06)
- J: The reader window has no name of its own: metonymically it is the **trip** (Polish: **wycieczka**), "open a trip". (Lookout / taras was chosen and dropped the same day.) The assistant is the **Vetting guide** (Polish: **przewodnik**); "VetAss" was dropped as too crude.
- J: A header over the Sights like the bench's: "Sights · <trip name>", the name given by the guide in `show(trip=...)`.
- J: The guide outside a trip is the **Vetting strip**, headed "Vetting Guide": on a selection in any window (context menu or the command palette, "Ask the Vetting Guide"), the window's own layout glides a quarter of its width aside, partly out of the window, and the strip glides in on the side of the selection (setting `strip_side`: auto, left, right). Quick, eased to a stop, not mechanical. No buttons: Esc or primary+w glides it out and the layout back. Opening a trip closes it. One conversation goes on across the strip and the trips' benches. (A small bench laid on top of the code was planned first and dropped: an unmovable box looks like old DOS software; a new window cannot be placed or kept on top.)
- J: The Vetting Bench may sit left or right of the Sights (setting `bench_side`, default left).
- English: the code column is **Sights**, a pane a **sight**, a **trip** is whatever one `show` opens as a window, however long; being on a list of trips does not make one (Jakub). Prepared trips keep from one branch point to the next. A vetting trip may take long: it serves review. The run order is the **Itinerary**, the UML diagram **Map**, the conversation **Vetting Bench**.
- Polish, a metaphor of its own (a "zabytek" sounds dead, and very negative in technology): **panorama**, **widok**, **wycieczka**, **marszruta** (users may learn a fine old word), **mapa**, **ławka**.
- The scroll strip is gone: its room goes to the code column, and the wheel has room everywhere else.

Code street
- J: Room between gutter and code comes from an inline phantom at each line's start, not from `margin` (Sublime paints the margin in the gutter's colour) and not from a cover cell (it would break line highlighting and selection).
- J: A pane at line 1 is cut across the whole width, not just the gutter: line 1's gutter (real view), line 1's code (twin, room above hidden by the header, so a long touchpad swipe does not stop on it), and the rest of the pane in a second view of the file, which has line 1 above it to move into. Line 1's view reaches down to line 10 so its gutter is as wide as the two-digit gutter below.
- J: Borders between panes are hidden by overlap, half taken by each neighbour, so neither covers the other's text.
- J: Below the last pane an invisible filler takes the wheel, like the strip.
- J: Faster putting-back at the reader's ends made the trembling worse; dropped.

Conversation pane
- J: No phantoms in typing areas. The conversation has a two-line read-only header in place of a tab (tabs are off), looking like the other headers: band and gutter, no border below (the header overlaps the conversation by `OVERLAP`). Its band is the scheme's text colour mixed into the background at `tint`, which always contrasts. Text: "Conversation · <status>", the status being a few words from the agent on what the conversation is about now (`say(text, status=...)`), kept until changed and wrapped or cut to two lines. At the right edge of the first line a help mark `?`, a phantom, faded and outlined at all times so it reads as read-only; hovering it shows the shortcuts.
- J: Shortcuts: primary+enter sends (conversation); the swap-line keys (Ctrl+Cmd+↓/↑ on macOS, Ctrl+Shift+↓/↑ elsewhere) work anywhere in the reader and send "Explain next." / "Explain previous.", meaning the next or previous step of the run shown. They leave the draft alone.
- J: The conversation pane ends at `default_conversation_height` (0.6 of the column, to be tested between 0.5 and 0.66) and holds the transcript tightly, the prompt at its bottom. The pane below is empty for now.
- J: The prompt is `>>> `; the old `› ` was too small.
- J: Columns 45 % conversation, 55 % code. No border lines between panes.
- J: The conversation lives to the left of the code, so the code and its gutter with line numbers sit next to it.
- J: Names of code in the conversation take the colours they have in the code, through the conversation syntax and a light markup the agent writes. `name`: functions and methods, scoped as calls (variable.function). **Name**: classes and types, scoped as defined classes (entity.name.class), except Python's built-in classes, which the syntax recognises by name and scopes as Python does (support.class). ~name~: variables, parameters and attributes, scoped as Python scopes them (meta.generic-name), plain in Mariana. Every marked name also gets a stippled underline in the text colour, so it reads as code in any scheme. Keywords and constants stay plain; bold is no longer for stress. The delimiters stay visible, faint like comments. No Markdown inheritance. Scopes taken from Jakub's reading of the code's own scopes. More categories may come with use. Chosen over regions alone (they cannot colour text) and a generated per-reader syntax.
- J: The markup is defined once, in the syntax. Every marked name carries `meta.symbol.sight-walk`, and the plugin finds the names to underline by that scope (`find_by_selector`), never by its own pattern; a new category in the syntax is underlined without plugin changes. Jakub asked for this before seeing the code, which Claude had already written the same way.
- J: One conversation pane, not a transcript plus input box, so the transcript can be copied with the keyboard without switching panes. The prompt stays at the bottom: an invisible block phantom fills the space above the transcript (below a blank first line), measured and corrected on each poll.
- J: The transcript is protected with `TextChangeListener.on_text_changed` (criteria: resilience, KISS, execution time). Claude had wrongly argued that any listener would leak; `on_text_command` would need a list of editing commands and cannot see what undo does. Fast path: changes after the protected length are ignored without reading the buffer.
- C: The draft boundary is the recorded length of the protected text, set before each of the plugin's own edits. The syntax is for colour only, because agent text could fake a prompt.

Marks
- J: Digits 1-9 may prove too few. If tests show it, continue with letters in a hexadecimal manner; not before.
- J: The outlines of marked lines take over the role of the code tint, so the code background loses its tint (the old code `tint` is gone; `tint`, formerly `header_tint`, sets band and gutter). Files are still told apart by the header band and the gutter.
- J: Marks move into Sublime's gutter as icons, and every marked line gets an outline around its text in the file's strong hue. The gutter takes the header's tint. Icons use Inter (OFL; SF Pro's licence forbids shipping work drawn with it). Icons are squares with corner radius 1/16, digit glyphs 12.5/16, letter glyphs 11/16, drawn by a script: green arrows for control (original size, stroke 1.7/16; pale lime #E4F7B5 glyphs), amber squares with semibold dark plum (#3A1838) digits 1-9 for ordered relations, blue squares with regular-weight pale butter (#FFEFB0) letters A-Z for lines without order (A alone = "this line"). No asterisk. A control jump is a pair (from, to): the sender's arrow leaves the right edge and bends up or down towards the target; the receiver's arrow arrives at the right edge from above (↳) or below (↱). There and back are always two separate point calls, so one line never needs two icons. Off-screen marks: an eye looking up in the gutter of the topmost visible code line when a mark is above, an eye looking down on the bottom visible line when one is below; the eye replaces any other icon on that line, whose outline stays. Eyes: no eyebrow, a tall eye (curve offset 8.5/16) with the pupil clipped inside it, graphite #1E1F23 on a pale butter (#FFEFB0) square. Point format: {"from": line, "to": line} for a jump (a "file:line" shown in several panes is an error naming them; then the pane form is needed), {"at": line, "mark": "1"} for digits and letters, a line being "file:line" or {"pane", "line"}.
- J: Only emoji on their own coloured square, visible on any theme. *️⃣ this line ("the missing part of what is being said"); ➡️ passes control, ⬅️ takes control (call/callee, return/call site, raise/handler); 1️⃣ 2️⃣ 3️⃣ other ordered relations; 🅰️ 🅱️ compare. The agent names the relation in the conversation. ⬆️/⬇️ for marks off screen.

Panes and scrolling
- J: Every pane and header has a cell at its place in the virtual document, also above and below the screen: a layout's rows may lie outside 0..1 (Jakub's experience). Scrolling only shifts the rows with one `set_layout`: no view changes group, size or scroll position, so a wheel step costs well under a millisecond (measured: moving views between groups cost 15-50 ms each, a full relayout 60-110 ms). Each pane's view stays at its range's first line; the cell moves.
- J: Borders between panes are back (`OVERLAP` = 0). Scroll bars are hidden while a reader has the focus: overlay scroll bars plus the package's own `Default`/`Adaptive` theme rules, gated by a setting set in memory only. Code views have no fold buttons and a 1 px margin, which narrows the gutter. The scroll strip is 104 px wide (twice the former gutter).
- J: Twins are dropped: scrolling many panes at once, each read and put back, cannot be made smooth on every machine. One empty scroll strip, the width of a gutter, stands between the conversation and the code, from top to bottom; only it takes the wheel. Panes take no part: the wheel over them scrolls just that view until the next render puts it back. Headers span the whole code column again and are plain one-line views. (Tried before this: reading the wheel from every pane, gutters as the scroll strip with twins for the code, a strip below the last pane; all removed.)
- J: The vetting pane is a rectangle under the conversation again (the L is dropped); the code column reaches the window's bottom.
- J: Code panes are read-only; the reader is for reading. Editing happens in the editor: an "Edit (Enter)" button at the right edge of every pane header (a phantom, faded and outlined like the help mark), or Enter in a pane, opens it. The editor is a full, normal view of the file laid over the lower right of the code column, flush with its right and bottom edges; its top left corner is set back past the panes' header and gutter plus 10 px (`INSET`), so no colour of the frame touches the same colour in the editor. It has a header like the panes' (the file's path, its hue) and the current marks of that file, which move with the edits. Esc closes the editor view the usual way and Sublime asks about unsaved changes itself (Jakub: no dialog of our own); afterwards a still-dirty file means Don't Save, so the panes revert and keep their ranges, and a clean one means the edits stay. The editor refuses to open while the file has unsaved changes in another view (Sublime shares the buffer across windows), since Don't Save would revert them too; Esc keeps its usual jobs first (completions, fields, several carets, popups, panels). primary+w is not blocked (Jakub, revising): a spoiled reader is easily recreated, and interfering with that shortcut is wrong. In the editor it closes the editor like Esc, so the reader catches up; elsewhere it does what it always does. On close the reader catches up: pane ranges and marks take their new lines (tracked as regions in the shared buffer), headers update, and the agent's next message carries `edited`.
- C: Sublime draws earlier groups over later ones, so the editor's cells come first in the layout. Read-only belongs to the buffer, so the panes of the edited file are editable while the editor is open and are locked again when it closes.
- J: No centring of code panes; it was of no use. `show` has no `center` argument any more and opens at the top (built, not verified). Other ways of scrolling and pulling attention may come later; for now the numbered marks do the job.
- J: The scroll strip is back, left of the code (see below). The mouse wheel over code panes and headers scrolls the reader. A code view never scrolls on its own by the wheel; its content moves only with focus changes, such as the caret moving with the arrow keys.
- J (agreed, not built): The caret stops at the first and last line of a pane's range. Following the caret into the next pane at the last line may come later.
- J: Every pane, the last one included, is exactly as tall as its range. An empty filler view takes the rest of the column.
- J: If the last pane fits on screen with its header, scrolling stops when its header reaches the top; otherwise when the end of its range reaches the bottom.
- C: The strip spans the whole column; wheel movement over it is read by polling an anchored buffer (the API has no wheel events).

Headers and colour
- J: Headers in a separate pane, not phantoms (phantom text cannot be copied). Header path relative to the repository root by default, `~/…` outside a repository; no setting until needed.
- J: No outline around the range. An `add_regions` outline was tried (it follows the text, not a rectangle) and removed: it looked bad.
- J: Header band clearly stronger than the code tint; a strong header makes different files' code tints harder to tell apart (simultaneous contrast), so the two are tuned together, in settings.

Name
- J: SightWalk, kept on 2026-10-06 after RunWalk was weighed again: it fits better than before, as the code column is now Sights. Spoken, it is close to "sidewalk"; written, it is clear. Originally: sightseeing with a guide, and a sidewalk (the conversation) running alongside the street of code. Chosen over RunWalk, RuntimeWalk, TraceWalk ("trace" suggests errors) and CodeSightWalk (the prefix hides the sidewalk). No software project or Package Control package uses the name (checked 2026-10-04); a 2024 accessibility campaign in Lima is called "SightWalks".

Bridge and tools
- J: Errors are the agent's only feedback, so each one says what was wrong and how to do it right, ready to use (the corrected form or the next step: retry, ask the user, rerun setup). Problems found together are reported together, so one retry fixes them all. Unexpected exceptions name their kind.

Process
- J: Whole files only when anything is pasted; checkpoints by hash (`shasum -a 256 -c`), now replaced by git commits.
- J: Development moves to a local Claude Code session in this repository, symlinked into Sublime.

## Jakub's strong contributions

Ideas and catches that changed the design or prevented a real defect, beyond everyday direction. Claude adds to this list when one happens; newest first.

- 2026-10-06, gap phantoms: room between gutter and code from an inline phantom per line, after catching that Claude's cover cell over the margin would have broken line highlighting and selection.
- 2026-10-06, borders split in half: each neighbour takes half the border, so overlap hides it without covering text.
- 2026-10-06, the line-1 pane: cutting the whole pane after line 1 (not only the gutter), keeping line 1's code a twin for long touchpad swipes, and reaching line 1's view down to line 10 for the gutter's width.
- 2026-10-06, layout rows beyond the screen: cells may lie above 0 and below 1 and slide in smoothly. Every pane got a permanent cell at its virtual place; scrolling became one cheap `set_layout`, after Claude's per-pane scrolling had hit 60-110 ms per step.
- 2026-10-06, giving up twins and pane-by-pane wheel reading for one scroll strip: too many views scrolled at once cannot be smooth on every machine.
- 2026-10-05, tabs from headers: the original "editable tab" idea behind the headers: tabs where a pane needs them and none where it doesn't. Applied to the pane below the conversation: a header made of a few small horizontal panes, as tabs over a space for the ledger, route map and legend.
- 2026-10-05, read-only panes and a separate editor: the reader stays a reader. The editor lies over the lower right of the code column, set back so no colour of the frame touches the same colour in it, and carries the file's marks, which move with the edits.
- 2026-10-05, no phantoms in typing areas, and a faded, outlined control as the sign of something read-only (the `?` and the `Edit (Enter)` button).
- 2026-10-05, the conversation header as a tab, with a status from the agent that follows the topic like a live chat title.
- 2026-10-05, the band from the scheme's text colour: it always contrasts with the background, where Claude's grey barely did.
- 2026-10-05, the conversation pane ending at about 0.6, holding the transcript tightly, the space below kept for later.
- 2026-10-05, explain next / previous on the swap-line keys, which are useless in a chat.
- 2026-10-05, primary+w: first blocked against closing the reader's views by accident, then restored: a spoiled reader is easily recreated, and a sacred shortcut must not be touched.
- 2026-10-05, Esc then Don't Save: found the double dialog, which came from Claude writing its own dialog, and the fix: close the view and let Sublime ask.
- 2026-10-05, "sounds like a bug?": questioned Claude's "probably" about a window surviving reloads; the real cause was an unsaved buffer, not the open editor.
- 2026-10-05, "why can't you close before each reload?": led to readers closing themselves in `plugin_unloaded`.
- 2026-10-05, focus: the phantom filler kept clicks from focusing the conversation; real blank lines instead.
- 2026-10-05, a clone closed without saving leaves its changes in the other views: checked by experiment on the side. Led to the editor refusing to open while the file has unsaved changes elsewhere.
- 2026-10-05, names coloured as in the code: after Claude's plan (a generated per-reader syntax) and the dead end of regions, the idea of a light markup bound to the conversation syntax, which gives each kind of name the scope it has in code. Then the real scopes, read from the code itself: calls for functions, defined and built-in classes told apart, and a stippled underline for every name because schemes like Mariana leave variables plain.
- 2026-10-05, errors are for the agent: they are its only feedback, so each says how to correct the call. Led to an audit of every error the bridge and tools return, and to the rule that problems found together are reported together.
- 2026-10-05, conversation left of the code: the code and its gutter with line numbers come next to the talk about them.
- 2026-10-05, no centring of code panes: tried in use and found of no value; the numbered marks pull attention better.
- 2026-10-05, scope as the single source: asked that the plugin find marked names by their scope, so the markup lives only in the syntax. Claude had written it that way already; the decision is recorded as Jakub's.
- 2026-10-04, `point` format: "file:line" is ambiguous when two panes show the same lines (a function called twice, recursion). The first pane was picked silently, so a mark could land on the wrong copy while the agent talked about the other. Found by reading the format, before any test hit it. Now an error naming the panes.
- 2026-10-04, layout: a small overlap of cells hides the border between panes, a Sublime trick Claude didn't know. A 2 px overlap removes the line under each header.
- 2026-10-04, eye on headers: noticed the off-screen eye skipped headers, so a header at the screen edge counted as invisible. Headers became lines that can carry the eye.
- 2026-10-04, header gutter: spotted the grey header gutter that led to the caret-line highlight painting it.
- 2026-10-04, no scroll strip: the wheel over code and headers scrolls the reader; a code view's content moves only with the caret. Removes a whole view and settles the bug where one scrolled view lost its icons.
- 2026-10-04, outlines instead of code tint: once marked lines are outlined, the tint has no job left. Fewer colours, same information.
- 2026-10-04, transcript ending at the pane's centre: turns the lower half of the conversation pane into new space (ledger, route map and legend ideas).
- 2026-10-04, off-screen eyes: an eye looking up or down replaces the ⬆️/⬇️ strip hints, sits in the gutter, and takes priority over the edge line's own icon while its outline stays.
- 2026-10-04, there and back as two steps: the agent never shows call and return in one `point` call, so a line never needs two icons. Removed the need for combined icons.
- 2026-10-04, marks next to the code: emoji in a separate strip were hard to align with their lines. The "vertical phantom" proposal led to icons in Sublime's own gutter.
- 2026-10-04, direction in the arrows: jumps show where control goes (⤴/⤵ as exemplars), leaving from the right edge, next to the code; the receiving arrow arrives from above or below.
- 2026-10-04, SF Pro: asked whether the icon font could be shipped. It can't; switched to Inter.
- Earlier, conversation guard: chose `TextChangeListener.on_text_changed` on resilience, simplicity and speed, and corrected Claude's wrong claim that any listener would leak.
- Earlier, one conversation pane instead of transcript plus input box, so the transcript can be copied with the keyboard without switching panes.
- Earlier, headers as panes, not phantoms, because phantom text can't be copied.
- Earlier, simultaneous contrast: a strong header band makes the code tints of different files harder to tell apart, so the two are tuned together.
