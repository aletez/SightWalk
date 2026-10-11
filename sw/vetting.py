"""The pane under the Vetting Bench: tabs for the Itinerary (the run order of the sights) and the
Map (a UML diagram of the code), still a placeholder."""

import sublime

from .views import BENCH_BUTTONS_HTML, bench_button, make_side_view, match_font

PLACEHOLDER = "\nItinerary · Map\n\n(the itinerary comes here)"
BUTTONS = {}


def make(window, conversation):
    view = make_side_view(window, "Itinerary", {"word_wrap": False, "scroll_past_end": False})
    match_font(view, conversation)
    view.run_command("sight_walk_replace", {"text": PLACEHOLDER})
    view.set_read_only(True)
    # Under the bench's floor, the top of this pane: the bench's buttons.
    BUTTONS[view.id()] = sublime.PhantomSet(view, "sight_walk_metaphor")
    buttons = sublime.Phantom(sublime.Region(0), BENCH_BUTTONS_HTML, sublime.LAYOUT_INLINE,
                              lambda href: bench_button(conversation, href))
    BUTTONS[view.id()].update([buttons])
    return view
