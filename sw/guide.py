"""Starting the Vetting guide from Sublime (Jakub): when no agent session is listening, asking the
guide starts a Claude Code session in the background, in the selection's repository, told to
listen. It talks only through the bridge; what it prints goes to ~/.sight_walk/guide.log."""

import os
import shutil
import subprocess
import time

import sublime

from . import state
from .config import SETTINGS_FILE

LOG = os.path.join(os.path.expanduser("~"), ".sight_walk", "guide.log")
# Where Claude Code is usually installed; Sublime does not see the shell's PATH.
PLACES = ["~/.local/bin", "~/.claude/local", "/opt/homebrew/bin", "/usr/local/bin"]
PROMPT = ("You are the Vetting guide. The user talks to you in SightWalk, in Sublime Text, never "
          "here: nothing you print reaches them. Call wait_for_user now. Answer every message "
          "with say(text=...), in the user's language, then call wait_for_user again. When the "
          "user wants to walk through code, call show. On a timeout, call wait_for_user again. "
          "Never end your turn.")
COMING = "the guide is coming…"
THINKING = "the guide is thinking…"
TOOLS = ["mcp__sight-walk", "Read", "Grep", "Glob"]
PROCESS = [None]


def listening():
    """An agent is waiting for the user, or was a moment ago (it answers between waits)."""
    return state.WAITING[0] > 0 or time.time() - state.LAST_WAIT[0] < 30


def running():
    return PROCESS[0] is not None and PROCESS[0].poll() is None


def find_claude():
    named = sublime.load_settings(SETTINGS_FILE).get("claude_path")
    if named:
        return os.path.expanduser(named)
    path = os.pathsep.join(os.path.expanduser(p) for p in PLACES)
    return shutil.which("claude", path=path + os.pathsep + os.environ.get("PATH", ""))


def ensure(folder):
    """Starts a guide in folder unless one listens or is starting. True if it started one."""
    if listening() or running():
        return False
    claude = find_claude()
    if claude is None:
        sublime.error_message("SightWalk could not find Claude Code. Set \"claude_path\" in "
                              "Preferences: SightWalk Settings, or start claude yourself.")
        return False
    sublime.set_timeout_async(lambda: start(claude, folder), 0)
    return True


def start(claude, folder):
    env = dict(os.environ, PATH=os.path.dirname(claude) + os.pathsep + os.environ.get("PATH", ""))
    with open(LOG, "a", encoding="utf-8") as log:
        log.write("\n--- %s, in %s\n" % (time.ctime(), folder))
        PROCESS[0] = subprocess.Popen([claude, "-p", PROMPT, "--allowedTools"] + TOOLS,
                                      cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                      stdout=log, stderr=log)


def stop():
    if running():
        PROCESS[0].terminate()
    PROCESS[0] = None


def await_answer(owner):
    """After the user's message: the bench's header says an answer is on its way, and a guide
    starts if none listens, so the user never waits without knowing (Jakub)."""
    owner.note_waiting(COMING if ensure(owner.folder()) else THINKING)
