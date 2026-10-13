"""Writes docs/trips.md: SightWalk's own code split into trips, each view a whole function at its
current lines. Run from the repository root after the code changes:

    python3 tools/trips.py           # writes docs/trips.md
    python3 tools/trips.py 1         # prints trip 1's views as one JSON list, for show
"""

import ast
import glob
import json
import sys

FILES = sorted(glob.glob("sw/*.py")) + ["sight_walk.py"]

TRIPS = [
    ("Plugin start and stop",
     "Sublime loads the plugin, the bridge starts listening; on unload, readers close and the "
     "bridge stops.",
     ["sight_walk.plugin_loaded", "bridge.load_config",
      "sight_walk.plugin_unloaded", "scrollbars.reader_focused", "state.close_all"]),
    ("Setting up the agent bridge",
     "The setup command writes the token and the MCP server; the server reads them and calls "
     "Sublime.",
     ["setup.SightWalkSetupCommand.run", "setup.ensure_token", "setup.write_config",
      "setup.show_instructions", "commands.SightWalkReplaceCommand.run"]),
    ("A request arrives",
     "From the socket to the show operation, with every check on the way.",
     ["bridge.run_on_main",
      "bridge.op_show", "bridge.check_sights", "spec.parse_spec", "bridge.file_lines"]),
    ("A new reader window",
     "The window and every view but the sights.",
     ["bridge.new_reader", "reader.Reader.__init__", "reader.Reader.make_side_views", "views.bench_font", "views.match_font",
      "views.make_blank_view", "views.make_side_view", "chat.start", "chat.make_header",
      "vetting.make", "state.register"]),
    ("Loading the sights",
     "Files read, each sight's copy, header and frozen lines made.",
     ["reader.Reader.load", "reader.Reader.close_sights", "views.wait_until_loaded",
      "reader.Reader.build", "views.make_copy", "views.FileCopy.__init__", "views.make_header", "views.write_header"]),
    ("Colours",
     "Every file in its own hue, schemes written and set once Sublime has indexed them.",
     ["reader.Reader.tint", "tint.apply_tint", "tint.schemes_for", "tint.hue_for",
      "tint.tinted_schemes", "tint.load_base_scheme", "tint.tint_color", "tint.write_scheme",
      "tint.set_schemes", "tint.when_indexed"]),
    ("Measuring",
     "The gap phantoms, the cells of the virtual document, and the window's height measured "
     "with two layouts.",
     ["reader.Reader.draw_gaps", "views.draw_gap", "reader.Reader.make_items", "views.line_top",
      "views.header_top", "reader.Reader.calibrate", "reader.Reader.measure_full",
      "reader.Reader.measure_half", "reader.Reader.start", "plan.stack"]),
    ("The layout",
     "From an offset to Sublime's layout: every sight's cells at its place, shifted.",
     ["reader.Reader.scroll_to", "plan.max_offset", "reader.Reader.render",
      "geometry.Geometry.column_rects", "geometry.Geometry.column", "geometry.Geometry.sight_cells", "reader.Reader.layout", "views.reader_layout", "views.to_layout"]),
    ("Arranging the views",
     "After a new layout: every view into its group, then back at its place.",
     ["reader.Reader.arrange", "reader.Reader.place", "reader.Reader.assign_groups",
      "views.hide_chrome", "reader.Reader.scroll_views", "reader.Reader.places", "views.anchor", "views.draw_edit_button"]),
    ("Polling and the wheel",
     "The two loops: the gutter measured once, the reader opening at the top; the wheel read "
     "and taken over.",
     ["reader.Reader.poll", "chat.keep_at_bottom", "reader.Reader.poll_wheel", "reader.Reader.alive",
      "reader.Reader.read_wheel", "reader.Reader.wheel_places", "reader.Reader.pinned_places", "reader.Reader.places",
      "reader.Reader.scroll_to"]),
    ("Pointing",
     "The agent's marks resolved to sights and lines, the reader scrolled to show them.",
     ["bridge.op_point", "state.require_ready", "reader.Reader.point",
      "marks.resolve_marks", "marks.jump", "marks.resolve_target", "marks.sight_target",
      "marks.icon_for", "marks.line_y"]),
    ("Drawing the marks",
     "Icons on screen, eyes for marks off it, outlines on marked lines.",
     ["reader.Reader.draw_gutter", "marks.visible_lines", "marks.gutter_icons", "views.draw_icons", "reader.Reader.draw_outlines", "views.draw_outlines"]),
    ("The agent says something",
     "A reply reaches the Vetting Bench past the transcript guard.",
     ["bridge.op_say", "reader.Reader.say", "reader.Reader.show_headers", "chat.show_header", "chat.make_status", "chat.show_status", "reader.Reader.tool_view", "reader.Reader.hidden_tool", "reader.Reader.select_tool", "reader.Reader.draw_map", "reader.Reader.map_nodes", "reader.Reader.owner", "reader.defined_name", "callmap.first_definition", "callmap.authored_calls", "callmap.node_id", "callmap.guess_warning", "bridge.split_sights", "bridge.check_calls", "vetting.make_map", "vetting.show_tabs", "vetting.find_dot", "vetting.draw_map", "vetting.render", "vetting.png_size", "vetting.show_image", "vetting.show_note", "callmap.Node.__init__", "callmap.function_name", "callmap.called_names", "callmap.callees", "callmap.in_run_order", "callmap.edges", "callmap.quote", "callmap.cluster", "callmap.node_line", "callmap.file_block", "callmap.dot_source", "reader.Reader.stop_answer", "reader.Reader.withdraw_unread_messages", "commands.SightWalkStopAnswerCommand.run", "bridge.check_not_stopped",
      "header.title_lines", "chat.say", "commands.SightWalkInsertCommand.run",
      "chat.Guard.on_text_changed", "chat.protected_end", "commands.SightWalkChatListener.on_modified"]),
    ("The user sends a message",
     "The draft becomes a message, with the focus and the visible sights, and the agent "
     "receives it.",
     ["commands.SightWalkSendCommand.run", "commands.send", "state.reader_for", "reader.Reader.context",
      "commands.SightWalkWindowListener.on_selection_modified", "reader.Reader.note_selection", "plan.lead", "plan.free_room", "plan.offset_range", "reader.Reader.centred_lead", "reader.Reader.surround", "reader.line_count", "reader.item_top", "plan.Sight.all_views", "views.forget", "views.kept", "views.phantoms", "spec.ancestors", "spec.breathing", "spec.indent", "spec.opens_block", "plan.Sight.items", "reader.Reader.draw_strip_buttons", "reader.Reader.strip_button", "reader.Reader.reset_sights", "plan.visible_specs", "chat.take_draft", "reader.Reader.take_edits",
      "bridge.wait_for_user"]),
    ("Opening the editor",
     "Enter or the header's button: the editor laid over the sights, ranges and marks held.",
     ["commands.SightWalkEditCommand.run", "reader.Reader.sight_of",
      "reader.Reader.open_editor", "editor.Editor.__init__", "editor.open_live", "editor.Editor.start",
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
    ("MCP over HTTP",
     "The plugin itself as an MCP server: one tool call from the request to the reply.",
     ["mcp_http.start", "mcp_http.start_server", "mcp_http.settings_changed", "manual.tool",
      "mcp_http.stop_server", "mcp_http.Handler.do_POST", "mcp_http.Handler.authorized",
      "mcp_http.reply", "mcp_http.answer", "mcp_http.tool_result", "mcp_http.call_tool",
      "mcp_http.Handler.send", "mcp_http.Handler.do_GET", "mcp_http.Handler.do_DELETE",
      "mcp_http.Handler.log_message", "mcp_http.stop"]),
    ("How Claude comes to listen to Sublime",
     "When no agent listens, asking the guide starts one; it calls wait_for_user through the "
     "bridge and waits on the shared inbox.",
     ["guide.await_answer", "guide.ensure", "guide.listening", "guide.running", "guide.find_claude", "guide.start",
      "bridge.wait_for_user"]),
    ("Talking on the bench",
     "A question goes to the inbox with what is selected; the answer comes back to the bench.",
     ["commands.SightWalkAskCommand.run", "views.selected_text",
      "chat.catch_up"]),
    ("Endings",
     "The guide is stopped, windows close.",
     ["commands.SightWalkStopGuideCommand.run", "commands.SightWalkStopGuideCommand.is_enabled",
      "guide.stop", "guide.stop_when_idle", "commands.SightWalkWindowListener.on_pre_close_window", "commands.SightWalkWindowListener.on_window_command", "commands.SightWalkCloseTripCommand.run", "commands.SightWalkResetSightsCommand.run", "commands.SightWalkResetSightsCommand.is_enabled", "state.forget", "bridge.op_close", "state.current_reader"]),
    ("Names and room",
     "How files and sights are named, and how much room the Sights and the bench get.",
     ["spec.sight_title", "spec.display_path", "spec.repo_root", "spec.matches",
      "geometry.Geometry.share", "geometry.Geometry.conversation_rows", "geometry.Geometry.head",
      "geometry.Geometry.room", "reader.Reader.draw_edit_buttons", "bridge.op_state",
      "reader.Reader.folder", "reader.Reader.note_waiting"]),
    ("Building blocks",
     "The small classes and hooks the trips above stand on.",
     ["plan.Item.__init__", "plan.Sight.__init__", "chat.Guard.__init__", "commands.SightWalkHeaderListener.is_applicable",
      "commands.SightWalkChatListener.is_applicable"]),
    ("Settings and the rest of the colours",
     "The agent's view of the settings, and colour helpers.",
     ["commands.SightWalkScrollCommand.is_enabled",
      "tint.band_amount", "tint.from_tm_theme", "tint.resolved_scheme", "tint.scheme_stem", "tint.hex_rgb", "tint.apply_grey"]),
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


def markdown(specs):
    gone = [name for _, _, names in TRIPS for name in names if name not in specs]
    if gone:
        sys.exit("trips name functions that are gone: " + ", ".join(gone))
    out = ["# Trips through SightWalk's own code", "",
           "Each trip follows one stretch of a run, in run order, one view per function. "
           "Written by `tools/trips.py`; run it again after the code changes.", ""]
    for number, (title, about, names) in enumerate(TRIPS, 1):
        out += ["## %d. %s (%d views)" % (number, title, len(names)), "", about, ""]
        out += ["- `%s` %s" % (specs[name], name.split(".", 1)[1]) for name in names] + [""]
    return "\n".join(out)


def main():
    specs = functions()
    if len(sys.argv) > 1:
        print(json.dumps([specs[name] for name in TRIPS[int(sys.argv[1]) - 1][2]]))
        return
    with open("docs/trips.md", "w", encoding="utf-8") as f:
        f.write(markdown(specs))
    # The whole code must be walked: say what no trip covers (Jakub).
    covered = set(name for _, _, names in TRIPS for name in names)
    for name in sorted(set(specs) - covered):
        print("not in any trip:", name, specs[name], file=sys.stderr)


if __name__ == "__main__":
    main()
