"""Unit tests for the modules free of the Sublime API. From the repository root:

    python3 -m unittest discover tests
"""

import os
import unittest

from sw import header, marks, plan, spec

LH = 10.0  # line height
OVERHEAD = 4.0  # px a cell adds to its content


def stacked(*ranges):
    """Segments for "a.py:begin-end" ranges, stacked as the reader stacks them."""
    sights, items = [], []
    for begin, end in ranges:
        sight = plan.Sight("/r/a.py:%d-%d" % (begin, end), "/r/a.py", begin, end)
        sight.header_item = plan.Item(None, 0.0, LH)
        sight.code_item = plan.Item(None, 0.0, (end - begin + 1) * LH)
        items += [sight.header_item, sight.code_item]
        sights.append(sight)
    plan.stack(items, OVERHEAD)
    return sights, items


class PlanTest(unittest.TestCase):
    def test_stack(self):
        _, items = stacked((1, 3), (10, 11))
        self.assertEqual([i.y for i in items], [0.0, 14.0, 48.0, 62.0])

    def test_max_offset_short_last_pane(self):
        _, items = stacked((1, 3), (10, 11))
        self.assertEqual(plan.max_offset(items, 100.0, OVERHEAD), 48.0)

    def test_max_offset_tall_last_pane(self):
        _, items = stacked((1, 3), (10, 30))
        self.assertEqual(plan.max_offset(items, 100.0, OVERHEAD), 62.0 + 210.0 + 4.0 - 100.0)

    def test_focus_and_visible(self):
        sights, _ = stacked((1, 3), (10, 11))
        self.assertIs(plan.focus_sight(sights, 0.0, 20.0, OVERHEAD), sights[0])
        self.assertIs(plan.focus_sight(sights, 50.0, 30.0, OVERHEAD), sights[1])
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


class SpecTest(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(spec.parse_spec("x.py:3-5", "/r"), (os.path.normpath("/r/x.py"), 3, 5))
        self.assertEqual(spec.parse_spec("/a/x.py:7")[1:], (7, 7))
        for bad in ("x.py", "x.py:5-3", "x.py:0-2", ":1-2"):
            with self.assertRaises(ValueError):
                spec.parse_spec(bad)

    def test_matches(self):
        sight = plan.Sight("/r/reader.py:1-2", "/r/reader.py", 1, 2)
        self.assertTrue(spec.matches(sight, "reader.py"))
        self.assertFalse(spec.matches(sight, "der.py"))


class HeaderTest(unittest.TestCase):
    def test_two_lines(self):
        text = header.title_lines("Vetting Bench", "a status " * 20, 40)
        first, second = text.split("\n")
        self.assertEqual(len(first), 34)
        self.assertTrue(second.endswith("…"))


if __name__ == "__main__":
    unittest.main()
