"""Command palette: 'SightWalk: Set Up Agent Bridge'. The plugin serves MCP over HTTP itself (see
mcp_http), so setting up is a token and one line for Claude Code."""

import json
import os
import secrets

import sublime
import sublime_plugin

from .config import DEFAULT_PORT, SETTINGS_FILE

FOLDER = os.path.join(os.path.expanduser("~"), ".sight_walk")

INSTRUCTIONS = """SightWalk: agent bridge set up.

1. Register SightWalk in Claude Code. This line is already on your clipboard:

   {command}

   If an older sight-walk is registered, remove it first:

   claude mcp remove --scope user sight-walk

2. Start a Claude Code session on this computer and check that /mcp lists sight-walk.

Running this command again keeps your token.
"""


class SightWalkSetupCommand(sublime_plugin.WindowCommand):
    def run(self):
        token, port = ensure_token()
        write_config(token, port)
        command = ('claude mcp add --scope user --transport http sight-walk '
                   'http://127.0.0.1:%d/mcp --header "Authorization: Bearer %s"' % (port, token))
        sublime.set_clipboard(command)
        show_instructions(self.window, INSTRUCTIONS.format(command=command))


def ensure_token():
    settings = sublime.load_settings(SETTINGS_FILE)
    token = settings.get("token")
    if not token:
        token = secrets.token_hex(16)
        settings.set("token", token)
        sublime.save_settings(SETTINGS_FILE)
    return token, settings.get("port", DEFAULT_PORT)


def write_config(token, port):
    """~/.sight_walk/config.json, for tools that talk to the plugin without Claude Code (poke)."""
    os.makedirs(FOLDER, exist_ok=True)
    config = os.path.join(FOLDER, "config.json")
    with open(config, "w", encoding="utf-8") as f:
        json.dump({"token": token, "port": port}, f)
    os.chmod(config, 0o600)


def show_instructions(window, text):
    panel = window.create_output_panel("sight_walk_setup")
    panel.run_command("sight_walk_replace", {"text": text})
    window.run_command("show_panel", {"panel": "output.sight_walk_setup"})
