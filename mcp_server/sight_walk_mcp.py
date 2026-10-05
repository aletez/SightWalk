import json
import os
import socket
from typing import Optional

from mcp.server.mcpserver import MCPServer

HERE = os.path.dirname(os.path.abspath(__file__))

MANUAL = """
You review code with the user in a Sublime Text reader window. The left column shows a
vertical sequence of panes, each a line range of a file, with a header above each. Your
marks appear as icons in the gutter, and the right pane is the conversation.

Showing code
- A pane is written <file>:<begin>-<end>, lines 1-based and inclusive.
- Show the panes in the order of one possible program run: the entry point first, then each
  function as control reaches it. When the user asks about another branch (an error, a
  different input, another caller), call show again with the sequence for that branch.
- Each pane holds exactly one whole function, from its signature to its last line.

Writing code that fits the reader
- Keep functions short, so that one and a half panes fit on the screen at once. With a
  typical window that means at most about 25 lines per function.
- When a function is longer, split it into well-named helpers before showing it.

Conversation
- Call wait_for_user to receive the user's next message. It returns the text, the pane
  nearest the middle of the screen (focus) and the visible panes. On timeout, call it again.
- The user can edit a shown file in the reader. Then wait_for_user also returns edited: the
  panes whose ranges changed, with their new ranges ("sw/a.py:10-20, now 10-23"). Use the new
  line numbers, and call show again if the run you are showing has changed.
- Resolve indexicals such as "here", "this", "it" or "this line" against focus, unless the
  message clearly points elsewhere.
- Answer with say. Keep answers short. Then call wait_for_user again.
- When the topic moves on, pass say a status: a few words on what the conversation is about
  now, like a chat title that follows along. It stays in the header until you change it.
- "Explain next." and "Explain previous." (sent by shortcuts) mean the next or previous step
  in the run order you are showing.
- Mark every name of code you mention, so it takes the colour it has in the code:
  `run_on_main` for functions and methods, **Reader** for classes and types, ~request~ for
  variables, parameters and attributes. Write keywords and constants plainly. Stress with
  wording, not with bold: ** is for class names.

Indicators
- Before or together with an answer that refers to specific lines, call point. Every marked
  line is outlined, and its icon sits in the gutter.
- A line is "file:line" (absolute file line) or {"pane": index, "line": line}.
- Jumps of control: {"from": line, "to": line}. Call site and the callee's first line, return
  and the call site it goes back to, raise and its handler. The arrows bend towards each other.
  Say in the conversation which jump it is. There and back are two separate point calls.
- Other marks: {"at": line, "mark": "A"}.
  A, B, C ... lines without an order: A alone is the line your sentence is about; A and B are
     two lines to compare.
  1, 2, 3 ... any ordered relation: a value produced and where it is used, a cause and its
     symptom, steps. Say what the order means.
- When a mark is off screen, an eye on the first or last visible line looks towards it.
"""

mcp = MCPServer("sight-walk", instructions=MANUAL)


def load_config():
    # Written by 'SightWalk: Set Up Agent Bridge' in Sublime, next to this file.
    with open(os.path.join(HERE, "config.json"), encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_config()


def call(op, timeout=15, **args):
    request = dict(args, op=op, token=CONFIG["token"])
    try:
        with socket.create_connection(("127.0.0.1", CONFIG["port"]), timeout=timeout) as conn:
            conn.sendall((json.dumps(request) + "\n").encode("utf-8"))
            line = conn.makefile(encoding="utf-8").readline()
        return json.loads(line)
    except (OSError, ValueError) as e:
        # Errors are the agent's only feedback, so each says what to do next.
        return {"error": "Sublime did not answer on port %d (%s). Right after a plugin reload, "
                         "retry in a second; otherwise ask the user whether Sublime is running "
                         "with SightWalk." % (CONFIG["port"], type(e).__name__)}


@mcp.tool()
def show(panes: list[str], root: Optional[str] = None) -> dict:
    """Open or replace the reader, scrolled to the top. panes: specs like "src/app.py:12-30" in
    program-run order. root: base folder for relative paths."""
    return call("show", panes=panes, root=root)


@mcp.tool()
def say(text: str, status: Optional[str] = None) -> dict:
    """Append your message to the conversation pane. status: a few words on what the
    conversation is about right now, shown in its header until changed."""
    return call("say", text=text, status=status)


@mcp.tool()
def point(marks: list[dict], reveal: bool = True, clear: bool = True) -> dict:
    """Place marks. A jump of control is {"from": "app.py:57", "to": "app.py:12"}; any other mark
    is {"at": "app.py:30", "mark": "1"} with a digit 1-9 or a letter A-Z (default "A"). A line is
    "file:line" or {"pane": 2, "line": 12}. reveal scrolls the marks into view. clear removes
    earlier marks first."""
    return call("point", marks=marks, reveal=reveal, clear=clear)


@mcp.tool()
def state() -> dict:
    """Return the panes, the focus pane nearest the screen centre and the visible panes."""
    return call("state")


@mcp.tool()
def close() -> dict:
    """Close the reader window."""
    return call("close")


@mcp.tool()
def settings(values: Optional[dict] = None) -> dict:
    """Read the user's SightWalk settings, or change them: values like {"tint": 0.2}.
    Editable, each from 0 to 1: tint (header band and gutter, as a share of the file's fully
    saturated hue; applies to the next reader window: close, then show) and conversation_height
    (bottom of the conversation pane as a share of the window; applies on the next scroll)."""
    return call("settings", values=values)


@mcp.tool()
def wait_for_user(timeout_s: int = 110) -> dict:
    """Wait for the user's next message. Returns text, focus and visible, or timeout."""
    return call("wait_for_user", timeout=timeout_s + 5, timeout_s=timeout_s)


if __name__ == "__main__":
    mcp.run()
