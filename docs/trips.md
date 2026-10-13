# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function. Written by `tools/trips.py`; run it again after the code changes.

## 1. Plugin start and stop (9 views)

Sublime loads the plugin, the bridge starts listening; on unload, readers close and the bridge stops.

- `sight_walk.py:34-38` plugin_loaded
- `sw/bridge.py:249-253` start
- `sw/bridge.py:225-232` load_config
- `sw/bridge.py:235-238` start_server
- `sight_walk.py:41-47` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:49-56` close_all
- `sw/bridge.py:256-258` stop
- `sw/bridge.py:241-246` stop_server

## 2. Setting up the agent bridge (8 views)

The setup command writes the token and the MCP server; the server reads them and calls Sublime.

- `sw/setup.py:37-44` SightWalkSetupCommand.run
- `sw/setup.py:47-54` ensure_token
- `sw/setup.py:57-67` install_server
- `sw/setup.py:70-73` show_instructions
- `sw/commands.py:13-20` SightWalkReplaceCommand.run
- `mcp_server/sight_walk_mcp.py:84-87` load_config
- `mcp_server/sight_walk_mcp.py:107-112` show
- `mcp_server/sight_walk_mcp.py:93-104` call

## 3. A request arrives (8 views)

From the socket to the show operation, with every check on the way.

- `sw/bridge.py:205-215` Handler.handle
- `sw/bridge.py:192-201` dispatch
- `sw/bridge.py:186-189` authorized
- `sw/bridge.py:148-164` run_on_main
- `sw/bridge.py:69-76` op_show
- `sw/bridge.py:33-47` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:28-30` file_lines

## 4. A new reader window (11 views)

The window and every view but the sights.

- `sw/bridge.py:50-60` new_reader
- `sw/reader.py:46-61` Reader.__init__
- `sw/reader.py:63-90` Reader.make_side_views
- `sw/views.py:166-175` bench_font
- `sw/views.py:178-182` match_font
- `sw/views.py:126-133` make_blank_view
- `sw/views.py:102-109` make_side_view
- `sw/chat.py:69-75` start
- `sw/chat.py:78-87` make_header
- `sw/vetting.py:11-15` make
- `sw/state.py:19-22` register

## 5. Loading the sights (8 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/reader.py:94-103` Reader.load
- `sw/reader.py:146-156` Reader.close_sights
- `sw/views.py:57-61` wait_until_loaded
- `sw/reader.py:158-171` Reader.build
- `sw/views.py:151-163` make_copy
- `sw/views.py:144-148` FileCopy.__init__
- `sw/views.py:187-193` make_header
- `sw/views.py:196-201` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:186-191` Reader.tint
- `sw/tint.py:158-161` apply_tint
- `sw/tint.py:138-144` schemes_for
- `sw/tint.py:20-24` hue_for
- `sw/tint.py:101-123` tinted_schemes
- `sw/tint.py:39-51` load_base_scheme
- `sw/tint.py:31-36` tint_color
- `sw/tint.py:70-75` write_scheme
- `sw/tint.py:147-155` set_schemes
- `sw/tint.py:126-135` when_indexed

## 7. Measuring (10 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/reader.py:193-197` Reader.draw_gaps
- `sw/views.py:252-259` draw_gap
- `sw/reader.py:199-210` Reader.make_items
- `sw/views.py:204-205` line_top
- `sw/views.py:208-209` header_top
- `sw/reader.py:212-217` Reader.calibrate
- `sw/reader.py:219-224` Reader.measure_full
- `sw/reader.py:226-230` Reader.measure_half
- `sw/reader.py:232-239` Reader.start
- `sw/plan.py:42-46` stack

## 8. The layout (9 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:315-320` Reader.scroll_to
- `sw/plan.py:49-56` max_offset
- `sw/reader.py:282-291` Reader.render
- `sw/geometry.py:74-96` Geometry.column_rects
- `sw/geometry.py:40-44` Geometry.column
- `sw/geometry.py:98-107` Geometry.sight_cells
- `sw/reader.py:243-251` Reader.layout
- `sw/views.py:74-97` reader_layout
- `sw/views.py:64-71` to_layout

## 9. Arranging the views (8 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:293-306` Reader.arrange
- `sw/reader.py:261-264` Reader.place
- `sw/reader.py:266-280` Reader.assign_groups
- `sw/views.py:51-54` hide_chrome
- `sw/reader.py:344-352` Reader.scroll_views
- `sw/reader.py:322-331` Reader.places
- `sw/views.py:136-138` anchor
- `sw/views.py:212-222` draw_edit_button

## 10. Polling and the wheel (9 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:377-385` Reader.poll
- `sw/chat.py:174-187` keep_at_bottom
- `sw/reader.py:387-394` Reader.poll_wheel
- `sw/reader.py:374-375` Reader.alive
- `sw/reader.py:354-370` Reader.read_wheel
- `sw/reader.py:333-336` Reader.wheel_places
- `sw/reader.py:338-342` Reader.pinned_places
- `sw/reader.py:322-331` Reader.places
- `sw/reader.py:315-320` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:126-132` point
- `sw/bridge.py:91-94` op_point
- `sw/state.py:40-46` require_ready
- `sw/reader.py:410-418` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (6 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:420-431` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:227-236` draw_icons
- `sw/reader.py:433-438` Reader.draw_outlines
- `sw/views.py:239-249` draw_outlines

## 13. The agent says something (16 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:115-123` say
- `sw/bridge.py:79-88` op_say
- `sw/reader.py:567-573` Reader.say
- `sw/reader.py:500-508` Reader.show_headers
- `sw/chat.py:90-109` show_header
- `sw/chat.py:115-124` make_status
- `sw/chat.py:127-137` show_status
- `sw/reader.py:550-558` Reader.stop_answer
- `sw/commands.py:160-163` SightWalkStopAnswerCommand.run
- `sw/bridge.py:63-66` check_not_stopped
- `sw/header.py:12-22` title_lines
- `sw/chat.py:147-154` say
- `sw/commands.py:24-25` SightWalkInsertCommand.run
- `sw/chat.py:49-66` Guard.on_text_changed
- `sw/chat.py:31-39` protected_end
- `sw/commands.py:102-104` SightWalkChatListener.on_modified

## 14. The user sends a message (30 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:37-41` SightWalkSendCommand.run
- `sw/commands.py:28-31` send
- `sw/state.py:32-33` reader_for
- `sw/reader.py:575-589` Reader.context
- `sw/commands.py:122-132` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:522-525` Reader.note_selection
- `sw/plan.py:65-70` lead
- `sw/plan.py:59-62` free_room
- `sw/plan.py:73-79` offset_range
- `sw/reader.py:310-313` Reader.centred_lead
- `sw/reader.py:173-184` Reader.surround
- `sw/reader.py:35-36` line_count
- `sw/reader.py:39-42` item_top
- `sw/plan.py:37-39` Sight.all_views
- `sw/views.py:45-46` forget
- `sw/views.py:33-34` kept
- `sw/views.py:37-42` phantoms
- `sw/spec.py:74-89` ancestors
- `sw/spec.py:92-99` breathing
- `sw/spec.py:61-62` indent
- `sw/spec.py:65-71` opens_block
- `sw/plan.py:33-35` Sight.items
- `sw/reader.py:532-540` Reader.draw_strip_buttons
- `sw/reader.py:542-544` Reader.strip_button
- `sw/reader.py:527-530` Reader.reset_sights
- `sw/plan.py:82-85` visible_specs
- `sw/chat.py:157-171` take_draft
- `sw/reader.py:493-496` Reader.take_edits
- `sw/bridge.py:167-181` wait_for_user
- `mcp_server/sight_walk_mcp.py:166-169` wait_for_user

## 15. Opening the editor (9 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:57-64` SightWalkEditCommand.run
- `sw/reader.py:459-464` Reader.sight_of
- `sw/reader.py:447-457` Reader.open_editor
- `sw/editor.py:22-30` Editor.__init__
- `sw/editor.py:14-18` open_live
- `sw/editor.py:32-37` Editor.start
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/geometry.py:64-72` Geometry.editor_geometry

## 16. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:70-73` SightWalkCloseEditorCommand.run
- `sw/reader.py:466-467` Reader.close_editor
- `sw/editor.py:74-85` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:469-484` Reader.editor_closed
- `sw/reader.py:486-491` Reader.move_range

## 17. Window events (13 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:396-406` Reader.follow_resize
- `sw/reader.py:253-259` Reader.keep_bench_width
- `sw/geometry.py:18-25` Geometry.spans
- `sw/geometry.py:27-31` Geometry.strip_span
- `sw/geometry.py:33-35` Geometry.strip_share
- `sw/geometry.py:37-38` Geometry.bench_side
- `sw/state.py:59-63` render_all
- `sw/bridge.py:134-141` op_settings
- `sw/bridge.py:124-131` check_setting
- `sw/commands.py:108-110` SightWalkWindowListener.on_activated
- `sw/commands.py:87-91` SightWalkScrollCommand.run
- `sw/commands.py:81-83` SightWalkHeaderListener.on_hover
- `sw/chat.py:140-144` show_help

## 18. primary+g (12 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:187-198` SightWalkToggleGuideCommand.run
- `sw/reader.py:510-520` Reader.toggle_focus
- `sw/commands.py:200-205` SightWalkToggleGuideCommand.folder
- `sw/reader.py:105-109` Reader.open_empty
- `sw/reader.py:111-127` Reader.empty_layout
- `sw/reader.py:129-134` Reader.close_hijacker
- `sw/commands.py:134-138` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:112-113` SightWalkWindowListener.on_load
- `sw/reader.py:136-144` Reader.take_file
- `sw/bridge.py:110-121` op_browse
- `mcp_server/sight_walk_mcp.py:148-153` browse
- `sw/views.py:112-123` make_browser

## 19. MCP over HTTP (a probe) (12 views)

The plugin itself as an MCP server: one tool call from the request to the reply.

- `sw/mcp_http.py:118-122` start
- `sw/mcp_http.py:94-105` Handler.do_POST
- `sw/mcp_http.py:78-81` Handler.authorized
- `sw/mcp_http.py:65-74` reply
- `sw/mcp_http.py:50-62` answer
- `sw/mcp_http.py:40-47` tool_result
- `sw/mcp_http.py:29-37` call_tool
- `sw/mcp_http.py:83-92` Handler.send
- `sw/mcp_http.py:107-108` Handler.do_GET
- `sw/mcp_http.py:110-112` Handler.do_DELETE
- `sw/mcp_http.py:114-115` Handler.log_message
- `sw/mcp_http.py:125-130` stop

## 20. How Claude comes to listen to Sublime (10 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:92-97` await_answer
- `sw/guide.py:48-58` ensure
- `sw/guide.py:31-33` listening
- `sw/guide.py:36-37` running
- `sw/guide.py:40-45` find_claude
- `sw/guide.py:61-70` start
- `mcp_server/sight_walk_mcp.py:166-169` wait_for_user
- `mcp_server/sight_walk_mcp.py:93-104` call
- `sw/bridge.py:192-201` dispatch
- `sw/bridge.py:167-181` wait_for_user

## 21. Talking on the bench (3 views)

A question goes to the inbox with what is selected; the answer comes back to the bench.

- `sw/commands.py:47-51` SightWalkAskCommand.run
- `sw/views.py:262-266` selected_text
- `sw/chat.py:190-198` catch_up

## 22. Endings (13 views)

The guide is stopped, windows close.

- `sw/commands.py:175-176` SightWalkStopGuideCommand.run
- `sw/commands.py:178-179` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:85-89` stop
- `sw/guide.py:73-82` stop_when_idle
- `sw/commands.py:140-141` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:115-120` SightWalkWindowListener.on_window_command
- `sw/commands.py:167-169` SightWalkCloseTripCommand.run
- `sw/commands.py:147-150` SightWalkResetSightsCommand.run
- `sw/commands.py:152-154` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:25-29` forget
- `mcp_server/sight_walk_mcp.py:142-145` close
- `sw/bridge.py:102-107` op_close
- `sw/state.py:36-37` current_reader

## 23. Names and room (12 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-50` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:53-58` matches
- `sw/geometry.py:12-16` Geometry.share
- `sw/geometry.py:46-54` Geometry.conversation_rows
- `sw/geometry.py:56-58` Geometry.head
- `sw/geometry.py:60-62` Geometry.room
- `sw/reader.py:442-445` Reader.draw_edit_buttons
- `sw/bridge.py:97-99` op_state
- `sw/reader.py:560-565` Reader.folder
- `sw/reader.py:546-548` Reader.note_waiting

## 24. Building blocks (5 views)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-14` Item.__init__
- `sw/plan.py:20-31` Sight.__init__
- `sw/chat.py:45-47` Guard.__init__
- `sw/commands.py:77-79` SightWalkHeaderListener.is_applicable
- `sw/commands.py:98-100` SightWalkChatListener.is_applicable

## 25. Settings and the rest of the colours (9 views)

The agent's view of the settings, and colour helpers.

- `mcp_server/sight_walk_mcp.py:156-163` settings
- `mcp_server/sight_walk_mcp.py:135-139` state
- `sw/commands.py:93-94` SightWalkScrollCommand.is_enabled
- `sw/tint.py:78-80` band_amount
- `sw/tint.py:57-67` from_tm_theme
- `sw/tint.py:90-98` resolved_scheme
- `sw/tint.py:83-87` scheme_stem
- `sw/tint.py:27-28` hex_rgb
- `sw/tint.py:164-169` apply_grey

## 26. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:158-171` Reader.build
- `sw/asked.py:32-43` draw
- `sw/asked.py:19-29` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 27. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/asked.py:46-56` mark
- `sw/asked.py:72-79` popup_html
- `sw/asked.py:82-83` escape
- `sw/commands.py:211-213` SightWalkSightListener.is_applicable
- `sw/commands.py:215-217` SightWalkSightListener.on_hover
- `sw/asked.py:86-91` show_popup
- `sw/asked.py:59-61` paint
- `sw/asked.py:64-69` toggle
- `sw/commands.py:223-224` SightWalkToggleSentinelsCommand.run
