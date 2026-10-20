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
from sw.ontology import (Tour, Informator, Transition, Trip, Sight, dumps,  # noqa: E402
                         tour_data, informator_data, trip_data)

FILES = sorted(glob.glob("sw/*.py")) + ["sight_walk.py"]

TRIPS = [
    ("Plugin start and stop",
     "Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, "
     "trips close and the server stops. The Restart command makes Sublime reload the plugin.",
     ["sight_walk.plugin_loaded", "subl_mcp_http.start", "subl_executor.load_config", "subl_mcp_http.start_server",
      "subl_mcp_http.settings_changed", "subl_mcp_http.stop_server", "sight_walk.plugin_unloaded",
      "subl_scrollbars.reader_focused", "state.close_all", "subl_mcp_http.stop",
      "subl_setup.SightWalkRestartCommand.run"]),
    ("Setting up the agent bridge",
     "The setup command keeps a token, writes it for poke, and puts Claude Code's registration "
     "line on the clipboard.",
     ["subl_setup.SightWalkSetupCommand.run", "subl_setup.ensure_token", "subl_setup.write_config",
      "subl_setup.show_instructions", "subl_commands.SightWalkReplaceCommand.run"]),
    ("A request arrives",
     "From the HTTP server's thread to the show operation on Sublime's, with every check on the "
     "way.",
     ["subl_executor.execute", "subl_executor.run_on_main", "subl_executor.facts",
      "subl_executor.sight_files", "subl_executor.sight_functions", "spec.functions_in", "spec.units_in", "spec.blocks_in", "spec.open_above",
      "validator.check", "validator.check_show", "validator.one_function",
      "subl_executor.op_show", "subl_executor.named", "validator.not_stopped", "validator.trip_of", "marks.trip_place", "ontology.Sight.parse",
      "ontology.Trip.__init__", "ontology.Network.__init__", "ontology.Network.problem",
      "validator.files", "spec.parse_spec", "subl_executor.file_lines"]),
    ("A new reader window",
     "The window and every view but the sights.",
     ["subl_executor.new_reader", "subl_reader.Reader.__init__", "subl_reader.Reader.make_side_views", "subl_views.bench_font", "subl_views.match_font",
      "subl_views.make_blank_view", "subl_views.make_side_view", "subl_chat.start", "subl_chat.make_header",
      "subl_chat.make_status", "subl_vetting.make_tool", "state.register"]),
    ("Loading the sights",
     "Files read, each sight's copy, header and frozen lines made.",
     ["subl_reader.Reader.load", "subl_chat.catch_up", "subl_reader.Reader.close_sights",
      "subl_reader.Reader.build", "subl_views.FileCopy.__init__", "subl_views.make_copy", "subl_reader.Reader.surround", "spec.elided", "spec.block_name", "spec.body_indent", "words.lines_of",
      "subl_reader.Reader.ellipses", "subl_reader.Reader.draw_ellipsis", "subl_views.draw_ellipsis",
      "subl_reader.Reader.room_px", "subl_reader.Reader.grow_ellipses",
      "spec.ancestors", "spec.indent", "spec.opens_block", "spec.breathing", "subl_views.make_header",
      "subl_views.write_header"]),
    ("Colours",
     "Every file in its own hue, schemes written and set once Sublime has indexed them.",
     ["subl_reader.Reader.tint", "subl_tint.apply_tint", "subl_tint.schemes_for", "subl_tint.hue_for",
      "subl_tint.tinted_schemes", "subl_tint.load_base_scheme", "subl_tint.tint_color", "subl_tint.write_scheme",
      "subl_tint.set_schemes", "subl_tint.when_indexed"]),
    ("Measuring",
     "The gap phantoms, the cells of the virtual document, and the window's height measured "
     "with two layouts.",
     ["subl_reader.Reader.draw_gaps", "subl_reader.line_count", "subl_views.draw_gap", "subl_reader.Reader.make_items", "subl_views.line_top",
      "subl_views.header_top", "subl_reader.Reader.calibrate", "subl_reader.Reader.measure_full",
      "subl_reader.Reader.measure_half", "subl_reader.Reader.start", "subl_reader.Reader.centred_lead",
      "plan.lead", "plan.free_room", "plan.stack",
      "plan.sight_groups", "subl_reader.Reader.write_strip"]),
    ("The layout",
     "From an offset to Sublime's layout: every sight's cells at its place, shifted.",
     ["subl_reader.Reader.scroll_to", "plan.offset_range", "subl_geometry.Geometry.bench_floor", "subl_reader.Reader.render",
      "subl_geometry.Geometry.column_rects", "subl_geometry.Geometry.column", "subl_geometry.Geometry.sight_cells", "subl_geometry.Geometry.floor_height", "subl_reader.Reader.layout", "subl_views.reader_layout", "subl_views.to_layout"]),
    ("Arranging the views",
     "After a new layout: every view into its group, then back at its place.",
     ["subl_reader.Reader.arrange", "subl_reader.Reader.place", "subl_reader.Reader.strip_in_front",
      "subl_geometry.Geometry.strip_rows", "subl_reader.Reader.clone", "subl_reader.Reader.assign_groups",
      "subl_views.hide_chrome",
      "subl_reader.Reader.scroll_views", "subl_reader.Reader.places", "subl_reader.Reader.strip_place", "subl_views.anchor",
      "subl_reader.Reader.draw_strip_buttons", "subl_reader.Reader.strip_button",
      "subl_reader.Reader.draw_edit_buttons", "subl_reader.Reader.title", "subl_views.draw_edit_button"]),
    ("Polling and the wheel",
     "The two loops: the gutter measured once, the reader opening at the top; the wheel read "
     "and taken over.",
     ["subl_reader.Reader.poll", "subl_chat.keep_at_bottom", "subl_chat.bottom_place", "subl_chat.kept_place", "subl_reader.Reader.poll_wheel", "subl_reader.Reader.alive",
      "subl_reader.Reader.read_wheel", "subl_reader.Reader.clamp_bench", "subl_reader.Reader.bench_edited", "subl_reader.Reader.wheel_places", "subl_reader.Reader.pinned_places",
      "subl_reader.item_top"]),
    ("Pointing",
     "The marks an answer places with its own tags, resolved to sights and lines, framed in its "
     "words, the reader scrolled to show them.",
     ["subl_executor.op_say", "marks.read_marks", "marks.mark_attributes", "marks.tag_marks", "marks.frame_scopes",
      "subl_reader.Reader.point",
      "marks.resolve_marks", "marks.jump", "marks.resolve_target", "marks.sight_target",
      "marks.icon_for", "marks.line_y", "subl_chat.outline_refs", "marks.sight_refs",
      "marks.sight_number", "spec.sight_index", "spec.sight_name", "marks.trip_place",
      "subl_reader.Reader.follow_frame", "subl_reader.Reader.frame_regions", "subl_chat.blanks", "subl_reader.Reader.show_places",
      "subl_reader.Reader.add_to_answer", "subl_reader.Reader.follow_label",
      "subl_reader.Reader.show_answer"]),
    ("Drawing the marks",
     "Icons on screen, eyes for marks off it, outlines on marked lines.",
     ["subl_reader.Reader.draw_gutter", "subl_reader.Reader.draw_strip_marks", "marks.strip_icons", "subl_views.draw_strip_icons", "marks.visible_lines", "marks.gutter_icons", "subl_views.draw_icons", "subl_reader.Reader.draw_outlines", "marks.icon_colour", "subl_views.draw_outlines"]),
    ("The agent says something",
     "A reply reaches the Vetting Bench past the transcript guard; the status line follows the "
     "topic.",
     ["subl_executor.op_say", "marks.untag", "marks.line_refs", "validator.MARK_FIRST", "marks.speaks_of_code", "marks.CODE_TALK",
      "subl_reader.Reader.say", "subl_reader.Reader.show_headers", "subl_chat.show_header",
      "header.title_lines", "subl_chat.show_status", "subl_chat.say", "subl_commands.SightWalkInsertCommand.run",
      "subl_chat.Guard.on_text_changed", "subl_chat.protected_end",
      "subl_commands.SightWalkChatListener.on_modified",
      "subl_commands.SightWalkChatListener.on_post_text_command", "marks.clean",
      "subl_chat.shade_variables"]),
    ("Stopping an answer",
     "Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.",
     ["subl_commands.SightWalkStopAnswerCommand.run", "subl_reader.Reader.stop_answer",
      "subl_reader.Reader.withdraw_unread_messages"]),
    ("The Tools pane's tabs",
     "Map and Scroll: the tab links, and the tab shown in the pane.",
     ["subl_reader.Reader.select_tool", "subl_vetting.show_tabs", "subl_vetting.toggle_html", "subl_vetting.tab_at", "subl_vetting.show_buttons", "subl_commands.SightWalkHeaderListener.on_selection_modified", "subl_geometry.Geometry.buttons_share",
      "subl_commands.SightWalkTogglePanningCommand.run", "subl_reader.Reader.toggle_panning",
      "subl_vetting.set_panning", "subl_vetting.content_point", "subl_reader.Reader.tools",
      "subl_reader.Reader.tool_view", "subl_reader.Reader.hidden_tools", "subl_reader.Reader.draw_map"]),
    ("The Map's nodes",
     "The trip's definitions and the calls its author named, as nodes for the graph.",
     ["subl_reader.Reader.draw_map", "subl_reader.Reader.answer_transitions", "subl_reader.map_style", "subl_reader.Reader.map_nodes", "subl_reader.fragment_of", "subl_reader.Reader.owner",
      "subl_reader.defined_name", "callmap.first_definition", "callmap.node_at",
      "callmap.Node.__init__", "callmap.edges", "callmap.node_at", "subl_vetting.draw_map"]),
    ("Drawing the Map",
     "The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.",
     ["subl_vetting.draw_map", "subl_vetting.find_dot", "callmap.dot_source", "callmap.file_block",
      "callmap.cluster", "callmap.node_line", "callmap.sight_blocks", "callmap.node_id", "callmap.quote",
      "callmap.arrow", "callmap.legend",
      "subl_vetting.render", "subl_vetting.png_size", "subl_vetting.show_image", "subl_vetting.zoom",
      "subl_commands.SightWalkZoomMapCommand.run", "subl_vetting.show_note"]),
    ("The user sends a message",
     "The draft becomes a message, with here, the visible sights and the edits, and the "
     "agent receives it.",
     ["subl_commands.SightWalkSendCommand.run", "subl_chat.take_draft", "subl_commands.send", "state.reader_for",
      "subl_reader.Reader.context", "subl_views.selected_text", "plan.visible_specs", "subl_reader.Reader.take_edits",
      "subl_executor.wait_for_user"]),
    ("Linking words to code",
     "primary+p joins words of the draft to selections in the sights, from either side; the "
     "words go out as a <here> tag, and a click on them shows their place.",
     ["subl_commands.SightWalkLinkCommand.run", "subl_links.Links.__init__",
      "subl_commands.SightWalkChatListener.on_selection_modified", "subl_links.Links.note_bench",
      "subl_links.Links.note_code", "subl_links.Links.link_from_code",
      "subl_links.Links.link_from_bench", "subl_links.Links.link_either", "subl_links.Links.add", "subl_links.carets",
      "subl_links.Links.tagged", "subl_links.Links.places", "subl_links.ends", "marks.place_text",
      "subl_links.Links.code", "subl_links.Links.draft_start",
      "subl_links.Links.follow", "subl_links.repaint", "subl_reader.Reader.show_place", "subl_links.Links.clear",
      "subl_links.Links.show_made", "subl_links.Links.remove", "subl_links.Links.prune",
      "subl_links.Links.draft_keys", "subl_links.Links.bench_region", "subl_links.Links.by_sight",
      "marks.span_relation", "marks.here_tags", "subl_links.Links.follow_code", "subl_links.Links.repaint_bench", "subl_links.Links.ask", "subl_links.Links.frame_question", "subl_links.Links.follow_question", "subl_links.Links.select", "subl_links.Links.kept_questions", "subl_links.Links.restore_questions", "subl_links.Links.forget_shown",
      "subl_commands.SightWalkWindowListener.on_post_text_command"]),
    ("Opening the editor",
     "Enter or the header's button: the editor laid over the sights, ranges and marks held.",
     ["subl_commands.SightWalkEditCommand.run", "subl_reader.Reader.sight_of",
      "subl_reader.Reader.open_editor", "subl_editor.Editor.__init__", "subl_views.wait_until_loaded", "subl_editor.open_live", "subl_editor.Editor.start",
      "subl_editor.Editor.track", "subl_editor.Editor.hold", "subl_geometry.Geometry.editor_geometry",
      "subl_geometry.Geometry.text_left"]),
    ("Closing the editor",
     "Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.",
     ["subl_commands.SightWalkCloseEditorCommand.run", "subl_reader.Reader.close_editor",
      "subl_editor.Editor.close", "subl_editor.Editor.read_back", "subl_editor.Editor.rows",
      "subl_reader.Reader.editor_closed", "subl_reader.Reader.move_range"]),
    ("Window events",
     "Everything that reacts to the user's window: resizing, settings, focus, keys, closing.",
     ["subl_reader.Reader.follow_resize", "subl_reader.Reader.keep_bench_width", "subl_geometry.Geometry.spans",
      "subl_geometry.Geometry.strip_span", "subl_geometry.Geometry.strip_share", "subl_geometry.Geometry.bench_side",
      "state.render_all", "subl_executor.op_settings", "validator.check_settings",
      "subl_commands.SightWalkWindowListener.on_activated",
      "subl_commands.SightWalkHeaderListener.on_hover", "subl_chat.show_help"]),
    ("One colour scheme for the trips",
     "SightWalk: Select Colour Scheme: general, light or dark, only schemes of that kind, previewed "
     "live in every trip; the files' hues derived from it again, the other views take it as it is.",
     ["subl_commands.SightWalkSelectColourSchemeCommand.run",
      "subl_commands.SightWalkSelectColourSchemeCommand.pick_kind", "subl_commands.all_schemes",
      "subl_tint.is_dark", "subl_commands.scheme_item",
      "subl_commands.SightWalkSelectColourSchemeCommand.preview", "subl_tint.refresh_all",
      "subl_reader.Reader.refresh_schemes", "subl_tint.chosen_scheme", "subl_tint.scheme_colours",
      "subl_tint.resolve_colour", "subl_tint.base_name", "subl_tint.plain_colour", "subl_tint.luminance", "subl_reader.Reader.plain_views", "subl_tint.apply_plain",
      "subl_commands.SightWalkSelectColourSchemeCommand.done"]),
    ("ctrl+tab",
     "The focus round the sights on screen, top to bottom, ctrl+shift+tab the other way.",
     ["subl_commands.SightWalkCycleSightsCommand.run", "subl_commands.SightWalkWindowListener.on_window_command", "subl_reader.Reader.cycle",
      "plan.visible_indices", "plan.cycled"]),
    ("primary+g",
     "In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new "
     "trip with no sights, the repository's files in their place.",
     ["subl_commands.SightWalkToggleGuideCommand.run", "subl_reader.Reader.toggle_focus",
      "subl_commands.SightWalkToggleGuideCommand.folder", "subl_reader.Reader.open_empty", "subl_reader.Reader.empty_layout", "subl_reader.Reader.close_hijacker",
      "subl_commands.SightWalkWindowListener.offer_to_browser", "subl_commands.SightWalkWindowListener.on_load",
      "subl_reader.Reader.take_file", "subl_executor.op_browse",
      "subl_views.make_browser"]),
    ("What the agent is told",
     "The guide's manual, the tools' descriptions and schemas it gets at its start, and the "
     "prompt a guide started from Sublime is given.",
     ["manual.MANUAL: opening", "manual.MANUAL: Showing code",
      "manual.MANUAL: Writing code that fits the reader", "manual.MANUAL: Conversation",
      "manual.MANUAL: Indicators", "manual.tool", "manual.TRANSITION", "manual.TOOLS",
      "validator.TRANSITION_FORM", "subl_guide.PROMPT", "permissions.FIELDS"]),
    ("What the validator refuses",
     "Every refusal of the guide's calls, judged before the executor acts, with the facts it is "
     "given; each message says what to do instead.",
     ["validator.check", "validator.not_stopped", "validator.trip_open",
      "validator.ready", "validator.files", "validator.check_show", "validator.check_open_trip",
      "subl_executor.trip_file", "validator.check_say", "validator.mask", "validator.crowded_lines",
      "validator.check_state", "validator.check_close", "validator.check_browse",
      "validator.check_settings", "validator.check_wait"]),
    ("One tool call over HTTP",
     "From the request to the reply: the token checked, the JSON-RPC message answered, the tool "
     "run on Sublime's thread.",
     ["subl_mcp_http.Handler.do_POST", "subl_mcp_http.Handler.authorized", "subl_mcp_http.reply",
      "subl_mcp_http.answer", "manual.tool", "subl_mcp_http.tool_result", "subl_mcp_http.call_tool",
      "subl_executor.wait_until_ready", "subl_executor.run_on_main", "subl_mcp_http.Handler.send",
      "subl_mcp_http.Handler.do_GET", "subl_mcp_http.Handler.do_DELETE", "subl_mcp_http.Handler.log_message"]),
    ("How Claude comes to listen to Sublime",
     "When no agent listens, asking the guide starts one; it calls wait_for_user through the "
     "bridge and waits on the shared inbox.",
     ["subl_guide.await_answer", "subl_guide.ensure", "subl_guide.listening", "subl_guide.running", "subl_guide.find_claude", "subl_guide.start",
      "subl_executor.wait_for_user"]),
    ("Here",
     "The caret or a selection in a sight becomes here.",
     ["subl_commands.SightWalkWindowListener.on_selection_modified", "subl_reader.Reader.note_selection"]),
    ("Words in two languages",
     "Switch Language: the setting changes, the words follow at once, in every open trip.",
     ["subl_commands.SightWalkSwitchLanguageCommand.run", "sight_walk.settings_changed",
      "words.set_language", "state.render_all", "words.word", "subl_chat.help_html",
      "subl_views.button_html", "subl_commands.SightWalkCompareFontsCommand.run",
      "subl_commands.kept_conversation"]),
    ("Endings",
     "The guide is stopped, windows close.",
     ["subl_commands.SightWalkStopGuideCommand.run", "subl_commands.SightWalkStopGuideCommand.is_enabled",
      "subl_guide.stop", "subl_guide.stop_when_idle", "subl_commands.SightWalkWindowListener.on_pre_close_window", "subl_commands.clear_schemes_if_unused", "subl_tint.first_load",
      "subl_tint.clear_schemes", "subl_tint.scheme_folder", "subl_commands.SightWalkWindowListener.on_window_command", "subl_commands.SightWalkCloseTripCommand.run", "subl_commands.SightWalkResetSightsCommand.run", "subl_reader.Reader.reset_sights", "subl_commands.SightWalkResetSightsCommand.is_enabled", "state.forget", "subl_executor.op_close", "state.current_reader"]),
    ("Names and room",
     "How files and sights are named, and how much room the Sights and the bench get.",
     ["spec.sight_title", "spec.display_path", "spec.repo_root", "spec.matches",
      "subl_geometry.Geometry.share", "subl_geometry.Geometry.conversation_rows", "subl_geometry.Geometry.head",
      "subl_geometry.Geometry.room", "subl_views.smaller", "subl_executor.op_state",
      "subl_reader.Reader.folder", "subl_reader.Reader.note_waiting"]),
    ("Building blocks",
     "The small classes and hooks the trips above stand on.",
     ["plan.Item.__init__", "plan.Pane.__init__", "plan.Pane.spec", "plan.Pane.items", "plan.Pane.all_views",
      "subl_views.kept", "subl_views.phantoms", "subl_views.forget", "subl_chat.Guard.__init__", "subl_commands.SightWalkHeaderListener.is_applicable",
      "subl_commands.SightWalkChatListener.is_applicable"]),
    ("Settings and the rest of the colours",
     "The agent's view of the settings, and colour helpers.",
     ["subl_tint.band_amount", "subl_tint.from_tm_theme", "subl_tint.resolved_scheme", "subl_tint.scheme_stem", "subl_tint.hex_rgb", "subl_tint.apply_grey"]),
    ("The ontology: collections and sights",
     "Members without order, sequences one can walk, places as paths into them, and the sight.",
     [ "ontology.Collection.__init__", "ontology.Collection.member",
      "ontology.Collection.has_place", "ontology.Collection.place_problem",
      "ontology.Collection.label", "ontology.Collection.member_label", "ontology.Sight.label",
      "ontology.Sight.member_label", "ontology.Sequence.__iter__", "ontology.Sequence.__len__",
      "ontology.Sequence.member", "ontology.Sight.__init__", "ontology.Sight.parse",
      "ontology.Sight.spec", "ontology.Sight.member"]),
    ("The ontology: networks",
     "Transitions between places, checked; the trip, the informator and the tour.",
     ["ontology.Network.__init__", "ontology.slug", "ontology.Network.add", "ontology.Network.problem",
      "ontology.Transition.__init__", "ontology.Transition.__eq__", "ontology.Transition.__repr__",
      "ontology.Transition.parts", "ontology.Trip.__init__", "ontology.Trip.label",
      "ontology.Trip.member_label", "ontology.Trip.moved", "ontology.Informator.__init__",
      "ontology.Informator.member",
      "ontology.Informator.label", "ontology.Informator.member_label",
      "ontology.Tour.__init__"]),
    ("An informator and its tour",
     "Open Tour: an informator's tours to choose from, the informator read from its files, "
     "its trips in the tour's order in the Tour tab, a trip opened from it, its "
     "conversation kept, a box ticked by hand.",
     ["subl_commands.SightWalkOpenTourCommand.run", "subl_commands.tour_choices",
      "subl_commands.found_files", "subl_commands.read_name", "subl_commands.read_field",
      "subl_commands.SightWalkOpenTourCommand.open", "words.trips_count", "subl_reader.Reader.open_tour", "subl_reader.read_json",
      "ontology.tour_from",
      "ontology.informator_from", "ontology.trip_from", "ontology.transition_from",
      "ontology.tour", "ontology.visit", "subl_vetting.read_walked",
      "subl_reader.Reader.tour_link", "subl_reader.Reader.keep_transcript", "subl_reader.Reader.kept_marks", "subl_reader.Reader.line_text", "subl_reader.Reader.restore_marks", "subl_reader.kept_frame", "subl_reader.transcripts_path",
      "subl_reader.read_transcripts", "subl_chat.set_transcript",
      "ontology.dumps", "subl_vetting.save_walked", "subl_reader.Reader.draw_tour",
      "subl_vetting.show_tour"]),
    ("Trip files",
     "A trip opened from its file by the guide, and the files written for an informator.",
     ["subl_executor.op_open_trip", "ontology.trip_from", "ontology.trip_data",
      "ontology.transition_data", "ontology.informator_data", "ontology.tour_data"]),
    ("Questions the code already asks",
     "Guards found in the code itself, carried to the sights that use the same objects without "
     "them.",
     ["subl_reader.Reader.build", "subl_asked.draw", "subl_asked.sources", "questions.catalogue",
      "questions.functions", "questions.conditions", "questions.asked_in", "questions.subject",
      "questions.unasked", "questions.uses"]),
    ("Seeing where the code asks",
     "The underline and the popup that says where the code asks the question.",
     ["subl_asked.mark", "subl_asked.popup_html", "subl_asked.escape",
      "subl_commands.SightWalkSightListener.is_applicable", "subl_commands.SightWalkSightListener.on_hover",
      "subl_asked.show_popup", "subl_asked.paint", "subl_asked.toggle",
      "subl_commands.SightWalkToggleSentinelsCommand.run"]),
    ("The guide's permissions",
     "The Permissions tab: a field ticked, remembered or not, and the guide SightWalk started "
     "restarted while it waits with the tools allowed now.",
     ["subl_reader.Reader.draw_permissions", "subl_vetting.show_permissions",
      "subl_reader.Reader.permission_link", "subl_vetting.show_tip", "subl_guide.toggle",
      "permissions.remembered", "subl_guide.restart", "subl_guide.chosen", "subl_guide.folders",
      "permissions.allowed_tools", "permissions.reminders", "subl_guide.ours",
      "subl_reader.Reader.add_folder", "subl_guide.set_folders"]),
    ("The tools over the window",
     "[⤢] in the Tools header lays the tools over almost the whole window under the top headers, "
     "kept apart; [Restore size] in the trip's header brings them back. Hovering a button says "
     "what it does.",
     ["subl_reader.Reader.toggle_maximized", "subl_commands.SightWalkToggleMaximizedCommand.run",
      "subl_reader.Reader.arrange_maximized", "subl_vetting.buttons_help",
      "subl_chat.show_trip_help"]),
    ("Back and forward through trips",
     "◀ ▶ in the Sights' header, primary+[ and primary+]: each trip the guide shows goes into the "
     "window's history with its own conversation, starting from the question that called it; a "
     "step keeps the conversation shown and brings the other trip's back.",
     ["subl_reader.Reader.visit", "history.last_exchange", "subl_reader.Reader.tell_story",
      "validator.check_story", "history.History.__init__",
      "history.History.visit", "subl_reader.Reader.leave", "history.History.keep",
      "history.History.current", "subl_reader.Reader.enter", "subl_chat.nav_phantom",
      "subl_commands.SightWalkStepCommand.run", "subl_reader.Reader.step", "history.History.can",
      "history.History.go", "subl_chat.help_or_link"]),
    ("Driving a trip from the terminal",
     "Tests without mouse or keys, in the guide's notation: sight_walk_fill sets the draft, whose "
     "<here> tags become links, sight_walk_select selects places, (>) the draft, and "
     "sight_walk_send_draft sends it.",
     ["subl_commands.SightWalkFillCommand.run", "marks.read_here", "subl_commands.place_region",
      "marks.parse_place", "subl_commands.SightWalkSelectCommand.run",
      "subl_commands.note_selection", "subl_commands.SightWalkSendDraftCommand.run"]),
    ("The bench's answers listed",
     "The Answers tab: the bench's questions and answers by their first words; a click shows "
     "one's icons or places and brings it into the bench, a second click hides them.",
     ["subl_reader.Reader.draw_answers", "subl_reader.Reader.bench_rows", "answers.entries",
      "subl_reader.Reader.answer_marks", "subl_vetting.show_answers", "subl_vetting.html_escape",
      "subl_reader.Reader.answer_link", "subl_reader.Reader.hide_answer",
      "subl_reader.Reader.scroll_bench"]),
]


# A function in several trips is discussed in its own trip (Jakub); the others show it on the way.
OWN_TRIPS = {
    "subl_executor.run_on_main": "One tool call over HTTP",
    "ontology.Sight.parse": "The ontology: collections and sights",
    "ontology.Trip.__init__": "The ontology: networks",
    "ontology.Network.__init__": "The ontology: networks",
    "ontology.Network.problem": "The ontology: networks",
    "subl_reader.Reader.build": "Loading the sights",
    "subl_reader.Reader.draw_map": "The Map's nodes",
    "subl_vetting.draw_map": "Drawing the Map",
    "subl_executor.wait_for_user": "The user sends a message",
    "manual.tool": "What the agent is told",
    "ontology.trip_from": "Trip files",
    "subl_reader.Reader.tool_view": "The Tools pane's tabs",
}

# The informator's reading paths (Jakub's leads_to and unblocks), written by hand: (from, to).
LEADS = [
    ("Plugin start and stop", "Setting up the agent bridge"),
    ("Setting up the agent bridge", "What the agent is told"),
    ("What the agent is told", "One tool call over HTTP"),
    ("Setting up the agent bridge", "How Claude comes to listen to Sublime"),
    ("One tool call over HTTP", "A request arrives"),
    ("A request arrives", "What the validator refuses"),
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
    ("The Tools pane's tabs", "The guide's permissions"),
    ("The Tools pane's tabs", "The bench's answers listed"),
    ("Linking words to code", "Driving a trip from the terminal"),
    ("The Map's nodes", "Drawing the Map"),
    ("How Claude comes to listen to Sublime", "The user sends a message"),
    ("The user sends a message", "Here"),
    ("Here", "Linking words to code"),
    ("Here", "Opening the editor"),
    ("Opening the editor", "Closing the editor"),
    ("Closing the editor", "primary+g"),
    ("primary+g", "ctrl+tab"),
    ("ctrl+tab", "One colour scheme for the trips"),
    ("One colour scheme for the trips", "Words in two languages"),
    ("Words in two languages", "Endings"),
    ("Drawing the Map", "Trip files"),
    ("Trip files", "An informator and its tour"),
]
NEEDS = [  # (trip, the trip it needs understood first)
    ("A request arrives", "The ontology: networks"),
    ("The ontology: networks", "The ontology: collections and sights"),
    ("Loading the sights", "Building blocks"),
    ("Measuring", "Names and room"),
    ("Colours", "Settings and the rest of the colours"),
    ("Polling and the wheel", "Window events"),
]

# Tours written by hand (Jakub): a name and the trips in their order.
TOURS = [
    ("How the program talks to the agent", [
        "Setting up the agent bridge", "What the agent is told", "One tool call over HTTP",
        "A request arrives", "How Claude comes to listen to Sublime", "The user sends a message",
        "The agent says something", "Stopping an answer", "Pointing", "Trip files"]),
]

# Not runs but surveys: all the places about one thing (see the manual on trips).
SURVEYS = {"What the agent is told", "What the validator refuses", "The Tools pane's tabs", "The ontology: collections and sights", "The ontology: networks", "Window events", "Endings", "Names and room", "Building blocks",
           "Settings and the rest of the colours"}

# Whose method a call on another object reaches, by the object's name: the code's own
# convention (a reader is called reader or owner), not a guess by the method's name.
RECEIVERS = {"informator": "ontology.Informator", "trip": "ontology.Trip",
             "reader": "subl_reader.Reader", "owner": "subl_reader.Reader", "current_reader": "subl_reader.Reader",
             "require_ready": "subl_reader.Reader", "new_reader": "subl_reader.Reader",
             "reader_for": "subl_reader.Reader", "editor": "subl_editor.Editor", "sight": "plan.Pane"}


# Jumps the code makes through data or by a name the rules below cannot follow, written and
# checked by hand: (caller, a piece of the calling line, callee). TRIP_JUMPS hold only in one
# trip's story (run_on_main runs whatever it is given).
OPS = ["show", "say", "state", "close", "settings", "browse", "open_trip"]
JUMPS = [("subl_executor.execute", "OPS[tool]", "subl_executor.op_" + op) for op in OPS] + [
    ("plan.Pane.spec", "self.sight.spec", "ontology.Sight.spec"),
    ("subl_reader.Reader.context", "marks.place_text(", "marks.place_text"),
    ("subl_reader.Reader.tint", "s.all_views()", "plan.Pane.all_views"),
]
# Where a receiver's name misleads the rules (RECEIVERS): there `sight` is an ontology.Sight,
# not a plan.Pane. (caller, a piece of the line, the callee the rules give, the right one.)
FIXES = [(caller, text, "plan.Pane.spec", "ontology.Sight.spec") for caller, text in [
    ("subl_executor.op_show", "for sight in made"), ("subl_executor.op_open_trip", "for sight in trip"),
    ("ontology.trip_data", "for sight in trip"), ("subl_reader.Reader.load", "for sight in trip")]]
TRIP_JUMPS = {
    "A request arrives": [("subl_executor.run_on_main", "fn()", "subl_executor.op_show")],
}
CLASSES = {}  # "module.Class": ["module.Base", ...], filled by definitions


# Texts that are no function but worth a sight of their own (Jakub): what the agent is told.
SECTIONED = ["manual.MANUAL"]
TEXTS = ["manual.MANUAL", "manual.TRANSITION", "manual.TOOLS", "subl_guide.PROMPT", "permissions.FIELDS",
         "validator.TRANSITION_FORM", "validator.MARK_FIRST", "marks.CODE_TALK"]


def texts(module, tree):
    """{"module.NAME": the assignment} for the TEXTS among a module's top-level assignments; a
    long text in parts, one per section (see sections)."""
    found = {}
    for node in tree.body:
        name = module + "." + node.targets[0].id if isinstance(node, ast.Assign) \
            and isinstance(node.targets[0], ast.Name) else None
        if name in TEXTS:
            found.update(sections(name, node) if name in SECTIONED else {name: node})
    return found


def sections(name, node):
    """A text split where a heading stands after a blank line: {"name: heading": part}, each part
    a stand-in node with the part's lines, so a sight holds one section (Jakub)."""
    lines = node.value.value.split("\n")
    starts = [0] + [i for i, line in enumerate(lines) if i and not lines[i - 1].strip()
                    and re.match(r"^[A-Z][^.]*$", line)]
    parts = {}
    for k, start in enumerate(starts):
        end = (starts[k + 1] - 2) if k + 1 < len(starts) else len(lines) - 1
        part = ast.Constant(value="", lineno=node.lineno + start,
                            end_lineno=node.lineno + end, col_offset=0)
        parts["%s: %s" % (name, lines[start].strip() if k else "opening")] = part
    return parts


def functions():
    """{"module.Class.function": "file:begin-end"} for every function in FILES, and the TEXTS."""
    specs = {}
    for path in FILES:
        module = path.rsplit("/", 1)[-1][:-3]
        tree = ast.parse(open(path, encoding="utf-8").read())
        specs.update((name, "%s:%d-%d" % (path, node.lineno, node.end_lineno))
                     for name, node in texts(module, tree).items())
        for node in tree.body:
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
        found.update((name, (module, None, node)) for name, node in texts(module, tree).items())
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
        return named("subl_commands.%s.run" % command, found) or named("subl_setup.%s.run" % command, found)
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
        if target and target != name and isinstance(found[target][2], ast.FunctionDef):
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


def make_trip(title, about, names, specs, found, imported, commit):
    """The trip's story: its own in STORIES (with <here> tags), else what the list says of it."""
    data = trip_sights(title, names, specs, found, imported)
    kind = "survey" if title in SURVEYS else "run"
    return Trip(title, [Sight.parse(spec) for spec in data["sights"]],
                [Transition(t["type"], t["from"], t["to"]) for t in data["transitions"]],
                commit, kind, STORIES.get(title, about))


# Trips' stories, told by their Pioneer (P:) first on their bench (Jakub, 2026-10-20), with <here>
# tags at their own sights; a trip without one tells what the list above says of it.
STORIES = {}
LONG_TRIP = 5


def own_trip(name):
    """The id of the trip that discusses name."""
    return Trip(OWN_TRIPS.get(name) or next(t for t, _, ns in TRIPS if name in ns), []).id


def between_trips(found, imported):
    """The informator's transitions: the reading paths (LEADS, NEEDS), every sight's own trip,
    and the calls that leave a trip, to the callee in its own trip."""
    ids = [Trip(title, []).id for title, _, _ in TRIPS]
    slug = lambda title: Trip(title, []).id  # noqa: E731
    out = [Transition("leads_to", (slug(a),), (slug(b),)) for a, b in LEADS]
    out += [Transition("unblocks", (slug(b),), (slug(a),)) for a, b in NEEDS]
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
    made = [make_trip(t, about, ns, specs, found, imported, commit) for t, about, ns in TRIPS]
    os.makedirs("docs/trips", exist_ok=True)
    os.makedirs("docs/informators", exist_ok=True)
    for trip in made:
        write_json("docs/trips/%s.json" % trip.id, trip_data(trip))
    informator = Informator("SightWalk", made, between_trips(found, imported), commit)
    files = {trip.id: "../trips/%s.json" % trip.id for trip in made}
    write_json("docs/informators/sightwalk.json", informator_data(informator, files))
    os.makedirs("docs/tours", exist_ok=True)
    for name, titles in TOURS:
        chosen = Tour(informator, [informator.member(Trip(t, []).id) for t in titles], (), name)
        write_json("docs/tours/%s.json" % Trip(name, []).id,
                   tour_data(chosen, "../informators/sightwalk.json"))


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        f.write(dumps(data))


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
    for name in sorted(set(specs) - covered - set(TEXTS)):
        print("not in any trip:", name, specs[name], file=sys.stderr)
    # Short trips keep the tour map readable and leave room for adventures (Jakub).
    long = ["%s (%d)" % (title, len(names)) for title, _, names in TRIPS if len(names) > LONG_TRIP]
    if long:
        print("%d trips longer than %d sights" % (len(long), LONG_TRIP), file=sys.stderr)


if __name__ == "__main__":
    main()
