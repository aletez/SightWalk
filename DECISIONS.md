# Decisions and status

Newest first within each section. "J" = decided by Jakub, "C" = proposed by Claude and accepted.

## Status

Verified in Sublime:
- Plugin loads; the setup command writes the token once and keeps it.
- `show` and `say` through the bridge.
- Headers and strip use the code view's font; headers are not selected on creation.
- Per-file hues: code tint 2%, header band 25%; schemes applied only after indexing (no error dialogs).

Changed, not yet verified in Sublime:
- `follow_resize` (panels, window resize).
- Squared marks in the agent manual (needs the setup command again and a fresh Claude Code session).
- Scroll limit (`plan.max_offset`) and the filler view below the last pane.
- Tint amounts read from settings (`tint`, `header_tint`).
- Conversation pane: transcript guard, prompt kept at the bottom by a filler phantom, conversation syntax.
- Repo-relative header paths, outlined ranges (`add_regions`), `~` in specs, suffix matching at path separators.

Open:
- Outline: explain to Jakub how the `add_regions` outline looks (it follows the text, not a rectangle) and decide whether that is what he wants.
- Long paths in narrow windows: shorten from the left (`…/sw/reader.py:1-30`) if repo-relative is not enough.
- HTML header pane with a copy link; key binding to copy the spec of the focused or centred pane.
- Header-jump artefact when a sliver merges into a neighbour.
- Dependency-free MCP server (standard library only) for shipping; `.gitattributes` export-ignore for dev files before Package Control.
- Self-vetting walk-through: Jakub reads the plugin's own code through the reader.
- Shipping defaults for `tint` / `header_tint` (Jakub is tuning).
- Possible VS Code port; open question: one scroll for the whole layout or per-pane scrolling.

## Decisions

Conversation pane
- J: One conversation pane, not a transcript plus input box, so the transcript can be copied with the keyboard without switching panes. The prompt stays at the bottom: an invisible block phantom fills the space above the transcript (below a blank first line), measured and corrected on each poll.
- J: The transcript is protected with `TextChangeListener.on_text_changed` (criteria: resilience, KISS, execution time). Claude had wrongly argued that any listener would leak; `on_text_command` would need a list of editing commands and cannot see what undo does. Fast path: changes after the protected length are ignored without reading the buffer.
- C: The draft boundary is the recorded length of the protected text, set before each of the plugin's own edits. The syntax is for colour only, because agent text could fake a prompt.

Marks
- J: Only emoji on their own coloured square, visible on any theme. *️⃣ this line ("the missing part of what is being said"); ➡️ passes control, ⬅️ takes control (call/callee, return/call site, raise/handler); 1️⃣ 2️⃣ 3️⃣ other ordered relations; 🅰️ 🅱️ compare. The agent names the relation in the conversation. ⬆️/⬇️ for marks off screen.

Panes and scrolling
- J: Every pane, the last one included, is exactly as tall as its range. An empty filler view takes the rest of the column.
- J: If the last pane fits on screen with its header, scrolling stops when its header reaches the top; otherwise when the end of its range reaches the bottom.
- C: The strip spans the whole column; wheel movement over it is read by polling an anchored buffer (the API has no wheel events).

Headers and colour
- J: Headers in a separate pane, not phantoms (phantom text cannot be copied). Header path relative to the repository root by default, `~/…` outside a repository; no setting until needed.
- J: The range is outlined with `add_regions`.
- J: Header band clearly stronger than the code tint; a strong header makes different files' code tints harder to tell apart (simultaneous contrast), so the two are tuned together, in settings.

Name
- J: SightWalk: sightseeing with a guide, and a sidewalk (the conversation) running alongside the street of code. Chosen over RunWalk, RuntimeWalk, TraceWalk ("trace" suggests errors) and CodeSightWalk (the prefix hides the sidewalk). No software project or Package Control package uses the name (checked 2026-10-04); a 2024 accessibility campaign in Lima is called "SightWalks".

Process
- J: Whole files only when anything is pasted; checkpoints by hash (`shasum -a 256 -c`), now replaced by git commits.
- J: Development moves to a local Claude Code session in this repository, symlinked into Sublime.
