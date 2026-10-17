# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:39-45` plugin_loaded
- `sw/subl_mcp_http.py:142-145` start
- `sw/subl_executor.py:237-241` load_config
- `sw/subl_mcp_http.py:118-122` start_server
- `sw/subl_mcp_http.py:133-139` settings_changed
- `sw/subl_mcp_http.py:125-130` stop_server
- `sight_walk.py:54-59` plugin_unloaded
- `sw/subl_scrollbars.py:13-25` reader_focused
- `sw/state.py:44-51` close_all
- `sw/subl_mcp_http.py:148-150` stop
- `sw/subl_setup.py:70-72` SightWalkRestartCommand.run

## 2. Setting up the agent bridge (5 views)

The setup command keeps a token, writes it for poke, and puts Claude Code's registration line on the clipboard.

- `sw/subl_setup.py:32-38` SightWalkSetupCommand.run
- `sw/subl_setup.py:41-48` ensure_token
- `sw/subl_setup.py:51-57` write_config
- `sw/subl_setup.py:60-63` show_instructions
- `sw/subl_commands.py:17-24` SightWalkReplaceCommand.run

## 3. A request arrives (20 views)

From the HTTP server's thread to the show operation on Sublime's, with every check on the way.

- `sw/subl_executor.py:178-185` execute
- `sw/subl_executor.py:188-204` run_on_main
- `sw/subl_executor.py:121-135` facts
- `sw/subl_executor.py:138-147` sight_files
- `sw/subl_executor.py:150-159` sight_functions
- `sw/spec.py:118-131` functions_in
- `sw/validator.py:24-29` check
- `sw/validator.py:93-97` check_show
- `sw/validator.py:83-90` one_function
- `sw/subl_executor.py:49-55` op_show
- `sw/subl_executor.py:58-60` named
- `sw/validator.py:51-54` not_stopped
- `sw/validator.py:32-48` trip_of
- `sw/ontology.py:129-137` Sight.parse
- `sw/ontology.py:160-164` Trip.__init__
- `sw/ontology.py:93-100` Network.__init__
- `sw/ontology.py:109-119` Network.problem
- `sw/validator.py:68-80` files
- `sw/spec.py:10-23` parse_spec
- `sw/subl_executor.py:31-33` file_lines

## 4. A new reader window (12 views)

The window and every view but the sights.

- `sw/subl_executor.py:36-46` new_reader
- `sw/subl_reader.py:71-94` Reader.__init__
- `sw/subl_reader.py:96-136` Reader.make_side_views
- `sw/subl_views.py:178-187` bench_font
- `sw/subl_views.py:190-194` match_font
- `sw/subl_views.py:138-145` make_blank_view
- `sw/subl_views.py:114-121` make_side_view
- `sw/subl_chat.py:73-79` start
- `sw/subl_chat.py:82-91` make_header
- `sw/subl_chat.py:119-128` make_status
- `sw/subl_vetting.py:26-33` make_tool
- `sw/state.py:23-26` register

## 5. Loading the sights (22 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/subl_reader.py:140-152` Reader.load
- `sw/subl_chat.py:211-219` catch_up
- `sw/subl_reader.py:198-208` Reader.close_sights
- `sw/subl_reader.py:210-224` Reader.build
- `sw/subl_views.py:156-160` FileCopy.__init__
- `sw/subl_views.py:163-175` make_copy
- `sw/subl_reader.py:226-246` Reader.surround
- `sw/spec.py:134-149` elided
- `sw/spec.py:162-166` block_name
- `sw/spec.py:152-159` body_indent
- `sw/words.py:62-67` lines_of
- `sw/subl_reader.py:248-255` Reader.ellipses
- `sw/subl_reader.py:257-268` Reader.draw_ellipsis
- `sw/subl_views.py:288-296` draw_ellipsis
- `sw/subl_reader.py:324-332` Reader.room_px
- `sw/subl_reader.py:270-279` Reader.grow_ellipses
- `sw/spec.py:97-112` ancestors
- `sw/spec.py:84-85` indent
- `sw/spec.py:88-94` opens_block
- `sw/spec.py:169-176` breathing
- `sw/subl_views.py:199-205` make_header
- `sw/subl_views.py:208-213` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/subl_reader.py:281-286` Reader.tint
- `sw/subl_tint.py:169-172` apply_tint
- `sw/subl_tint.py:149-155` schemes_for
- `sw/subl_tint.py:22-26` hue_for
- `sw/subl_tint.py:107-134` tinted_schemes
- `sw/subl_tint.py:41-53` load_base_scheme
- `sw/subl_tint.py:33-38` tint_color
- `sw/subl_tint.py:76-81` write_scheme
- `sw/subl_tint.py:158-166` set_schemes
- `sw/subl_tint.py:137-146` when_indexed

## 7. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/subl_reader.py:288-292` Reader.draw_gaps
- `sw/subl_reader.py:52-53` line_count
- `sw/subl_views.py:299-306` draw_gap
- `sw/subl_reader.py:307-322` Reader.make_items
- `sw/subl_views.py:216-217` line_top
- `sw/subl_views.py:220-221` header_top
- `sw/subl_reader.py:334-339` Reader.calibrate
- `sw/subl_reader.py:341-346` Reader.measure_full
- `sw/subl_reader.py:348-352` Reader.measure_half
- `sw/subl_reader.py:354-368` Reader.start
- `sw/subl_reader.py:472-475` Reader.centred_lead
- `sw/plan.py:85-90` lead
- `sw/plan.py:79-82` free_room
- `sw/plan.py:50-66` stack
- `sw/plan.py:69-76` sight_groups
- `sw/subl_reader.py:556-562` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/subl_reader.py:477-483` Reader.scroll_to
- `sw/plan.py:93-101` offset_range
- `sw/subl_geometry.py:60-63` Geometry.bench_floor
- `sw/subl_reader.py:438-448` Reader.render
- `sw/subl_geometry.py:79-110` Geometry.column_rects
- `sw/subl_geometry.py:40-44` Geometry.column
- `sw/subl_geometry.py:127-138` Geometry.sight_cells
- `sw/subl_geometry.py:123-125` Geometry.floor_height
- `sw/subl_reader.py:372-379` Reader.layout
- `sw/subl_views.py:86-109` reader_layout
- `sw/subl_views.py:76-83` to_layout

## 9. Arranging the views (16 views)

After a new layout: every view into its group, then back at its place.

- `sw/subl_reader.py:450-468` Reader.arrange
- `sw/subl_reader.py:407-412` Reader.place
- `sw/subl_reader.py:381-396` Reader.strip_in_front
- `sw/subl_geometry.py:112-121` Geometry.strip_rows
- `sw/subl_reader.py:294-305` Reader.clone
- `sw/subl_reader.py:414-436` Reader.assign_groups
- `sw/subl_views.py:63-66` hide_chrome
- `sw/subl_reader.py:515-526` Reader.scroll_views
- `sw/subl_reader.py:485-493` Reader.places
- `sw/subl_reader.py:550-554` Reader.strip_place
- `sw/subl_views.py:148-150` anchor
- `sw/subl_reader.py:740-747` Reader.draw_strip_buttons
- `sw/subl_reader.py:749-751` Reader.strip_button
- `sw/subl_reader.py:651-654` Reader.draw_edit_buttons
- `sw/subl_reader.py:646-649` Reader.title
- `sw/subl_views.py:224-236` draw_edit_button

## 10. Polling and the wheel (10 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/subl_reader.py:569-577` Reader.poll
- `sw/subl_chat.py:180-190` keep_at_bottom
- `sw/subl_chat.py:199-202` bottom_place
- `sw/subl_chat.py:193-196` kept_place
- `sw/subl_reader.py:579-586` Reader.poll_wheel
- `sw/subl_reader.py:566-567` Reader.alive
- `sw/subl_reader.py:528-548` Reader.read_wheel
- `sw/subl_reader.py:495-507` Reader.wheel_places
- `sw/subl_reader.py:509-513` Reader.pinned_places
- `sw/subl_reader.py:64-67` item_top

## 11. Pointing (16 views)

The marks an answer places with its own tags, resolved to sights and lines, framed in its words, the reader scrolled to show them.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:224-245` read_marks
- `sw/marks.py:215-221` place
- `sw/marks.py:248-257` frame_scopes
- `sw/subl_reader.py:602-610` Reader.point
- `sw/marks.py:91-107` resolve_marks
- `sw/marks.py:80-88` jump
- `sw/marks.py:18-37` resolve_target
- `sw/marks.py:46-53` sight_target
- `sw/marks.py:56-62` icon_for
- `sw/marks.py:14-15` line_y
- `sw/subl_chat.py:222-238` outline_refs
- `sw/marks.py:175-178` sight_refs
- `sw/marks.py:40-43` sight_number
- `sw/spec.py:58-64` sight_index
- `sw/spec.py:50-55` sight_name

## 12. Drawing the marks (10 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/subl_reader.py:612-625` Reader.draw_gutter
- `sw/subl_reader.py:627-632` Reader.draw_strip_marks
- `sw/marks.py:143-154` strip_icons
- `sw/subl_views.py:253-262` draw_strip_icons
- `sw/marks.py:110-122` visible_lines
- `sw/marks.py:125-140` gutter_icons
- `sw/subl_views.py:241-250` draw_icons
- `sw/subl_reader.py:634-642` Reader.draw_outlines
- `sw/marks.py:71-77` icon_colour
- `sw/subl_views.py:268-281` draw_outlines

## 13. The agent says something (19 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:189-204` untag
- `sw/marks.py:271-273` line_refs
- `sw/validator.py:12-15` MARK_FIRST
- `sw/marks.py:160-162` speaks_of_code
- `sw/marks.py:157-157` CODE_TALK
- `sw/subl_reader.py:914-930` Reader.say
- `sw/subl_reader.py:707-716` Reader.show_headers
- `sw/subl_chat.py:94-113` show_header
- `sw/header.py:12-22` title_lines
- `sw/subl_chat.py:131-140` show_status
- `sw/subl_chat.py:150-160` say
- `sw/subl_commands.py:28-29` SightWalkInsertCommand.run
- `sw/subl_chat.py:53-70` Guard.on_text_changed
- `sw/subl_chat.py:35-43` protected_end
- `sw/subl_commands.py:110-113` SightWalkChatListener.on_modified
- `sw/subl_commands.py:115-119` SightWalkChatListener.on_post_text_command
- `sw/marks.py:260-262` clean
- `sw/subl_chat.py:241-246` shade_variables

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/subl_commands.py:181-184` SightWalkStopAnswerCommand.run
- `sw/subl_reader.py:893-900` Reader.stop_answer
- `sw/subl_reader.py:902-905` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (10 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/subl_reader.py:764-769` Reader.select_tool
- `sw/subl_vetting.py:56-75` show_tabs
- `sw/subl_commands.py:273-276` SightWalkTogglePanningCommand.run
- `sw/subl_reader.py:771-781` Reader.toggle_panning
- `sw/subl_vetting.py:36-44` set_panning
- `sw/subl_vetting.py:47-49` content_point
- `sw/subl_reader.py:755-756` Reader.tools
- `sw/subl_reader.py:758-759` Reader.tool_view
- `sw/subl_reader.py:761-762` Reader.hidden_tools
- `sw/subl_reader.py:857-865` Reader.draw_map

## 16. The Map's nodes (12 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/subl_reader.py:857-865` Reader.draw_map
- `sw/subl_reader.py:971-978` map_style
- `sw/subl_reader.py:867-881` Reader.map_nodes
- `sw/subl_reader.py:45-49` fragment_of
- `sw/subl_reader.py:883-887` Reader.owner
- `sw/subl_reader.py:56-61` defined_name
- `sw/callmap.py:33-39` first_definition
- `sw/callmap.py:42-49` node_at
- `sw/callmap.py:28-30` Node.__init__
- `sw/callmap.py:52-59` edges
- `sw/callmap.py:42-49` node_at
- `sw/subl_vetting.py:87-94` draw_map

## 17. Drawing the Map (17 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/subl_vetting.py:87-94` draw_map
- `sw/subl_vetting.py:80-84` find_dot
- `sw/callmap.py:118-132` dot_source
- `sw/callmap.py:93-99` file_block
- `sw/callmap.py:70-73` cluster
- `sw/callmap.py:76-78` node_line
- `sw/callmap.py:81-90` sight_blocks
- `sw/callmap.py:62-63` node_id
- `sw/callmap.py:66-67` quote
- `sw/callmap.py:102-104` arrow
- `sw/callmap.py:107-115` legend
- `sw/subl_vetting.py:97-109` render
- `sw/subl_vetting.py:112-114` png_size
- `sw/subl_vetting.py:123-138` show_image
- `sw/subl_vetting.py:141-146` zoom
- `sw/subl_commands.py:266-267` SightWalkZoomMapCommand.run
- `sw/subl_vetting.py:149-152` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with the focus, the visible sights and the edits, and the agent receives it.

- `sw/subl_commands.py:42-46` SightWalkSendCommand.run
- `sw/subl_chat.py:163-177` take_draft
- `sw/subl_commands.py:32-36` send
- `sw/state.py:36-37` reader_for
- `sw/subl_reader.py:932-946` Reader.context
- `sw/subl_views.py:309-313` selected_text
- `sw/plan.py:104-107` visible_specs
- `sw/subl_reader.py:700-703` Reader.take_edits
- `sw/subl_executor.py:218-232` wait_for_user

## 19. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/subl_commands.py:62-72` SightWalkEditCommand.run
- `sw/subl_reader.py:668-673` Reader.sight_of
- `sw/subl_reader.py:656-666` Reader.open_editor
- `sw/subl_editor.py:24-32` Editor.__init__
- `sw/subl_views.py:69-73` wait_until_loaded
- `sw/subl_editor.py:16-20` open_live
- `sw/subl_editor.py:34-44` Editor.start
- `sw/subl_editor.py:46-58` Editor.track
- `sw/subl_editor.py:60-65` Editor.hold
- `sw/subl_geometry.py:69-77` Geometry.editor_geometry

## 20. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/subl_commands.py:78-81` SightWalkCloseEditorCommand.run
- `sw/subl_reader.py:675-676` Reader.close_editor
- `sw/subl_editor.py:81-92` Editor.close
- `sw/subl_editor.py:74-79` Editor.read_back
- `sw/subl_editor.py:67-72` Editor.rows
- `sw/subl_reader.py:678-691` Reader.editor_closed
- `sw/subl_reader.py:693-698` Reader.move_range

## 21. Window events (13 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/subl_reader.py:588-598` Reader.follow_resize
- `sw/subl_reader.py:398-405` Reader.keep_bench_width
- `sw/subl_geometry.py:18-25` Geometry.spans
- `sw/subl_geometry.py:27-31` Geometry.strip_span
- `sw/subl_geometry.py:33-35` Geometry.strip_share
- `sw/subl_geometry.py:37-38` Geometry.bench_side
- `sw/state.py:54-59` render_all
- `sw/subl_executor.py:99-106` op_settings
- `sw/validator.py:143-151` check_settings
- `sw/subl_commands.py:123-125` SightWalkWindowListener.on_activated
- `sw/subl_commands.py:95-99` SightWalkScrollCommand.run
- `sw/subl_commands.py:89-91` SightWalkHeaderListener.on_hover
- `sw/subl_chat.py:143-147` show_help

## 22. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/subl_commands.py:294-305` SightWalkToggleGuideCommand.run
- `sw/subl_reader.py:718-728` Reader.toggle_focus
- `sw/subl_commands.py:307-312` SightWalkToggleGuideCommand.folder
- `sw/subl_reader.py:154-158` Reader.open_empty
- `sw/subl_reader.py:160-179` Reader.empty_layout
- `sw/subl_reader.py:181-186` Reader.close_hijacker
- `sw/subl_commands.py:149-153` SightWalkWindowListener.offer_to_browser
- `sw/subl_commands.py:127-128` SightWalkWindowListener.on_load
- `sw/subl_reader.py:188-196` Reader.take_file
- `sw/subl_executor.py:88-96` op_browse
- `sw/subl_views.py:124-135` make_browser

## 23. What the agent is told (11 views, survey)

The guide's manual, the tools' descriptions and schemas it gets at its start, and the prompt a guide started from Sublime is given.

- `sw/manual.py:6-19` MANUAL: opening
- `sw/manual.py:21-47` MANUAL: Showing code
- `sw/manual.py:49-52` MANUAL: Writing code that fits the reader
- `sw/manual.py:54-85` MANUAL: Conversation
- `sw/manual.py:87-118` MANUAL: Indicators
- `sw/manual.py:121-124` tool
- `sw/manual.py:127-130` TRANSITION
- `sw/manual.py:132-164` TOOLS
- `sw/validator.py:10-11` TRANSITION_FORM
- `sw/subl_guide.py:19-24` PROMPT
- `sw/subl_guide.py:25-25` TOOLS

## 24. What the validator refuses (14 views, survey)

Every refusal of the guide's calls, judged before the executor acts, with the facts it is given; each message says what to do instead.

- `sw/validator.py:24-29` check
- `sw/validator.py:51-54` not_stopped
- `sw/validator.py:57-59` trip_open
- `sw/validator.py:62-65` ready
- `sw/validator.py:68-80` files
- `sw/validator.py:93-97` check_show
- `sw/validator.py:100-105` check_open_trip
- `sw/subl_executor.py:162-171` trip_file
- `sw/validator.py:108-125` check_say
- `sw/validator.py:128-129` check_state
- `sw/validator.py:132-134` check_close
- `sw/validator.py:137-140` check_browse
- `sw/validator.py:143-151` check_settings
- `sw/validator.py:154-155` check_wait

## 25. One tool call over HTTP (13 views)

From the request to the reply: the token checked, the JSON-RPC message answered, the tool run on Sublime's thread.

- `sw/subl_mcp_http.py:94-105` Handler.do_POST
- `sw/subl_mcp_http.py:78-81` Handler.authorized
- `sw/subl_mcp_http.py:65-74` reply
- `sw/subl_mcp_http.py:50-62` answer
- `sw/manual.py:121-124` tool
- `sw/subl_mcp_http.py:38-47` tool_result
- `sw/subl_mcp_http.py:23-35` call_tool
- `sw/subl_executor.py:207-215` wait_until_ready
- `sw/subl_executor.py:188-204` run_on_main
- `sw/subl_mcp_http.py:83-92` Handler.send
- `sw/subl_mcp_http.py:107-108` Handler.do_GET
- `sw/subl_mcp_http.py:110-112` Handler.do_DELETE
- `sw/subl_mcp_http.py:114-115` Handler.log_message

## 26. How Claude comes to listen to Sublime (7 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/subl_guide.py:90-95` await_answer
- `sw/subl_guide.py:47-56` ensure
- `sw/subl_guide.py:30-32` listening
- `sw/subl_guide.py:35-36` running
- `sw/subl_guide.py:39-44` find_claude
- `sw/subl_guide.py:59-68` start
- `sw/subl_executor.py:218-232` wait_for_user

## 27. Here, and asking by a shortcut (3 views)

The caret or a selection in a sight becomes here; a shortcut sends a question, like "Explain next.", as a message.

- `sw/subl_commands.py:137-147` SightWalkWindowListener.on_selection_modified
- `sw/subl_reader.py:730-733` Reader.note_selection
- `sw/subl_commands.py:52-56` SightWalkAskCommand.run

## 28. Words in two languages (9 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/subl_commands.py:257-260` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:48-51` settings_changed
- `sw/words.py:57-59` set_language
- `sw/state.py:54-59` render_all
- `sw/words.py:53-54` word
- `sw/subl_chat.py:28-32` help_html
- `sw/subl_views.py:33-35` button_html
- `sw/subl_commands.py:342-354` SightWalkCompareFontsCommand.run
- `sw/subl_commands.py:357-365` kept_conversation

## 29. Endings (16 views, survey)

The guide is stopped, windows close.

- `sw/subl_commands.py:282-283` SightWalkStopGuideCommand.run
- `sw/subl_commands.py:285-286` SightWalkStopGuideCommand.is_enabled
- `sw/subl_guide.py:83-87` stop
- `sw/subl_guide.py:71-80` stop_when_idle
- `sw/subl_commands.py:155-157` SightWalkWindowListener.on_pre_close_window
- `sw/subl_commands.py:160-162` clear_schemes_if_unused
- `sw/subl_tint.py:183-209` clear_schemes
- `sw/subl_tint.py:72-73` scheme_folder
- `sw/subl_commands.py:130-135` SightWalkWindowListener.on_window_command
- `sw/subl_commands.py:188-190` SightWalkCloseTripCommand.run
- `sw/subl_commands.py:168-171` SightWalkResetSightsCommand.run
- `sw/subl_reader.py:735-738` Reader.reset_sights
- `sw/subl_commands.py:173-175` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:29-33` forget
- `sw/subl_executor.py:83-85` op_close
- `sw/state.py:40-41` current_reader

## 30. Names and room (11 views, survey)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:67-73` sight_title
- `sw/spec.py:37-44` display_path
- `sw/spec.py:26-34` repo_root
- `sw/spec.py:76-81` matches
- `sw/subl_geometry.py:12-16` Geometry.share
- `sw/subl_geometry.py:46-54` Geometry.conversation_rows
- `sw/subl_geometry.py:56-58` Geometry.head
- `sw/subl_geometry.py:65-67` Geometry.room
- `sw/subl_executor.py:78-80` op_state
- `sw/subl_reader.py:907-912` Reader.folder
- `sw/subl_reader.py:889-891` Reader.note_waiting

## 31. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-15` Item.__init__
- `sw/plan.py:22-35` Pane.__init__
- `sw/plan.py:37-39` Pane.spec
- `sw/plan.py:41-43` Pane.items
- `sw/plan.py:45-47` Pane.all_views
- `sw/subl_views.py:45-46` kept
- `sw/subl_views.py:49-54` phantoms
- `sw/subl_views.py:57-58` forget
- `sw/subl_chat.py:49-51` Guard.__init__
- `sw/subl_commands.py:85-87` SightWalkHeaderListener.is_applicable
- `sw/subl_commands.py:106-108` SightWalkChatListener.is_applicable

## 32. Settings and the rest of the colours (7 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/subl_commands.py:101-102` SightWalkScrollCommand.is_enabled
- `sw/subl_tint.py:84-86` band_amount
- `sw/subl_tint.py:59-69` from_tm_theme
- `sw/subl_tint.py:96-104` resolved_scheme
- `sw/subl_tint.py:89-93` scheme_stem
- `sw/subl_tint.py:29-30` hex_rgb
- `sw/subl_tint.py:175-180` apply_grey

## 33. The ontology: collections and sights (15 views, survey)

Members without order, sequences one can walk, places as paths into them, and the sight.

- `sw/ontology.py:25-26` Collection.__init__
- `sw/ontology.py:28-30` Collection.member
- `sw/ontology.py:32-33` Collection.has_place
- `sw/ontology.py:35-47` Collection.place_problem
- `sw/ontology.py:49-51` Collection.label
- `sw/ontology.py:53-54` Collection.member_label
- `sw/ontology.py:146-147` Sight.label
- `sw/ontology.py:149-150` Sight.member_label
- `sw/ontology.py:61-62` Sequence.__iter__
- `sw/ontology.py:64-65` Sequence.__len__
- `sw/ontology.py:67-69` Sequence.member
- `sw/ontology.py:125-127` Sight.__init__
- `sw/ontology.py:129-137` Sight.parse
- `sw/ontology.py:139-141` Sight.spec
- `sw/ontology.py:143-144` Sight.member

## 34. The ontology: networks (17 views, survey)

Transitions between places, checked; the trip, the informator and the tour.

- `sw/ontology.py:93-100` Network.__init__
- `sw/ontology.py:16-18` slug
- `sw/ontology.py:102-107` Network.add
- `sw/ontology.py:109-119` Network.problem
- `sw/ontology.py:76-77` Transition.__init__
- `sw/ontology.py:79-80` Transition.__eq__
- `sw/ontology.py:82-83` Transition.__repr__
- `sw/ontology.py:85-86` Transition.parts
- `sw/ontology.py:160-164` Trip.__init__
- `sw/ontology.py:166-167` Trip.label
- `sw/ontology.py:169-170` Trip.member_label
- `sw/ontology.py:172-177` Trip.moved
- `sw/ontology.py:185-187` Informator.__init__
- `sw/ontology.py:189-190` Informator.member
- `sw/ontology.py:192-193` Informator.label
- `sw/ontology.py:195-196` Informator.member_label
- `sw/ontology.py:203-209` Tour.__init__

## 35. An informator and its tour (28 views)

Open Tour: an informator's tours to choose from, the informator read from its files, its trips in the tour's order in the Tour tab, a trip opened from it, its conversation kept, a box ticked by hand.

- `sw/subl_commands.py:198-204` SightWalkOpenTourCommand.run
- `sw/subl_commands.py:213-226` tour_choices
- `sw/subl_commands.py:229-239` found_files
- `sw/subl_commands.py:242-243` read_name
- `sw/subl_commands.py:246-251` read_field
- `sw/subl_commands.py:206-210` SightWalkOpenTourCommand.open
- `sw/words.py:70-77` trips_count
- `sw/subl_reader.py:785-799` Reader.open_tour
- `sw/subl_reader.py:962-964` read_json
- `sw/ontology.py:294-300` tour_from
- `sw/ontology.py:273-277` informator_from
- `sw/ontology.py:257-260` trip_from
- `sw/ontology.py:247-248` transition_from
- `sw/ontology.py:212-225` tour
- `sw/ontology.py:228-236` visit
- `sw/subl_vetting.py:176-182` read_walked
- `sw/subl_reader.py:801-814` Reader.tour_link
- `sw/subl_reader.py:816-825` Reader.keep_transcript
- `sw/subl_reader.py:827-832` Reader.kept_marks
- `sw/subl_reader.py:834-836` Reader.line_text
- `sw/subl_reader.py:838-851` Reader.restore_marks
- `sw/subl_reader.py:949-951` transcripts_path
- `sw/subl_reader.py:954-959` read_transcripts
- `sw/subl_chat.py:205-208` set_transcript
- `sw/ontology.py:280-284` dumps
- `sw/subl_vetting.py:185-194` save_walked
- `sw/subl_reader.py:853-855` Reader.draw_tour
- `sw/subl_vetting.py:157-173` show_tour

## 36. Trip files (6 views)

A trip opened from its file by the guide, and the files written for an informator.

- `sw/subl_executor.py:109-116` op_open_trip
- `sw/ontology.py:257-260` trip_from
- `sw/ontology.py:251-254` trip_data
- `sw/ontology.py:242-244` transition_data
- `sw/ontology.py:263-270` informator_data
- `sw/ontology.py:287-291` tour_data

## 37. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/subl_reader.py:210-224` Reader.build
- `sw/subl_asked.py:33-44` draw
- `sw/subl_asked.py:20-30` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 38. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/subl_asked.py:47-57` mark
- `sw/subl_asked.py:73-80` popup_html
- `sw/subl_asked.py:83-84` escape
- `sw/subl_commands.py:318-320` SightWalkSightListener.is_applicable
- `sw/subl_commands.py:322-324` SightWalkSightListener.on_hover
- `sw/subl_asked.py:87-92` show_popup
- `sw/subl_asked.py:60-62` paint
- `sw/subl_asked.py:65-70` toggle
- `sw/subl_commands.py:330-331` SightWalkToggleSentinelsCommand.run
