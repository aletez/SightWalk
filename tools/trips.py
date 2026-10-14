"""Writes docs/trips.md: SightWalk's own code split into trips, each view a whole function at its
current lines. Run from the repository root after the code changes:

    python3 tools/trips.py           # writes docs/trips.md
    python3 tools/trips.py 1         # prints trip 1's views as one JSON list, for show
"""

import ast
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, ".")
from sw.ontology import (Informator, Transition, Trip, Sight, informator_data,  # noqa: E402
                         trip_data)

FILES = sorted(glob.glob("sw/*.py")) + ["sight_walk.py"]

TRIPS = [
    ("Plugin start and stop",
     "Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, "
     "trips close and the server stops. The Restart command makes Sublime reload the plugin.",
     ["sight_walk.plugin_loaded", "mcp_http.start", "bridge.load_config", "mcp_http.start_server",
      "mcp_http.settings_changed", "mcp_http.stop_server", "sight_walk.plugin_unloaded",
      "scrollbars.reader_focused", "state.close_all", "mcp_http.stop",
      "setup.SightWalkRestartCommand.run"]),
    ("Setting up the agent bridge",
     "The setup command keeps a token, writes it for poke, and puts Claude Code's registration "
     "line on the clipboard.",
     ["setup.SightWalkSetupCommand.run", "setup.ensure_token", "setup.write_config",
      "setup.show_instructions", "commands.SightWalkReplaceCommand.run"]),
    ("A request arrives",
     "From the HTTP server's thread to the show operation on Sublime's, with every check on the "
     "way.",
     ["bridge.run_on_main",
      "bridge.op_show", "bridge.check_not_stopped", "bridge.make_trip", "ontology.Sight.parse",
      "ontology.Trip.__init__", "ontology.Network.__init__", "ontology.Network.problem",
      "bridge.check_sights", "spec.parse_spec", "bridge.file_lines"]),
    ("A new reader window",
     "The window and every view but the sights.",
     ["bridge.new_reader", "reader.Reader.__init__", "reader.Reader.make_side_views", "views.bench_font", "views.match_font",
      "views.make_blank_view", "views.make_side_view", "chat.start", "chat.make_header",
      "chat.make_status", "vetting.make", "vetting.make_tool", "state.register"]),
    ("Loading the sights",
     "Files read, each sight's copy, header and frozen lines made.",
     ["reader.Reader.load", "chat.catch_up", "reader.Reader.close_sights",
      "reader.Reader.build", "views.FileCopy.__init__", "views.make_copy", "reader.Reader.surround",
      "spec.ancestors", "spec.indent", "spec.opens_block", "spec.breathing", "views.make_header",
      "views.write_header"]),
    ("Colours",
     "Every file in its own hue, schemes written and set once Sublime has indexed them.",
     ["reader.Reader.tint", "tint.apply_tint", "tint.schemes_for", "tint.hue_for",
      "tint.tinted_schemes", "tint.load_base_scheme", "tint.tint_color", "tint.write_scheme",
      "tint.set_schemes", "tint.when_indexed"]),
    ("Measuring",
     "The gap phantoms, the cells of the virtual document, and the window's height measured "
     "with two layouts.",
     ["reader.Reader.draw_gaps", "reader.line_count", "views.draw_gap", "reader.Reader.make_items", "views.line_top",
      "views.header_top", "reader.Reader.calibrate", "reader.Reader.measure_full",
      "reader.Reader.measure_half", "reader.Reader.start", "reader.Reader.centred_lead",
      "plan.lead", "plan.free_room", "plan.stack",
      "plan.sight_groups", "reader.Reader.write_strip"]),
    ("The layout",
     "From an offset to Sublime's layout: every sight's cells at its place, shifted.",
     ["reader.Reader.scroll_to", "plan.offset_range", "plan.max_offset", "reader.Reader.render",
      "geometry.Geometry.column_rects", "geometry.Geometry.column", "geometry.Geometry.sight_cells", "geometry.Geometry.floor_height", "reader.Reader.layout", "views.reader_layout", "views.to_layout"]),
    ("Arranging the views",
     "After a new layout: every view into its group, then back at its place.",
     ["reader.Reader.arrange", "reader.Reader.place", "reader.Reader.assign_groups",
      "views.hide_chrome",
      "reader.Reader.scroll_views", "reader.Reader.places", "reader.Reader.strip_place", "views.anchor",
      "reader.Reader.draw_strip_buttons", "reader.Reader.strip_button",
      "reader.Reader.draw_edit_buttons", "views.draw_edit_button"]),
    ("Polling and the wheel",
     "The two loops: the gutter measured once, the reader opening at the top; the wheel read "
     "and taken over.",
     ["reader.Reader.poll", "chat.keep_at_bottom", "reader.Reader.poll_wheel", "reader.Reader.alive",
      "reader.Reader.read_wheel", "reader.Reader.wheel_places", "reader.Reader.pinned_places",
      "reader.item_top"]),
    ("Pointing",
     "The agent's marks resolved to sights and lines, the reader scrolled to show them.",
     ["bridge.op_point", "state.require_ready", "reader.Reader.point",
      "marks.resolve_marks", "marks.jump", "marks.resolve_target", "marks.sight_target",
      "marks.icon_for", "marks.line_y"]),
    ("Drawing the marks",
     "Icons on screen, eyes for marks off it, outlines on marked lines.",
     ["reader.Reader.draw_gutter", "reader.Reader.draw_strip_marks", "marks.strip_icons", "views.draw_strip_icons", "marks.visible_lines", "marks.gutter_icons", "views.draw_icons", "reader.Reader.draw_outlines", "views.draw_outlines"]),
    ("The agent says something",
     "A reply reaches the Vetting Bench past the transcript guard; the status line follows the "
     "topic.",
     ["bridge.op_say", "reader.Reader.say", "reader.Reader.show_headers", "chat.show_header",
      "header.title_lines", "chat.show_status", "chat.say", "commands.SightWalkInsertCommand.run",
      "chat.Guard.on_text_changed", "chat.protected_end",
      "commands.SightWalkChatListener.on_modified"]),
    ("Stopping an answer",
     "Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.",
     ["commands.SightWalkStopAnswerCommand.run", "reader.Reader.stop_answer",
      "reader.Reader.withdraw_unread_messages"]),
    ("The Tools pane's tabs",
     "Map and Scroll: the tab links, and the tab shown in the pane.",
     ["reader.Reader.select_tool", "vetting.show_tabs", "reader.Reader.panning",
      "commands.SightWalkTogglePanningCommand.run", "reader.Reader.toggle_panning",
      "vetting.set_panning", "vetting.content_point", "reader.Reader.tools",
      "reader.Reader.tool_view", "reader.Reader.hidden_tools", "reader.Reader.draw_map"]),
    ("The Map's nodes",
     "The trip's definitions and the calls its author named, as nodes for the graph.",
     ["reader.Reader.draw_map", "reader.Reader.map_nodes", "reader.Reader.owner",
      "reader.defined_name", "callmap.first_definition", "callmap.node_at",
      "callmap.Node.__init__", "callmap.edges", "callmap.node_at", "vetting.draw_map"]),
    ("Drawing the Map",
     "The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.",
     ["vetting.draw_map", "vetting.find_dot", "callmap.dot_source", "callmap.file_block",
      "callmap.cluster", "callmap.node_line", "callmap.node_id", "callmap.quote",
      "callmap.arrow", "callmap.legend",
      "vetting.render", "vetting.png_size", "vetting.show_image", "vetting.show_note"]),
    ("The user sends a message",
     "The draft becomes a message, with the focus, the visible sights and the edits, and the "
     "agent receives it.",
     ["commands.SightWalkSendCommand.run", "chat.take_draft", "commands.send", "state.reader_for",
      "reader.Reader.context", "views.selected_text", "plan.visible_specs", "reader.Reader.take_edits",
      "bridge.wait_for_user"]),
    ("Opening the editor",
     "Enter or the header's button: the editor laid over the sights, ranges and marks held.",
     ["commands.SightWalkEditCommand.run", "reader.Reader.sight_of",
      "reader.Reader.open_editor", "editor.Editor.__init__", "views.wait_until_loaded", "editor.open_live", "editor.Editor.start",
      "editor.Editor.track", "editor.Editor.hold", "geometry.Geometry.editor_geometry"]),
    ("Closing the editor",
     "Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.",
     ["commands.SightWalkCloseEditorCommand.run", "reader.Reader.close_editor",
      "editor.Editor.close", "editor.Editor.read_back", "editor.Editor.rows",
      "reader.Reader.editor_closed", "reader.Reader.move_range"]),
    ("Window events",
     "Everything that reacts to the user's window: resizing, settings, focus, keys, closing.",
     ["reader.Reader.follow_resize", "reader.Reader.keep_bench_width", "geometry.Geometry.spans",
      "geometry.Geometry.strip_span", "geometry.Geometry.strip_share", "geometry.Geometry.bench_side",
      "state.render_all", "bridge.op_settings", "bridge.check_setting",
      "commands.SightWalkWindowListener.on_activated", "commands.SightWalkScrollCommand.run",
      "commands.SightWalkHeaderListener.on_hover", "chat.show_help"]),
    ("primary+g",
     "In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new "
     "trip with no sights, the repository's files in their place.",
     ["commands.SightWalkToggleGuideCommand.run", "reader.Reader.toggle_focus",
      "commands.SightWalkToggleGuideCommand.folder", "reader.Reader.open_empty", "reader.Reader.empty_layout", "reader.Reader.close_hijacker",
      "commands.SightWalkWindowListener.offer_to_browser", "commands.SightWalkWindowListener.on_load",
      "reader.Reader.take_file", "bridge.op_browse",
      "views.make_browser"]),
    ("One tool call over HTTP",
     "From the request to the reply: the token checked, the JSON-RPC message answered, the tool "
     "run on Sublime's thread.",
     ["mcp_http.Handler.do_POST", "mcp_http.Handler.authorized", "mcp_http.reply",
      "mcp_http.answer", "manual.tool", "mcp_http.tool_result", "mcp_http.call_tool",
      "bridge.wait_until_ready", "bridge.run_on_main", "mcp_http.Handler.send",
      "mcp_http.Handler.do_GET", "mcp_http.Handler.do_DELETE", "mcp_http.Handler.log_message"]),
    ("How Claude comes to listen to Sublime",
     "When no agent listens, asking the guide starts one; it calls wait_for_user through the "
     "bridge and waits on the shared inbox.",
     ["guide.await_answer", "guide.ensure", "guide.listening", "guide.running", "guide.find_claude", "guide.start",
      "bridge.wait_for_user"]),
    ("Here, and asking by a shortcut",
     "The caret or a selection in a sight becomes here; a shortcut sends a question, like "
     "\"Explain next.\", as a message.",
     ["commands.SightWalkWindowListener.on_selection_modified", "reader.Reader.note_selection",
      "commands.SightWalkAskCommand.run"]),
    ("Endings",
     "The guide is stopped, windows close.",
     ["commands.SightWalkStopGuideCommand.run", "commands.SightWalkStopGuideCommand.is_enabled",
      "guide.stop", "guide.stop_when_idle", "commands.SightWalkWindowListener.on_pre_close_window", "commands.SightWalkWindowListener.on_window_command", "commands.SightWalkCloseTripCommand.run", "commands.SightWalkResetSightsCommand.run", "reader.Reader.reset_sights", "commands.SightWalkResetSightsCommand.is_enabled", "state.forget", "bridge.op_close", "state.current_reader"]),
    ("Names and room",
     "How files and sights are named, and how much room the Sights and the bench get.",
     ["spec.sight_title", "spec.display_path", "spec.repo_root", "spec.matches",
      "geometry.Geometry.share", "geometry.Geometry.conversation_rows", "geometry.Geometry.head",
      "geometry.Geometry.room", "bridge.op_state",
      "reader.Reader.folder", "reader.Reader.note_waiting"]),
    ("Building blocks",
     "The small classes and hooks the trips above stand on.",
     ["plan.Item.__init__", "plan.Pane.__init__", "plan.Pane.spec", "plan.Pane.items", "plan.Pane.all_views",
      "views.kept", "views.phantoms", "views.forget", "chat.Guard.__init__", "commands.SightWalkHeaderListener.is_applicable",
      "commands.SightWalkChatListener.is_applicable"]),
    ("Settings and the rest of the colours",
     "The agent's view of the settings, and colour helpers.",
     ["commands.SightWalkScrollCommand.is_enabled",
      "tint.band_amount", "tint.from_tm_theme", "tint.resolved_scheme", "tint.scheme_stem", "tint.hex_rgb", "tint.apply_grey"]),
    ("The ontology: collections and sights",
     "Members without order, sequences one can walk, places as paths into them, and the sight.",
     [ "ontology.Collection.__init__", "ontology.Collection.member",
      "ontology.Collection.has_place", "ontology.Collection.place_problem",
      "ontology.Collection.label", "ontology.Collection.member_label", "ontology.Sight.label",
      "ontology.Sight.member_label", "ontology.Sequence.__iter__", "ontology.Sequence.__len__",
      "ontology.Sequence.member", "ontology.Sight.__init__", "ontology.Sight.parse",
      "ontology.Sight.spec", "ontology.Sight.member"]),
    ("The ontology: networks",
     "Transitions between places, checked; the trip, the informator and the holiday.",
     ["ontology.Network.__init__", "ontology.slug", "ontology.Network.add", "ontology.Network.problem",
      "ontology.Transition.__init__", "ontology.Transition.__eq__", "ontology.Transition.__repr__",
      "ontology.Transition.parts", "ontology.Trip.__init__", "ontology.Trip.label",
      "ontology.Trip.member_label", "ontology.Trip.moved", "ontology.Informator.member",
      "ontology.Informator.label", "ontology.Informator.member_label",
      "ontology.Holiday.__init__"]),
    ("An informator and its holiday",
     "Open Informator: the informator read from its files, its trips laid out in one order, the "
     "Holiday tab drawn, a trip opened from it and ticked as walked.",
     ["commands.SightWalkOpenInformatorCommand.run", "commands.informator_files",
      "commands.SightWalkOpenInformatorCommand.open", "reader.Reader.open_informator",
      "ontology.informator_from", "ontology.trip_from", "ontology.transition_from",
      "ontology.holiday", "ontology.visit", "vetting.read_walked",
      "reader.Reader.holiday_link", "vetting.save_walked", "reader.Reader.draw_holiday",
      "vetting.show_holiday"]),
    ("Trip files",
     "A trip opened from its file by the guide, and the files written for an informator.",
     ["bridge.op_open_trip", "ontology.trip_from", "ontology.trip_data",
      "ontology.transition_data", "ontology.informator_data"]),
    ("Questions the code already asks",
     "Guards found in the code itself, carried to the sights that use the same objects without "
     "them.",
     ["reader.Reader.build", "asked.draw", "asked.sources", "questions.catalogue",
      "questions.functions", "questions.conditions", "questions.asked_in", "questions.subject",
      "questions.unasked", "questions.uses"]),
    ("Seeing where the code asks",
     "The underline and the popup that says where the code asks the question.",
     ["asked.mark", "asked.popup_html", "asked.escape",
      "commands.SightWalkSightListener.is_applicable", "commands.SightWalkSightListener.on_hover",
      "asked.show_popup", "asked.paint", "asked.toggle",
      "commands.SightWalkToggleSentinelsCommand.run"]),
]


# A function in several trips is discussed in its own trip (Jakub); the others show it on the way.
OWN_TRIPS = {
    "bridge.run_on_main": "One tool call over HTTP",
    "ontology.Sight.parse": "The ontology: collections and sights",
    "ontology.Trip.__init__": "The ontology: networks",
    "ontology.Network.__init__": "The ontology: networks",
    "ontology.Network.problem": "The ontology: networks",
    "reader.Reader.build": "Loading the sights",
    "reader.Reader.draw_map": "The Map's nodes",
    "vetting.draw_map": "Drawing the Map",
    "bridge.wait_for_user": "The user sends a message",
    "ontology.trip_from": "Trip files",
    "reader.Reader.tool_view": "The Tools pane's tabs",
}

# The informator's reading paths (Jakub's leads_to and 101s), written by hand: (from, to).
LEADS = [
    ("Plugin start and stop", "Setting up the agent bridge"),
    ("Setting up the agent bridge", "One tool call over HTTP"),
    ("Setting up the agent bridge", "How Claude comes to listen to Sublime"),
    ("One tool call over HTTP", "A request arrives"),
    ("A request arrives", "A new reader window"),
    ("A new reader window", "Loading the sights"),
    ("Loading the sights", "Colours"),
    ("Loading the sights", "Questions the code already asks"),
    ("Questions the code already asks", "Seeing where the code asks"),
    ("Colours", "Measuring"),
    ("Measuring", "The layout"),
    ("The layout", "Arranging the views"),
    ("Arranging the views", "Polling and the wheel"),
    ("Polling and the wheel", "Pointing"),
    ("Pointing", "Drawing the marks"),
    ("Drawing the marks", "The agent says something"),
    ("The agent says something", "Stopping an answer"),
    ("The agent says something", "The Tools pane's tabs"),
    ("The Tools pane's tabs", "The Map's nodes"),
    ("The Map's nodes", "Drawing the Map"),
    ("How Claude comes to listen to Sublime", "The user sends a message"),
    ("The user sends a message", "Here, and asking by a shortcut"),
    ("Here, and asking by a shortcut", "Opening the editor"),
    ("Opening the editor", "Closing the editor"),
    ("Closing the editor", "primary+g"),
    ("primary+g", "Endings"),
    ("Drawing the Map", "Trip files"),
    ("Trip files", "An informator and its holiday"),
]
NEEDS = [  # (trip, the trip it needs understood first)
    ("A request arrives", "The ontology: networks"),
    ("The ontology: networks", "The ontology: collections and sights"),
    ("Loading the sights", "Building blocks"),
    ("Measuring", "Names and room"),
    ("Colours", "Settings and the rest of the colours"),
    ("Polling and the wheel", "Window events"),
]

# Not runs but surveys: all the places about one thing (see the manual on trips).
SURVEYS = {"The Tools pane's tabs", "The ontology: collections and sights", "The ontology: networks", "Window events", "Endings", "Names and room", "Building blocks",
           "Settings and the rest of the colours"}

# Whose method a call on another object reaches, by the object's name: the code's own
# convention (a reader is called reader or owner), not a guess by the method's name.
RECEIVERS = {"informator": "ontology.Informator", "trip": "ontology.Trip",
             "reader": "reader.Reader", "owner": "reader.Reader", "current_reader": "reader.Reader",
             "require_ready": "reader.Reader", "new_reader": "reader.Reader",
             "reader_for": "reader.Reader", "editor": "editor.Editor", "sight": "plan.Pane"}


# Jumps the code makes through data or by a name the rules below cannot follow, written and
# checked by hand: (caller, a piece of the calling line, callee). TRIP_JUMPS hold only in one
# trip's story (run_on_main runs whatever it is given).
OPS = ["show", "say", "point", "state", "close", "settings", "browse", "open_trip"]
JUMPS = [("mcp_http.call_tool", "bridge.OPS[name]", "bridge.op_" + op) for op in OPS] + [
    ("plan.Pane.spec", "self.sight.spec", "ontology.Sight.spec"),
    ("reader.Reader.context", "self.sights[index].spec", "plan.Pane.spec"),
    ("reader.Reader.tint", "s.all_views()", "plan.Pane.all_views"),
]
# Where a receiver's name misleads the rules (RECEIVERS): there `sight` is an ontology.Sight,
# not a plan.Pane. (caller, a piece of the line, the callee the rules give, the right one.)
FIXES = [(caller, text, "plan.Pane.spec", "ontology.Sight.spec") for caller, text in [
    ("bridge.op_show", "for sight in made"), ("bridge.op_open_trip", "for sight in trip"),
    ("ontology.trip_data", "for sight in trip"), ("reader.Reader.load", "for sight in trip")]]
TRIP_JUMPS = {
    "A request arrives": [("bridge.run_on_main", "fn()", "bridge.op_show")],
}
CLASSES = {}  # "module.Class": ["module.Base", ...], filled by definitions


def functions():
    """{"module.Class.function": "file:begin-end"} for every function in FILES."""
    specs = {}
    for path in FILES:
        module = path.rsplit("/", 1)[-1][:-3]
        for node in ast.parse(open(path, encoding="utf-8").read()).body:
            members = [(node.name + ".", m) for m in node.body] if isinstance(node, ast.ClassDef) \
                else [("", node)]
            for prefix, fn in members:
                if isinstance(fn, ast.FunctionDef):
                    begin = fn.decorator_list[0].lineno if fn.decorator_list else fn.lineno
                    specs[module + "." + prefix + fn.name] = "%s:%d-%d" % (path, begin, fn.end_lineno)
    return specs


def definitions():
    """{"module.Class.function": (module, class or None, node)}, and each module's names
    imported from the package {module: {name: "module.name" or "module"}}."""
    found, imported = {}, {}
    for path in FILES:
        module = path.rsplit("/", 1)[-1][:-3]
        tree = ast.parse(open(path, encoding="utf-8").read())
        imported[module] = {a.asname or a.name: ((n.module or "") + "." + a.name).lstrip(".")
                            .replace("sw.", "", 1)
                            for n in tree.body if isinstance(n, ast.ImportFrom) and n.level
                            for a in n.names}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                CLASSES[module + "." + node.name] = [
                    imported[module].get(b.id, module + "." + b.id) for b in node.bases
                    if isinstance(b, ast.Name)]
            members = [(node.name, m) for m in node.body] if isinstance(node, ast.ClassDef) \
                else [(None, node)]
            for cls, fn in members:
                if isinstance(fn, ast.FunctionDef):
                    name = ".".join(x for x in (module, cls, fn.name) if x)
                    found[name] = (module, cls, fn)
    return found, imported


def named(name, found):
    """A function by its full name, or a class by its constructor."""
    return name if name in found else name + ".__init__" if name + ".__init__" in found else None


def receiver_class(value, module, cls, imported):
    """The class whose method value.attribute reaches: self's own, a class named in the code,
    super()'s, or one the receiver's name gives (RECEIVERS)."""
    if isinstance(value, ast.Name) and value.id == "self":
        return module + "." + cls if cls else None
    if isinstance(value, ast.Name):
        named_class = imported[module].get(value.id, module + "." + value.id)
        if named_class in CLASSES:
            return named_class
    if isinstance(value, ast.BoolOp):  # (current_reader() or new_reader()).load
        found = {receiver_class(v, module, cls, imported) for v in value.values}
        return found.pop() if len(found) == 1 else None
    if isinstance(value, ast.Call):
        value = value.func
    last = value.attr if isinstance(value, ast.Attribute) else getattr(value, "id", None)
    return RECEIVERS.get(last)


def method(cls, attribute, found, own=True):
    """cls's method, its own (unless not own: super()) or a base class's, nearest first."""
    if own and cls + "." + attribute in found:
        return cls + "." + attribute
    for base in CLASSES.get(cls, []):
        hit = method(base, attribute, found)
        if hit:
            return hit
    return None


def reference(node, module, cls, found, imported, called):
    """The function a name or attribute in the code refers to, called or passed on, or None. A
    class counts only where it is called (made), not in isinstance or the like."""
    if isinstance(node, ast.Name):
        hit = named(module + "." + node.id, found) or named(imported[module].get(node.id, "-"),
                                                            found)
        return None if hit and hit.endswith(".__init__") and node not in called else hit
    if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "run_command" \
            and node.args and isinstance(node.args[0], ast.Constant):
        command = "".join(w.title() for w in str(node.args[0].value).split("_")) + "Command"
        return named("commands.%s.run" % command, found) or named("setup.%s.run" % command, found)
    if not isinstance(node, ast.Attribute):
        return None
    target = imported[module].get(getattr(node.value, "id", None))
    if target and "." not in target:  # a module of the package
        return named(target + "." + node.attr, found)
    if isinstance(node.value, ast.Call) and getattr(node.value.func, "id", None) == "super":
        return method(module + "." + cls, node.attr, found, own=False) if cls else None
    owner = receiver_class(node.value, module, cls, imported)
    return method(owner, node.attr, found) if owner else None


def calls(name, found, imported, title=None):
    """[(line, function)] for every reference in name's body to another function, and the jumps
    written by hand (JUMPS, and title's TRIP_JUMPS)."""
    module, cls, fn = found[name]
    called = {node.func for node in ast.walk(fn) if isinstance(node, ast.Call)}
    out = set()
    for node in ast.walk(fn):
        target = reference(node, module, cls, found, imported, called) if node is not fn else None
        if target and target != name:
            out.add((node.lineno, target))
    out.update((line, callee) for caller, line, callee in jumps(title, found) if caller == name)
    for caller, line, wrong, right in fixes(found):
        if caller == name and (line, wrong) in out:
            out = (out - {(line, wrong)}) | {(line, right)}
    return sorted(out)


def jumps(title, found):
    """[(caller, line, callee)] of JUMPS and title's TRIP_JUMPS, each line found by its text."""
    return [(caller, line_of(caller, text, found), callee)
            for caller, text, callee in JUMPS + TRIP_JUMPS.get(title, [])]


def fixes(found):
    return [(caller, line_of(caller, text, found), wrong, right)
            for caller, text, wrong, right in FIXES]


def line_of(caller, text, found):
    """The line of caller's body that holds text."""
    fn = found[caller][2]
    path = FILES[[f.rsplit("/", 1)[-1][:-3] for f in FILES].index(found[caller][0])]
    lines = open(path, encoding="utf-8").read().split("\n")
    return next(n for n in range(fn.lineno, fn.end_lineno + 1) if text in lines[n - 1])


def trip_sights(title, names, specs, found, imported):
    """The trip for show: its sights, and the calls between them as transitions."""
    index = {name: i for i, name in enumerate(names)}
    transitions = []
    for i, name in enumerate(names):
        mine = calls(name, found, imported, title)
        transitions += [{"type": "calls", "from": [i, line], "to": [index[t], found[t][2].lineno]}
                        for line, t in mine if t in index]
    return {"sights": [specs[name] for name in names], "transitions": transitions}


def markdown(specs):
    gone = [name for _, _, names in TRIPS for name in names if name not in specs]
    if gone:
        sys.exit("trips name functions that are gone: " + ", ".join(gone))
    out = ["# Trips through SightWalk's own code", "",
           "Each trip follows one stretch of a run, in run order, one view per function; a "
           "survey shows all the places about one thing. Written by `tools/trips.py`; run it "
           "again after the code changes. `python3 tools/trips.py N` prints trip N for show, "
           "with the calls between its sights.", ""]
    for number, (title, about, names) in enumerate(TRIPS, 1):
        kind = ", survey" if title in SURVEYS else ""
        out += ["## %d. %s (%d views%s)" % (number, title, len(names), kind), "", about, ""]
        out += ["- `%s` %s" % (specs[name], name.split(".", 1)[1]) for name in names] + [""]
    return "\n".join(out)


def make_trip(title, names, specs, found, imported, commit):
    data = trip_sights(title, names, specs, found, imported)
    kind = "survey" if title in SURVEYS else "run"
    return Trip(title, [Sight.parse(spec) for spec in data["sights"]],
                [Transition(t["type"], t["from"], t["to"]) for t in data["transitions"]],
                commit, kind)


def own_trip(name):
    """The id of the trip that discusses name."""
    return Trip(OWN_TRIPS.get(name) or next(t for t, _, ns in TRIPS if name in ns), []).id


def between_trips(found, imported):
    """The informator's transitions: the reading paths (LEADS, NEEDS), every sight's own trip,
    and the calls that leave a trip, to the callee in its own trip."""
    ids = [Trip(title, []).id for title, _, _ in TRIPS]
    slug = lambda title: Trip(title, []).id  # noqa: E731
    out = [Transition("leads_to", (slug(a),), (slug(b),)) for a, b in LEADS]
    out += [Transition("101s", (slug(a),), (slug(b),)) for a, b in NEEDS]
    for (title, _, names), trip in zip(TRIPS, ids):
        for i, name in enumerate(names):
            out.append(Transition("own_trip", (trip, i, found[name][2].lineno), (own_trip(name),)))
            for line, callee in calls(name, found, imported):
                if callee not in names and any(callee in ns for _, _, ns in TRIPS):
                    home = own_trip(callee)
                    sight = next(ns for t, _, ns in TRIPS if Trip(t, []).id == home).index(callee)
                    out.append(Transition("calls", (trip, i, line),
                                          (home, sight, found[callee][2].lineno)))
    return out


def write_files(specs, commit):
    """docs/trips/<id>.json for every trip, docs/informators/sightwalk.json naming them."""
    found, imported = definitions()
    made = [make_trip(t, ns, specs, found, imported, commit) for t, _, ns in TRIPS]
    os.makedirs("docs/trips", exist_ok=True)
    os.makedirs("docs/informators", exist_ok=True)
    for trip in made:
        write_json("docs/trips/%s.json" % trip.id, trip_data(trip))
    informator = Informator("SightWalk", made, between_trips(found, imported), commit)
    files = {trip.id: "../trips/%s.json" % trip.id for trip in made}
    write_json("docs/informators/sightwalk.json", informator_data(informator, files))


def write_json(path, data):
    """Indented, but each place on one line: [3, 42]."""
    text = json.dumps(data, indent=1, ensure_ascii=False)
    text = re.sub(r"\[\s*([^\[\]{}]*?)\s*\]",
                  lambda m: "[%s]" % re.sub(r",\s+", ", ", m.group(1)) if '"' not in m.group(1)
                  else m.group(0), text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")


def main():
    specs = functions()
    if len(sys.argv) > 1:
        title, _, names = TRIPS[int(sys.argv[1]) - 1]
        found, imported = definitions()
        print(json.dumps(dict(trip_sights(title, names, specs, found, imported), trip=title)))
        return
    with open("docs/trips.md", "w", encoding="utf-8") as f:
        f.write(markdown(specs))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    write_files(specs, commit)
    # The whole code must be walked: say what no trip covers (Jakub).
    covered = set(name for _, _, names in TRIPS for name in names)
    for name in sorted(set(specs) - covered):
        print("not in any trip:", name, specs[name], file=sys.stderr)


if __name__ == "__main__":
    main()
