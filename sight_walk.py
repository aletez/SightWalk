"""The plugin's entry point. Sublime registers the commands and listeners it finds here."""

import sys

import sublime

# Sublime reloads only top-level plugin files, so drop the submodules to pick up their edits too.
for _name in [m for m in sys.modules if m.startswith(__package__ + ".sw")]:
    del sys.modules[_name]

from .sw import bridge, guide, mcp_http, scrollbars, state  # noqa: E402
from .sw.commands import (  # noqa: E402,F401
    SightWalkAskCommand,
    SightWalkChatListener,
    SightWalkCloseEditorCommand,
    SightWalkCloseTripCommand,
    SightWalkEditCommand,
    SightWalkHeaderListener,
    SightWalkInsertCommand,
    SightWalkReplaceCommand,
    SightWalkResetSightsCommand,
    SightWalkScrollCommand,
    SightWalkSendCommand,
    SightWalkSightListener,
    SightWalkStopAnswerCommand,
    SightWalkStopGuideCommand,
    SightWalkToggleSentinelsCommand,
    SightWalkToggleGuideCommand,
    SightWalkWindowListener,
)
from .sw.setup import SightWalkSetupCommand  # noqa: E402,F401


def plugin_loaded():
    bridge.start()
    mcp_http.start()
    sublime.load_settings("SightWalk.sublime-settings").add_on_change("sight_walk_layout",
                                                                    state.render_all)


def plugin_unloaded():
    scrollbars.reader_focused(False)
    sublime.load_settings("SightWalk.sublime-settings").clear_on_change("sight_walk_layout")
    state.close_all()
    guide.stop()
    bridge.stop()
    mcp_http.stop()
