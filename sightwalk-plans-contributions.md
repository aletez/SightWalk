# SightWalk: plans and Jakub's contributions (export, 2026-10-07)

Concept and design: Jakub Kozakoszczak. Code: written by Claude. Source: DECISIONS.md and Claude's memory of the project.

## Plans (Jakub)

- Philosophy (Jakub): vettable code or no code at all.
- Vettify / vettification (names, Jakub): making code vettable, the mechanical refactorer below.
- A mechanical refactorer for legacy code (Jakub): it reshapes existing code into walkable functions with a guarantee that the logic did not change; only then vetting by trips. Shape (Claude): a small catalogue of transformations (extract a block into a function, split a function at a statement boundary), each applied only where its preconditions are checked on the syntax tree (single entry and exit, no return/yield/break/continue/nonlocal in the block, the variables it reads become parameters, those it writes and later reads become results), and refused anywhere else. Each result is validated by translation: inlining it back mechanically must give the original tree, normalised. The model may only propose where to cut and what to call the new functions; names are the one part the human vets, the logic is untouched by construction. Stated limits: Python's introspection (locals(), frames, tracebacks, recursion depth) is outside the guarantee.
- README: the English README links to a Polish one, written in the Polish metaphor (panorama, widok, wycieczka, marszruta, mapa, ławka).
- Far future, only after SightWalk has been used in recruitment: a Polish-language version of the tool.
- If this approach to vetting catches on: promote writing code for it. Tell the coding assistant to write with trips in mind: each trip from one branch point to the next (not necessarily at most six sights), so that at the end of a trip the user can decide on the values of the new variables.
- Assistant personalities, two or three to choose from in later versions: a senior who explains hard code well; a junior who presents their code to a senior and states their doubts clearly.
- Vetting on the dry, ideas (2026-10-06), all without running the code:
  - Questions the code already asks, carried elsewhere (Jakub's implicit clever question as a mechanism): every guard in the code (is_valid, is None, emptiness) is a question its author once asked; where the same kind of object is used without it, the trip says where the code asks it. Done first (see Status).
  - Crossings: a sight on several trips shows all its arrivals, who comes and with what, from the call graph; bugs live where a function assumes one arrival's state and gets another's.
  - The user tells the trip back, in a metaphor, as the spec; a sceptical guide only checks, sentence by sentence, where the code does something else. A "Change the metaphor" button retells a step or a trip and reminds the user they can tell it too.
- Three further ideas (Claude, for safe and effective generation at superhuman speed):
  - Trust seals that survive changes: a sight walked carries a seal (who, when, which trip, content hash); a change breaks only the seals it touches, and SightWalk plans the shortest itinerary that restores them. Review cost follows the change, not the codebase; the generating agent sees the seal map.
  - Stories as specification: the user's own tellings stay with the sights; every later change is checked, dry, against all earlier stories about those places (a regression of meaning).
  - Walkable code or none: a mechanical gate before any human looks (each function fits a sight, each changed line lies on a named trip from branch point to branch point); and the guide is never the session that wrote the code.
- Open, 2026-10-07 (from Jakub's first real use): icons in the gutter.
  - Two icons side by side on one line, so a jump and a numbered mark no longer hide each other.
  - `show` takes the marks right away, so a trip never opens without icons.
  - The guide refers to icons in the bench with characters that can't be typed (e.g. ❶, Ⓐ), coloured like the icons by their own scope. Jakub's idea came from the guide writing **1** around icon numbers.

## Memory notes

- The README: the English README links to a Polish one, written in the Polish metaphor (panorama, widok, wycieczka, marszruta, mapa, ławka); "zabytek" sounds dead and negative in technology.
- The Polish prepositions: "w ławce", "w wycieczce" (the panel and the window), not "na ławce" and never "przez ławkę".

## Jakub's strong contributions

Ideas and catches that changed the design or prevented a real defect, beyond everyday direction. Claude adds to this list when one happens; newest first.

- 2026-10-06, the strip lives as long as its window: parked out of the window instead of closed, so what the user set on it stays, and an empty window no longer closes.
- 2026-10-06, the bridge validates say: a guide that says something with nothing to answer is refused, after instructions alone failed twice.
- 2026-10-06, "this" is the selection at the moment of asking, not at opening, and an expression, not the function around it.
- 2026-10-06, the guide starts from Sublime: asking with no agent listening starts one, so the user never goes to a terminal; and the indicator that an answer is coming.
- 2026-10-06, the Vetting strip: instead of Claude's box laid over the code (which would recall DOS-era software), the window's layout glides aside and the conversation glides in on the selection's side; no header (the user may show tabs), a floor under the prompt, the status in the status bar or under the floor.
- 2026-10-06, the names: Sights, sight, trip (whatever one show opens, however long), Itinerary, Map, Vetting Bench, Vetting Guide; a separate Polish metaphor (panorama, widok, wycieczka, marszruta, mapa, ławka, przewodnik), because "zabytek" sounds dead in technology.
- 2026-10-06, the whole code covered by trips of similar difficulty, and the plan to write code for trips from one branch point to the next.
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
