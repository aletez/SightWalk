"""The open trips (Reader, one per window), the one the agent talks to, the small bench if one is
open, and the messages waiting for the agent."""

import queue

READERS = {}
ACTIVE = [None]
BENCH = [None]
INBOX = queue.Queue()  # the user's messages, from a trip or the Vetting strip
WAITING = [0]  # agents waiting for the user right now
LAST_WAIT = [0.0]  # when an agent last stopped waiting


def register(reader):
    READERS[reader.window.id()] = reader
    ACTIVE[0] = reader


def forget(window):
    reader = READERS.pop(window.id(), None)
    if reader is not None and ACTIVE[0] is reader:
        ACTIVE[0] = None


def reader_for(window):
    return READERS.get(window.id()) if window else None


def current_reader():
    reader = ACTIVE[0]
    return reader if reader is not None and reader.window.is_valid() else None


def require_ready():
    reader = current_reader()
    if reader is None:
        raise RuntimeError("No reader window is open. Call show first.")
    if not reader.ready:
        raise RuntimeError("The reader is still loading. Retry in a moment.")
    return reader


def close_all():
    # Called before a reload: the new modules would not know these windows, so they'd be orphans.
    for reader in list(READERS.values()):
        if reader.window.is_valid():
            reader.window.run_command("close_window")
    READERS.clear()
    ACTIVE[0] = None
    if current_bench() is not None:
        BENCH[0].closed()  # at once: no frames run after an unload
    BENCH[0] = None


def render_all():
    # A changed setting (such as the conversation's height) shows at once.
    for reader in list(READERS.values()):
        if reader.ready and reader.window.is_valid():
            reader.render()


def current_bench():
    bench = BENCH[0]
    return bench if bench is not None and bench.is_open() else None


def listener():
    """Where the agent talks: the small bench while one is open, else the current trip."""
    return current_bench() or current_reader()


def owner(view):
    """The trip or the Vetting strip whose conversation the view is, or None."""
    bench = current_bench()
    if bench is not None and view in bench.views():
        return bench
    return reader_for(view.window())
