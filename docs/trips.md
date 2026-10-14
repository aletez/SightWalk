# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:36-39` plugin_loaded
- `sw/mcp_http.py:140-143` start
- `sw/bridge.py:233-237` load_config
- `sw/mcp_http.py:116-120` start_server
- `sw/mcp_http.py:131-137` settings_changed
- `sw/mcp_http.py:123-128` stop_server
- `sight_walk.py:42-47` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:49-56` close_all
- `sw/mcp_http.py:146-148` stop
- `sw/setup.py:70-72` SightWalkRestartCommand.run

## 2. Setting up the agent bridge (5 views)

The setup command keeps a token, writes it for poke, and puts Claude Code's registration line on the clipboard.

- `sw/setup.py:32-38` SightWalkSetupCommand.run
- `sw/setup.py:41-48` ensure_token
- `sw/setup.py:51-57` write_config
- `sw/setup.py:60-63` show_instructions
- `sw/commands.py:14-21` SightWalkReplaceCommand.run

## 3. A request arrives (11 views)

From the HTTP server's thread to the show operation on Sublime's, with every check on the way.

- `sw/bridge.py:184-200` run_on_main
- `sw/bridge.py:87-95` op_show
- `sw/bridge.py:81-84` check_not_stopped
- `sw/bridge.py:53-65` make_trip
- `sw/ontology.py:125-133` Sight.parse
- `sw/ontology.py:153-157` Trip.__init__
- `sw/ontology.py:89-96` Network.__init__
- `sw/ontology.py:105-115` Network.problem
- `sw/bridge.py:32-46` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:27-29` file_lines

## 4. A new reader window (13 views)

The window and every view but the sights.

- `sw/bridge.py:68-78` new_reader
- `sw/reader.py:58-78` Reader.__init__
- `sw/reader.py:80-118` Reader.make_side_views
- `sw/views.py:170-179` bench_font
- `sw/views.py:182-186` match_font
- `sw/views.py:130-137` make_blank_view
- `sw/views.py:106-113` make_side_view
- `sw/chat.py:69-75` start
- `sw/chat.py:78-87` make_header
- `sw/chat.py:115-124` make_status
- `sw/vetting.py:33-37` make
- `sw/vetting.py:40-46` make_tool
- `sw/state.py:19-22` register

## 5. Loading the sights (13 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/reader.py:122-132` Reader.load
- `sw/chat.py:190-198` catch_up
- `sw/reader.py:176-186` Reader.close_sights
- `sw/reader.py:188-201` Reader.build
- `sw/views.py:148-152` FileCopy.__init__
- `sw/views.py:155-167` make_copy
- `sw/reader.py:203-214` Reader.surround
- `sw/spec.py:74-89` ancestors
- `sw/spec.py:61-62` indent
- `sw/spec.py:65-71` opens_block
- `sw/spec.py:92-99` breathing
- `sw/views.py:191-197` make_header
- `sw/views.py:200-205` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:216-221` Reader.tint
- `sw/tint.py:158-161` apply_tint
- `sw/tint.py:138-144` schemes_for
- `sw/tint.py:20-24` hue_for
- `sw/tint.py:101-123` tinted_schemes
- `sw/tint.py:39-51` load_base_scheme
- `sw/tint.py:31-36` tint_color
- `sw/tint.py:70-75` write_scheme
- `sw/tint.py:147-155` set_schemes
- `sw/tint.py:126-135` when_indexed

## 7. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/reader.py:223-227` Reader.draw_gaps
- `sw/reader.py:39-40` line_count
- `sw/views.py:268-275` draw_gap
- `sw/reader.py:229-241` Reader.make_items
- `sw/views.py:208-209` line_top
- `sw/views.py:212-213` header_top
- `sw/reader.py:243-248` Reader.calibrate
- `sw/reader.py:250-255` Reader.measure_full
- `sw/reader.py:257-261` Reader.measure_half
- `sw/reader.py:263-273` Reader.start
- `sw/reader.py:351-354` Reader.centred_lead
- `sw/plan.py:92-97` lead
- `sw/plan.py:86-89` free_room
- `sw/plan.py:47-63` stack
- `sw/plan.py:66-73` sight_groups
- `sw/reader.py:427-433` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:356-361` Reader.scroll_to
- `sw/plan.py:100-106` offset_range
- `sw/plan.py:76-83` max_offset
- `sw/reader.py:323-332` Reader.render
- `sw/geometry.py:74-98` Geometry.column_rects
- `sw/geometry.py:40-44` Geometry.column
- `sw/geometry.py:104-113` Geometry.sight_cells
- `sw/geometry.py:100-102` Geometry.floor_height
- `sw/reader.py:277-287` Reader.layout
- `sw/views.py:78-101` reader_layout
- `sw/views.py:68-75` to_layout

## 9. Arranging the views (12 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:334-347` Reader.arrange
- `sw/reader.py:297-300` Reader.place
- `sw/reader.py:302-321` Reader.assign_groups
- `sw/views.py:55-58` hide_chrome
- `sw/reader.py:388-399` Reader.scroll_views
- `sw/reader.py:363-374` Reader.places
- `sw/reader.py:421-425` Reader.strip_place
- `sw/views.py:140-142` anchor
- `sw/reader.py:602-609` Reader.draw_strip_buttons
- `sw/reader.py:611-613` Reader.strip_button
- `sw/reader.py:514-517` Reader.draw_edit_buttons
- `sw/views.py:216-226` draw_edit_button

## 10. Polling and the wheel (8 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:440-448` Reader.poll
- `sw/chat.py:174-187` keep_at_bottom
- `sw/reader.py:450-457` Reader.poll_wheel
- `sw/reader.py:437-438` Reader.alive
- `sw/reader.py:401-419` Reader.read_wheel
- `sw/reader.py:376-380` Reader.wheel_places
- `sw/reader.py:382-386` Reader.pinned_places
- `sw/reader.py:51-54` item_top

## 11. Pointing (9 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `sw/bridge.py:110-113` op_point
- `sw/state.py:40-46` require_ready
- `sw/reader.py:473-481` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (9 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:483-496` Reader.draw_gutter
- `sw/reader.py:498-503` Reader.draw_strip_marks
- `sw/marks.py:117-128` strip_icons
- `sw/views.py:243-252` draw_strip_icons
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-114` gutter_icons
- `sw/views.py:231-240` draw_icons
- `sw/reader.py:505-510` Reader.draw_outlines
- `sw/views.py:255-265` draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/bridge.py:98-107` op_say
- `sw/reader.py:734-740` Reader.say
- `sw/reader.py:570-578` Reader.show_headers
- `sw/chat.py:90-109` show_header
- `sw/header.py:12-22` title_lines
- `sw/chat.py:127-137` show_status
- `sw/chat.py:147-154` say
- `sw/commands.py:25-26` SightWalkInsertCommand.run
- `sw/chat.py:49-66` Guard.on_text_changed
- `sw/chat.py:31-39` protected_end
- `sw/commands.py:103-105` SightWalkChatListener.on_modified

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/commands.py:161-164` SightWalkStopAnswerCommand.run
- `sw/reader.py:713-720` Reader.stop_answer
- `sw/reader.py:722-725` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (11 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/reader.py:626-631` Reader.select_tool
- `sw/vetting.py:69-88` show_tabs
- `sw/reader.py:633-635` Reader.panning
- `sw/commands.py:206-209` SightWalkTogglePanningCommand.run
- `sw/reader.py:637-643` Reader.toggle_panning
- `sw/vetting.py:49-56` set_panning
- `sw/vetting.py:59-61` content_point
- `sw/reader.py:617-618` Reader.tools
- `sw/reader.py:620-621` Reader.tool_view
- `sw/reader.py:623-624` Reader.hidden_tools
- `sw/reader.py:678-686` Reader.draw_map

## 16. The Map's nodes (10 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/reader.py:678-686` Reader.draw_map
- `sw/reader.py:688-701` Reader.map_nodes
- `sw/reader.py:703-707` Reader.owner
- `sw/reader.py:43-48` defined_name
- `sw/callmap.py:32-38` first_definition
- `sw/callmap.py:41-48` node_at
- `sw/callmap.py:27-29` Node.__init__
- `sw/callmap.py:51-58` edges
- `sw/callmap.py:41-48` node_at
- `sw/vetting.py:100-107` draw_map

## 17. Drawing the Map (14 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/vetting.py:100-107` draw_map
- `sw/vetting.py:93-97` find_dot
- `sw/callmap.py:105-118` dot_source
- `sw/callmap.py:80-86` file_block
- `sw/callmap.py:69-72` cluster
- `sw/callmap.py:75-77` node_line
- `sw/callmap.py:61-62` node_id
- `sw/callmap.py:65-66` quote
- `sw/callmap.py:89-91` arrow
- `sw/callmap.py:94-102` legend
- `sw/vetting.py:110-122` render
- `sw/vetting.py:125-127` png_size
- `sw/vetting.py:130-138` show_image
- `sw/vetting.py:141-144` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with the focus, the visible sights and the edits, and the agent receives it.

- `sw/commands.py:38-42` SightWalkSendCommand.run
- `sw/chat.py:157-171` take_draft
- `sw/commands.py:29-32` send
- `sw/state.py:32-33` reader_for
- `sw/reader.py:742-756` Reader.context
- `sw/views.py:278-282` selected_text
- `sw/plan.py:109-112` visible_specs
- `sw/reader.py:563-566` Reader.take_edits
- `sw/bridge.py:214-228` wait_for_user

## 19. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:58-65` SightWalkEditCommand.run
- `sw/reader.py:531-536` Reader.sight_of
- `sw/reader.py:519-529` Reader.open_editor
- `sw/editor.py:22-30` Editor.__init__
- `sw/views.py:61-65` wait_until_loaded
- `sw/editor.py:14-18` open_live
- `sw/editor.py:32-37` Editor.start
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/geometry.py:64-72` Geometry.editor_geometry

## 20. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:71-74` SightWalkCloseEditorCommand.run
- `sw/reader.py:538-539` Reader.close_editor
- `sw/editor.py:74-85` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:541-554` Reader.editor_closed
- `sw/reader.py:556-561` Reader.move_range

## 21. Window events (13 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:459-469` Reader.follow_resize
- `sw/reader.py:289-295` Reader.keep_bench_width
- `sw/geometry.py:18-25` Geometry.spans
- `sw/geometry.py:27-31` Geometry.strip_span
- `sw/geometry.py:33-35` Geometry.strip_share
- `sw/geometry.py:37-38` Geometry.bench_side
- `sw/state.py:59-63` render_all
- `sw/bridge.py:153-160` op_settings
- `sw/bridge.py:143-150` check_setting
- `sw/commands.py:109-111` SightWalkWindowListener.on_activated
- `sw/commands.py:88-92` SightWalkScrollCommand.run
- `sw/commands.py:82-84` SightWalkHeaderListener.on_hover
- `sw/chat.py:140-144` show_help

## 22. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:227-238` SightWalkToggleGuideCommand.run
- `sw/reader.py:580-590` Reader.toggle_focus
- `sw/commands.py:240-245` SightWalkToggleGuideCommand.folder
- `sw/reader.py:134-138` Reader.open_empty
- `sw/reader.py:140-157` Reader.empty_layout
- `sw/reader.py:159-164` Reader.close_hijacker
- `sw/commands.py:135-139` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:113-114` SightWalkWindowListener.on_load
- `sw/reader.py:166-174` Reader.take_file
- `sw/bridge.py:129-140` op_browse
- `sw/views.py:116-127` make_browser

## 23. One tool call over HTTP (13 views)

From the request to the reply: the token checked, the JSON-RPC message answered, the tool run on Sublime's thread.

- `sw/mcp_http.py:92-103` Handler.do_POST
- `sw/mcp_http.py:76-79` Handler.authorized
- `sw/mcp_http.py:63-72` reply
- `sw/mcp_http.py:48-60` answer
- `sw/manual.py:100-103` tool
- `sw/mcp_http.py:36-45` tool_result
- `sw/mcp_http.py:23-33` call_tool
- `sw/bridge.py:203-211` wait_until_ready
- `sw/bridge.py:184-200` run_on_main
- `sw/mcp_http.py:81-90` Handler.send
- `sw/mcp_http.py:105-106` Handler.do_GET
- `sw/mcp_http.py:108-110` Handler.do_DELETE
- `sw/mcp_http.py:112-113` Handler.log_message

## 24. How Claude comes to listen to Sublime (7 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:92-97` await_answer
- `sw/guide.py:48-58` ensure
- `sw/guide.py:31-33` listening
- `sw/guide.py:36-37` running
- `sw/guide.py:40-45` find_claude
- `sw/guide.py:61-70` start
- `sw/bridge.py:214-228` wait_for_user

## 25. Here, and asking by a shortcut (3 views)

The caret or a selection in a sight becomes here; a shortcut sends a question, like "Explain next.", as a message.

- `sw/commands.py:123-133` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:592-595` Reader.note_selection
- `sw/commands.py:48-52` SightWalkAskCommand.run

## 26. Endings (13 views, survey)

The guide is stopped, windows close.

- `sw/commands.py:215-216` SightWalkStopGuideCommand.run
- `sw/commands.py:218-219` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:85-89` stop
- `sw/guide.py:73-82` stop_when_idle
- `sw/commands.py:141-142` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:116-121` SightWalkWindowListener.on_window_command
- `sw/commands.py:168-170` SightWalkCloseTripCommand.run
- `sw/commands.py:148-151` SightWalkResetSightsCommand.run
- `sw/reader.py:597-600` Reader.reset_sights
- `sw/commands.py:153-155` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:25-29` forget
- `sw/bridge.py:121-126` op_close
- `sw/state.py:36-37` current_reader

## 27. Names and room (11 views, survey)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-50` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:53-58` matches
- `sw/geometry.py:12-16` Geometry.share
- `sw/geometry.py:46-54` Geometry.conversation_rows
- `sw/geometry.py:56-58` Geometry.head
- `sw/geometry.py:60-62` Geometry.room
- `sw/bridge.py:116-118` op_state
- `sw/reader.py:727-732` Reader.folder
- `sw/reader.py:709-711` Reader.note_waiting

## 28. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-14` Item.__init__
- `sw/plan.py:21-32` Pane.__init__
- `sw/plan.py:34-36` Pane.spec
- `sw/plan.py:38-40` Pane.items
- `sw/plan.py:42-44` Pane.all_views
- `sw/views.py:37-38` kept
- `sw/views.py:41-46` phantoms
- `sw/views.py:49-50` forget
- `sw/chat.py:45-47` Guard.__init__
- `sw/commands.py:78-80` SightWalkHeaderListener.is_applicable
- `sw/commands.py:99-101` SightWalkChatListener.is_applicable

## 29. Settings and the rest of the colours (7 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/commands.py:94-95` SightWalkScrollCommand.is_enabled
- `sw/tint.py:78-80` band_amount
- `sw/tint.py:57-67` from_tm_theme
- `sw/tint.py:90-98` resolved_scheme
- `sw/tint.py:83-87` scheme_stem
- `sw/tint.py:27-28` hex_rgb
- `sw/tint.py:164-169` apply_grey

## 30. The ontology: collections and sights (15 views, survey)

Members without order, sequences one can walk, places as paths into them, and the sight.

- `sw/ontology.py:21-22` Collection.__init__
- `sw/ontology.py:24-26` Collection.member
- `sw/ontology.py:28-29` Collection.has_place
- `sw/ontology.py:31-43` Collection.place_problem
- `sw/ontology.py:45-47` Collection.label
- `sw/ontology.py:49-50` Collection.member_label
- `sw/ontology.py:142-143` Sight.label
- `sw/ontology.py:145-146` Sight.member_label
- `sw/ontology.py:57-58` Sequence.__iter__
- `sw/ontology.py:60-61` Sequence.__len__
- `sw/ontology.py:63-65` Sequence.member
- `sw/ontology.py:121-123` Sight.__init__
- `sw/ontology.py:125-133` Sight.parse
- `sw/ontology.py:135-137` Sight.spec
- `sw/ontology.py:139-140` Sight.member

## 31. The ontology: networks (16 views, survey)

Transitions between places, checked; the trip, the informator and the holiday.

- `sw/ontology.py:89-96` Network.__init__
- `sw/ontology.py:12-14` slug
- `sw/ontology.py:98-103` Network.add
- `sw/ontology.py:105-115` Network.problem
- `sw/ontology.py:72-73` Transition.__init__
- `sw/ontology.py:75-76` Transition.__eq__
- `sw/ontology.py:78-79` Transition.__repr__
- `sw/ontology.py:81-82` Transition.parts
- `sw/ontology.py:153-157` Trip.__init__
- `sw/ontology.py:159-160` Trip.label
- `sw/ontology.py:162-163` Trip.member_label
- `sw/ontology.py:165-170` Trip.moved
- `sw/ontology.py:177-178` Informator.member
- `sw/ontology.py:180-181` Informator.label
- `sw/ontology.py:183-184` Informator.member_label
- `sw/ontology.py:190-195` Holiday.__init__

## 32. An informator and its holiday (14 views)

Open Informator: the informator read from its files, its trips laid out in one order, the Holiday tab drawn, a trip opened from it and ticked as walked.

- `sw/commands.py:177-182` SightWalkOpenInformatorCommand.run
- `sw/commands.py:191-200` informator_files
- `sw/commands.py:184-188` SightWalkOpenInformatorCommand.open
- `sw/reader.py:647-661` Reader.open_informator
- `sw/ontology.py:256-260` informator_from
- `sw/ontology.py:243-246` trip_from
- `sw/ontology.py:233-234` transition_from
- `sw/ontology.py:198-211` holiday
- `sw/ontology.py:214-222` visit
- `sw/vetting.py:168-174` read_walked
- `sw/reader.py:663-672` Reader.holiday_link
- `sw/vetting.py:177-186` save_walked
- `sw/reader.py:674-676` Reader.draw_holiday
- `sw/vetting.py:149-165` show_holiday

## 33. Trip files (5 views)

A trip opened from its file by the guide, and the files written for an informator.

- `sw/bridge.py:163-177` op_open_trip
- `sw/ontology.py:243-246` trip_from
- `sw/ontology.py:237-240` trip_data
- `sw/ontology.py:228-230` transition_data
- `sw/ontology.py:249-253` informator_data

## 34. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:188-201` Reader.build
- `sw/asked.py:32-43` draw
- `sw/asked.py:19-29` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 35. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/asked.py:46-56` mark
- `sw/asked.py:72-79` popup_html
- `sw/asked.py:82-83` escape
- `sw/commands.py:251-253` SightWalkSightListener.is_applicable
- `sw/commands.py:255-257` SightWalkSightListener.on_hover
- `sw/asked.py:86-91` show_popup
- `sw/asked.py:59-61` paint
- `sw/asked.py:64-69` toggle
- `sw/commands.py:263-264` SightWalkToggleSentinelsCommand.run
