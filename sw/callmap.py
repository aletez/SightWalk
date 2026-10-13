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
    """The names the code calls: f(...) and obj.f(...). Code that does not parse gives none."""
    try:
        tree = ast.parse(textwrap.dedent(text))
    except SyntaxError:
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            names.add(func.id if isinstance(func, ast.Name) else getattr(func, "attr", ""))
    return names - {""}


def edges(nodes):
    """(caller key, callee key) for each call from one sight to another sight's function."""
    by_name = {}
    for node in nodes:
        by_name.setdefault(node.function, []).append(node.key)
    return sorted({(n.key, callee) for n in nodes for name in n.calls
                   for callee in by_name.get(name, []) if callee != n.key})


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
