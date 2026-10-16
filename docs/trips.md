# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:39-45` plugin_loaded
- `sw/mcp_http.py:140-143` start
- `sw/bridge.py:259-263` load_config
- `sw/mcp_http.py:116-120` start_server
- `sw/mcp_http.py:131-137` settings_changed
- `sw/mcp_http.py:123-128` stop_server
- `sight_walk.py:54-59` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:53-60` close_all
- `sw/mcp_http.py:146-148` stop
- `sw/setup.py:70-72` SightWalkRestartCommand.run

## 2. Setting up the agent bridge (5 views)

The setup command keeps a token, writes it for poke, and puts Claude Code's registration line on the clipboard.

- `sw/setup.py:32-38` SightWalkSetupCommand.run
- `sw/setup.py:41-48` ensure_token
- `sw/setup.py:51-57` write_config
- `sw/setup.py:60-63` show_instructions
- `sw/commands.py:17-24` SightWalkReplaceCommand.run

## 3. A request arrives (12 views)

From the HTTP server's thread to the show operation on Sublime's, with every check on the way.

- `sw/bridge.py:208-224` run_on_main
- `sw/bridge.py:88-96` op_show
- `sw/bridge.py:99-101` named
- `sw/bridge.py:82-85` check_not_stopped
- `sw/bridge.py:54-66` make_trip
- `sw/ontology.py:126-134` Sight.parse
- `sw/ontology.py:154-158` Trip.__init__
- `sw/ontology.py:90-97` Network.__init__
- `sw/ontology.py:106-116` Network.problem
- `sw/bridge.py:33-47` check_sights
- `sw/spec.py:10-23` parse_spec
- `sw/bridge.py:28-30` file_lines

## 4. A new reader window (12 views)

The window and every view but the sights.

- `sw/bridge.py:69-79` new_reader
- `sw/reader.py:63-84` Reader.__init__
- `sw/reader.py:86-126` Reader.make_side_views
- `sw/views.py:176-185` bench_font
- `sw/views.py:188-192` match_font
- `sw/views.py:136-143` make_blank_view
- `sw/views.py:112-119` make_side_view
- `sw/chat.py:73-79` start
- `sw/chat.py:82-91` make_header
- `sw/chat.py:119-128` make_status
- `sw/vetting.py:26-33` make_tool
- `sw/state.py:23-26` register

## 5. Loading the sights (13 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/reader.py:130-140` Reader.load
- `sw/chat.py:208-216` catch_up
- `sw/reader.py:186-196` Reader.close_sights
- `sw/reader.py:198-212` Reader.build
- `sw/views.py:154-158` FileCopy.__init__
- `sw/views.py:161-173` make_copy
- `sw/reader.py:214-227` Reader.surround
- `sw/spec.py:97-112` ancestors
- `sw/spec.py:84-85` indent
- `sw/spec.py:88-94` opens_block
- `sw/spec.py:131-138` breathing
- `sw/views.py:197-203` make_header
- `sw/views.py:206-211` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:264-269` Reader.tint
- `sw/tint.py:169-172` apply_tint
- `sw/tint.py:149-155` schemes_for
- `sw/tint.py:22-26` hue_for
- `sw/tint.py:107-134` tinted_schemes
- `sw/tint.py:41-53` load_base_scheme
- `sw/tint.py:33-38` tint_color
- `sw/tint.py:76-81` write_scheme
- `sw/tint.py:158-166` set_schemes
- `sw/tint.py:137-146` when_indexed

## 7. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/reader.py:271-275` Reader.draw_gaps
- `sw/reader.py:44-45` line_count
- `sw/views.py:297-304` draw_gap
- `sw/reader.py:290-305` Reader.make_items
- `sw/views.py:214-215` line_top
- `sw/views.py:218-219` header_top
- `sw/reader.py:317-322` Reader.calibrate
- `sw/reader.py:324-329` Reader.measure_full
- `sw/reader.py:331-335` Reader.measure_half
- `sw/reader.py:337-348` Reader.start
- `sw/reader.py:452-455` Reader.centred_lead
- `sw/plan.py:85-90` lead
- `sw/plan.py:79-82` free_room
- `sw/plan.py:50-66` stack
- `sw/plan.py:69-76` sight_groups
- `sw/reader.py:536-542` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:457-463` Reader.scroll_to
- `sw/plan.py:93-101` offset_range
- `sw/geometry.py:60-63` Geometry.bench_floor
- `sw/reader.py:418-428` Reader.render
- `sw/geometry.py:79-110` Geometry.column_rects
- `sw/geometry.py:40-44` Geometry.column
- `sw/geometry.py:127-138` Geometry.sight_cells
- `sw/geometry.py:123-125` Geometry.floor_height
- `sw/reader.py:352-359` Reader.layout
- `sw/views.py:84-107` reader_layout
- `sw/views.py:74-81` to_layout

## 9. Arranging the views (16 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:430-448` Reader.arrange
- `sw/reader.py:387-392` Reader.place
- `sw/reader.py:361-376` Reader.strip_in_front
- `sw/geometry.py:112-121` Geometry.strip_rows
- `sw/reader.py:277-288` Reader.clone
- `sw/reader.py:394-416` Reader.assign_groups
- `sw/views.py:61-64` hide_chrome
- `sw/reader.py:495-506` Reader.scroll_views
- `sw/reader.py:465-473` Reader.places
- `sw/reader.py:530-534` Reader.strip_place
- `sw/views.py:146-148` anchor
- `sw/reader.py:721-728` Reader.draw_strip_buttons
- `sw/reader.py:730-732` Reader.strip_button
- `sw/reader.py:632-635` Reader.draw_edit_buttons
- `sw/reader.py:627-630` Reader.title
- `sw/views.py:222-234` draw_edit_button

## 10. Polling and the wheel (10 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:549-557` Reader.poll
- `sw/chat.py:177-187` keep_at_bottom
- `sw/chat.py:196-199` bottom_place
- `sw/chat.py:190-193` kept_place
- `sw/reader.py:559-566` Reader.poll_wheel
- `sw/reader.py:546-547` Reader.alive
- `sw/reader.py:508-528` Reader.read_wheel
- `sw/reader.py:475-487` Reader.wheel_places
- `sw/reader.py:489-493` Reader.pinned_places
- `sw/reader.py:56-59` item_top

## 11. Pointing (15 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `sw/bridge.py:133-137` op_point
- `sw/state.py:44-50` require_ready
- `sw/reader.py:582-591` Reader.point
- `sw/marks.py:91-107` resolve_marks
- `sw/marks.py:80-88` jump
- `sw/marks.py:18-37` resolve_target
- `sw/marks.py:46-53` sight_target
- `sw/marks.py:56-62` icon_for
- `sw/marks.py:14-15` line_y
- `sw/chat.py:219-234` outline_refs
- `sw/marks.py:178-187` icon_refs
- `sw/marks.py:172-175` sight_refs
- `sw/marks.py:40-43` sight_number
- `sw/spec.py:58-64` sight_index
- `sw/spec.py:50-55` sight_name

## 12. Drawing the marks (10 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:593-606` Reader.draw_gutter
- `sw/reader.py:608-613` Reader.draw_strip_marks
- `sw/marks.py:143-154` strip_icons
- `sw/views.py:251-260` draw_strip_icons
- `sw/marks.py:110-122` visible_lines
- `sw/marks.py:125-140` gutter_icons
- `sw/views.py:239-248` draw_icons
- `sw/reader.py:615-623` Reader.draw_outlines
- `sw/marks.py:71-77` icon_colour
- `sw/views.py:266-279` draw_outlines

## 13. The agent says something (19 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/bridge.py:114-130` op_say
- `sw/marks.py:197-212` untag
- `sw/marks.py:226-228` line_refs
- `sw/bridge.py:104-107` MARK_FIRST
- `sw/marks.py:160-162` speaks_of_code
- `sw/marks.py:157-157` CODE_TALK
- `sw/reader.py:866-874` Reader.say
- `sw/reader.py:688-697` Reader.show_headers
- `sw/chat.py:94-113` show_header
- `sw/header.py:12-22` title_lines
- `sw/chat.py:131-140` show_status
- `sw/chat.py:150-157` say
- `sw/commands.py:28-29` SightWalkInsertCommand.run
- `sw/chat.py:53-70` Guard.on_text_changed
- `sw/chat.py:35-43` protected_end
- `sw/commands.py:110-113` SightWalkChatListener.on_modified
- `sw/commands.py:115-119` SightWalkChatListener.on_post_text_command
- `sw/marks.py:215-217` clean
- `sw/chat.py:237-242` shade_variables

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/commands.py:181-184` SightWalkStopAnswerCommand.run
- `sw/reader.py:845-852` Reader.stop_answer
- `sw/reader.py:854-857` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (10 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/reader.py:745-750` Reader.select_tool
- `sw/vetting.py:56-75` show_tabs
- `sw/commands.py:273-276` SightWalkTogglePanningCommand.run
- `sw/reader.py:752-762` Reader.toggle_panning
- `sw/vetting.py:36-44` set_panning
- `sw/vetting.py:47-49` content_point
- `sw/reader.py:736-737` Reader.tools
- `sw/reader.py:739-740` Reader.tool_view
- `sw/reader.py:742-743` Reader.hidden_tools
- `sw/reader.py:810-818` Reader.draw_map

## 16. The Map's nodes (11 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/reader.py:810-818` Reader.draw_map
- `sw/reader.py:915-922` map_style
- `sw/reader.py:820-833` Reader.map_nodes
- `sw/reader.py:835-839` Reader.owner
- `sw/reader.py:48-53` defined_name
- `sw/callmap.py:33-39` first_definition
- `sw/callmap.py:42-49` node_at
- `sw/callmap.py:28-30` Node.__init__
- `sw/callmap.py:52-59` edges
- `sw/callmap.py:42-49` node_at
- `sw/vetting.py:87-94` draw_map

## 17. Drawing the Map (17 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/vetting.py:87-94` draw_map
- `sw/vetting.py:80-84` find_dot
- `sw/callmap.py:118-132` dot_source
- `sw/callmap.py:93-99` file_block
- `sw/callmap.py:70-73` cluster
- `sw/callmap.py:76-78` node_line
- `sw/callmap.py:81-90` sight_blocks
- `sw/callmap.py:62-63` node_id
- `sw/callmap.py:66-67` quote
- `sw/callmap.py:102-104` arrow
- `sw/callmap.py:107-115` legend
- `sw/vetting.py:97-109` render
- `sw/vetting.py:112-114` png_size
- `sw/vetting.py:123-138` show_image
- `sw/vetting.py:141-146` zoom
- `sw/commands.py:266-267` SightWalkZoomMapCommand.run
- `sw/vetting.py:149-152` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with the focus, the visible sights and the edits, and the agent receives it.

- `sw/commands.py:42-46` SightWalkSendCommand.run
- `sw/chat.py:160-174` take_draft
- `sw/commands.py:32-36` send
- `sw/state.py:36-37` reader_for
- `sw/reader.py:876-890` Reader.context
- `sw/views.py:307-311` selected_text
- `sw/plan.py:104-107` visible_specs
- `sw/reader.py:681-684` Reader.take_edits
- `sw/bridge.py:238-254` wait_for_user

## 19. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:62-72` SightWalkEditCommand.run
- `sw/reader.py:649-654` Reader.sight_of
- `sw/reader.py:637-647` Reader.open_editor
- `sw/editor.py:24-32` Editor.__init__
- `sw/views.py:67-71` wait_until_loaded
- `sw/editor.py:16-20` open_live
- `sw/editor.py:34-44` Editor.start
- `sw/editor.py:46-58` Editor.track
- `sw/editor.py:60-65` Editor.hold
- `sw/geometry.py:69-77` Geometry.editor_geometry

## 20. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:78-81` SightWalkCloseEditorCommand.run
- `sw/reader.py:656-657` Reader.close_editor
- `sw/editor.py:81-92` Editor.close
- `sw/editor.py:74-79` Editor.read_back
- `sw/editor.py:67-72` Editor.rows
- `sw/reader.py:659-672` Reader.editor_closed
- `sw/reader.py:674-679` Reader.move_range

## 21. Window events (13 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:568-578` Reader.follow_resize
- `sw/reader.py:378-385` Reader.keep_bench_width
- `sw/geometry.py:18-25` Geometry.spans
- `sw/geometry.py:27-31` Geometry.strip_span
- `sw/geometry.py:33-35` Geometry.strip_share
- `sw/geometry.py:37-38` Geometry.bench_side
- `sw/state.py:63-68` render_all
- `sw/bridge.py:177-184` op_settings
- `sw/bridge.py:167-174` check_setting
- `sw/commands.py:123-125` SightWalkWindowListener.on_activated
- `sw/commands.py:95-99` SightWalkScrollCommand.run
- `sw/commands.py:89-91` SightWalkHeaderListener.on_hover
- `sw/chat.py:143-147` show_help

## 22. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:294-305` SightWalkToggleGuideCommand.run
- `sw/reader.py:699-709` Reader.toggle_focus
- `sw/commands.py:307-312` SightWalkToggleGuideCommand.folder
- `sw/reader.py:142-146` Reader.open_empty
- `sw/reader.py:148-167` Reader.empty_layout
- `sw/reader.py:169-174` Reader.close_hijacker
- `sw/commands.py:149-153` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:127-128` SightWalkWindowListener.on_load
- `sw/reader.py:176-184` Reader.take_file
- `sw/bridge.py:153-164` op_browse
- `sw/views.py:122-133` make_browser

## 23. What the agent is told (11 views, survey)

The guide's manual, the tools' descriptions and schemas it gets at its start, and the prompt a guide started from Sublime is given.

- `sw/manual.py:4-17` MANUAL: opening
- `sw/manual.py:19-43` MANUAL: Showing code
- `sw/manual.py:45-48` MANUAL: Writing code that fits the reader
- `sw/manual.py:50-81` MANUAL: Conversation
- `sw/manual.py:83-112` MANUAL: Indicators
- `sw/manual.py:115-118` tool
- `sw/manual.py:121-125` TRANSITION
- `sw/manual.py:127-165` TOOLS
- `sw/bridge.py:50-51` TRANSITION_FORM
- `sw/guide.py:19-24` PROMPT
- `sw/guide.py:25-25` TOOLS

## 24. One tool call over HTTP (13 views)

From the request to the reply: the token checked, the JSON-RPC message answered, the tool run on Sublime's thread.

- `sw/mcp_http.py:92-103` Handler.do_POST
- `sw/mcp_http.py:76-79` Handler.authorized
- `sw/mcp_http.py:63-72` reply
- `sw/mcp_http.py:48-60` answer
- `sw/manual.py:115-118` tool
- `sw/mcp_http.py:36-45` tool_result
- `sw/mcp_http.py:23-33` call_tool
- `sw/bridge.py:227-235` wait_until_ready
- `sw/bridge.py:208-224` run_on_main
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
- `sw/bridge.py:238-254` wait_for_user

## 26. Here, and asking by a shortcut (3 views)

The caret or a selection in a sight becomes here; a shortcut sends a question, like "Explain next.", as a message.

- `sw/commands.py:137-147` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:711-714` Reader.note_selection
- `sw/commands.py:52-56` SightWalkAskCommand.run

## 27. Words in two languages (9 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/commands.py:257-260` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:48-51` settings_changed
- `sw/words.py:57-59` set_language
- `sw/state.py:63-68` render_all
- `sw/words.py:53-54` word
- `sw/chat.py:28-32` help_html
- `sw/views.py:31-33` button_html
- `sw/commands.py:342-354` SightWalkCompareFontsCommand.run
- `sw/commands.py:357-365` kept_conversation

## 28. Endings (16 views, survey)

The guide is stopped, windows close.

- `sw/commands.py:282-283` SightWalkStopGuideCommand.run
- `sw/commands.py:285-286` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:83-87` stop
- `sw/guide.py:71-80` stop_when_idle
- `sw/commands.py:155-157` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:160-162` clear_schemes_if_unused
- `sw/tint.py:183-209` clear_schemes
- `sw/tint.py:72-73` scheme_folder
- `sw/commands.py:130-135` SightWalkWindowListener.on_window_command
- `sw/commands.py:188-190` SightWalkCloseTripCommand.run
- `sw/commands.py:168-171` SightWalkResetSightsCommand.run
- `sw/reader.py:716-719` Reader.reset_sights
- `sw/commands.py:173-175` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:29-33` forget
- `sw/bridge.py:145-150` op_close
- `sw/state.py:40-41` current_reader

## 29. Names and room (11 views, survey)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:67-73` sight_title
- `sw/spec.py:37-44` display_path
- `sw/spec.py:26-34` repo_root
- `sw/spec.py:76-81` matches
- `sw/geometry.py:12-16` Geometry.share
- `sw/geometry.py:46-54` Geometry.conversation_rows
- `sw/geometry.py:56-58` Geometry.head
- `sw/geometry.py:65-67` Geometry.room
- `sw/bridge.py:140-142` op_state
- `sw/reader.py:859-864` Reader.folder
- `sw/reader.py:841-843` Reader.note_waiting

## 30. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-15` Item.__init__
- `sw/plan.py:22-35` Pane.__init__
- `sw/plan.py:37-39` Pane.spec
- `sw/plan.py:41-43` Pane.items
- `sw/plan.py:45-47` Pane.all_views
- `sw/views.py:43-44` kept
- `sw/views.py:47-52` phantoms
- `sw/views.py:55-56` forget
- `sw/chat.py:49-51` Guard.__init__
- `sw/commands.py:85-87` SightWalkHeaderListener.is_applicable
- `sw/commands.py:106-108` SightWalkChatListener.is_applicable

## 31. Settings and the rest of the colours (7 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/commands.py:101-102` SightWalkScrollCommand.is_enabled
- `sw/tint.py:84-86` band_amount
- `sw/tint.py:59-69` from_tm_theme
- `sw/tint.py:96-104` resolved_scheme
- `sw/tint.py:89-93` scheme_stem
- `sw/tint.py:29-30` hex_rgb
- `sw/tint.py:175-180` apply_grey

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

- `sw/commands.py:198-204` SightWalkOpenTourCommand.run
- `sw/commands.py:213-226` tour_choices
- `sw/commands.py:229-239` found_files
- `sw/commands.py:242-243` read_name
- `sw/commands.py:246-251` read_field
- `sw/commands.py:206-210` SightWalkOpenTourCommand.open
- `sw/words.py:62-69` trips_count
- `sw/reader.py:766-780` Reader.open_tour
- `sw/reader.py:906-908` read_json
- `sw/ontology.py:288-294` tour_from
- `sw/ontology.py:267-271` informator_from
- `sw/ontology.py:251-254` trip_from
- `sw/ontology.py:241-242` transition_from
- `sw/ontology.py:206-219` tour
- `sw/ontology.py:222-230` visit
- `sw/vetting.py:176-182` read_walked
- `sw/reader.py:782-794` Reader.tour_link
- `sw/reader.py:796-804` Reader.keep_transcript
- `sw/reader.py:893-895` transcripts_path
- `sw/reader.py:898-903` read_transcripts
- `sw/chat.py:202-205` set_transcript
- `sw/ontology.py:274-278` dumps
- `sw/vetting.py:185-194` save_walked
- `sw/reader.py:806-808` Reader.draw_tour
- `sw/vetting.py:157-173` show_tour

## 35. Trip files (6 views)

A trip opened from its file by the guide, and the files written for an informator.

- `sw/bridge.py:187-201` op_open_trip
- `sw/ontology.py:251-254` trip_from
- `sw/ontology.py:245-248` trip_data
- `sw/ontology.py:236-238` transition_data
- `sw/ontology.py:257-264` informator_data
- `sw/ontology.py:281-285` tour_data

## 36. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:198-212` Reader.build
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
- `sw/commands.py:318-320` SightWalkSightListener.is_applicable
- `sw/commands.py:322-324` SightWalkSightListener.on_hover
- `sw/asked.py:87-92` show_popup
- `sw/asked.py:60-62` paint
- `sw/asked.py:65-70` toggle
- `sw/commands.py:330-331` SightWalkToggleSentinelsCommand.run
