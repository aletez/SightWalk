"""Unit tests for the modules free of the Sublime API. From the repository root:

    python3 -m unittest discover tests
"""

import os
import unittest

from sw import callmap, header, marks, plan, questions, spec
from sw.ontology import Sight

LH = 10.0  # line height
OVERHEAD = 4.0  # px a cell adds to its content


def stacked(*ranges):
    """Segments for "a.py:begin-end" ranges, stacked as the reader stacks them."""
    sights, items = [], []
    for begin, end in ranges:
        sight = plan.Pane(Sight("/r/a.py", begin, end), "/r/a.py", begin, end)
        sight.header_item = plan.Item(None, 0.0, LH, header=True)
        sight.code_item = plan.Item(None, 0.0, (end - begin + 1) * LH)
        items += [sight.header_item, sight.code_item]
        sights.append(sight)
    plan.stack(items, OVERHEAD)
    return sights, items


class PlanTest(unittest.TestCase):
    def test_stack(self):
        _, items = stacked((1, 3), (10, 11))
        self.assertEqual([i.y for i in items], [0.0, 14.0, 48.0, 62.0])

    def test_stack_on_lines(self):
        # Code starts at 14 and, unaligned, at 62: 2 px of slack make it 64 = 14 + 5 lines.
        _, items = stacked((1, 3), (10, 11))
        plan.stack(items, OVERHEAD, LH)
        self.assertEqual([i.y for i in items], [0.0, 14.0, 50.0, 64.0])
        self.assertEqual(items[1].content, 32.0)  # the slack at the bottom of the code above
        self.assertEqual(items[3].content, 20.0)  # the last code keeps its height

    def test_stack_on_lines_with_frozen(self):
        header = plan.Item(None, 0.0, LH, header=True)
        frozen = plan.Item(None, 0.0, LH, line=1)
        items = [plan.Item(None, 0.0, LH, header=True), plan.Item(None, 0.0, 25.0, line=2),
                 header, frozen, plan.Item(None, 0.0, LH, line=5)]
        plan.stack(items, OVERHEAD, LH)
        self.assertEqual((items[4].y - items[1].y) % LH, 0.0)
        self.assertEqual(frozen.y - header.y, LH + OVERHEAD)  # nothing between header and code

    def test_range_up_to_the_bench_floor(self):
        _, items = stacked((1, 3), (10, 30))  # ends at 62 + 210 + 4 = 276
        self.assertEqual(plan.offset_range(items, 100.0, OVERHEAD, 0.0, 60.0), (0.0, 216.0))

    def test_lead_and_range(self):
        _, items = stacked((1, 3), (10, 11))  # ends at 62 + 2 lines + 4 = 86
        self.assertEqual(plan.lead(items, 186.0, OVERHEAD, 93.0), 50.0)  # centred on 93
        self.assertEqual(plan.lead(items, 186.0, OVERHEAD, 10.0), 0.0)  # no higher than the top
        self.assertEqual(plan.lead(items, 50.0, OVERHEAD, 25.0), 0.0)  # taller than the screen
        # A short trip scrolls from the floor up until its end is level with the bench's floor.
        self.assertEqual(plan.offset_range(items, 186.0, OVERHEAD, 50.0, 40.0), (-50.0, 96.0))
        # Its end already above that floor: no further up than where it starts.
        self.assertEqual(plan.offset_range(items, 186.0, OVERHEAD, 50.0, 120.0), (-50.0, 50.0))

    def test_visible(self):
        sights, _ = stacked((1, 3), (10, 11))
        self.assertEqual(plan.visible_specs(sights, 0.0, 20.0), [sights[0].spec])


class CodeTalkTest(unittest.TestCase):
    def test_names_code(self):
        for text in ["`run_on_main` puts it on the main thread", "see sw/bridge.py:184",
                     "line 12 calls it", "w linii 40 jest return"]:
            self.assertTrue(marks.speaks_of_code(text), text)
        for text in ["Yes, exactly.", "Dwa kroki dalej.", "about 12 people"]:
            self.assertFalse(marks.speaks_of_code(text), text)


class SightNamesTest(unittest.TestCase):
    def test_names_and_back(self):
        self.assertEqual([spec.sight_name(i) for i in (0, 2, 25, 26, 27)],
                         ["(a)", "(c)", "(z)", "(a2)", "(b2)"])
        for i in (0, 2, 25, 26, 27):
            self.assertEqual(spec.sight_index(spec.sight_name(i)), i)
        self.assertEqual([spec.sight_index(x) for x in ("c", "c)", "(c)")], [2, 2, 2])
        for bad in ("(A)", "a1", "gamma", ""):
            self.assertIsNone(spec.sight_index(bad))

    def test_refs_in_text(self):
        self.assertEqual(marks.sight_refs("No a (a)? (c) calls (b), (q) is none.", 3),
                         [(5, 8), (10, 13), (20, 23)])

    def test_marks_by_name(self):
        sights, _ = stacked((1, 3), (10, 11))
        self.assertEqual(marks.resolve_target(sights, {"sight": "(b)", "line": 11}), (1, 11))
        with self.assertRaises(ValueError):
            marks.resolve_target(sights, {"sight": "(q)", "line": 11})


class LineRefsTest(unittest.TestCase):
    def test_found(self):
        text = ("1. (linia 33) zwraca token, (l. 42) ładuje, line 12 calls, "
                "sw/setup.py:32-38 i (35), linie 15-28.")
        self.assertEqual(marks.line_refs(text), ["linia 33", "l. 42", "line 12",
                                                 "sw/setup.py:32-38", "(35)", "linie 15-28"])

    def test_icons_and_counts_pass(self):
        self.assertEqual(marks.line_refs("Kroki 1 i 2, potem A (3). 32 znaki, port 8765, token_hex(16), \u2061f\u2061(10)."), [])


class AnswerMarksTest(unittest.TestCase):
    def test_read(self):
        text, found, frames = marks.read_marks(
            'At <icon at="(a):3">1</icon> it <jump from="(a):3" to="(b):10">calls</jump>.')
        self.assertEqual(text, "At 1 it calls.")
        self.assertEqual(found, [{"at": {"sight": "(a)", "line": 3}, "mark": "1"},
                                 {"from": {"sight": "(a)", "line": 3},
                                  "to": {"sight": "(b)", "line": 10}}])
        self.assertEqual(frames, [(3, 4, "icon"), (8, 13, 0)])
        self.assertEqual(marks.frame_scopes(frames, text), ["region.orangish", "region.greenish"])

    def test_same_tag_again(self):
        jump = '<jump from="(a):3" to="(b):10">%s</jump>'
        text, found, frames = marks.read_marks(
            (jump % "calls") + ', <jump from="(a):2" to="(b):11">x</jump>, then ' + (jump % "it"))
        self.assertEqual(len(found), 2)  # one mark per jump
        self.assertEqual([kind for _, _, kind in frames], [0, 1, 0])  # the first jump's colour


class TagsTest(unittest.TestCase):
    def test_tags_become_invisible(self):
        text = marks.untag("<func>run</func> takes <var>token</var> from <class>Reader</class>")
        self.assertEqual(text, "\u2061run\u2061 takes \u2063token\u2063 from \u2062Reader\u2062")
        self.assertEqual(marks.clean(text), "run takes token from Reader")
        self.assertTrue(marks.speaks_of_code(text))
        self.assertEqual(marks.untag("a < b, plainly"), "a < b, plainly")

    def test_refused(self):
        for bad in ["`run`", "**Reader**", "<fn>run</fn>", "<func>run", "<func>a\nb</func>"]:
            with self.assertRaises(ValueError):
                marks.untag(bad)


class MarksTest(unittest.TestCase):
    def test_icon_colours(self):
        self.assertEqual([marks.icon_colour(i) for i in
                          ("digit_3", "letter_a", "pass_up", "take_below_red", "pass_down_brown")],
                         ["digit", "letter", "green", "red", "brown"])

    def test_targets(self):
        sights, _ = stacked((1, 3), (10, 11))
        self.assertEqual(marks.resolve_target(sights, "a.py:11"), (1, 11))
        self.assertEqual(marks.resolve_target(sights, {"sight": 0, "line": 2}), (0, 2))
        for bad in ("a.py:5", {"sight": 2, "line": 1}, {"sight": 0, "line": 9}, "nope"):
            with self.assertRaises(ValueError):
                marks.resolve_target(sights, bad)

    def test_resolve_marks(self):
        sights, _ = stacked((1, 3), (10, 11))
        resolved = marks.resolve_marks(sights, [{"from": "a.py:11", "to": "a.py:2"},
                                              {"at": "a.py:3", "mark": "7"}])
        self.assertEqual([m["icon"] for m in resolved], ["pass_up", "take_below", "digit_7"])
        two = marks.resolve_marks(sights, [{"from": "a.py:2", "to": "a.py:11"},
                                           {"from": "a.py:3", "to": "a.py:10"}])
        self.assertEqual([m["icon"] for m in two],  # each jump its own colour, both ends alike
                         ["pass_down", "take_above", "pass_down_red", "take_above_red"])
        with self.assertRaises(ValueError):
            marks.resolve_marks(sights, [{"from": "a.py:2"}])

    def test_gutter_icons_with_eyes(self):
        sights, _ = stacked((1, 3), (10, 11))
        indicators = [{"sight": 0, "line": 1, "icon": "digit_1"},
                      {"sight": 1, "line": 11, "icon": "digit_2"}]
        first, last = marks.visible_lines(sights, 0.0, 60.0, LH)
        self.assertEqual((first, last), ((0, 0), (1, 0)))  # line 0 is a sight's header
        self.assertEqual(marks.gutter_icons(indicators, first, last),
                         {(0, 1): "digit_1", (1, 0): "eye_down"})


    def test_strip_icons(self):
        sights, items = stacked((1, 3), (10, 11))
        plan.stack(items, OVERHEAD, LH)  # code starts at 14 and 64: 5 lines apart
        marks_ = [{"sight": 0, "line": 2, "icon": "digit_1"},
                  {"sight": 1, "line": 11, "icon": "letter_a"},
                  {"sight": 1, "line": 11, "icon": "pass_down"}]
        self.assertEqual(marks.strip_icons(sights, marks_, LH),
                         {6: ["pass_down"]})  # the second; the first is in the gutter
        self.assertEqual(marks.gutter_icons(marks_, (0, 0), (1, 11)),
                         {(0, 2): "digit_1", (1, 11): "letter_a"})


class QuestionsTest(unittest.TestCase):
    GUARDS = (
        "def a(self):\n    if self.window.is_valid():\n        self.window.run()\n"
        "def b(reader):\n    if reader.window.is_valid():\n        pass\n")
    USE = "def c(self):\n    self.view.close()\n    self.window.set_layout(x)\n"

    def test_catalogue_keeps_habits(self):
        known = questions.catalogue({"g.py": self.GUARDS})
        self.assertEqual(list(known), [("window", "is_valid")])
        self.assertEqual(len(known[("window", "is_valid")]), 2)

    def test_unasked(self):
        known = questions.catalogue({"g.py": self.GUARDS})
        found = questions.unasked(self.USE, 1, 3, known)
        self.assertEqual([(f[0], f[3]) for f in found], [(3, [("window", "is_valid")])])
        self.assertEqual(questions.unasked(self.GUARDS, 1, 3, known), [])

    def test_modules_are_no_subjects(self):
        known = questions.catalogue({"g.py": "def a(p):\n    if os.path.exists(p):\n        pass\n"
                                              "def b(p):\n    if os.path.exists(p):\n        pass\n"})
        self.assertEqual(known, {})


class SpecTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(spec.parse_spec("x.py:3-5", "/r"), (os.path.normpath("/r/x.py"), 3, 5))
        self.assertEqual(spec.parse_spec("/a/x.py:7")[1:], (7, 7))
        for bad in ("x.py", "x.py:5-3", "x.py:0-2", ":1-2"):
            with self.assertRaises(ValueError):
                spec.parse_spec(bad)

    def test_matches(self):
        sight = plan.Pane(Sight("/r/reader.py", 1, 2), "/r/reader.py", 1, 2)
        self.assertTrue(spec.matches(sight, "reader.py"))
        self.assertFalse(spec.matches(sight, "der.py"))


class HeaderTest(unittest.TestCase):
    def test_two_lines(self):
        text = header.title_lines("Vetting Bench", "a status " * 20, 40)
        first, second = text.split("\n")
        self.assertEqual(len(first), 34)
        self.assertTrue(second.endswith("…"))



class AncestorsTest(unittest.TestCase):
    LINES = ["class A:", "    x = 1", "", "    def run(self):", "        if x:",
             "            return 1", "", "", "def f():", "    pass", ""]

    def test_class_and_def(self):
        self.assertEqual(spec.ancestors(self.LINES, 4, {"class", "def"}), [1])
        self.assertEqual(spec.ancestors(self.LINES, 6, {"class", "def"}), [1, 4])
        self.assertEqual(spec.ancestors(self.LINES, 6, {"class", "def", "if"}), [1, 4, 5])
        self.assertEqual(spec.ancestors(self.LINES, 9, {"class", "def"}), [])

    def test_elided(self):
        # Lines of the innermost frozen block left out above and below the range.
        self.assertEqual(spec.elided(self.LINES, 4, 6, [1]), (2, 0))
        self.assertEqual(spec.elided(self.LINES, 5, 6, [1, 4]), (0, 0))
        self.assertEqual(spec.elided(self.LINES, 6, 6, [1, 4]), (1, 0))
        self.assertEqual(spec.elided(self.LINES, 5, 5, [1, 4]), (0, 1))
        self.assertEqual(spec.elided(self.LINES, 9, 10, []), (0, 0))
        self.assertEqual((spec.block_name(self.LINES, [1, 4]), spec.body_indent(self.LINES, [1, 4])),
                         ("run", 8))

    def test_one_function(self):
        self.assertEqual(spec.functions_in(self.LINES, 1, 10), ["run", "f"])  # a method counts
        self.assertEqual(spec.functions_in(self.LINES, 4, 6), ["run"])
        self.assertEqual(spec.functions_in(["def a():", "    def b():", "        pass"], 1, 3),
                         ["a"])

    def test_breathing(self):
        self.assertEqual(spec.breathing(self.LINES, 4, 6), (3, 7))
        self.assertEqual(spec.breathing(self.LINES, 9, 10), (8, 11))
        self.assertEqual(spec.breathing(self.LINES, 1, 2), (1, 3))


if __name__ == "__main__":
    unittest.main()


class CallMapTest(unittest.TestCase):
    def node(self, key, function, owner):
        return callmap.Node((key, 1), function, owner, "a.py", "#ffffff")

    def test_definitions(self):
        lines = ["class A:", "    def run(self):", "        self.go(1)"]
        self.assertEqual(callmap.first_definition(lines, 1, 3), (2, "run"))
        self.assertIsNone(callmap.first_definition(lines, 3, 3))

    def test_node_at(self):
        definitions = {0: [10, 20], 1: [5]}
        self.assertEqual(callmap.node_at(definitions, (0, 15)), (0, 10))
        self.assertEqual(callmap.node_at(definitions, (0, 25)), (0, 20))
        self.assertEqual(callmap.node_at(definitions, (0, 5)), (0, 10))
        self.assertEqual(callmap.node_at(definitions, (0,)), (0, 10))
        self.assertIsNone(callmap.node_at(definitions, (2, 1)))

    def test_typed_edges_and_dot(self):
        definitions = {0: [1], 1: [1]}
        arrows = callmap.edges(definitions, [("calls", (0, 3), (1, 1)), ("returns", (1, 4), (0, 3)),
                                             ("calls", (0, 2), (0, 1)), ("unknown", (0, 1), (1, 1))])
        self.assertEqual(arrows, [((0, 1), (1, 1), "calls"), ((1, 1), (0, 1), "returns")])
        nodes = [self.node(0, "run", "A"), self.node(1, "go", "")]
        source = callmap.dot_source(nodes, arrows, ("Helvetica", "#000000", "#888888", "#ffffff"))
        self.assertIn('"s0_1" -> "s1_1";', source)
        self.assertIn('"s1_1" -> "s0_1" [style=dashed, arrowhead=vee];', source)
        self.assertIn('label="class A";', source)
        self.assertIn('label="returns"', source)
        self.assertNotIn('label="leads_to"', source)
        framed = callmap.dot_source([callmap.Node((0, 1), "run", "", "a.py", "#fff", "(a)")], [],
                                    ("Helvetica", "#000000", "#888888", "#ffffff"))
        self.assertIn('label="(a)"; style=dashed;', framed)
