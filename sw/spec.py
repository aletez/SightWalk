"""Sight specs ("file:begin-end") and how files are named to the user and the agent. No Sublime
API."""

import os

BAD_SPEC = 'Bad sight %r: write "file:begin-end" with 1 <= begin <= end, like "app.py:12-30".'


def parse_spec(spec, root=None):
    path, _, lines = str(spec).rpartition(":")
    begin, _, end = lines.partition("-")
    try:
        begin = int(begin)
        end = int(end) if end else begin
    except ValueError:
        raise ValueError(BAD_SPEC % spec) from None
    if not path or not 1 <= begin <= end:
        raise ValueError(BAD_SPEC % spec)
    path = os.path.expanduser(path)
    if root and not os.path.isabs(path):
        path = os.path.join(os.path.expanduser(root), path)
    return os.path.normpath(path), begin, end


def repo_root(path):
    folder = os.path.dirname(os.path.realpath(path))
    while True:
        if os.path.exists(os.path.join(folder, ".git")):
            return folder
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def display_path(path):
    """The path as the agent and the user talk about it: relative to the repository root, or
    from the home folder when the file is in no repository."""
    root = repo_root(path)
    if root:
        return os.path.relpath(os.path.realpath(path), root)
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


def sight_title(sight):
    """A sight's header: its file and lines."""
    lines = str(sight.begin) if sight.begin == sight.end else "%d-%d" % (sight.begin, sight.end)
    return "%s:%s" % (display_path(sight.path), lines)


def matches(sight, name):
    # A suffix counts only at a path separator, so "der.py" does not match "reader.py".
    name = os.path.normpath(name)
    return (sight.spec == name
            or sight.path == name
            or sight.path.endswith(os.sep + name))
