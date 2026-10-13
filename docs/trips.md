# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function. Written by `tools/trips.py`; run it again after the code changes.

## 1. Plugin start and stop (9 views)

Sublime loads the plugin, the bridge starts listening; on unload, readers close and the bridge stops.

- `sight_walk.py:33-37` plugin_loaded
- `sw/bridge.py:240-244` start
- `sw/bridge.py:216-223` load_config
- `sw/bridge.py:226-229` start_server
- `sight_walk.py:40-46` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:46-53` close_all
- `sw/bridge.py:247-249` stop
- `sw/bridge.py:232-237` stop_server

## 2. Setting up the agent bridge (8 views)

The setup command writes the token and the MCP server; the server reads them and calls Sublime.

- `sw/setup.py:37-44` SightWalkSetupCommand.run
- `sw/setup.py:47-54` ensure_token
- `sw/setup.py:57-67` install_server
- `sw/setup.py:70-73` show_instructions
- `sw/commands.py:13-20` SightWalkReplaceCommand.run
- `mcp_server/sight_walk_mcp.py:82-85` load_config
- `mcp_server/sight_walk_mcp.py:105-110` show
- `mcp_server/sight_walk_mcp.py:91-102` call

## 3. A request arrives (8 views)

From the socket to the show operation, with every check on the way.

- `sw/bridge.py:196-206` Handler.handle
- `sw/bridge.py:183-192` dispatch
- `sw/bridge.py:177-180` authorized
- `sw/bridge.py:139-155` run_on_main
- `sw/bridge.py:63-69` op_show
- `sw/bridge.py:33-47` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:28-30` file_lines

## 4. A new reader window (11 views)

The window and every view but the sights.

- `sw/bridge.py:50-60` new_reader
- `sw/reader.py:46-62` Reader.__init__
- `sw/reader.py:64-89` Reader.make_side_views
- `sw/views.py:161-170` bench_font
- `sw/views.py:173-177` match_font
- `sw/views.py:121-128` make_blank_view
- `sw/views.py:97-104` make_side_view
- `sw/chat.py:69-75` start
- `sw/chat.py:78-87` make_header
- `sw/vetting.py:11-15` make
- `sw/state.py:16-19` register

## 5. Loading the sights (11 views)

Files opened, each sight's views made; a sight at line 1 gets its two extra views.

- `sw/reader.py:93-103` Reader.load
- `sw/reader.py:144-154` Reader.close_sights
- `sw/views.py:57-61` wait_until_loaded
- `sw/reader.py:156-171` Reader.build
- `sw/views.py:146-158` make_copy
- `sw/views.py:139-143` FileCopy.__init__
- `sw/views.py:182-188` make_header
- `sw/views.py:191-196` write_header
- `sw/line_one.py:21-24` LineOne.__init__
- `sw/twin.py:17-28` make
- `sw/twin.py:31-36` fill

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

- `sw/reader.py:193-199` Reader.draw_gaps
- `sw/views.py:243-250` draw_gap
- `sw/reader.py:201-212` Reader.make_items
- `sw/line_one.py:16-17` line_top
- `sw/views.py:199-200` header_top
- `sw/reader.py:214-219` Reader.calibrate
- `sw/reader.py:221-226` Reader.measure_full
- `sw/reader.py:228-232` Reader.measure_half
- `sw/reader.py:234-238` Reader.start
- `sw/plan.py:47-51` stack

## 8. The layout (10 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:428-433` Reader.scroll_to
- `sw/plan.py:54-61` max_offset
- `sw/reader.py:395-404` Reader.render
- `sw/reader.py:320-342` Reader.column_rects
- `sw/reader.py:286-290` Reader.column
- `sw/reader.py:344-358` Reader.sight_cells
- `sw/line_one.py:43-55` LineOne.rects
- `sw/reader.py:360-366` Reader.layout
- `sw/views.py:74-92` reader_layout
- `sw/views.py:64-71` to_layout

## 9. Arranging the views (9 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:406-419` Reader.arrange
- `sw/reader.py:376-379` Reader.place
- `sw/reader.py:381-393` Reader.assign_groups
- `sw/views.py:51-54` hide_chrome
- `sw/reader.py:455-463` Reader.scroll_views
- `sw/reader.py:435-446` Reader.places
- `sw/line_one.py:38-41` LineOne.places
- `sw/views.py:131-133` anchor
- `sw/views.py:203-213` draw_edit_button

## 10. Polling and the wheel (10 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:484-495` Reader.poll
- `sw/chat.py:146-160` keep_at_bottom
- `sw/reader.py:240-254` Reader.measure_gutter
- `sw/line_one.py:29-33` LineOne.misalignment
- `sw/reader.py:497-504` Reader.poll_wheel
- `sw/reader.py:481-482` Reader.alive
- `sw/reader.py:465-477` Reader.read_wheel
- `sw/reader.py:448-453` Reader.wheel_places
- `sw/reader.py:435-446` Reader.places
- `sw/reader.py:428-433` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:124-130` point
- `sw/bridge.py:83-85` op_point
- `sw/state.py:37-43` require_ready
- `sw/reader.py:520-528` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (8 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:530-543` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:218-227` draw_icons
- `sw/line_one.py:61-62` LineOne.draw_icons
- `sw/reader.py:545-552` Reader.draw_outlines
- `sw/views.py:230-240` draw_outlines
- `sw/line_one.py:64-66` LineOne.draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:113-121` say
- `sw/bridge.py:72-80` op_say
- `sw/reader.py:670-676` Reader.say
- `sw/reader.py:614-620` Reader.show_headers
- `sw/chat.py:90-109` show_header
- `sw/header.py:12-22` title_lines
- `sw/chat.py:119-126` say
- `sw/commands.py:24-25` SightWalkInsertCommand.run
- `sw/chat.py:49-66` Guard.on_text_changed
- `sw/chat.py:31-39` protected_end
- `sw/commands.py:102-104` SightWalkChatListener.on_modified

## 14. The user sends a message (29 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:31-39` SightWalkSendCommand.run
- `sw/state.py:29-30` reader_for
- `sw/reader.py:678-692` Reader.context
- `sw/commands.py:122-132` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:635-638` Reader.note_selection
- `sw/plan.py:70-75` lead
- `sw/plan.py:64-67` free_room
- `sw/plan.py:78-84` offset_range
- `sw/reader.py:423-426` Reader.centred_lead
- `sw/reader.py:173-184` Reader.surround
- `sw/reader.py:35-36` line_count
- `sw/reader.py:39-42` item_top
- `sw/plan.py:42-44` Sight.all_views
- `sw/views.py:45-46` forget
- `sw/views.py:33-34` kept
- `sw/views.py:37-42` phantoms
- `sw/spec.py:74-89` ancestors
- `sw/spec.py:92-99` breathing
- `sw/spec.py:61-62` indent
- `sw/spec.py:65-71` opens_block
- `sw/plan.py:34-36` Sight.items
- `sw/reader.py:645-653` Reader.draw_strip_buttons
- `sw/reader.py:655-657` Reader.strip_button
- `sw/reader.py:640-643` Reader.reset_sights
- `sw/plan.py:87-90` visible_specs
- `sw/chat.py:129-143` take_draft
- `sw/reader.py:607-610` Reader.take_edits
- `sw/bridge.py:158-172` wait_for_user
- `mcp_server/sight_walk_mcp.py:164-167` wait_for_user

## 15. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:57-64` SightWalkEditCommand.run
- `sw/reader.py:573-578` Reader.sight_of
- `sw/plan.py:38-40` Sight.code_views
- `sw/reader.py:561-571` Reader.open_editor
- `sw/editor.py:21-29` Editor.__init__
- `sw/editor.py:13-17` open_live
- `sw/editor.py:31-36` Editor.start
- `sw/editor.py:38-50` Editor.track
- `sw/editor.py:52-57` Editor.hold
- `sw/reader.py:310-318` Reader.editor_geometry

## 16. Closing the editor (8 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:70-73` SightWalkCloseEditorCommand.run
- `sw/reader.py:580-581` Reader.close_editor
- `sw/editor.py:73-84` Editor.close
- `sw/editor.py:66-71` Editor.read_back
- `sw/editor.py:59-64` Editor.rows
- `sw/reader.py:583-598` Reader.editor_closed
- `sw/reader.py:600-605` Reader.move_range
- `sw/twin.py:31-36` fill

## 17. Window events (13 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:506-516` Reader.follow_resize
- `sw/reader.py:368-374` Reader.keep_bench_width
- `sw/reader.py:264-271` Reader.spans
- `sw/reader.py:273-277` Reader.strip_span
- `sw/reader.py:279-281` Reader.strip_share
- `sw/reader.py:283-284` Reader.bench_side
- `sw/state.py:56-60` render_all
- `sw/bridge.py:125-132` op_settings
- `sw/bridge.py:115-122` check_setting
- `sw/commands.py:108-110` SightWalkWindowListener.on_activated
- `sw/commands.py:87-91` SightWalkScrollCommand.run
- `sw/commands.py:81-83` SightWalkHeaderListener.on_hover
- `sw/chat.py:112-116` show_help

## 18. primary+g (12 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:178-189` SightWalkToggleGuideCommand.run
- `sw/reader.py:622-633` Reader.toggle_focus
- `sw/commands.py:191-196` SightWalkToggleGuideCommand.folder
- `sw/reader.py:105-109` Reader.open_empty
- `sw/reader.py:111-125` Reader.empty_layout
- `sw/reader.py:127-132` Reader.close_hijacker
- `sw/commands.py:134-138` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:112-113` SightWalkWindowListener.on_load
- `sw/reader.py:134-142` Reader.take_file
- `sw/bridge.py:101-112` op_browse
- `mcp_server/sight_walk_mcp.py:146-151` browse
- `sw/views.py:107-118` make_browser

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
- `mcp_server/sight_walk_mcp.py:164-167` wait_for_user
- `mcp_server/sight_walk_mcp.py:91-102` call
- `sw/bridge.py:183-192` dispatch
- `sw/bridge.py:158-172` wait_for_user

## 21. Talking on the bench (3 views)

A question goes to the inbox with what is selected; the answer comes back to the bench.

- `sw/commands.py:45-51` SightWalkAskCommand.run
- `sw/views.py:253-257` selected_text
- `sw/chat.py:163-171` catch_up

## 22. Endings (13 views)

The guide is stopped, windows close.

- `sw/commands.py:166-167` SightWalkStopGuideCommand.run
- `sw/commands.py:169-170` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:85-89` stop
- `sw/guide.py:73-82` stop_when_idle
- `sw/commands.py:140-141` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:115-120` SightWalkWindowListener.on_window_command
- `sw/commands.py:158-160` SightWalkCloseTripCommand.run
- `sw/commands.py:147-150` SightWalkResetSightsCommand.run
- `sw/commands.py:152-154` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:22-26` forget
- `mcp_server/sight_walk_mcp.py:140-143` close
- `sw/bridge.py:93-98` op_close
- `sw/state.py:33-34` current_reader

## 23. Names and room (12 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-50` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:53-58` matches
- `sw/reader.py:258-262` Reader.share
- `sw/reader.py:292-300` Reader.conversation_rows
- `sw/reader.py:302-304` Reader.head
- `sw/reader.py:306-308` Reader.room
- `sw/reader.py:556-559` Reader.draw_edit_buttons
- `sw/bridge.py:88-90` op_state
- `sw/reader.py:663-668` Reader.folder
- `sw/reader.py:659-661` Reader.note_waiting

## 24. Building blocks (10 views)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-14` Item.__init__
- `sw/plan.py:20-32` Sight.__init__
- `sw/line_one.py:26-27` LineOne.first_line
- `sw/line_one.py:35-36` LineOne.views
- `sw/line_one.py:57-59` LineOne.draw_gaps
- `sw/line_one.py:68-71` LineOne.close
- `sw/twin.py:39-41` content_top
- `sw/chat.py:45-47` Guard.__init__
- `sw/commands.py:77-79` SightWalkHeaderListener.is_applicable
- `sw/commands.py:98-100` SightWalkChatListener.is_applicable

## 25. Settings and the rest of the colours (9 views)

The agent's view of the settings, and colour helpers.

- `mcp_server/sight_walk_mcp.py:154-161` settings
- `mcp_server/sight_walk_mcp.py:133-137` state
- `sw/commands.py:93-94` SightWalkScrollCommand.is_enabled
- `sw/tint.py:78-80` band_amount
- `sw/tint.py:57-67` from_tm_theme
- `sw/tint.py:90-98` resolved_scheme
- `sw/tint.py:83-87` scheme_stem
- `sw/tint.py:27-28` hex_rgb
- `sw/tint.py:164-169` apply_grey

## 26. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:156-171` Reader.build
- `sw/asked.py:32-44` draw
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

- `sw/asked.py:47-57` mark
- `sw/asked.py:73-80` popup_html
- `sw/asked.py:83-84` escape
- `sw/commands.py:202-204` SightWalkSightListener.is_applicable
- `sw/commands.py:206-208` SightWalkSightListener.on_hover
- `sw/asked.py:87-92` show_popup
- `sw/asked.py:60-62` paint
- `sw/asked.py:65-70` toggle
- `sw/commands.py:214-215` SightWalkToggleSentinelsCommand.run
