"""The Map tab's graph: the trip's sights as nodes, grouped by file and class, and an arrow where
one sight's code calls another sight's function (Jakub). Pure functions, no Sublime API: the calls
are read statically with ast, nothing runs."""

import ast
import re
import textwrap

DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


class Node:
    """A sight on the map: its key (the sight's index), the function it shows, the class around
    it (or ""), its file as shown, its colour and the names its code calls."""

    def __init__(self, key, function, owner, file, colour, calls):
        self.key, self.function, self.owner, self.file = key, function, owner, file
        self.colour, self.calls = colour, calls


def function_name(lines, begin, end):
    """The first function defined in lines begin..end (1-based), or None."""
    for line in lines[begin - 1:end]:
        found = DEF.match(line)
        if found:
            return found.group(1)
    return None


def called_names(text):
    """What the code calls, as (on, name): on is "" for f(...), the name before the dot for
    self.f(...) or Class.f(...), and None when the call is on anything else (obj().f, a[0].f).
    Code that does not parse gives none."""
    try:
        tree = ast.parse(textwrap.dedent(text))
    except SyntaxError:
        return set()
    calls = set()
    for node in ast.walk(tree):
        func = getattr(node, "func", None) if isinstance(node, ast.Call) else None
        if isinstance(func, ast.Name):
            calls.add(("", func.id))
        elif isinstance(func, ast.Attribute):
            on = func.value.id if isinstance(func.value, ast.Name) else None
            calls.add((on, func.attr))
    return calls


def callees(caller, on, name, nodes):
    """The sights a call may reach (Jakub: by class, not by name alone): f() a function outside
    any class, self.f() and cls.f() the caller's own class, Class.f() that class; on another
    object, whose class is not known, any sight's f."""
    named = [n for n in nodes if n.function == name and n.key != caller.key]
    if on == "":
        return [n for n in named if not n.owner]
    if on in ("self", "cls"):
        return [n for n in named if n.owner == caller.owner]
    owned = [n for n in named if n.owner == on]
    return owned or ([] if on in {n.owner for n in nodes} else named)


def edges(nodes):
    """(caller key, callee key) for each call from one sight to another sight's function."""
    return sorted({(n.key, callee.key) for n in nodes for on, name in n.calls
                   for callee in callees(n, on, name, nodes)})


def quote(text):
    return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"')


def cluster(name, label, body, indent):
    pad = "  " * indent
    return ["%ssubgraph %s {" % (pad, quote("cluster_" + name)),
            "%s  label=%s;" % (pad, quote(label))] + body + ["%s}" % pad]


def node_line(node, indent):
    return '%s%s [label=%s, fillcolor="%s"];' % ("  " * indent, quote("s%d" % node.key),
                                                 quote(node.function), node.colour)


def file_block(file, nodes):
    """A file's cluster, with a nested cluster per class."""
    body = [node_line(n, 2) for n in nodes if not n.owner]
    for owner in sorted({n.owner for n in nodes if n.owner}):
        mine = [node_line(n, 3) for n in nodes if n.owner == owner]
        body += cluster(file + "/" + owner, "class " + owner, mine, 2)
    return cluster(file, file, body, 1)


def dot_source(nodes, style):
    """The graph in Graphviz's dot language. style: (font, text colour, line colour)."""
    font, text, line = style
    lines = ["digraph map {", "  rankdir=LR;",
             '  graph [fontname=%s, fontcolor="%s", color="%s"];' % (quote(font), text, line),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line),
             '  edge [color="%s"];' % line]
    for file in sorted({n.file for n in nodes}):
        lines += file_block(file, [n for n in nodes if n.file == file])
    lines += ['  "s%d" -> "s%d";' % pair for pair in edges(nodes)]
    return "\n".join(lines + ["}"])
