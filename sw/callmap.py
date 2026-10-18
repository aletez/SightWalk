"""The Map tab's graph: the functions the trip's sights show, grouped by file and class, and the
trip's transitions between them, each type drawn its own way, with a legend (Jakub). A node is a
definition: (sight, line). The arrows are the transitions the trip's author names; nothing is
guessed (Jakub). Pure functions, no Sublime API."""

import re

DEF = re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")


# How each transition type is drawn (Jakub): told apart by line and head, as the nodes take
# their files' hues.
STYLES = {
    "calls": "",
    "returns": "style=dashed, arrowhead=vee",
    "leads_to": "penwidth=2.5",
    "101s": "style=dotted, arrowhead=diamond",
    "passes_data": 'color="#2C6ED5", arrowhead=dot',
    "comparable": "style=dotted, dir=none",
}


class Node:
    """A definition on the map: its key (sight index, line), the function's name (or the sight's
    lines, for top-level code), the class around it (or ""), its file as shown, its colour, and
    the name of the sight it is in, "(b)"."""

    def __init__(self, key, function, owner, file, colour, name=""):
        self.key, self.function, self.owner, self.file = key, function, owner, file
        self.colour, self.name = colour, name


def first_definition(lines, begin, end):
    """(line, name) of the first function defined in lines begin..end (1-based), or None."""
    for number in range(begin, end + 1):
        found = DEF.match(lines[number - 1]) if number <= len(lines) else None
        if found:
            return number, found.group(1)
    return None


def node_at(definitions, place):
    """The node a place (sight, line) or (sight,) lies in: the last of the sight's definitions
    {sight: [lines]} at or above the line, else the sight's first."""
    mine = definitions.get(place[0])
    if not mine:
        return None
    above = [d for d in mine if len(place) > 1 and d <= place[1]]
    return place[0], max(above) if above else min(mine)


def edges(definitions, transitions):
    """(from key, to key, type) for every transition between two nodes."""
    found = set()
    for kind, source, target in transitions:
        a, b = node_at(definitions, source), node_at(definitions, target)
        if a and b and a != b and kind in STYLES:
            found.add((a, b, kind))
    return sorted(found)


def node_id(key):
    return quote("s%d_%d" % key)


def quote(text):
    return '"%s"' % text.replace("\\", "\\\\").replace('"', '\\"')


def cluster(name, label, body, indent, extra=""):
    pad = "  " * indent
    return ["%ssubgraph %s {" % (pad, quote("cluster_" + name)),
            "%s  label=%s;%s" % (pad, quote(label), extra)] + body + ["%s}" % pad]


def node_line(node, indent):
    return '%s%s [label=%s, fillcolor="%s"];' % ("  " * indent, node_id(node.key),
                                                 quote(node.function), node.colour)


def sight_blocks(nodes, indent, faded):
    """Each sight's nodes in a dashed frame titled with its name, "(b)" (Jakub): a sight may hold
    several definitions the trip's calls reach."""
    body = []
    for name in sorted({n.name for n in nodes}, key=lambda name: min(n.key for n in nodes
                                                                      if n.name == name)):
        mine = [node_line(n, indent + 1) for n in nodes if n.name == name]
        body += cluster("sight" + name, name, mine, indent,
                        " style=dashed; fontcolor=%s;" % quote(faded))
    return body


def file_block(file, nodes, faded):
    """A file's cluster, with a nested cluster per class, and in either one per sight."""
    body = sight_blocks([n for n in nodes if not n.owner], 2, faded)
    for owner in sorted({n.owner for n in nodes if n.owner}):
        mine = sight_blocks([n for n in nodes if n.owner == owner], 3, faded)
        body += cluster(file + "/" + owner, "class " + owner, mine, 2)
    return cluster(file, file, body, 1)


def arrow(a, b, kind, lit=None):
    """An arrow drawn its type's way; lit, a colour: the arrow the user clicked a jump of (Jakub),
    in the jump's colour and thicker."""
    attributes = ", ".join(x for x in (STYLES[kind], lit and 'color="%s", penwidth=3' % lit) if x)
    return "  %s -> %s%s;" % (node_id(a), node_id(b), " [%s]" % attributes if attributes else "")


def legend(kinds):
    """A cluster with one short arrow per transition type drawn, named."""
    body = []
    for kind in reversed(kinds):  # dot stacks them bottom up
        a, b = quote("legend_%s_a" % kind), quote("legend_%s_b" % kind)
        body += ['    %s [shape=plaintext, style="", label=%s];' % (a, quote(kind)),
                 '    %s [shape=point, style=invis, width=0.01];' % b,
                 "    %s -> %s%s;" % (a, b, " [%s]" % STYLES[kind] if STYLES[kind] else "")]
    return cluster("legend", "", body, 1) if body else []


def dot_source(nodes, arrows, style, lit=None):
    """The graph in Graphviz's dot language. arrows: (from key, to key, type).
    style: (font, text colour, line colour, background). lit: (from key, to key, colour), a
    jump the user clicked: its arrow lit, or, with no arrow between those nodes, the two nodes'
    borders (Jakub)."""
    font, text, line, background = style
    lines = ["digraph map {", "  rankdir=LR;",
             '  graph [fontname=%s, fontcolor="%s", color="%s", bgcolor="%s"];'
             % (quote(font), text, line, background),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line),
             '  edge [color="%s"];' % line]
    for file in sorted({n.file for n in nodes}):
        lines += file_block(file, [n for n in nodes if n.file == file], line)
    lit_arrow = lit and any((a, b) == lit[:2] for a, b, _ in arrows)
    lines += [arrow(a, b, kind, lit[2] if lit_arrow and (a, b) == lit[:2] else None)
              for a, b, kind in arrows]
    if lit and not lit_arrow:
        lines += ['  %s [color="%s", penwidth=3];' % (node_id(key), lit[2])
                  for key in lit[:2] if key]
    lines += legend([k for k in STYLES if any(kind == k for _, _, kind in arrows)])
    return "\n".join(lines + ["}"])

