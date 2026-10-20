"""The plugin's entry point. Sublime registers the commands and listeners it finds here."""

import sys

import sublime

# Sublime reloads only top-level plugin files, so drop the submodules to pick up their edits too.
for _name in [m for m in sys.modules if m.startswith(__package__ + ".sw")]:
    del sys.modules[_name]

from .sw import subl_commands, subl_guide, subl_mcp_http, subl_scrollbars, subl_tint, state, words  # noqa: E402
from .sw.subl_commands import (  # noqa: E402,F401
    SightWalkAskCommand,
    SightWalkChatListener,
    SightWalkCloseEditorCommand,
    SightWalkCompareFontsCommand,
    SightWalkCycleSightsCommand,
    SightWalkSelectColourSchemeCommand,
    SightWalkCloseTripCommand,
    SightWalkEditCommand,
    SightWalkHeaderListener,
    SightWalkInsertCommand,
    SightWalkLinkCommand,
    SightWalkSelectCommand,
    SightWalkSendDraftCommand,
    SightWalkFillCommand,
    SightWalkOpenTourCommand,
    SightWalkReplaceCommand,
    SightWalkResetSightsCommand,
    SightWalkScrollCommand,
    SightWalkSendCommand,
    SightWalkStepCommand,
    SightWalkSightListener,
    SightWalkSwitchLanguageCommand,
    SightWalkStopAnswerCommand,
    SightWalkStopGuideCommand,
    SightWalkToggleSentinelsCommand,
    SightWalkToggleGuideCommand,
    SightWalkTogglePanningCommand,
    SightWalkWindowListener,
    SightWalkZoomMapCommand,
)
from .sw.subl_setup import SightWalkRestartCommand, SightWalkSetupCommand  # noqa: E402,F401


def plugin_loaded():
    subl_mcp_http.start()
    # Schemes left by an earlier session; never after a reload (see subl_tint.clear_schemes).
    if subl_tint.first_load():
        sublime.set_timeout(subl_commands.clear_schemes_if_unused, 2000)
    settings = sublime.load_settings("SightWalk.sublime-settings")
    words.set_language(settings.get("language"))
    settings.add_on_change("sight_walk_layout", settings_changed)


def settings_changed():
    """A changed setting shows at once, the language included."""
    words.set_language(sublime.load_settings("SightWalk.sublime-settings").get("language"))
    state.render_all()
    subl_tint.refresh_all()


def plugin_unloaded():
    subl_tint.RELOADING = True
    subl_scrollbars.reader_focused(False)
    sublime.load_settings("SightWalk.sublime-settings").clear_on_change("sight_walk_layout")
    state.close_all()
    subl_guide.stop()
    subl_mcp_http.stop()
