"""What the agent's tools do in Sublime (see mcp_http, which serves them): each operation runs on
Sublime's main thread; wait_for_user waits on the inbox on the server's own thread."""

import os
import queue
import threading
import time

import sublime

from . import scrollbars, state
from .config import (DEFAULT_BENCH_SIDE, DEFAULT_CONVERSATION_HEIGHT, DEFAULT_PORT, SETTINGS_FILE,
                     TINT)
from .ontology import Sight, Transition, Trip
from .reader import Reader
from .spec import parse_spec
from .views import hide_chrome

CONFIG = {"token": None, "port": DEFAULT_PORT}
EDITABLE = {"tint": TINT, "default_conversation_height": DEFAULT_CONVERSATION_HEIGHT,
            "bench_side": DEFAULT_BENCH_SIDE}


# Operations, run on Sublime's main thread

def file_lines(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def check_sights(sights, root):
    """Every problem with the sights in one message, so the agent can fix them all at once."""
    if not sights:
        raise ValueError('Give at least one sight, like "app.py:12-30".')
    problems = []
    for spec in sights:
        path, _, end = parse_spec(spec, root)
        if not os.path.isfile(path):
            problems.append("%s: no file at %s" % (spec, path))
        elif end > file_lines(path):
            problems.append("%s: the file has %d lines" % (spec, file_lines(path)))
    if problems and not root and any("no file" in p for p in problems):
        problems.append("relative paths need root, or give absolute paths")
    if problems:
        raise ValueError("; ".join(problems) + ".")


SIGHT_FORM = ('{"sight": "file:begin-end", "calls": [{"line": 15, "to": [3, 42]}]}: line 15 '
              'of this sight calls the definition at line 42 of sight 3 (sights from 0, file '
              'lines); "calls": [] when it calls no other sight')


def make_trip(sights, name):
    """The trip show was given, its calls checked by the ontology. Every sight names its calls,
    an empty list included: the map never guesses (Jakub)."""
    found, calls = [], []
    for i, entry in enumerate(sights or []):
        if not isinstance(entry, dict) or not isinstance(entry.get("sight"), str) \
                or not isinstance(entry.get("calls"), list) \
                or not all(isinstance(c, dict) for c in entry["calls"]):
            raise ValueError("Sight %d: give each sight as %s. Name every call between the "
                             "trip's sights; the Map draws them." % (i, SIGHT_FORM))
        found.append(Sight.parse(entry["sight"]))
        calls += [Transition("calls", (i, c.get("line")), c.get("to") or ())
                  for c in entry["calls"]]
    return Trip(name or "", found, calls)


def new_reader():
    """A new window for a reader, its two polling loops started."""
    sublime.run_command("new_window")
    window = sublime.active_window()
    hide_chrome(window)
    reader = Reader(window)
    state.register(reader)
    sublime.set_timeout(reader.close_hijacker, 500)  # see Reader.close_hijacker
    reader.poll()
    reader.poll_wheel()
    return reader


def check_not_stopped():
    if state.STOPPED:
        raise RuntimeError("The user stopped this answer. Say and show nothing more about it; "
                           "call wait_for_user.")


def op_show(sights=None, root=None, trip=None):
    check_not_stopped()
    made = make_trip(sights, trip)
    check_sights([sight.spec for sight in made], root)
    reader = state.current_reader() or new_reader()
    reader.load(made, root)
    state.ADDRESSED = True  # the agent may say what the trip is about
    scrollbars.reader_focused(True)  # a new window is not reported as activated
    return {"ok": True}


def op_say(text, status=None):
    check_not_stopped()
    reader = state.current_reader()
    if reader is None:
        raise RuntimeError("No trip is open. Call show first.")
    if not state.ADDRESSED:
        raise ValueError("Nothing to answer: the user has said nothing since you last waited. "
                         "Say nothing; call wait_for_user.")
    reader.say(text, status)
    return {"ok": True}


def op_point(marks, reveal=True, clear=True):
    check_not_stopped()
    state.require_ready().point(marks, reveal, clear)
    return {"ok": True}


def op_state():
    reader = state.require_ready()
    return dict(reader.context(), sights=[sight.spec for sight in reader.sights])


def op_close():
    reader = state.current_reader()
    if reader is None:
        raise RuntimeError("No reader window is open, so there is nothing to close.")
    reader.window.run_command("close_window")
    return {"ok": True}


def op_browse(folder):
    """A trip with no sights, the folder's files in their place (Jakub); it replaces the open
    trip, the conversation goes on. A file the user opens there becomes the trip's sight."""
    folder = os.path.expanduser(folder)
    if not os.path.isdir(folder):
        raise ValueError("Not a folder: %s. Give an absolute path to an existing folder." % folder)
    reader = state.current_reader()
    if reader is not None:
        reader.window.run_command("close_window")
    new_reader().open_empty(folder)
    scrollbars.reader_focused(True)
    return {"ok": True}


def check_setting(key, value):
    if key not in EDITABLE:
        raise ValueError("Not editable: %s. Editable: %s" % (key, ", ".join(EDITABLE)))
    if key == "bench_side":
        if value not in ("left", "right"):
            raise ValueError('bench_side must be "left" or "right".')
    elif not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
        raise ValueError("%s must be a number from 0 to 1." % key)


def op_settings(values=None):
    settings = sublime.load_settings(SETTINGS_FILE)
    for key, value in (values or {}).items():
        check_setting(key, value)
        settings.set(key, value)
    if values:
        sublime.save_settings(SETTINGS_FILE)
    return {key: settings.get(key, default) for key, default in EDITABLE.items()}


OPS = {"show": op_show, "say": op_say, "point": op_point, "state": op_state,
       "close": op_close, "settings": op_settings, "browse": op_browse}


def run_on_main(fn, timeout=10):
    done, box = threading.Event(), {}

    def run():
        try:
            box["value"] = fn()
        except Exception as e:
            box["error"] = e
        done.set()

    sublime.set_timeout(run, 0)
    if not done.wait(timeout):
        raise RuntimeError("Sublime did not respond within %d s. It may be busy indexing or "
                           "showing a dialog: retry once, then ask the user to look." % timeout)
    if "error" in box:
        raise box["error"]
    return box["value"]


def wait_until_ready(timeout=8):
    """Off the main thread: until the open trip has laid itself out, so marks given right after
    show are not lost (Jakub). Gives up quietly; the operation then says why."""
    end = time.time() + timeout
    while time.time() < end:
        reader = run_on_main(state.current_reader)
        if reader is None or reader.ready:
            return
        time.sleep(0.05)


def wait_for_user(timeout_s=110):
    if state.current_reader() is None:
        return {"error": "No trip is open. Call show first."}
    state.WAITING += 1
    state.ADDRESSED = state.STOPPED = False
    try:
        message = state.INBOX.get(timeout=timeout_s)
        state.ADDRESSED = True
        return message
    except queue.Empty:
        # The agent must not fill the silence: the user sees every say (Jakub).
        return {"timeout": True, "next": "No message yet. Say nothing; call wait_for_user again."}
    finally:
        state.WAITING -= 1
        state.LAST_WAIT = time.time()


# Settings

def load_config():
    """The token Claude Code must send and the port the server listens on (see mcp_http)."""
    settings = sublime.load_settings(SETTINGS_FILE)
    CONFIG["token"] = settings.get("token")
    CONFIG["port"] = settings.get("port", DEFAULT_PORT)
