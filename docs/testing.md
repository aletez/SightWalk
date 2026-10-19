# Testing in Sublime

Each step checks one link in the chain. If a step fails, stop and record the step number, what you saw, and the console output or a screenshot.

## 0. Install

The repository root is the package. It is symlinked into Sublime:

```bash
ln -s ~/code/SightWalk ~/Library/Application\ Support/Sublime\ Text/Packages/SightWalk
```

After changing anything under `sw/`, run the unit tests (`python3 -m unittest discover tests`), then restart Sublime or save `sight_walk.py`, which reloads the `sw` modules. Reader windows close themselves on a reload.

## 1. The plugin loads

Console (View > Show Console): `reloading plugin SightWalk.sight_walk`, with no traceback after it.

## 2. Setup command

Command palette: **SightWalk: Set Up Agent Bridge**. Pass:
- An output panel with three steps appears.
- `~/.sight_walk/config.json` holds the token and port, `-rw-------`.
- The clipboard holds `claude mcp add --scope user --transport http sight-walk http://127.0.0.1:47321/mcp --header "Authorization: Bearer …"`.
- `Packages/User/SightWalk.sublime-settings` contains a `token`.

Running it again keeps the token.

## 3. The executor without the agent

From the repository root. A Sublime command that runs `poke.py` must start the subprocess off the main thread (`sublime.set_timeout_async`), because the executor needs the main thread to answer; otherwise Sublime freezes for 10 s and the call fails.

| Command | Pass |
|---|---|
| `python3 tools/poke.py show` | `{"ok": true}`. A window without tabs or sidebar: headers in two different hues above two sights, one whole function each, with a plain background and a gutter in the header's hue, the conversation on the left under a one-line grey header "Bench" with a faded `[?]` at its right; hovering it lists the shortcuts. |
| `python3 tools/poke.py say` | `A: Hello from the bridge.` appears above the prompt. |
| `python3 tools/poke.py marks` | An answer placing its own marks, counted from each sight's `def` line d: `1` framed in the text and as an icon on line d+3 of (a), `A` on d+7, "the jump" framed, from (a) d+1 to (b) d+2. A mark off screen shows an eye on the first or last visible line instead. |
| `python3 tools/poke.py double` | Two marks on line d+3 of (a): the first in the gutter, the second on the strip between the bench and the Sights. |
| `python3 tools/poke.py state` | JSON with `sights` and `visible`, and `here` (`"(a):12:5"`) once a sight has the caret. |
| `python3 tools/poke.py badtoken` | `Unauthorized…` |

## 4. Geometry and editing, by hand

- The wheel moves the whole trip only over the scroll strip, the empty fillers and ▼'s cell, and over the bench and the Tools pane while ⌘S lets them take it ([⇕] in the Tools header). Over a sight's code it scrolls that sight alone; over a header or a frozen line it does nothing. ▲▼ on the strip, Alt+↓/↑ (3 lines) and PageDown/PageUp (about a screen) move the trip too.
- Each sight is exactly as tall as its range. The last sight, when it fits with its header, scrolls up until its header is at the top, with the empty filler below. A taller last sight stops when the end of its range reaches the bottom.
- Marks sit in the gutter on their lines. Compare with the file opened normally.
- Opening or closing a panel, or resizing the window, keeps everything aligned.
- Enter in a sight, or the header's Edit button, opens the editor over the sights; it saves to the real file, Esc or End editing closes it and the panes return to where they were. Undo afterwards.

## 5. Vetting Bench

- The prompt sits at the bottom of the pane from the start.
- Type after `>>> ` and send with Cmd+Enter (Ctrl+Enter on Windows and Linux): the draft becomes `U: …`, a new prompt opens.
- Backspace at the start of the draft, typing into an `A:` line, cut from the transcript, Ctrl+Z after an answer arrived: the transcript comes back each time.
- The transcript can be selected and copied with the keyboard.

## 6. The agent

1. Paste the clipboard line from step 2, start a fresh `claude` session, check `/mcp` lists `sight-walk` with 8 tools.
3. Prompt: "Use the sight-walk tools to walk me through what happens when the plugin receives a show request, from subl_mcp_http's do_POST to Reader.column_rects, in execution order, then wait for my questions with wait_for_user. Use absolute paths."
4. Check: sights in run order, one function at most each; "what does this return?" answered about what is selected; "mark the call and its callee" gives a framed jump with its arrow icons; "what if the file doesn't exist?" rebuilds the trip.
