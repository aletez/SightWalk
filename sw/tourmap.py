"""The tour map (Jakub, 2026-10-20): what the Map is to a trip, the Tour tab shows for a tour, a
signpost of the main and secret passages between its trips, as in IKEA. Each trip a column of its
sights in a frame with its number and title, the columns side by side at whatever height their
passages give them (Jakub); a sight named file:function, its height hinting at its lines, in its
file's hue, as in the sights' headers; arrows only between trips, with a legend. A click on a
trip's frame opens it, so the picture is cut into tiles, each a link (see tiles). Pure."""

from .callmap import STYLES, legend, quote

# A signpost shows the passages between departments, not every call (Jakub: leads_to and unblocks
# first); calls would bury them.
PASSAGES = ("leads_to", "unblocks", "comparable")
def node(trip, sight):
    return quote("t%d_s%d" % (trip, sight))


def height(lines):
    """A sight's box in inches: taller with more lines, within reason."""
    return round(0.3 + min(lines, 60) / 60.0, 2)


def column(k, title, sights):
    """Trip k's frame: its sights, (label, lines, colour), one under another."""
    body = ['  subgraph cluster_%d {' % k, '    label=%s; style=rounded;' % quote(title)]
    for s, (label, lines, colour) in enumerate(sights):
        body.append('    %s [label=%s, height=%s, fillcolor="%s"];'
                    % (node(k, s), quote(label), height(lines), colour))
    body += ["    %s -> %s [style=invis, weight=10];" % (node(k, s), node(k, s + 1))
             for s in range(len(sights) - 1)]
    return body + ["  }"]


def tour_dot(trips, arrows, style):
    """trips: [(title, [(label, lines, colour)])] in the tour's order; arrows: [((trip, sight), (trip,
    sight), type)] between trips; style: (font, text colour, line colour, background)."""
    font, text, line, background = style
    lines = ["digraph tour {", "  rankdir=TB; newrank=true; pad=0; nodesep=0.3; ranksep=0.3;",
             '  graph [fontname=%s, fontcolor="%s", color="%s", bgcolor="%s", labeljust=l];'
             % (quote(font), text, line, background),
             '  node [shape=box, style="rounded,filled", fontname=%s, fontcolor="%s", '
             'color="%s"];' % (quote(font), text, line), '  edge [color="%s"];' % line]
    for k, (title, sights) in enumerate(trips):
        lines += column(k, "%d. %s" % (k + 1, title), sights)
    for (a, b, kind) in arrows:  # a passage lays its target out below its source; comparable not
        flow = "" if kind != "comparable" else "constraint=false"
        attributes = ", ".join(x for x in (STYLES.get(kind, ""), flow) if x)
        lines.append("  %s -> %s%s;" % (node(*a), node(*b), " [%s]" % attributes if attributes
                                          else ""))
    lines += legend([kind for kind in PASSAGES if any(k == kind for _, _, k in arrows)])
    return "\n".join(lines + ["}"])


def cross_arrows(transitions, ids, sizes):
    """The informator's passages between two trips of the tour, as ((trip, sight), (trip,
    sight), type); a trip named alone stands at its last sight as a source, its first as a
    target, so a passage runs from where one trip ends to where the next begins."""
    found = set()
    for t in transitions:
        if t.type not in PASSAGES or not t.source or not t.target:
            continue
        a, b = t.source[0], t.target[0]
        if a in ids and b in ids and a != b:
            ka, kb = ids.index(a), ids.index(b)
            found.add(((ka, t.source[1] if len(t.source) > 1 else sizes[ka] - 1),
                       (kb, t.target[1] if len(t.target) > 1 else 0), t.type))
    return sorted(found)


def tiles(graph_bb, frames, width, height, size):
    """The picture (width x height px) cut into rows of tiles about size px, each tile the trip
    whose frame holds its centre, or None; neighbours of one trip in a row joined. frames:
    {trip: (x0, y0, x1, y1)} and graph_bb in dot's points, y up. Returns [(y0, y1, [(x0, x1,
    trip)])] in px."""
    scale = width / max(graph_bb[2] - graph_bb[0], 1)
    boxes = {k: ((x0 - graph_bb[0]) * scale, (graph_bb[3] - y1) * scale,
                 (x1 - graph_bb[0]) * scale, (graph_bb[3] - y0) * scale)
             for k, (x0, y0, x1, y1) in frames.items()}
    rows = []
    for y0 in range(0, height, size):
        y1, cells = min(y0 + size, height), []
        for x0 in range(0, width, size):
            x1 = min(x0 + size, width)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            trip = next((k for k, (a, b, c, d) in boxes.items() if a <= cx <= c and b <= cy <= d),
                        None)
            if cells and cells[-1][2] == trip:
                cells[-1] = (cells[-1][0], x1, trip)
            else:
                cells.append((x0, x1, trip))
        rows.append((y0, y1, cells))
    return rows
