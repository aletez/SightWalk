import os

BAD_SPEC = 'Bad pane %r: write "file:begin-end" with 1 <= begin <= end, like "app.py:12-30".'


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


def header_text(seg):
    lines = str(seg.begin) if seg.begin == seg.end else "%d-%d" % (seg.begin, seg.end)
    return "%s:%s" % (display_path(seg.path), lines)


def matches(seg, name):
    # A suffix counts only at a path separator, so "der.py" does not match "reader.py".
    name = os.path.normpath(name)
    return (seg.spec == name
            or seg.path == name
            or seg.path.endswith(os.sep + name))
