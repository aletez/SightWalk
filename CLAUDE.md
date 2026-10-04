# SightWalk: instructions for every session

## What this is
A Sublime Text plugin for vetting AI-generated code. An agent connected over MCP opens a reader window and shows a sequence of panes (`file:begin-end`) that mirrors one run of the program, one whole function per pane. It marks lines in a narrow strip and talks with the user in a conversation pane, resolving "here" and "this" against the pane nearest the centre.

Concept and design: Jakub Kozakoszczak. Code: written by Claude. Say it that way; never call the code Jakub's.

Read `DECISIONS.md` before changing behaviour: it holds the design decisions, the reasons, and the current status.

## Layout
- The repository root is the Sublime package, symlinked as `Packages/SightWalk`.
- `sight_walk.py`: entry point. Imports the commands into its namespace (that is how Sublime registers them) and drops the `sw` modules from `sys.modules` so they reload.
- `sw/`: `config` (constants), `spec` (specs, display paths), `plan` (geometry of the virtual document), `marks` (strip indicators), `chat` (conversation pane, transcript guard, bottom filler), `views` (view and layout helpers), `tint` (per-file hues, colour schemes), `state` (open readers), `reader` (the Reader class), `commands`, `bridge` (local socket server for the MCP bridge), `setup` (setup command).
- `plan.py`, `marks.py` and `spec.py` must stay free of the Sublime API, so they can be tested with plain Python.
- `mcp_server/sight_walk_mcp.py`: the MCP server Claude Code runs. Sublime never loads it (subfolder). The setup command copies it to `~/.sight_walk/` with `config.json` (token, port).
- `SightWalkChat.sublime-syntax`: colours of the conversation pane, display only.
- `tools/poke.py`: drives the plugin without an agent. `docs/testing.md`: the test procedure.

## Working agreements
- Jakub designs, Claude implements. For new UI behaviour, restate the rule in your own words before building, and ask when it is ambiguous. Propose alternatives with reasons; don't decide UI behaviour alone.
- Never report a feature as working before Jakub has seen it in Sublime. Keep the status in `DECISIONS.md` current: verified in Sublime, changed but unverified, open.
- Work in small steps: one change, test (unit tests for pure modules, `tools/poke.py` against the running plugin), Jakub checks in Sublime, commit. Clear commit messages, no model names in them.
- Functions stay short (about 25 lines or fewer): the plugin is vetted with itself, one function per pane.
- The plugin runs in Sublime's Python 3.8 host (`.python-version`). The MCP server needs Python ≥ 3.10 and `mcp` ≥ 2 (`from mcp.server.mcpserver import MCPServer`).
- After changing `sw/`: Sublime needs a reload (restart, or save `sight_walk.py`), and old reader windows must be closed. After changing `mcp_server/`: run "SightWalk: Set Up Agent Bridge" and start a new Claude Code session.
- If anything ever has to be pasted by Jakub, give whole files, never partial edits.

## Style
- Concise. At most two questions per turn, and end the turn after a question.
- No narration, no apologies; if something you said was wrong, give the correct version.
- Answer in the language Jakub writes in.

## Sublime facts learned the hard way
- Text commands, listeners, `plugin_loaded` are found by scanning the top-level plugin module's namespace; imported names count.
- View settings override syntax-specific settings. Plain Text has Jakub's own font, so headers and the strip copy the code view's font settings (`match_font`).
- A freshly written colour scheme is usable only after Sublime indexes it; poll `find_resources` (`when_indexed`), never a fixed delay.
- Replacing text that contains the caret selects the new text.
- On macOS, `viewport_extent` leaves out the overlay horizontal-scrollbar strip, although text is painted there.
- An open panel or a window resize changes the layout height; the strip spans the whole column, so its extent tracks the change (`follow_resize`).
- A subprocess started from a command blocks the main thread, which the bridge needs (`run_on_main`): use `sublime.set_timeout_async`.
- `TextChangeListener.on_text_changed` reports every real edit with positions, whatever command made it; `on_modified` only says that something changed.
- Block phantoms sit below a line, never above the first one.
