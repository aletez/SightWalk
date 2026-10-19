"""The open trips (Reader, one per window), the one the agent talks to, and the messages waiting
for the agent."""

import queue

READERS = {}
ACTIVE = None  # the trip the agent talks to
INBOX = queue.Queue()  # the user's messages, from a trip
WAITING = 0  # agents waiting for the user right now
LAST_WAIT = 0.0  # when an agent last stopped waiting
# Something to say about: a message came, or the agent opened a trip, since it last waited. A say
# without it would only fill the silence ("I am here, waiting"), so the validator refuses it (Jakub).
ADDRESSED = False
# The user stopped the answer on its way: the agent's say, show and point are refused until it
# waits for the user again (Jakub).
STOPPED = False
# The agent pointed at lines since the user last spoke: an answer that names code needs it (Jakub).
POINTED = False
ANSWERED = False  # a say since the user's last message
LAST_MESSAGE = None  # the user's last message, given again while unanswered


def register(reader):
    global ACTIVE
    READERS[reader.window.id()] = reader
    ACTIVE = reader


def forget(window):
    global ACTIVE
    reader = READERS.pop(window.id(), None)
    if reader is not None and ACTIVE is reader:
        ACTIVE = None


def reader_for(window):
    return READERS.get(window.id()) if window else None


def current_reader():
    return ACTIVE if ACTIVE is not None and ACTIVE.window.is_valid() else None


def close_all():
    global ACTIVE
    # Called before a reload: the new modules would not know these windows, so they'd be orphans.
    for reader in list(READERS.values()):
        if reader.window.is_valid():
            reader.window.run_command("close_window")
    READERS.clear()
    ACTIVE = None


def refresh_schemes_all():
    """A chosen colour scheme shows in every trip at once."""
    for reader in list(READERS.values()):
        if reader.ready and reader.window.is_valid():
            reader.refresh_schemes()


def render_all():
    # A changed setting (such as the conversation's height) shows at once.
    for reader in list(READERS.values()):
        if reader.ready and reader.window.is_valid():
            reader.render()
            reader.draw_tour()  # its words may be in another language now

