"""Command palette: 'SightWalk: Set Up Agent Bridge'."""

import json
import os
import secrets

import sublime
import sublime_plugin

from .config import DEFAULT_PORT, SETTINGS_FILE

PACKAGE = __package__.split(".")[0]
SERVER_RESOURCE = "Packages/%s/mcp_server/sight_walk_mcp.py" % PACKAGE
INSTALL_DIR = os.path.join(os.path.expanduser("~"), ".sight_walk")
VENV_DIR = os.path.join(INSTALL_DIR, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")

INSTRUCTIONS = """SightWalk: agent bridge set up.

The bridge is installed in {folder}

1. Create a Python environment for the bridge, with Python 3.10 or newer as python3:

   python3 -m venv "{venv}" && "{python}" -m pip install "mcp>=2"

2. Register the bridge in Claude Code. This line is already on your clipboard:

   {command}

3. Start a Claude Code session on this computer and check that /mcp lists sight-walk.

Running this command again keeps your token and refreshes the bridge file.
"""


class SightWalkSetupCommand(sublime_plugin.WindowCommand):
    def run(self):
        token, port = ensure_token()
        path = install_server(token, port)
        command = 'claude mcp add --scope user sight-walk -- "%s" "%s"' % (VENV_PYTHON, path)
        sublime.set_clipboard(command)
        text = INSTRUCTIONS.format(folder=INSTALL_DIR, venv=VENV_DIR, python=VENV_PYTHON,
                                   command=command)
        show_instructions(self.window, text)


def ensure_token():
    settings = sublime.load_settings(SETTINGS_FILE)
    token = settings.get("token")
    if not token:
        token = secrets.token_hex(16)
        settings.set("token", token)
        sublime.save_settings(SETTINGS_FILE)
    return token, settings.get("port", DEFAULT_PORT)


def install_server(token, port):
    # The package may be a zip, so the bridge is read as a resource and written out as a plain file.
    os.makedirs(INSTALL_DIR, exist_ok=True)
    path = os.path.join(INSTALL_DIR, "sight_walk_mcp.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(sublime.load_resource(SERVER_RESOURCE))
    config = os.path.join(INSTALL_DIR, "config.json")
    with open(config, "w", encoding="utf-8") as f:
        json.dump({"token": token, "port": port}, f)
    os.chmod(config, 0o600)
    return path


def show_instructions(window, text):
    panel = window.create_output_panel("sight_walk_setup")
    panel.run_command("sight_walk_replace", {"text": text})
    window.run_command("show_panel", {"panel": "output.sight_walk_setup"})
