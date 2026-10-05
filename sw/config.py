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
SETTLE_S = 0.05  # s after a render in which view movements are put back, not read as the wheel
ROOM_LINES = 20  # lines of room above and below a twin's text, for the wheel
TAIL_LINES = 200  # blank lines above and below the middle of the strip below the last pane
VETTING_LINES = 5  # lines of the vetting pane under the code
SCROLLBAR = 24  # px of a twin's left strip hidden under the twin, which covers its scroll bar
INSET = 10  # px between the panes' header and gutter and the editor laid over them
OVERLAP = 2  # px a header reaches into its code pane, to hide the border

PROMPT = ">>> "
DEFAULT_MARK = "A"
