# SightWalk: instructions for every session

## What this is
A Sublime Text plugin for vetting AI-generated code. An agent connected over MCP opens a reader window and shows a sequence of panes (`file:begin-end`) chosen for one question: most often one run of the program, or a comparison, or a survey; one whole function per pane. It marks lines with icons in the gutter and talks with the user in a conversation pane, resolving "here" and "this" against the pane nearest the centre.

Names (see DECISIONS.md): the code column is **Sights** and a pane a **sight**; whatever one `show` opens is a **trip**, however long (the window too is called the trip; `docs/trips.md` only lists prepared ones); the UML diagram is the **Map**; a set of trips with the transitions between them is an **informator**, its trips in one planned order a **tour**; the conversation is the **Vetting Bench**; the reader window is, metonymically, the **trip**; the assistant is the **Vetting guide**. In code too a sight is a sight (`ontology.Sight`; as shown on screen, `plan.Pane`; `reader.sights`); the agent's `show` takes `sights` and a mark `{"sight": index, "line": line}`. The Polish names are a metaphor of their own: panorama, widok, wycieczka, mapa, informator, turnus, ławka, przewodnik (and wycieczka for the window too).

Concept and design: Jakub Kozakoszczak. Code: written by Claude. Say it that way; never call the code Jakub's.

Read `DECISIONS.md` before changing behaviour: it holds the design decisions, the reasons, and the current status.

## Layout
- The repository root is the Sublime package, symlinked as `Packages/SightWalk`.
- `sight_walk.py`: entry point. Imports the commands into its namespace (that is how Sublime registers them) and drops the `sw` modules from `sys.modules` so they reload.
- `sw/`: `config` (constants), `spec` (specs, display paths, pane titles), `plan` (geometry of the virtual document), `marks` (gutter icons, eyes), `header` (conversation header text), `chat` (conversation pane and header, transcript guard), `vetting` (the Tools pane under the conversation: tabs Map, drawn by Graphviz, Tour, a tour's trips in order, and Scroll), `scrollbars` (overlay scroll bars while a reader has the focus), `editor` (the editor over the panes), `views` (making views, drawing on them, the window layout), `guide` (starting a Claude Code guide in the background), `tint` (per-file hues, colour schemes), `state` (open readers), `geometry` (where the reader's columns and cells lie; Reader inherits it), `reader` (the Reader class), `commands`, `bridge` (what the agent's tools do in Sublime), `mcp_http` (the plugin itself as the MCP server, over HTTP), `manual` (the agent's manual and the tools' schemas), `callmap` (the Map tab's call graph, pure), `ontology` (sights, trips, informators, tours, places and transitions, pure; see DECISIONS.md), `questions` (guards the code already asks, pure), `asked` (their underlines and popups in a trip), `setup` (setup command), `words` (the words the user reads, English or Polish, pure).
- `plan.py`, `marks.py`, `spec.py`, `header.py`, `questions.py`, `ontology.py` and `words.py` must stay free of the Sublime API, so they can be tested with plain Python: `python3 -m unittest discover tests`.
- The MCP server is the plugin itself (`mcp_http`, HTTP on the settings' port, a bearer token). The setup command puts the `claude mcp add --transport http` line on the clipboard and writes `~/.sight_walk/config.json` (token, port) for `tools/poke.py`.
- `SightWalkChat.sublime-syntax`: colours of the conversation pane, display only.
- `tools/poke.py`: drives the plugin without an agent. `tests/`: unit tests of the pure modules. `docs/trips.md`: the plugin's own code split into trips, every function in one at least, written by `tools/trips.py` (run it after changing the code; it names what no trip covers). `docs/testing.md`: the test procedure.

## Working agreements
- Jakub designs, Claude implements. For new UI behaviour, restate the rule in your own words before building, and ask when it is ambiguous. Propose alternatives with reasons; don't decide UI behaviour alone.
- Never report a feature as working before Jakub has seen it in Sublime. Keep the status in `DECISIONS.md` current: verified in Sublime, changed but unverified, open.
- Work in small steps: one change, test (unit tests for pure modules, `tools/poke.py` against the running plugin), Jakub checks in Sublime, commit. Clear commit messages, no model names in them.
- Functions stay short (about 25 lines or fewer): the plugin is vetted with itself, one function per pane.
- The plugin runs in Sublime's Python 3.8 host (`.python-version`), the MCP server included: standard library only. The Map tab needs Graphviz's `dot` (a program, `brew install graphviz`).
- After changing `sw/`: Sublime needs a reload (restart, or save `sight_walk.py`). Reader windows close themselves on reload; the agent calls `show` again afterwards. After changing the manual or the tools (`sw/manual.py`): start a new Claude Code session, which reads them at its start.
- If anything ever has to be pasted by Jakub, give whole files, never partial edits.

## Style
- Concise. At most two questions per turn, and end the turn after a question.
- No narration, no apologies; if something you said was wrong, give the correct version.
- Answer in the language Jakub writes in.

## Sublime facts learned the hard way
- Text commands, listeners, `plugin_loaded` are found by scanning the top-level plugin module's namespace; imported names count.
- View settings override syntax-specific settings. Plain Text has Jakub's own font, so headers and side views copy a font's settings (`match_font`).
- A freshly written colour scheme is usable only after Sublime indexes it; poll `find_resources` (`when_indexed`), never a fixed delay.
- Replacing text that contains the caret selects the new text.
- On macOS, `viewport_extent` leaves out the overlay horizontal-scrollbar strip, although text is painted there.
- An open panel or a window resize changes the layout height; the conversation and the vetting pane together change one to one with it (`follow_resize`).
- Sublime draws earlier groups over later ones; overlapping cells hide borders and let one pane lie over another.
- Read-only belongs to the buffer, not the view: all clones of a file share it.
- `text_to_window` of a pane's text start comes back relative to the pane, which gives its gutter width.
- A subprocess started from a command blocks the main thread, which the bridge needs (`run_on_main`): use `sublime.set_timeout_async`.
- `TextChangeListener.on_text_changed` reports every real edit with positions, whatever command made it; `on_modified` only says that something changed.
- Block phantoms sit below a line, never above the first one; a tall inline phantom draws its line's text at the top, so it makes room below, not above.
- `viewport_extent` is 0 until Sublime has laid a view out: measure after a render, not in the same call.
