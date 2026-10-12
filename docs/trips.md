# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function. Written by `tools/trips.py`; run it again after the code changes.

## 1. Plugin start and stop (9 views)

Sublime loads the plugin, the bridge starts listening; on unload, readers close and the bridge stops.

- `sight_walk.py:33-37` plugin_loaded
- `sw/bridge.py:251-255` start
- `sw/bridge.py:227-234` load_config
- `sw/bridge.py:237-240` start_server
- `sight_walk.py:40-46` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:45-51` close_all
- `sw/bridge.py:258-260` stop
- `sw/bridge.py:243-248` stop_server

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

## 3. A request arrives (9 views)

From the socket to the show operation, with every check on the way.

- `sw/bridge.py:207-217` Handler.handle
- `sw/bridge.py:194-203` dispatch
- `sw/bridge.py:188-191` authorized
- `sw/bridge.py:150-166` run_on_main
- `sw/bridge.py:73-80` op_show
- `sw/bridge.py:61-70` check_show
- `sw/bridge.py:33-45` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:28-30` line_count

## 4. A new reader window (11 views)

The window and every view but the sights.

- `sw/bridge.py:48-58` new_reader
- `sw/reader.py:42-58` Reader.__init__
- `sw/reader.py:60-85` Reader.make_side_views
- `sw/views.py:142-151` bench_font
- `sw/views.py:154-158` match_font
- `sw/views.py:102-109` make_blank_view
- `sw/views.py:78-85` make_side_view
- `sw/chat.py:70-76` start
- `sw/chat.py:79-88` make_header
- `sw/vetting.py:11-15` make
- `sw/state.py:16-18` register

## 5. Loading the sights (11 views)

Files opened, each sight's views made; a sight at line 1 gets its two extra views.

- `sw/reader.py:89-99` Reader.load
- `sw/reader.py:140-160` Reader.close_sights
- `sw/views.py:38-42` wait_until_loaded
- `sw/reader.py:162-177` Reader.build
- `sw/views.py:127-139` make_copy
- `sw/views.py:120-124` FileCopy.__init__
- `sw/views.py:163-169` make_header
- `sw/views.py:172-177` write_header
- `sw/line_one.py:21-24` LineOne.__init__
- `sw/twin.py:18-29` make
- `sw/twin.py:32-38` fill

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:192-197` Reader.tint
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

- `sw/reader.py:199-205` Reader.draw_gaps
- `sw/views.py:225-238` draw_gap
- `sw/reader.py:207-218` Reader.make_items
- `sw/line_one.py:16-17` line_top
- `sw/views.py:180-181` header_top
- `sw/reader.py:220-225` Reader.calibrate
- `sw/reader.py:227-232` Reader.measure_full
- `sw/reader.py:234-238` Reader.measure_half
- `sw/reader.py:240-244` Reader.start
- `sw/plan.py:43-47` stack

## 8. The layout (10 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:434-439` Reader.scroll_to
- `sw/plan.py:50-57` max_offset
- `sw/reader.py:401-410` Reader.render
- `sw/reader.py:326-348` Reader.column_rects
- `sw/reader.py:292-296` Reader.column
- `sw/reader.py:350-364` Reader.sight_cells
- `sw/line_one.py:43-55` LineOne.rects
- `sw/reader.py:366-372` Reader.layout
- `sw/views.py:55-73` reader_layout
- `sw/views.py:45-52` to_layout

## 9. Arranging the views (9 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:412-425` Reader.arrange
- `sw/reader.py:382-385` Reader.place
- `sw/reader.py:387-399` Reader.assign_groups
- `sw/views.py:32-35` hide_chrome
- `sw/reader.py:464-472` Reader.scroll_views
- `sw/reader.py:441-454` Reader.places
- `sw/line_one.py:38-41` LineOne.places
- `sw/views.py:112-114` anchor
- `sw/views.py:184-195` draw_edit_button

## 10. Polling and the wheel (10 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:493-504` Reader.poll
- `sw/chat.py:145-159` keep_at_bottom
- `sw/reader.py:246-260` Reader.measure_gutter
- `sw/line_one.py:29-33` LineOne.misalignment
- `sw/reader.py:506-513` Reader.poll_wheel
- `sw/reader.py:490-491` Reader.alive
- `sw/reader.py:474-486` Reader.read_wheel
- `sw/reader.py:456-462` Reader.wheel_places
- `sw/reader.py:441-454` Reader.places
- `sw/reader.py:434-439` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:124-130` point
- `sw/bridge.py:94-96` op_point
- `sw/state.py:36-42` require_ready
- `sw/reader.py:529-537` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (8 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:539-552` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:200-209` draw_icons
- `sw/line_one.py:61-62` LineOne.draw_icons
- `sw/reader.py:554-561` Reader.draw_outlines
- `sw/views.py:212-222` draw_outlines
- `sw/line_one.py:64-66` LineOne.draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:113-121` say
- `sw/bridge.py:83-91` op_say
- `sw/reader.py:679-685` Reader.say
- `sw/reader.py:623-629` Reader.show_headers
- `sw/chat.py:91-110` show_header
- `sw/header.py:12-22` title_lines
- `sw/chat.py:120-126` say
- `sw/commands.py:24-25` SightWalkInsertCommand.run
- `sw/chat.py:50-67` Guard.on_text_changed
- `sw/chat.py:32-40` protected_end
- `sw/commands.py:102-104` SightWalkChatListener.on_modified

## 14. The user sends a message (25 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:31-39` SightWalkSendCommand.run
- `sw/state.py:27-28` reader_for
- `sw/reader.py:687-701` Reader.context
- `sw/commands.py:122-132` SightWalkWindowListener.on_selection_modified
- `sw/reader.py:644-647` Reader.note_selection
- `sw/plan.py:66-71` lead
- `sw/plan.py:60-63` free_room
- `sw/plan.py:74-80` offset_range
- `sw/reader.py:429-432` Reader.centred_lead
- `sw/reader.py:179-190` Reader.surround
- `sw/reader.py:37-38` line_count
- `sw/views.py:241-243` forget_gaps
- `sw/spec.py:74-89` ancestors
- `sw/spec.py:92-99` breathing
- `sw/spec.py:61-62` indent
- `sw/spec.py:65-71` opens_block
- `sw/plan.py:34-36` Sight.items
- `sw/reader.py:654-662` Reader.draw_strip_buttons
- `sw/reader.py:664-666` Reader.strip_button
- `sw/reader.py:649-652` Reader.reset_sights
- `sw/plan.py:83-86` visible_specs
- `sw/chat.py:129-142` take_draft
- `sw/reader.py:616-619` Reader.take_edits
- `sw/bridge.py:169-183` wait_for_user
- `mcp_server/sight_walk_mcp.py:164-167` wait_for_user

## 15. Opening the editor (10 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:57-64` SightWalkEditCommand.run
- `sw/reader.py:582-587` Reader.sight_of
- `sw/plan.py:38-40` Sight.code_views
- `sw/reader.py:570-580` Reader.open_editor
- `sw/editor.py:21-29` Editor.__init__
- `sw/editor.py:13-17` open_live
- `sw/editor.py:31-36` Editor.start
- `sw/editor.py:38-50` Editor.track
- `sw/editor.py:52-57` Editor.hold
- `sw/reader.py:316-324` Reader.editor_geometry

## 16. Closing the editor (8 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:70-73` SightWalkCloseEditorCommand.run
- `sw/reader.py:589-590` Reader.close_editor
- `sw/editor.py:73-84` Editor.close
- `sw/editor.py:66-71` Editor.read_back
- `sw/editor.py:59-64` Editor.rows
- `sw/reader.py:592-607` Reader.editor_closed
- `sw/reader.py:609-614` Reader.move_range
- `sw/twin.py:32-38` fill

## 17. Window events (13 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:515-525` Reader.follow_resize
- `sw/reader.py:374-380` Reader.keep_bench_width
- `sw/reader.py:270-277` Reader.spans
- `sw/reader.py:279-283` Reader.strip_span
- `sw/reader.py:285-287` Reader.strip_share
- `sw/reader.py:289-290` Reader.bench_side
- `sw/state.py:54-58` render_all
- `sw/bridge.py:136-143` op_settings
- `sw/bridge.py:126-133` check_setting
- `sw/commands.py:108-110` SightWalkWindowListener.on_activated
- `sw/commands.py:87-91` SightWalkScrollCommand.run
- `sw/commands.py:81-83` SightWalkHeaderListener.on_hover
- `sw/chat.py:113-117` show_help

## 18. primary+g (12 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/commands.py:178-189` SightWalkToggleGuideCommand.run
- `sw/reader.py:631-642` Reader.toggle_focus
- `sw/commands.py:191-196` SightWalkToggleGuideCommand.folder
- `sw/reader.py:101-105` Reader.open_empty
- `sw/reader.py:107-121` Reader.empty_layout
- `sw/reader.py:123-128` Reader.close_hijacker
- `sw/commands.py:134-138` SightWalkWindowListener.offer_to_browser
- `sw/commands.py:112-113` SightWalkWindowListener.on_load
- `sw/reader.py:130-138` Reader.take_file
- `sw/bridge.py:112-123` op_browse
- `mcp_server/sight_walk_mcp.py:146-151` browse
- `sw/views.py:88-99` make_browser

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

- `sw/guide.py:90-94` await_answer
- `sw/guide.py:48-58` ensure
- `sw/guide.py:31-33` listening
- `sw/guide.py:36-37` running
- `sw/guide.py:40-45` find_claude
- `sw/guide.py:61-69` start
- `mcp_server/sight_walk_mcp.py:164-167` wait_for_user
- `mcp_server/sight_walk_mcp.py:91-102` call
- `sw/bridge.py:194-203` dispatch
- `sw/bridge.py:169-183` wait_for_user

## 21. Talking on the bench (4 views)

A question goes to the inbox with what is selected; the answer comes back to the bench.

- `sw/commands.py:45-51` SightWalkAskCommand.run
- `sw/state.py:61-63` owner
- `sw/views.py:246-250` selected_text
- `sw/chat.py:162-170` catch_up

## 22. Endings (13 views)

The guide is stopped, windows close.

- `sw/commands.py:166-167` SightWalkStopGuideCommand.run
- `sw/commands.py:169-170` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:84-87` stop
- `sw/guide.py:72-81` stop_when_idle
- `sw/commands.py:140-141` SightWalkWindowListener.on_pre_close_window
- `sw/commands.py:115-120` SightWalkWindowListener.on_window_command
- `sw/commands.py:158-160` SightWalkCloseTripCommand.run
- `sw/commands.py:147-150` SightWalkResetSightsCommand.run
- `sw/commands.py:152-154` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:21-24` forget
- `mcp_server/sight_walk_mcp.py:140-143` close
- `sw/bridge.py:104-109` op_close
- `sw/state.py:31-33` current_reader

## 23. Names and room (12 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-50` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:53-58` matches
- `sw/reader.py:264-268` Reader.share
- `sw/reader.py:298-306` Reader.conversation_rows
- `sw/reader.py:308-310` Reader.head
- `sw/reader.py:312-314` Reader.room
- `sw/reader.py:565-568` Reader.draw_edit_buttons
- `sw/bridge.py:99-101` op_state
- `sw/reader.py:672-677` Reader.folder
- `sw/reader.py:668-670` Reader.note_waiting

## 24. Building blocks (10 views)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-14` Item.__init__
- `sw/plan.py:20-32` Sight.__init__
- `sw/line_one.py:26-27` LineOne.first_line
- `sw/line_one.py:35-36` LineOne.views
- `sw/line_one.py:57-59` LineOne.draw_gaps
- `sw/line_one.py:68-71` LineOne.close
- `sw/twin.py:41-43` content_top
- `sw/chat.py:46-48` Guard.__init__
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

- `sw/reader.py:162-177` Reader.build
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
