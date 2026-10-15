"""What the agent's tools do in Sublime (see mcp_http, which serves them): each operation runs on
Sublime's main thread; wait_for_user waits on the inbox on the server's own thread."""

import json
import os
import queue
import threading
import time

import sublime

from . import scrollbars, state
from .config import (DEFAULT_BENCH_SIDE, DEFAULT_CONVERSATION_HEIGHT, DEFAULT_PORT, SETTINGS_FILE,
                     TINT)
from .marks import line_refs, speaks_of_code, untag
from .ontology import Sight, Transition, Trip, trip_from
from .reader import Reader
from .spec import parse_spec, repo_root
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


TRANSITION_FORM = ('{"type": "calls", "from": [0, 15], "to": [3, 42]}: line 15 of sight 0 '
                   'calls the definition at line 42 of sight 3 (sights from 0, file lines)')


def make_trip(sights, transitions, name):
    """The trip show was given, its transitions checked by the ontology. transitions is required,
    an empty list included: the map never guesses (Jakub)."""
    if not isinstance(sights, list) or not all(isinstance(s, str) for s in sights):
        raise ValueError('sights: a list like ["app.py:12-30", "app.py:40-52"].')
    if not isinstance(transitions, list) or not all(
            isinstance(t, dict) and all(isinstance(t.get(end), list) for end in ("from", "to"))
            for t in transitions):
        raise ValueError("transitions: name every call (and other transition) between the "
                         "trip's sights, each as %s; [] when there are none. The Map draws "
                         "them." % TRANSITION_FORM)
    made = [Transition(t.get("type"), t["from"], t["to"]) for t in transitions]
    return Trip(name or "", [Sight.parse(spec) for spec in sights], made)


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


def op_show(sights=None, transitions=None, root=None, trip=None):
    check_not_stopped()
    made = make_trip(sights, transitions, trip)
    check_sights([sight.spec for sight in made], root)
    reader = state.current_reader() or new_reader()
    reader.load(made, root)
    state.ADDRESSED = True  # the agent may say what the trip is about
    scrollbars.reader_focused(True)  # a new window is not reported as activated
    return {"ok": True}


MARK_FIRST = ("This answer names code, and nothing is marked yet: call point first with the lines "
              "it speaks of (each gets an outline and an icon), then say it again. The user "
              "asked that every answer about code comes with its marks. Do not call wait_for_user "
              "before you have answered.")
NO_LINE_NUMBERS = ("Line numbers obscure the answer (the user asked): point at the lines and name "
                   "them by their icons, 1, 2, A, B, never by numbers or file:line. Found: %s.")
UNANSWERED = ("This message is still unanswered (a guide before you may have taken it): answer "
              "it with say, point first if the answer names code, then wait.")


def op_say(text, status=None):
    check_not_stopped()
    reader = state.current_reader()
    if reader is None:
        raise RuntimeError("No trip is open. Call show first.")
    if not state.ADDRESSED:
        raise ValueError("Nothing to answer: the user has said nothing since you last waited. "
                         "Say nothing; call wait_for_user.")
    text = untag(text)
    numbers = line_refs(text)
    if numbers:
        raise ValueError(NO_LINE_NUMBERS % ", ".join(numbers))
    if not state.POINTED and speaks_of_code(text):
        raise ValueError(MARK_FIRST)
    reader.say(text, status)
    state.ANSWERED = True
    return {"ok": True}


def op_point(marks, reveal=True, clear=True):
    check_not_stopped()
    state.require_ready().point(marks, reveal, clear)
    state.POINTED = True
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


def op_open_trip(file, root=None):
    """A trip from its file (written by an informator's author), its paths relative to root, by
    default the file's repository."""
    check_not_stopped()
    try:
        with open(os.path.expanduser(file), encoding="utf-8") as f:
            trip = trip_from(json.load(f))
    except (OSError, ValueError, KeyError) as e:
        raise ValueError("Cannot read a trip from %s: %s" % (file, e)) from None
    root = root or repo_root(os.path.expanduser(file))
    check_sights([sight.spec for sight in trip], root)
    (state.current_reader() or new_reader()).load(trip, root)
    state.ADDRESSED = True
    scrollbars.reader_focused(True)
    return {"ok": True, "trip": trip.name, "sights": [sight.spec for sight in trip]}


OPS = {"show": op_show, "say": op_say, "point": op_point, "state": op_state,
       "close": op_close, "settings": op_settings, "browse": op_browse, "open_trip": op_open_trip}


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
    if state.ADDRESSED and not state.ANSWERED and not state.STOPPED and state.LAST_MESSAGE:
        return dict(state.LAST_MESSAGE, unanswered=UNANSWERED)
    state.WAITING += 1
    state.ADDRESSED = state.STOPPED = state.POINTED = state.ANSWERED = False
    try:
        message = state.INBOX.get(timeout=timeout_s)
        state.ADDRESSED, state.LAST_MESSAGE = True, message
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
