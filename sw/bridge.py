"""Local socket server that the MCP bridge talks to. One JSON object per line each way."""

import hmac
import json
import os
import queue
import socketserver
import threading

import sublime

from . import state
from .config import DEFAULT_PORT, SETTINGS_FILE, TINT
from .reader import Reader
from .spec import parse_spec
from .views import hide_chrome

CONFIG = {"token": None, "port": DEFAULT_PORT}
SERVER = [None]
EDITABLE = {"tint": TINT}


# Operations, run on Sublime's main thread

def line_count(path):
    with open(path, "rb") as f:
        return sum(1 for _ in f)


def check_panes(panes, root):
    """Every problem with the panes in one message, so the agent can fix them all at once."""
    problems = []
    for spec in panes:
        path, _, end = parse_spec(spec, root)
        if not os.path.isfile(path):
            problems.append("%s: no file at %s" % (spec, path))
        elif end > line_count(path):
            problems.append("%s: the file has %d lines" % (spec, line_count(path)))
    if problems and not root and any("no file" in p for p in problems):
        problems.append("relative paths need root, or give absolute paths")
    if problems:
        raise ValueError("; ".join(problems) + ".")


def op_show(panes, root=None, center=None):
    # Older MCP servers still send center=None; a real value means an outdated agent manual.
    if center is not None:
        raise ValueError("show has no center any more: the reader opens at the top. Leave it out.")
    if not panes:
        raise ValueError('Give at least one pane, like "app.py:12-30".')
    check_panes(panes, root)
    reader = state.current_reader()
    if reader is None:
        sublime.run_command("new_window")
        window = sublime.active_window()
        hide_chrome(window)
        reader = Reader(window)
        state.register(reader)
        reader.poll()
    reader.load(panes, root)
    return {"ok": True}


def op_say(text):
    reader = state.current_reader()
    if reader is None:
        raise RuntimeError("No reader window is open. Call show first.")
    reader.say(text)
    return {"ok": True}


def op_point(marks, reveal=True, clear=True):
    state.require_ready().point(marks, reveal, clear)
    return {"ok": True}


def op_state():
    reader = state.require_ready()
    return dict(reader.context(), panes=[seg.spec for seg in reader.segments])


def op_close():
    reader = state.current_reader()
    if reader is None:
        raise RuntimeError("No reader window is open, so there is nothing to close.")
    reader.window.run_command("close_window")
    return {"ok": True}


def op_settings(values=None):
    settings = sublime.load_settings(SETTINGS_FILE)
    for key, value in (values or {}).items():
        if key not in EDITABLE:
            raise ValueError("Not editable: %s. Editable: %s" % (key, ", ".join(EDITABLE)))
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise ValueError("%s must be a number from 0 to 1." % key)
        settings.set(key, value)
    if values:
        sublime.save_settings(SETTINGS_FILE)
    return {key: settings.get(key, default) for key, default in EDITABLE.items()}


OPS = {"show": op_show, "say": op_say, "point": op_point, "state": op_state,
       "close": op_close, "settings": op_settings}


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


def wait_for_user(timeout_s=110):
    reader = state.current_reader()
    if reader is None:
        return {"error": "No reader window is open. Call show first."}
    try:
        return reader.inbox.get(timeout=timeout_s)
    except queue.Empty:
        return {"timeout": True}


# Request handling, on server threads

def authorized(request):
    expected = CONFIG["token"]
    given = request.pop("token", "") or ""
    return bool(expected) and hmac.compare_digest(str(given), expected)


def dispatch(request):
    if not authorized(request):
        return {"error": "Unauthorized. Run 'SightWalk: Set Up Agent Bridge' in Sublime."}
    op = request.pop("op", None)
    if op == "wait_for_user":
        return wait_for_user(**request)
    if op in OPS:
        return run_on_main(lambda: OPS[op](**request))
    return {"error": "Unknown op %r. Known: wait_for_user, %s. If the agent's tools are newer than "
                     "the plugin, update the plugin and restart Sublime." % (op, ", ".join(OPS))}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw in self.rfile:
            try:
                result = dispatch(json.loads(raw.decode("utf-8")))
            except (ValueError, RuntimeError) as e:
                result = {"error": str(e)}
            except Exception as e:
                # Unexpected: name the kind, so it can be told apart from a wrong argument.
                result = {"error": "%s in SightWalk: %s" % (type(e).__name__, e)}
            self.wfile.write((json.dumps(result, ensure_ascii=False) + "\n").encode("utf-8"))
            self.wfile.flush()


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


# Lifecycle

def load_config():
    settings = sublime.load_settings(SETTINGS_FILE)
    old_port = CONFIG["port"]
    CONFIG["token"] = settings.get("token")
    CONFIG["port"] = settings.get("port", DEFAULT_PORT)
    if SERVER[0] is not None and CONFIG["port"] != old_port:
        stop_server()
        start_server()


def start_server():
    server = Server(("127.0.0.1", CONFIG["port"]), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    SERVER[0] = server


def stop_server():
    server = SERVER[0]
    if server is not None:
        server.shutdown()
        server.server_close()
        SERVER[0] = None


def start():
    settings = sublime.load_settings(SETTINGS_FILE)
    settings.add_on_change("sight_walk_bridge", load_config)
    load_config()
    start_server()


def stop():
    sublime.load_settings(SETTINGS_FILE).clear_on_change("sight_walk_bridge")
    stop_server()
