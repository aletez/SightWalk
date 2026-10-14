"""The plugin's entry point. Sublime registers the commands and listeners it finds here."""

import sys

import sublime

# Sublime reloads only top-level plugin files, so drop the submodules to pick up their edits too.
for _name in [m for m in sys.modules if m.startswith(__package__ + ".sw")]:
    del sys.modules[_name]

from .sw import guide, mcp_http, scrollbars, state, words  # noqa: E402
from .sw.commands import (  # noqa: E402,F401
    SightWalkAskCommand,
    SightWalkChatListener,
    SightWalkCloseEditorCommand,
    SightWalkCloseTripCommand,
    SightWalkEditCommand,
    SightWalkHeaderListener,
    SightWalkInsertCommand,
    SightWalkOpenTourCommand,
    SightWalkReplaceCommand,
    SightWalkResetSightsCommand,
    SightWalkScrollCommand,
    SightWalkSendCommand,
    SightWalkSightListener,
    SightWalkSwitchLanguageCommand,
    SightWalkStopAnswerCommand,
    SightWalkStopGuideCommand,
    SightWalkToggleSentinelsCommand,
    SightWalkToggleGuideCommand,
    SightWalkTogglePanningCommand,
    SightWalkWindowListener,
)
from .sw.setup import SightWalkRestartCommand, SightWalkSetupCommand  # noqa: E402,F401


def plugin_loaded():
    mcp_http.start()
    settings = sublime.load_settings("SightWalk.sublime-settings")
    words.set_language(settings.get("language"))
    settings.add_on_change("sight_walk_layout", settings_changed)


def settings_changed():
    """A changed setting shows at once, the language included."""
    words.set_language(sublime.load_settings("SightWalk.sublime-settings").get("language"))
    state.render_all()


def plugin_unloaded():
    scrollbars.reader_focused(False)
    sublime.load_settings("SightWalk.sublime-settings").clear_on_change("sight_walk_layout")
    state.close_all()
    guide.stop()
    mcp_http.stop()
