# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:37-41` plugin_loaded
- `sw/mcp_http.py:140-143` start
- `sw/bridge.py:233-237` load_config
- `sw/mcp_http.py:116-120` start_server
- `sw/mcp_http.py:131-137` settings_changed
- `sw/mcp_http.py:123-128` stop_server
- `sight_walk.py:50-55` plugin_unloaded
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
- `sw/commands.py:17-24` SightWalkReplaceCommand.run

## 3. A request arrives (11 views)

From the HTTP server's thread to the show operation on Sublime's, with every check on the way.

- `sw/bridge.py:184-200` run_on_main
- `sw/bridge.py:87-95` op_show
- `sw/bridge.py:81-84` check_not_stopped
- `sw/bridge.py:53-65` make_trip
- `sw/ontology.py:126-134` Sight.parse
- `sw/ontology.py:154-158` Trip.__init__
- `sw/ontology.py:90-97` Network.__init__
- `sw/ontology.py:106-116` Network.problem
- `sw/bridge.py:32-46` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:27-29` file_lines

## 4. A new reader window (13 views)

The window and every view but the sights.

- `sw/bridge.py:68-78` new_reader
- `sw/reader.py:59-80` Reader.__init__
- `sw/reader.py:82-121` Reader.make_side_views
- `sw/views.py:175-184` bench_font
- `sw/views.py:187-191` match_font
- `sw/views.py:135-142` make_blank_view
- `sw/views.py:111-118` make_side_view
- `sw/chat.py:72-78` start
- `sw/chat.py:81-90` make_header
- `sw/chat.py:118-127` make_status
- `sw/vetting.py:29-33` make
- `sw/vetting.py:36-42` make_tool
- `sw/state.py:19-22` register

## 5. Loading the sights (13 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/reader.py:125-135` Reader.load
- `sw/chat.py:200-208` catch_up
- `sw/reader.py:179-189` Reader.close_sights
- `sw/reader.py:191-204` Reader.build
- `sw/views.py:153-157` FileCopy.__init__
- `sw/views.py:160-172` make_copy
- `sw/reader.py:206-217` Reader.surround
- `sw/spec.py:74-89` ancestors
- `sw/spec.py:61-62` indent
- `sw/spec.py:65-71` opens_block
- `sw/spec.py:92-99` breathing
- `sw/views.py:196-202` make_header
- `sw/views.py:205-210` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:219-224` Reader.tint
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

- `sw/reader.py:226-230` Reader.draw_gaps
- `sw/reader.py:40-41` line_count
- `sw/views.py:275-282` draw_gap
- `sw/reader.py:232-244` Reader.make_items
- `sw/views.py:213-214` line_top
- `sw/views.py:217-218` header_top
- `sw/reader.py:246-251` Reader.calibrate
- `sw/reader.py:253-258` Reader.measure_full
- `sw/reader.py:260-264` Reader.measure_half
- `sw/reader.py:266-276` Reader.start
- `sw/reader.py:370-373` Reader.centred_lead
- `sw/plan.py:92-97` lead
- `sw/plan.py:86-89` free_room
- `sw/plan.py:47-63` stack
- `sw/plan.py:66-73` sight_groups
- `sw/reader.py:448-454` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:375-380` Reader.scroll_to
- `sw/plan.py:100-106` offset_range
- `sw/plan.py:76-83` max_offset
- `sw/reader.py:341-351` Reader.render
- `sw/geometry.py:74-100` Geometry.column_rects
- `sw/geometry.py:40-44` Geometry.column
- `sw/geometry.py:106-117` Geometry.sight_cells
- `sw/geometry.py:102-104` Geometry.floor_height
- `sw/reader.py:280-287` Reader.layout
- `sw/views.py:83-106` reader_layout
- `sw/views.py:73-80` to_layout

## 9. Arranging the views (13 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:353-366` Reader.arrange
- `sw/reader.py:311-316` Reader.place
- `sw/reader.py:289-300` Reader.strip_in_front
- `sw/reader.py:318-339` Reader.assign_groups
- `sw/views.py:60-63` hide_chrome
- `sw/reader.py:409-420` Reader.scroll_views
- `sw/reader.py:382-395` Reader.places
- `sw/reader.py:442-446` Reader.strip_place
- `sw/views.py:145-147` anchor
- `sw/reader.py:624-631` Reader.draw_strip_buttons
- `sw/reader.py:633-635` Reader.strip_button
- `sw/reader.py:535-538` Reader.draw_edit_buttons
- `sw/views.py:221-233` draw_edit_button

## 10. Polling and the wheel (9 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:461-469` Reader.poll
- `sw/chat.py:176-185` keep_at_bottom
- `sw/chat.py:188-191` bottom_place
- `sw/reader.py:471-478` Reader.poll_wheel
- `sw/reader.py:458-459` Reader.alive
- `sw/reader.py:422-440` Reader.read_wheel
- `sw/reader.py:397-401` Reader.wheel_places
- `sw/reader.py:403-407` Reader.pinned_places
- `sw/reader.py:52-55` item_top

## 11. Pointing (9 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `sw/bridge.py:110-113` op_point
- `sw/state.py:40-46` require_ready
- `sw/reader.py:494-502` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (9 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:504-517` Reader.draw_gutter
- `sw/reader.py:519-524` Reader.draw_strip_marks
- `sw/marks.py:117-128` strip_icons
- `sw/views.py:250-259` draw_strip_icons
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-114` gutter_icons
- `sw/views.py:238-247` draw_icons
- `sw/reader.py:526-531` Reader.draw_outlines
- `sw/views.py:262-272` draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/bridge.py:98-107` op_say
- `sw/reader.py:770-777` Reader.say
- `sw/reader.py:591-600` Reader.show_headers
- `sw/chat.py:93-112` show_header
- `sw/header.py:12-22` title_lines
- `sw/chat.py:130-139` show_status
- `sw/chat.py:149-156` say
- `sw/commands.py:28-29` SightWalkInsertCommand.run
- `sw/chat.py:52-69` Guard.on_text_changed
- `sw/chat.py:34-42` protected_end
- `sw/commands.py:107-109` SightWalkChatListener.on_modified

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/commands.py:165-168` SightWalkStopAnswerCommand.run
- `sw/reader.py:749-756` Reader.stop_answer
- `sw/reader.py:758-761` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (11 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/reader.py:648-653` Reader.select_tool
- `sw/vetting.py:64-83` show_tabs
- `sw/reader.py:655-657` Reader.panning
- `sw/commands.py:250-253` SightWalkTogglePanningCommand.run
- `sw/reader.py:659-666` Reader.toggle_panning
- `sw/vetting.py:45-52` set_panning
- `sw/vetting.py:55-57` content_point
- `sw/reader.py:639-640` Reader.tools
- `sw/reader.py:642-643` Reader.tool_view
- `sw/reader.py:645-646` Reader.hidden_tools
- `sw/reader.py:714-722` Reader.draw_map

## 16. The Map's nodes (10 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/reader.py:714-722` Reader.draw_map
- `sw/reader.py:724-737` Reader.map_nodes
- `sw/reader.py:739-743` Reader.owner
- `sw/reader.py:44-49` defined_name
- `sw/callmap.py:32-38` first_definition
- `sw/callmap.py:41-48` node_at
- `sw/callmap.py:27-29` Node.__init__
- `sw/callmap.py:51-58` edges
- `sw/callmap.py:41-48` node_at
- `sw/vetting.py:95-102` draw_map

## 17. Drawing the Map (14 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/vetting.py:95-102` draw_map
- `sw/vetting.py:88-92` find_dot
- `sw/callmap.py:105-118` dot_source
- `sw/callmap.py:80-86` file_block
- `sw/callmap.py:69-72` cluster
- `sw/callmap.py:75-77` node_line
- `sw/callmap.py:61-62` node_id
- `sw/callmap.py:65-66` quote
- `sw/callmap.py:89-91` arrow
- `sw/callmap.py:94-102` legend
- `sw/vetting.py:105-117` render
- `sw/vetting.py:120-122` png_size
- `sw/vetting.py:125-133` show_image
- `sw/vetting.py:136-139` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with the focus, the visible sights and the edits, and the agent receives it.

- `sw/commands.py:42-46` SightWalkSendCommand.run
- `sw/chat.py:159-173` take_draft
- `sw/commands.py:32-36` send
- `sw/state.py:32-33` reader_for
- `sw/reader.py:779-793` Reader.context
- `sw/views.py:285-289` selected_text
- `sw/plan.py:109-112` visible_specs
- `sw/reader.py:584-587` Reader.take_edits
- `sw/bridge.py:214-228` wait_for_user

## 19. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:62-69` SightWalkEditCommand.run
- `sw/reader.py:552-557` Reader.sight_of
- `sw/reader.py:540-550` Reader.open_editor
- `sw/editor.py:22-30` Editor.__init__
- `sw/views.py:66-70` wait_until_loaded
- `sw/editor.py:14-18` open_live
- `sw/editor.py:32-37` Editor.start
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/geometry.py:64-72` Geometry.editor_geometry

## 20. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:75-78` SightWalkCloseEditorCommand.run
- `sw/reader.py:559-560` Reader.close_editor
- `sw/editor.py:74-85` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:562-575` Reader.editor_closed
- `sw/reader.py:577-582` Reader.move_range

## 21. Window events (13 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:480-490` Reader.follow_resize
- `sw/reader.py:302-309` Reader.keep_bench_width
- `sw/geometry.py:18-25` Geometry.spans
- `sw/geometry.py:27-31` Geometry.strip_span
- `sw/geometry.py:33-35` Geometry.strip_share
- `sw/geometry.py:37-38` Geometry.bench_side
- `sw/state.py:59-64` render_all
- `sw/bridge.py:153-160` op_settings
- `sw/bridge.py:143-150` check_setting
- `sw/commands.py:113-115` SightWalkWindowListener.on_activated
- `sw/commands.py:92-96` SightWalkScrollCommand.run
- `sw/commands.py:86-88` SightWalkHeaderListener.on_hover
- `sw/chat.py:142-146` show_help

## 22. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:271-282` SightWalkToggleGuideCommand.run
- `sw/reader.py:602-612` Reader.toggle_focus
- `sw/commands.py:284-289` SightWalkToggleGuideCommand.folder
- `sw/reader.py:137-141` Reader.open_empty
- `sw/reader.py:143-160` Reader.empty_layout
- `sw/reader.py:162-167` Reader.close_hijacker
- `sw/commands.py:139-143` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:117-118` SightWalkWindowListener.on_load
- `sw/reader.py:169-177` Reader.take_file
- `sw/bridge.py:129-140` op_browse
- `sw/views.py:121-132` make_browser

## 23. What the agent is told (11 views, survey)

The guide's manual, the tools' descriptions and schemas it gets at its start, and the prompt a guide started from Sublime is given.

- `sw/manual.py:4-17` MANUAL: opening
- `sw/manual.py:19-40` MANUAL: Showing code
- `sw/manual.py:42-45` MANUAL: Writing code that fits the reader
- `sw/manual.py:47-78` MANUAL: Conversation
- `sw/manual.py:80-97` MANUAL: Indicators
- `sw/manual.py:100-103` tool
- `sw/manual.py:106-110` TRANSITION
- `sw/manual.py:112-150` TOOLS
- `sw/bridge.py:49-50` TRANSITION_FORM
- `sw/guide.py:19-24` PROMPT
- `sw/guide.py:25-25` TOOLS

## 24. One tool call over HTTP (13 views)

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

## 25. How Claude comes to listen to Sublime (7 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:90-95` await_answer
- `sw/guide.py:47-56` ensure
- `sw/guide.py:30-32` listening
- `sw/guide.py:35-36` running
- `sw/guide.py:39-44` find_claude
- `sw/guide.py:59-68` start
- `sw/bridge.py:214-228` wait_for_user

## 26. Here, and asking by a shortcut (3 views)

The caret or a selection in a sight becomes here; a shortcut sends a question, like "Explain next.", as a message.

- `sw/commands.py:127-137` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:614-617` Reader.note_selection
- `sw/commands.py:52-56` SightWalkAskCommand.run

## 27. Words in two languages (7 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/commands.py:241-244` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:44-47` settings_changed
- `sw/words.py:57-59` set_language
- `sw/state.py:59-64` render_all
- `sw/words.py:53-54` word
- `sw/chat.py:27-31` help_html
- `sw/views.py:30-32` button_html

## 28. Endings (13 views, survey)

The guide is stopped, windows close.

- `sw/commands.py:259-260` SightWalkStopGuideCommand.run
- `sw/commands.py:262-263` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:83-87` stop
- `sw/guide.py:71-80` stop_when_idle
- `sw/commands.py:145-146` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:120-125` SightWalkWindowListener.on_window_command
- `sw/commands.py:172-174` SightWalkCloseTripCommand.run
- `sw/commands.py:152-155` SightWalkResetSightsCommand.run
- `sw/reader.py:619-622` Reader.reset_sights
- `sw/commands.py:157-159` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:25-29` forget
- `sw/bridge.py:121-126` op_close
- `sw/state.py:36-37` current_reader

## 29. Names and room (11 views, survey)

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
- `sw/reader.py:763-768` Reader.folder
- `sw/reader.py:745-747` Reader.note_waiting

## 30. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-14` Item.__init__
- `sw/plan.py:21-32` Pane.__init__
- `sw/plan.py:34-36` Pane.spec
- `sw/plan.py:38-40` Pane.items
- `sw/plan.py:42-44` Pane.all_views
- `sw/views.py:42-43` kept
- `sw/views.py:46-51` phantoms
- `sw/views.py:54-55` forget
- `sw/chat.py:48-50` Guard.__init__
- `sw/commands.py:82-84` SightWalkHeaderListener.is_applicable
- `sw/commands.py:103-105` SightWalkChatListener.is_applicable

## 31. Settings and the rest of the colours (7 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/commands.py:98-99` SightWalkScrollCommand.is_enabled
- `sw/tint.py:78-80` band_amount
- `sw/tint.py:57-67` from_tm_theme
- `sw/tint.py:90-98` resolved_scheme
- `sw/tint.py:83-87` scheme_stem
- `sw/tint.py:27-28` hex_rgb
- `sw/tint.py:164-169` apply_grey

## 32. The ontology: collections and sights (15 views, survey)

Members without order, sequences one can walk, places as paths into them, and the sight.

- `sw/ontology.py:22-23` Collection.__init__
- `sw/ontology.py:25-27` Collection.member
- `sw/ontology.py:29-30` Collection.has_place
- `sw/ontology.py:32-44` Collection.place_problem
- `sw/ontology.py:46-48` Collection.label
- `sw/ontology.py:50-51` Collection.member_label
- `sw/ontology.py:143-144` Sight.label
- `sw/ontology.py:146-147` Sight.member_label
- `sw/ontology.py:58-59` Sequence.__iter__
- `sw/ontology.py:61-62` Sequence.__len__
- `sw/ontology.py:64-66` Sequence.member
- `sw/ontology.py:122-124` Sight.__init__
- `sw/ontology.py:126-134` Sight.parse
- `sw/ontology.py:136-138` Sight.spec
- `sw/ontology.py:140-141` Sight.member

## 33. The ontology: networks (17 views, survey)

Transitions between places, checked; the trip, the informator and the tour.

- `sw/ontology.py:90-97` Network.__init__
- `sw/ontology.py:13-15` slug
- `sw/ontology.py:99-104` Network.add
- `sw/ontology.py:106-116` Network.problem
- `sw/ontology.py:73-74` Transition.__init__
- `sw/ontology.py:76-77` Transition.__eq__
- `sw/ontology.py:79-80` Transition.__repr__
- `sw/ontology.py:82-83` Transition.parts
- `sw/ontology.py:154-158` Trip.__init__
- `sw/ontology.py:160-161` Trip.label
- `sw/ontology.py:163-164` Trip.member_label
- `sw/ontology.py:166-171` Trip.moved
- `sw/ontology.py:179-181` Informator.__init__
- `sw/ontology.py:183-184` Informator.member
- `sw/ontology.py:186-187` Informator.label
- `sw/ontology.py:189-190` Informator.member_label
- `sw/ontology.py:197-203` Tour.__init__

## 34. An informator and its tour (25 views)

Open Tour: an informator's tours to choose from, the informator read from its files, its trips in the tour's order in the Tour tab, a trip opened from it, its conversation kept, a box ticked by hand.

- `sw/commands.py:182-188` SightWalkOpenTourCommand.run
- `sw/commands.py:197-210` tour_choices
- `sw/commands.py:213-223` found_files
- `sw/commands.py:226-227` read_name
- `sw/commands.py:230-235` read_field
- `sw/commands.py:190-194` SightWalkOpenTourCommand.open
- `sw/words.py:62-69` trips_count
- `sw/reader.py:670-684` Reader.open_tour
- `sw/reader.py:809-811` read_json
- `sw/ontology.py:288-294` tour_from
- `sw/ontology.py:267-271` informator_from
- `sw/ontology.py:251-254` trip_from
- `sw/ontology.py:241-242` transition_from
- `sw/ontology.py:206-219` tour
- `sw/ontology.py:222-230` visit
- `sw/vetting.py:163-169` read_walked
- `sw/reader.py:686-698` Reader.tour_link
- `sw/reader.py:700-708` Reader.keep_transcript
- `sw/reader.py:796-798` transcripts_path
- `sw/reader.py:801-806` read_transcripts
- `sw/chat.py:194-197` set_transcript
- `sw/ontology.py:274-278` dumps
- `sw/vetting.py:172-181` save_walked
- `sw/reader.py:710-712` Reader.draw_tour
- `sw/vetting.py:144-160` show_tour

## 35. Trip files (6 views)

A trip opened from its file by the guide, and the files written for an informator.

- `sw/bridge.py:163-177` op_open_trip
- `sw/ontology.py:251-254` trip_from
- `sw/ontology.py:245-248` trip_data
- `sw/ontology.py:236-238` transition_data
- `sw/ontology.py:257-264` informator_data
- `sw/ontology.py:281-285` tour_data

## 36. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:191-204` Reader.build
- `sw/asked.py:33-44` draw
- `sw/asked.py:20-30` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 37. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/asked.py:47-57` mark
- `sw/asked.py:73-80` popup_html
- `sw/asked.py:83-84` escape
- `sw/commands.py:295-297` SightWalkSightListener.is_applicable
- `sw/commands.py:299-301` SightWalkSightListener.on_hover
- `sw/asked.py:87-92` show_popup
- `sw/asked.py:60-62` paint
- `sw/asked.py:65-70` toggle
- `sw/commands.py:307-308` SightWalkToggleSentinelsCommand.run
