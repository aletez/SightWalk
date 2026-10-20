"""Constants. Lengths in px unless named otherwise; times in ms (_MS) or s (_S)."""

SETTINGS_FILE = "SightWalk.sublime-settings"
DEFAULT_PORT = 47321

# Timing
SETTLE_MS = 50  # a wait for Sublime to lay views out or load files
POLL_MS = 16  # the reader's slow loop
WHEEL_MS = 4  # how often the wheel is read: the shorter, the less give before the sights follow
SETTLE_S = 0.1  # after a new layout, moved views are put back, not read as the wheel

# Layout
BENCH_WIDTH = 0.35  # the Vetting Bench, as a share of the width; the Sights take the rest
DEFAULT_BENCH_SIDE = "left"  # or "right" of the Sights
BENCH_FONTS = {"osx": "Charter", "windows": "Segoe UI", "linux": "Noto Sans"}  # the bench
GUIDE_IDLE_S = 15 * 60  # a guide started in the background stops after this long without a message
DEFAULT_CONVERSATION_HEIGHT = 0.6  # bottom of the conversation pane, as a share of the column
BLANK_LINES = 400  # blank lines above and below a blank view's anchor (the filler)
ROOM_LINES = 20  # lines of room for the wheel above and below a header's text
FROZEN_PARENTS = ["class", "def"]  # blocks whose opening line is frozen above a sight (Jakub)
STRIP_STEP = 0.15  # how far ▲ and ▼ on the strip move the trip, as a share of the screen
STRIP_PX = 32  # the scroll strip between the bench and the Sights: twice a scroll bar (Jakub)
STRIP_ICON_SHIFT = 6  # a strip icon's push right: it mirrors the gutter's icon across the border
GUTTER_PX = 26  # about a sight's gutter, for the editor's setback (see Reader.editor_geometry)
MIN_ELIDED = 6  # fewer lines of a function left out are shown instead of a "⋮" (Jakub)
GAP_PX = 16  # room between the gutter and the code, a phantom at each line's start (Jakub)
BUTTONS_EM = 9  # the Tools header's buttons' pane, in the headers' em
OVERLAP = 2  # border between sights, half taken by each neighbour (Jakub)
INSET = 10  # between the sights' header and gutter and the editor laid over them

# Colours
TINT = 0.25  # the band: the file's hue mixed into the background
OUTLINE_TINT = 0.7  # outlines of marked lines

# Conversation and marks
PROMPT = ">>> "
DEFAULT_MARK = "A"
BENCH_MARGIN = 14  # px between the bench's left edge and its text (Jakub: it read too close)
