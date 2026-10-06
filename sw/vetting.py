"""The pane under the Vetting Bench: tabs for the Itinerary (the run order of the sights) and the
Map (a UML diagram of the code), still a placeholder."""

from .views import make_side_view, match_font

PLACEHOLDER = "Itinerary · Map\n\n(the itinerary comes here)"


def make(window, conversation):
    view = make_side_view(window, "Itinerary", {"word_wrap": False, "scroll_past_end": False})
    match_font(view, conversation)
    view.run_command("sight_walk_replace", {"text": PLACEHOLDER})
    view.set_read_only(True)
    return view
