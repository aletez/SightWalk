READERS = {}
ACTIVE = [None]


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


def render_all():
    # A changed setting (such as the conversation's height) shows at once.
    for reader in list(READERS.values()):
        if reader.ready and reader.window.is_valid():
            reader.render()
