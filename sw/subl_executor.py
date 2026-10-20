"""The executor: what the guide's tools do in Sublime, once the validator let the call through
(see subl_mcp_http, which serves them). It also gathers the facts the validator judges by. Each
operation runs on Sublime's main thread; wait_for_user waits on the inbox on the server's own
thread."""

import json
import os
import queue
import threading
import time

import sublime

from . import subl_chat, subl_scrollbars, state
from .config import (DEFAULT_BENCH_SIDE, DEFAULT_CONVERSATION_HEIGHT, DEFAULT_PORT, SETTINGS_FILE,
                     TINT)
from .marks import read_marks, untag
from .ontology import trip_from
from .subl_reader import Reader
from .spec import functions_in, units_in, parse_spec, repo_root, sight_name
from .validator import check, trip_of
from .subl_views import hide_chrome

CONFIG = {"token": None, "port": DEFAULT_PORT}
EDITABLE = {"tint": TINT, "default_conversation_height": DEFAULT_CONVERSATION_HEIGHT,
            "bench_side": DEFAULT_BENCH_SIDE}


# Operations, run on Sublime's main thread

def file_lines(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)


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


def op_show(args, facts):
    made = trip_of(args)
    made.story = args["story"]
    reader = state.current_reader()
    if args.get("aside") and reader is not None:
        open_adventure(reader, reader.go_on_adventure(made, args.get("root")))
    else:
        (reader or new_reader()).visit(made, args.get("root"))
    state.ADDRESSED = True  # the guide may say what the trip is about
    subl_scrollbars.reader_focused(True)  # a new window is not reported as activated
    done = {"ok": True, "sights": named([sight.spec for sight in made])}
    if len(made) > LONG_TRIP:
        done["note"] = LONG_NOTE % len(made)
    return done


LONG_TRIP = 5
LONG_NOTE = ("A trip of %d sights is long: next time, about five steps of similar length, each one "
             "an adventure could open up, or several trips joined by leads_to.")


def open_adventure(mother, record):
    """An adventure's window over its mother's (Jakub, 2026-10-20): macOS sets it off a little
    by itself. The guide talks to it until it closes."""
    reader = new_reader()
    reader.mother, record["reader"] = mother, reader
    reader.adventure(record)
    subl_scrollbars.reader_focused(True)


def named(specs):
    """The trip's sights by their names, the names the user reads in the headers."""
    return {sight_name(i): spec for i, spec in enumerate(specs)}


UNANSWERED = ("This message is still unanswered (a guide before you may have taken it): answer "
              "it with say, its marks as tags in the text if the answer names code, then wait.")


def op_say(args, facts):
    """The answer on the bench, its marks placed from its own tags: the first answer with marks
    since the user spoke replaces the marks before, a later one adds to them."""
    text, marks, frames = read_marks(untag(args["text"].strip()))
    state.current_reader().say(text, args.get("status"), placed=marks, frames=frames,
                               clear=not state.POINTED)
    state.ANSWERED = True
    state.POINTED = state.POINTED or bool(marks)
    return {"ok": True}


def op_state(args, facts):
    reader = state.current_reader()
    return dict(reader.context(), sights=named([sight.spec for sight in reader.sights]))


def op_close(args, facts):
    state.current_reader().window.run_command("close_window")
    return {"ok": True}


def op_browse(args, facts):
    """A trip with no sights, the folder's files in their place (Jakub); it replaces the open
    trip, the conversation goes on. A file the user opens there becomes the trip's sight."""
    reader = state.current_reader()
    said = subl_chat.transcript(reader.chat) if reader is not None else ""
    if reader is not None:
        reader.window.run_command("close_window")
    browser = new_reader()
    subl_chat.set_transcript(browser.chat, said)  # the conversation goes on
    subl_chat.catch_up(browser.chat)
    browser.open_empty(os.path.expanduser(args["folder"]))
    subl_scrollbars.reader_focused(True)
    return {"ok": True}


def op_settings(args, facts):
    settings = sublime.load_settings(SETTINGS_FILE)
    values = args.get("values") or {}
    for key, value in values.items():
        settings.set(key, value)
    if values:
        sublime.save_settings(SETTINGS_FILE)
    return {key: settings.get(key, default) for key, default in EDITABLE.items()}


def op_open_trip(args, facts):
    """A trip from its file (written by an informator's author), its paths relative to root, by
    default the file's repository."""
    trip = facts["trip"]
    (state.current_reader() or new_reader()).visit(trip, facts["root"])
    state.ADDRESSED = True
    subl_scrollbars.reader_focused(True)
    return {"ok": True, "trip": trip.name, "sights": named([sight.spec for sight in trip])}


# Facts for the validator, gathered on the main thread

def facts(tool, args):
    """What the validator judges the call by (see validator.check)."""
    reader = state.current_reader()
    found = {"stopped": state.STOPPED, "trip_open": reader is not None,
             "ready": reader is not None and reader.ready, "addressed": state.ADDRESSED,
             "pointed": state.POINTED, "sights": reader.sights if reader is not None else []}
    if tool == "show":
        sights = args.get("sights")
        found["files"] = sight_files(sights if isinstance(sights, list) else [], args.get("root"))
        found["functions"] = sight_functions(found["files"])
    elif tool == "open_trip":
        found.update(trip_file(args.get("file") or "", args.get("root")))
    elif tool == "browse":
        found["is_folder"] = os.path.isdir(os.path.expanduser(args.get("folder") or ""))
    return found


def sight_files(specs, root):
    """[(spec, path, the file's line count or None, last line)] of the sights' files."""
    found = []
    for spec in specs:
        try:
            path, _, end = parse_spec(spec, root)
        except ValueError:
            continue  # the validator names a spec it cannot parse
        found.append((spec, path, file_lines(path) if os.path.isfile(path) else None, end))
    return found


def sight_functions(found):
    """[(spec, its functions, its outermost functions and classes)] of the sights whose files
    exist (see spec.functions_in, spec.units_in)."""
    result = []
    for spec, path, lines, end in found:
        if lines is None or end > lines:
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read().split("\n")
        begin = parse_spec(spec)[1]
        result.append((spec, functions_in(text, begin, end), units_in(text, begin, end)))
    return result


def trip_file(file, root):
    path = os.path.expanduser(file)
    try:
        with open(path, encoding="utf-8") as f:
            trip = trip_from(json.load(f))
    except (OSError, ValueError, KeyError) as e:
        return {"trip_error": str(e)}
    root = root or repo_root(path)
    found = sight_files([sight.spec for sight in trip], root)
    return {"trip": trip, "root": root, "files": found, "functions": sight_functions(found)}


OPS = {"show": op_show, "say": op_say, "state": op_state,
       "close": op_close, "settings": op_settings, "browse": op_browse, "open_trip": op_open_trip}


def execute(tool, args):
    """One tool call: its facts gathered, the validator's judgment, then the operation, the
    first and last on Sublime's main thread. A refusal raises validator.Refusal."""
    found = run_on_main(lambda: facts(tool, args))
    check(tool, args, found)
    if tool == "wait_for_user":
        return wait_for_user(args.get("timeout_s", 110))
    return run_on_main(lambda: OPS[tool](args, found))


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
