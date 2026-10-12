"""A probe (2026-10-12): the plugin itself as an MCP server over HTTP (Streamable HTTP, JSON
replies only, no event stream), so Claude Code connects without a separate process. Two tools:
state, and probe_wait, which holds a request open to see how long Claude Code lets it run."""

import hmac
import http.server
import json
import threading
import time
import uuid

from . import bridge

PORT = 47322
SERVER = None
SESSIONS = {}  # session id: when it began
SEEN = []  # probe: (method, the session id the request carried), the last 50
TOOLS = [
    {"name": "state", "description": "The sights shown, the one in focus and the visible ones.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "probe_sessions", "description": "The session ids requests carried. A test.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "probe_wait", "description": "Waits the given seconds, then answers. A test.",
     "inputSchema": {"type": "object", "properties": {"seconds": {"type": "number"}},
                     "required": ["seconds"]}},
]


def call_tool(name, args):
    if name == "state":
        return bridge.dispatch(dict(op="state", token=bridge.CONFIG["token"]))
    if name == "probe_sessions":
        return {"seen": SEEN[-20:], "sessions": list(SESSIONS)}
    if name == "probe_wait":
        time.sleep(float(args.get("seconds", 0)))
        return {"waited": args.get("seconds")}
    raise ValueError("Unknown tool %r" % name)


def tool_result(name, args):
    try:
        result = call_tool(name, args)
        error = "error" in result
    except Exception as e:
        result, error = {"error": "%s: %s" % (type(e).__name__, e)}, True
    text = json.dumps(result, ensure_ascii=False)
    return {"content": [{"type": "text", "text": text}], "isError": error}


def answer(method, params):
    """The result of one JSON-RPC request."""
    if method == "initialize":
        return {"protocolVersion": params.get("protocolVersion", "2025-06-18"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "sight-walk-http", "version": "0.1"}}
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
            return self.send(401, {"error": "Unauthorized"})
        message = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        headers = []
        SEEN[:] = SEEN[-49:] + [(message.get("method"), self.headers.get("Mcp-Session-Id"))]
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


def start():
    global SERVER
    SERVER = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    SERVER.daemon_threads = True
    threading.Thread(target=SERVER.serve_forever, daemon=True).start()


def stop():
    global SERVER
    if SERVER is not None:
        SERVER.shutdown()
        SERVER.server_close()
        SERVER = None
