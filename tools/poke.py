"""Talks to the running plugin without an agent, one operation per call.

Usage: python3 tools/poke.py show|say|point|state|close|settings|badtoken [file1 file2]

Without files it shows two of the plugin's own modules, so it works from any checkout.
"""
import json
import os
import socket
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILES = [os.path.join(HERE, "..", "sw", "reader.py"), os.path.join(HERE, "..", "sw", "tint.py")]
CONFIG = os.path.expanduser("~/.sight_walk/config.json")


def call(config, op, **args):
    conn = socket.create_connection(("127.0.0.1", config["port"]), timeout=15)
    conn.sendall((json.dumps(dict(args, op=op, token=config["token"])) + "\n").encode("utf-8"))
    print(op, "->", conn.makefile(encoding="utf-8").readline().strip())


def main():
    config = json.load(open(CONFIG, encoding="utf-8"))
    op = sys.argv[1]
    first, second = [os.path.normpath(f) for f in (sys.argv[2:4] or DEFAULT_FILES)]
    if op == "show":
        call(config, "show", panes=[first + ":1-30", second + ":31-60"])
    elif op == "say":
        call(config, "say", text="Hello from the bridge.")
    elif op == "point":
        jump = {"from": {"pane": 0, "line": 5}, "to": {"pane": 1, "line": 40}}
        call(config, "point", marks=[jump, {"at": {"pane": 0, "line": 8}, "mark": "1"},
                                     {"at": {"pane": 0, "line": 12}, "mark": "A"}])
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
