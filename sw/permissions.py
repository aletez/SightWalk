"""What the guide SightWalk starts may do (Jakub, see docs/guide-permissions.md): the fields of the
Permissions tab, the --allowedTools they make, and which choices are remembered. Pure."""

BASE = ["mcp__sight-walk", "Read", "Grep", "Glob"]

# key, the tools it allows, remembered: "yes", "remind" (shown on the bench's header) or "never"
# (one guide session only).
FIELDS = [
    ("edit", [], "yes"),  # Edit and Write in the chosen folders, see allowed_tools
    ("git_look", ["Bash(git status:*)", "Bash(git log:*)", "Bash(git diff:*)",
                  "Bash(git show:*)", "Bash(git blame:*)"], "yes"),
    ("tests", ["Bash(python3 -m unittest:*)", "Bash(pytest:*)", "Bash(npm test:*)"], "yes"),
    ("web", ["WebFetch", "WebSearch"], "yes"),
    ("scripts", ["Bash(python3:*)", "Bash(node:*)"], "remind"),
    ("git_commit", ["Bash(git add:*)", "Bash(git commit:*)"], "remind"),
    ("install", ["Bash(pip install:*)", "Bash(npm install:*)", "Bash(brew install:*)"], "remind"),
    ("git_push", ["Bash(git push:*)"], "never"),
    ("bash_all", ["Bash"], "never"),
]
KEYS = [key for key, _, _ in FIELDS]


def allowed_tools(chosen, folders):
    """--allowedTools for the chosen fields; editing only in folders (absolute paths)."""
    tools = list(BASE)
    for key, allows, _ in FIELDS:
        if key not in chosen:
            continue
        if key == "edit":
            for folder in folders:
                rule = "//%s/**" % folder.strip("/")
                tools += ["Edit(%s)" % rule, "Write(%s)" % rule]
        tools += allows
    return tools


def remembered(chosen):
    """The chosen fields a next guide starts with: all but the "never" ones."""
    return [key for key, _, keep in FIELDS if key in chosen and keep != "never"]


def reminders(chosen):
    """The chosen fields the bench's header names while they are on: "remind" and "never"."""
    return [key for key, _, keep in FIELDS if key in chosen and keep != "yes"]
