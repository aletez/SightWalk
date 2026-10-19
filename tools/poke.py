"""Talks to the running plugin without an agent, one tool call per run, over MCP's HTTP.

Usage: python3 tools/poke.py show|say|marks|double|state|close|settings|badtoken [file1 file2]

Without files it shows a function of each of two of the plugin's own modules, so it works from
any checkout. With files, the first top-level function of ten lines or more in each: show takes
one function a sight, and marks and double place their marks relative to those functions.
"""
import ast
import json
import os
import urllib.error
import urllib.request
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILES = [os.path.join(HERE, "..", "sw", "subl_mcp_http.py"),
                 os.path.join(HERE, "..", "sw", "subl_executor.py")]
CONFIG = os.path.expanduser("~/.sight_walk/config.json")


def call(config, op, **args):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": op, "arguments": args}}
    request = urllib.request.Request(
        "http://127.0.0.1:%d/mcp" % config["port"], json.dumps(body).encode("utf-8"),
        {"Content-Type": "application/json", "Authorization": "Bearer " + config["token"]})
    try:
        reply = json.load(urllib.request.urlopen(request, timeout=60))
        print(op, "->", reply["result"]["content"][0]["text"])
    except urllib.error.HTTPError as e:
        print(op, "->", e.code, e.read().decode("utf-8"))


def function_range(path):
    """(begin, end) of the first top-level function of ten lines or more in the file."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    found = [(n.lineno, n.end_lineno) for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.end_lineno - n.lineno >= 9]
    if not found:
        sys.exit("No function of ten lines or more in " + path)
    return found[0]


def mark_texts(a, b):
    """The say texts of marks and double, their lines counted from each function's def."""
    marks = ('<icon at="(a):%d">1</icon> and <icon at="(a):%d">A</icon>, then '
             '<jump from="(a):%d" to="(b):%d">the jump</jump>.' % (a + 3, a + 7, a + 1, b + 2))
    double = ('<icon at="(a):%d">1</icon>, <icon at="(a):%d">A</icon>, <icon at="(a):%d">2</icon>, '
              '<jump from="(a):%d" to="(b):%d">the jump</jump>.' % (a + 3, a + 3, a + 7, a + 7, b + 2))
    return marks, double


def main():
    config = json.load(open(CONFIG, encoding="utf-8"))
    op = sys.argv[1]
    files = [os.path.normpath(f) for f in (sys.argv[2:4] or DEFAULT_FILES)]
    (a0, a1), (b0, b1) = [function_range(f) for f in files]
    marks, double = mark_texts(a0, b0)
    if op == "show":
        call(config, "show", sights=["%s:%d-%d" % (files[0], a0, a1), "%s:%d-%d" % (files[1], b0, b1)],
             transitions=[], trip="Poke")
    elif op == "say":
        call(config, "say", text="Hello from the bridge.")
    elif op == "marks":  # an answer placing its own marks (after a message from the user)
        call(config, "say", text=marks)
    elif op == "double":  # two marks on one line, and a jump that starts beside a mark
        call(config, "say", text=double)
    elif op == "state":
        call(config, "state")
    elif op == "close":
        call(config, "close")
    elif op == "settings":
        call(config, "settings")
    elif op == "badtoken":
        call(dict(config, token="wrong"), "state")
    else:
        sys.exit("Unknown operation: " + op)


if __name__ == "__main__":
    main()
