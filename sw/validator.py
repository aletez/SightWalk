"""The validator (Jakub): every refusal of the guide's tool calls, judged before the executor acts.
Pure, no Sublime API: it judges a call by its arguments and the facts subl_executor gathers for it
(see facts there), and changes nothing. A refusal is a Refusal whose message tells the guide how
to correct the call; the server returns it as the tool's error."""

from .marks import line_refs, resolve_marks, speaks_of_code, untag
from .ontology import Sight, Transition, Trip

EDITABLE = ("tint", "default_conversation_height", "bench_side")
TRANSITION_FORM = ('{"type": "calls", "from": [0, 15], "to": [3, 42]}: line 15 of sight 0 '
                   'calls the definition at line 42 of sight 3 (sights from 0, file lines)')
MARK_FIRST = ("This answer names code, and nothing is marked yet: call point first with the lines "
              "it speaks of (each gets an outline and an icon), then say it again. The user "
              "asked that every answer about code comes with its marks. Do not call wait_for_user "
              "before you have answered.")
NO_LINE_NUMBERS = ("Line numbers obscure the answer (the user asked): point at the lines and name "
                   "them by their icons, 1, 2, A, B, never by numbers or file:line. Found: %s.")


class Refusal(ValueError):
    """A call the validator refuses, with what to do instead."""


def check(tool, args, facts):
    """Refuses the call (raises Refusal) or lets it through. facts: what the executor knows,
    a dict (see subl_executor.facts)."""
    judge = CHECKS.get(tool)
    if judge is not None:
        judge(args, facts)


def trip_of(args):
    """The trip show was given, its transitions checked by the ontology. transitions is required,
    an empty list included: the map never guesses (Jakub)."""
    sights, transitions = args.get("sights"), args.get("transitions")
    if not isinstance(sights, list) or not all(isinstance(s, str) for s in sights):
        raise Refusal('sights: a list like ["app.py:12-30", "app.py:40-52"].')
    if not isinstance(transitions, list) or not all(
            isinstance(t, dict) and all(isinstance(t.get(end), list) for end in ("from", "to"))
            for t in transitions):
        raise Refusal("transitions: name every call (and other transition) between the trip's "
                      "sights, each as %s; [] when there are none. The Map draws them."
                      % TRANSITION_FORM)
    try:
        made = [Transition(t.get("type"), t["from"], t["to"]) for t in transitions]
        return Trip(args.get("trip") or "", [Sight.parse(spec) for spec in sights], made)
    except ValueError as e:
        raise Refusal(str(e)) from None


def not_stopped(facts):
    if facts.get("stopped"):
        raise Refusal("The user stopped this answer. Say and show nothing more about it; call "
                      "wait_for_user.")


def trip_open(facts):
    if not facts.get("trip_open"):
        raise Refusal("No trip is open. Call show first.")


def ready(facts):
    trip_open(facts)
    if not facts.get("ready"):
        raise Refusal("The reader is still loading. Retry in a moment.")


def files(facts, root):
    """Every problem with the sights' files in one message, so the guide fixes them at once.
    facts["files"]: [(spec, path, lines in the file or None if there is none, last line)]."""
    found = facts.get("files") or []
    if not found:
        raise Refusal('Give at least one sight, like "app.py:12-30".')
    problems = ["%s: no file at %s" % (spec, path) if lines is None else
                "%s: the file has %d lines" % (spec, lines)
                for spec, path, lines, end in found if lines is None or end > lines]
    if problems and not root and any("no file" in p for p in problems):
        problems.append("relative paths need root, or give absolute paths")
    if problems:
        raise Refusal("; ".join(problems) + ".")


def one_function(facts):
    """A sight holds one function at most, whole or a fragment (Jakub). facts["functions"]:
    [(spec, the functions defined in it)]."""
    crowded = ["%s holds %s" % (spec, ", ".join(names))
               for spec, names in facts.get("functions") or [] if len(names) > 1]
    if crowded:
        raise Refusal("A sight holds one function at most, whole or a fragment: split %s into "
                      "one sight per function." % "; ".join(crowded))


def check_show(args, facts):
    not_stopped(facts)
    trip_of(args)
    files(facts, args.get("root"))
    one_function(facts)


def check_open_trip(args, facts):
    not_stopped(facts)
    if facts.get("trip_error"):
        raise Refusal("Cannot read a trip from %s: %s" % (args.get("file"), facts["trip_error"]))
    files(facts, facts.get("root"))
    one_function(facts)


def check_say(args, facts):
    """An answer only to a message, its names tagged, no line numbers, its lines marked first."""
    not_stopped(facts)
    trip_open(facts)
    if not facts.get("addressed"):
        raise Refusal("Nothing to answer: the user has said nothing since you last waited. Say "
                      "nothing; call wait_for_user.")
    try:
        text = untag(args.get("text") or "")
    except ValueError as e:
        raise Refusal(str(e)) from None
    numbers = line_refs(text)
    if numbers:
        raise Refusal(NO_LINE_NUMBERS % ", ".join(numbers))
    if not facts.get("pointed") and speaks_of_code(text):
        raise Refusal(MARK_FIRST)


def check_point(args, facts):
    not_stopped(facts)
    ready(facts)
    try:
        resolve_marks(facts.get("sights") or [], args.get("marks") or [])
    except ValueError as e:
        raise Refusal(str(e)) from None


def check_state(args, facts):
    ready(facts)


def check_close(args, facts):
    if not facts.get("trip_open"):
        raise Refusal("No reader window is open, so there is nothing to close.")


def check_browse(args, facts):
    if not facts.get("is_folder"):
        raise Refusal("Not a folder: %s. Give an absolute path to an existing folder."
                      % args.get("folder"))


def check_settings(args, facts):
    for key, value in (args.get("values") or {}).items():
        if key not in EDITABLE:
            raise Refusal("Not editable: %s. Editable: %s" % (key, ", ".join(EDITABLE)))
        if key == "bench_side":
            if value not in ("left", "right"):
                raise Refusal('bench_side must be "left" or "right".')
        elif not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise Refusal("%s must be a number from 0 to 1." % key)


def check_wait(args, facts):
    trip_open(facts)


CHECKS = {"show": check_show, "open_trip": check_open_trip, "say": check_say,
          "point": check_point, "state": check_state, "close": check_close,
          "browse": check_browse, "settings": check_settings, "wait_for_user": check_wait}
