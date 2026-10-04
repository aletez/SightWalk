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

def op_show(panes, center=None, root=None):
    missing = [spec for spec in panes if not os.path.isfile(parse_spec(spec, root)[0])]
    if missing:
        raise ValueError("Files not found: " + ", ".join(missing))
    reader = state.current_reader()
    if reader is None:
        sublime.run_command("new_window")
        window = sublime.active_window()
        hide_chrome(window)
        reader = Reader(window)
        state.register(reader)
        reader.poll()
    reader.load(panes, center, root)
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
        raise RuntimeError("No reader window is open.")
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
        raise RuntimeError("Sublime did not respond in time.")
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
    return {"error": "Unknown op %r" % op}


class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        for raw in self.rfile:
            try:
                result = dispatch(json.loads(raw.decode("utf-8")))
            except Exception as e:
                result = {"error": str(e)}
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
