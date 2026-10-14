"""Starting the Vetting guide from Sublime (Jakub): when no agent session is listening, a message
on the bench starts a Claude Code session in the background, in the trip's repository, told to
listen. It talks only through the bridge; what it prints goes to ~/.sight_walk/guide.log."""

import os
import shutil
import subprocess
import time

import sublime

from . import state
from .config import GUIDE_IDLE_S, SETTINGS_FILE
from .words import word

LOG = os.path.join(os.path.expanduser("~"), ".sight_walk", "guide.log")
# Where Claude Code is usually installed; Sublime does not see the shell's PATH.
PLACES = ["~/.local/bin", "~/.claude/local", "/opt/homebrew/bin", "/usr/local/bin"]
PROMPT = ("You are the Vetting guide. The user talks to you in SightWalk, in Sublime Text, never "
          "here: nothing you print reaches them. Call wait_for_user now. Answer every message "
          "with say(text=...), in the user's language, then call wait_for_user again. When the "
          "user wants to walk through code, call show. A message with selected is about exactly "
          "that text, not the function around it. On a timeout, call wait_for_user again at once "
          "and say nothing: never announce that you wait. Never end your turn.")
TOOLS = ["mcp__sight-walk", "Read", "Grep", "Glob"]
PROCESS = None  # the guide SightWalk started, if it did
LAST_ASKED = 0.0  # when the user last sent the guide something


def listening():
    """An agent is waiting for the user, or was a moment ago (it answers between waits)."""
    return state.WAITING > 0 or time.time() - state.LAST_WAIT < 30


def running():
    return PROCESS is not None and PROCESS.poll() is None


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
        sublime.error_message(word("no_claude"))
        return False
    sublime.set_timeout_async(lambda: start(claude, folder), 0)
    return True


def start(claude, folder):
    global PROCESS, LAST_ASKED
    env = dict(os.environ, PATH=os.path.dirname(claude) + os.pathsep + os.environ.get("PATH", ""))
    with open(LOG, "a", encoding="utf-8") as log:
        log.write("\n--- %s, in %s\n" % (time.ctime(), folder))
        PROCESS = subprocess.Popen([claude, "-p", PROMPT, "--allowedTools"] + TOOLS,
                                   cwd=folder, env=env, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=log)
    LAST_ASKED = time.time()
    sublime.set_timeout(stop_when_idle, 60000)


def stop_when_idle():
    """A waiting guide costs a little every two minutes and its context grows, so after
    GUIDE_IDLE_S without a message it is stopped; the next question starts a new one (Jakub).
    Only while it waits: never in the middle of an answer."""
    if not running():
        return
    if state.WAITING > 0 and time.time() - LAST_ASKED > GUIDE_IDLE_S:
        stop()
        return
    sublime.set_timeout(stop_when_idle, 60000)


def stop():
    global PROCESS
    if running():
        PROCESS.terminate()
    PROCESS = None


def await_answer(owner):
    """After the user's message: the bench's header says an answer is on its way, and a guide
    starts if none listens, so the user never waits without knowing (Jakub)."""
    global LAST_ASKED
    LAST_ASKED = time.time()
    owner.note_waiting(word("coming") if ensure(owner.folder()) else word("thinking"))
