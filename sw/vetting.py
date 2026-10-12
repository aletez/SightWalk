"""The Tools pane (Jakub's name for now) under the Vetting Bench. Tabs in its header will choose what it shows
(Itinerary, Map, Scroll; Jakub); for now there is one, Scroll: a blank pane in the bench's colours
whose wheel moves the whole trip, like the Sights' fillers."""

from .chat import SYNTAX
from .views import make_blank_view, match_font

TABS = "Scroll"


def make(window, conversation):
    view = make_blank_view(window, TABS)
    match_font(view, conversation)
    view.assign_syntax(SYNTAX)  # the bench's colours down the whole column (Jakub)
    return view
