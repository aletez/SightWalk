SETTINGS_FILE = "SightWalk.sublime-settings"
DEFAULT_PORT = 47321

SETTLE_MS = 50
POLL_MS = 16
WHEEL_MS = 4  # how often the wheel is read: the shorter, the less give before the panes follow
MIN_LINES_IN_CELL = 1
# Conversation, code.
COLS = [0.0, 0.45, 1.0]
TINT = 0.25
DEFAULT_CONVERSATION_HEIGHT = 0.6  # bottom of the conversation pane, as a share of the column
OUTLINE_TINT = 0.7
STRIP_LINES = 400  # blank lines above and below the scroll strip's anchor
STRIP_DEFAULT = 26  # px of a gutter until one is measured
SETTLE_S = 0.1  # s after a new layout in which the strip is put back, not read
STRIP_PX = 104  # the scroll strip's width: twice a usual gutter
ROOM_LINES = 20  # lines of room above and below a twin's text and a header's
VETTING_LINES = 5  # lines of the vetting pane under the code
INSET = 10  # px between the panes' header and gutter and the editor laid over them
GAP_PX = 16  # room between the gutter and the code, a phantom at each line's start (Jakub)
GUTTER_REACH = 10  # lines line 1's view of a pane at line 1 spans: two-digit numbers
OVERLAP = 2  # px of border between panes, half taken by each neighbour (Jakub)

PROMPT = ">>> "
DEFAULT_MARK = "A"
