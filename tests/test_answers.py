import unittest

from sw.answers import entries


class Entries(unittest.TestCase):
    def test_questions_and_answers_in_order(self):
        text = "U: what is this\n\nA: a check of\nthe token, said twice over here\n"
        self.assertEqual(entries(text, words=4), [
            ("U", 0, "what is this"), ("A", 17, "a check of the …")])

    def test_label_only_at_line_start(self):
        self.assertEqual(entries("A: see U: there"), [("A", 0, "see U: there")])


if __name__ == "__main__":
    unittest.main()
