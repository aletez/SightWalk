import unittest

from sw.permissions import allowed_tools, remembered, reminders


class Permissions(unittest.TestCase):
    def test_base_only(self):
        self.assertEqual(allowed_tools([], ["/r"]), ["mcp__sight-walk", "Read", "Grep", "Glob"])

    def test_edit_in_folders(self):
        tools = allowed_tools(["edit"], ["/Users/j/repo/"])
        self.assertIn("Edit(//Users/j/repo/**)", tools)
        self.assertIn("Write(//Users/j/repo/**)", tools)

    def test_remembered_and_reminders(self):
        chosen = ["edit", "scripts", "git_push", "bash_all"]
        self.assertEqual(remembered(chosen), ["edit", "scripts"])
        self.assertEqual(reminders(chosen), ["scripts", "git_push", "bash_all"])


if __name__ == "__main__":
    unittest.main()
