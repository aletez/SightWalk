"""The plugin as an MCP server over HTTP (Streamable HTTP, JSON replies only, no event stream), so
Claude Code connects to Sublime itself: no separate process, nothing to install. Claude Code
registers it with `claude mcp add --transport http` and a bearer token (see setup)."""

import hmac
import http.server
import json
import threading
import time
import uuid

import sublime

from . import bridge
from .config import SETTINGS_FILE
from .manual import MANUAL, TOOLS

SERVER = None
SESSIONS = {}  # session id: when it began
WAIT_S = 50  # Claude Code cuts a tool call off after about 60 s


def call_tool(name, args):
    if name == "wait_for_user":
        return bridge.wait_for_user(min(int(args.get("timeout_s") or WAIT_S), WAIT_S))
    if name == "say" and "message" in args:  # an agent may name text so
        args = dict(args, text=args.get("text") or args.pop("message"))
    if name not in bridge.OPS:
        names = ", ".join(t["name"] for t in TOOLS)
        raise ValueError("Unknown tool %r. Tools: %s." % (name, names))
    return bridge.run_on_main(lambda: bridge.OPS[name](**args))


def tool_result(name, args):
    try:
        result = call_tool(name, args)
    except (ValueError, RuntimeError, TypeError) as e:
        result = {"error": str(e)}
    except Exception as e:
        # Unexpected: name the kind, so it can be told apart from a wrong argument.
        result = {"error": "%s in SightWalk: %s" % (type(e).__name__, e)}
    text = json.dumps(result, ensure_ascii=False)
    return {"content": [{"type": "text", "text": text}], "isError": "error" in result}


def answer(method, params):
    """The result of one JSON-RPC request."""
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}}, "instructions": MANUAL,
                "serverInfo": {"name": "sight-walk", "version": "1.0"}}
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        return tool_result(params.get("name"), params.get("arguments") or {})
    if method == "ping":
        return {}
    raise LookupError(method)


def reply(message):
    """The JSON-RPC reply to message, or None for a notification."""
    if "id" not in message:
        return None
    try:
        result = answer(message.get("method"), message.get("params") or {})
        return {"jsonrpc": "2.0", "id": message["id"], "result": result}
    except LookupError as e:
        error = {"code": -32601, "message": "Method not found: %s" % e}
        return {"jsonrpc": "2.0", "id": message["id"], "error": error}


class Handler(http.server.BaseHTTPRequestHandler):
    def authorized(self):
        expected = bridge.CONFIG["token"] or ""
        given = self.headers.get("Authorization", "")
        return bool(expected) and hmac.compare_digest(given, "Bearer " + expected)

    def send(self, status, body=None, headers=()):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        for key, value in headers:
            self.send_header(key, value)
        if body is not None:
            self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if not self.authorized():
            return self.send(401, {"error": "Unauthorized. Run 'SightWalk: Set Up Agent Bridge' "
                                            "in Sublime and register the server again."})
        message = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        headers = []
        if message.get("method") == "initialize":
            session = uuid.uuid4().hex
            SESSIONS[session] = time.time()
            headers.append(("Mcp-Session-Id", session))
        response = reply(message)
        self.send(202 if response is None else 200, response, headers)

    def do_GET(self):
        self.send(405)  # no event stream from the server

    def do_DELETE(self):
        SESSIONS.pop(self.headers.get("Mcp-Session-Id"), None)
        self.send(200)

    def log_message(self, *args):
        pass


def start_server():
    global SERVER
    SERVER = http.server.ThreadingHTTPServer(("127.0.0.1", bridge.CONFIG["port"]), Handler)
    SERVER.daemon_threads = True
    threading.Thread(target=SERVER.serve_forever, daemon=True).start()


def stop_server():
    global SERVER
    if SERVER is not None:
        SERVER.shutdown()
        SERVER.server_close()
        SERVER = None


def settings_changed():
    """A new token applies at once; a new port restarts the server."""
    port = bridge.CONFIG["port"]
    bridge.load_config()
    if SERVER is not None and bridge.CONFIG["port"] != port:
        stop_server()
        start_server()


def start():
    sublime.load_settings(SETTINGS_FILE).add_on_change("sight_walk_bridge", settings_changed)
    bridge.load_config()
    start_server()


def stop():
    sublime.load_settings(SETTINGS_FILE).clear_on_change("sight_walk_bridge")
    stop_server()
