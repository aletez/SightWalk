"""Talks to the running plugin without an agent, one tool call per run, over MCP's HTTP.

Usage: python3 tools/poke.py show|say|marks|double|state|close|settings|badtoken [file1 file2]

Without files it shows two of the plugin's own modules, so it works from any checkout.
"""
import json
import os
import urllib.error
import urllib.request
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILES = [os.path.join(HERE, "..", "sw", "reader.py"), os.path.join(HERE, "..", "sw", "tint.py")]
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


def main():
    config = json.load(open(CONFIG, encoding="utf-8"))
    op = sys.argv[1]
    first, second = [os.path.normpath(f) for f in (sys.argv[2:4] or DEFAULT_FILES)]
    if op == "show":
        call(config, "show", sights=[first + ":1-30", second + ":31-60"], transitions=[], trip="Poke")
    elif op == "say":
        call(config, "say", text="Hello from the bridge.")
    elif op == "marks":  # an answer placing its own marks (after a message from the user)
        call(config, "say", text='<icon at="(a):8">1</icon> and <icon at="(a):12">A</icon>, '
                                 'then <jump from="(a):5" to="(b):40">the jump</jump>.')
    elif op == "double":  # two marks on line 8, and a jump that starts on line 12 beside a mark
        call(config, "say", text='<icon at="(a):8">1</icon>, <icon at="(a):8">A</icon>, '
                                 '<icon at="(a):12">2</icon>, <jump from="(a):12" to="(b):40">'
                                 'the jump</jump>.')
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
