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

    def test_max_offset_short_last_pane(self):
        _, items = stacked((1, 3), (10, 11))
        self.assertEqual(plan.max_offset(items, 100.0, OVERHEAD), 48.0)

    def test_max_offset_tall_last_pane(self):
        _, items = stacked((1, 3), (10, 30))
        self.assertEqual(plan.max_offset(items, 100.0, OVERHEAD), 62.0 + 210.0 + 4.0 - 100.0)

    def test_lead_and_range(self):
        _, items = stacked((1, 3), (10, 11))  # ends at 62 + 2 lines + 4 = 86
        self.assertEqual(plan.lead(items, 186.0, OVERHEAD, 93.0), 50.0)  # centred on 93
        self.assertEqual(plan.lead(items, 186.0, OVERHEAD, 10.0), 0.0)  # no higher than the top
        self.assertEqual(plan.lead(items, 50.0, OVERHEAD, 25.0), 0.0)  # taller than the screen
        self.assertEqual(plan.offset_range(items, 186.0, OVERHEAD, 50.0), (-50.0, 50.0))

    def test_visible(self):
        sights, _ = stacked((1, 3), (10, 11))
        self.assertEqual(plan.visible_specs(sights, 0.0, 20.0), [sights[0].spec])


class MarksTest(unittest.TestCase):
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

    def test_breathing(self):
        self.assertEqual(spec.breathing(self.LINES, 4, 6), (3, 7))
        self.assertEqual(spec.breathing(self.LINES, 9, 10), (8, 11))
        self.assertEqual(spec.breathing(self.LINES, 1, 2), (1, 3))


if __name__ == "__main__":
    unittest.main()


class CallMapTest(unittest.TestCase):
    def node(self, key, function, owner, calls):
        return callmap.Node((key, 1), function, owner, "a.py", "#ffffff", calls)

    def test_definitions(self):
        lines = ["class A:", "    def run(self):", "        self.go(1)"]
        self.assertEqual(callmap.first_definition(lines, 1, 3), (2, "run"))
        self.assertIsNone(callmap.first_definition(lines, 3, 3))

    def test_authored_calls_and_dot(self):
        found = callmap.authored_calls([10, 20], [(15, (1, 5)), (25, (2, 7)), (5, (3, 9))])
        self.assertEqual(found, {10: [(1, 5), (3, 9)], 20: [(2, 7)]})
        nodes = [self.node(0, "run", "A", [(1, 1)]), self.node(1, "go", "", [])]
        self.assertEqual(callmap.edges(nodes), [((0, 1), (1, 1))])
        source = callmap.dot_source(nodes, ("Helvetica", "#000000", "#888888"))
        self.assertIn('"s0_1" -> "s1_1";', source)
        self.assertIn('label="class A";', source)
