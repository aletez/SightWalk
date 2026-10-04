# Testing in Sublime

Each step checks one link in the chain. If a step fails, stop and record the step number, what you saw, and the console output or a screenshot.

## 0. Install

The repository root is the package. It is symlinked into Sublime:

```bash
ln -s ~/code/SightWalk ~/Library/Application\ Support/Sublime\ Text/Packages/SightWalk
```

After changing anything under `sw/`, restart Sublime (or save `sight_walk.py`, which reloads the `sw` modules). Close any reader window that was open before the reload: the plugin forgets it.

## 1. The plugin loads

Console (View > Show Console): `reloading plugin SightWalk.sight_walk`, with no traceback after it.

## 2. Setup command

Command palette: **SightWalk: Set Up Agent Bridge**. Pass:
- An output panel with three steps appears.
- `~/.sight_walk/` contains `sight_walk_mcp.py` and `config.json`; `config.json` is `-rw-------`.
- The clipboard holds `claude mcp add --scope user sight-walk -- "/Users/…/.sight_walk/venv/bin/python" "/Users/…/.sight_walk/sight_walk_mcp.py"`.
- `Packages/User/SightWalk.sublime-settings` contains a `token`.

Running it again keeps the token. Run it after every change in `mcp_server/`.

## 3. The bridge without the agent

From the repository root. A Sublime command that runs `poke.py` must start the subprocess off the main thread (`sublime.set_timeout_async`), because the bridge needs the main thread to answer; otherwise Sublime freezes for 10 s and the call fails.

| Command | Pass |
|---|---|
| `python3 tools/poke.py show` | `{"ok": true}`. A window without tabs or sidebar: headers in two different hues above two panes with a plain background and a gutter in the header's hue, the strip, and the conversation with a faint `⌘+Enter to send` after the prompt. |
| `python3 tools/poke.py say` | `A: Hello from the bridge.` appears above the prompt. |
| `python3 tools/poke.py point` | Gutter icons, each line outlined: ⤵ on line 5 and ↳ on line 40, a 1 on line 8, an A on line 12. A mark off screen shows an eye on the first or last visible line instead. |
| `python3 tools/poke.py state` | JSON with `panes`, `focus` and `visible`. |
| `python3 tools/poke.py badtoken` | `Unauthorized…` |

## 4. Geometry and editing, by hand

- Wheel over the strip: all panes scroll together and the strip snaps back. Alt+↓/↑ scroll 3 lines, PageDown/PageUp about a screen.
- Each pane is exactly as tall as its range. The last pane, when it fits with its header, scrolls up until its header is at the top, with the empty filler below. A taller last pane stops when the end of its range reaches the bottom.
- Lines in each pane line up with their marks in the strip. Compare with the file opened normally.
- Opening or closing a panel, or resizing the window, keeps everything aligned.
- A code pane is editable and saves to the real file. Undo afterwards.

## 5. Conversation pane

- The prompt sits at the bottom of the pane from the start.
- Type after `› ` and send with Cmd+Enter (Ctrl+Enter on Windows and Linux): the draft becomes `U: …`, a new prompt opens.
- Backspace at the start of the draft, typing into an `A:` line, cut from the transcript, Ctrl+Z after an answer arrived: the transcript comes back each time.
- The transcript can be selected and copied with the keyboard.

## 6. The agent

1. `~/.sight_walk/venv/bin/python -c "import mcp.server.mcpserver"` runs silently (the environment from the setup panel, step 1).
2. Paste the clipboard line from step 2, start a fresh `claude` session, check `/mcp` lists `sight-walk` with 7 tools.
3. Prompt: "Use the sight-walk tools to walk me through what happens when the bridge receives a show request, from sw/bridge.py dispatch to plan.visible_cells, in execution order, then wait for my questions with wait_for_user. Use absolute paths."
4. Check: panes in run order, one whole function each; "what does this return?" answered about the centred pane; "point at the call and its callee" gives ⤵ and ↳; "what if the file doesn't exist?" rebuilds the sequence.
