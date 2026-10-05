import sys

# Sublime reloads only top-level plugin files, so drop the submodules to pick up their edits too.
for _name in [m for m in sys.modules if m.startswith(__package__ + ".sw")]:
    del sys.modules[_name]

from .sw import bridge, state  # noqa: E402
from .sw.commands import (  # noqa: E402,F401
    SightWalkChatListener,
    SightWalkInsertCommand,
    SightWalkReplaceCommand,
    SightWalkScrollCommand,
    SightWalkSendCommand,
    SightWalkWindowListener,
)
from .sw.setup import SightWalkSetupCommand  # noqa: E402,F401


def plugin_loaded():
    bridge.start()


def plugin_unloaded():
    state.close_all()
    bridge.stop()
