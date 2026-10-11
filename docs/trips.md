# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function. Written by `tools/trips.py`; run it again after the code changes.

## 1. Plugin start and stop (9 views)

Sublime loads the plugin, the bridge starts listening; on unload, readers close and the bridge stops.

- `sight_walk.py:31-34` plugin_loaded
- `sw/bridge.py:236-240` start
- `sw/bridge.py:212-219` load_config
- `sw/bridge.py:222-225` start_server
- `sight_walk.py:37-42` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:45-51` close_all
- `sw/bridge.py:243-245` stop
- `sw/bridge.py:228-233` stop_server

## 2. Setting up the agent bridge (8 views)

The setup command writes the token and the MCP server; the server reads them and calls Sublime.

- `sw/setup.py:37-44` SightWalkSetupCommand.run
- `sw/setup.py:47-54` ensure_token
- `sw/setup.py:57-67` install_server
- `sw/setup.py:70-73` show_instructions
- `sw/commands.py:10-17` SightWalkReplaceCommand.run
- `mcp_server/sight_walk_mcp.py:77-80` load_config
- `mcp_server/sight_walk_mcp.py:100-105` show
- `mcp_server/sight_walk_mcp.py:86-97` call

## 3. A request arrives (9 views)

From the socket to the show operation, with every check on the way.

- `sw/bridge.py:192-202` Handler.handle
- `sw/bridge.py:179-188` dispatch
- `sw/bridge.py:173-176` authorized
- `sw/bridge.py:135-151` run_on_main
- `sw/bridge.py:72-79` op_show
- `sw/bridge.py:60-69` check_show
- `sw/bridge.py:33-45` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:28-30` line_count

## 4. A new reader window (11 views)

The window and every view but the sights.

- `sw/bridge.py:48-57` new_reader
- `sw/reader.py:31-45` Reader.__init__
- `sw/reader.py:47-60` Reader.make_side_views
- `sw/views.py:119-128` bench_font
- `sw/views.py:131-135` match_font
- `sw/views.py:92-100` make_blank_view
- `sw/views.py:82-89` make_side_view
- `sw/chat.py:70-76` start
- `sw/chat.py:79-88` make_header
- `sw/vetting.py:12-22` make
- `sw/state.py:16-18` register

## 5. Loading the sights (10 views)

Files opened, each sight's views made; a sight at line 1 gets its two extra views.

- `sw/reader.py:64-74` Reader.load
- `sw/reader.py:76-86` Reader.close_sights
- `sw/views.py:45-49` wait_until_loaded
- `sw/reader.py:88-104` Reader.build
- `sw/views.py:108-116` prepare_code_view
- `sw/views.py:140-146` make_header
- `sw/views.py:149-154` write_header
- `sw/line_one.py:21-24` LineOne.__init__
- `sw/twin.py:18-29` make
- `sw/twin.py:32-38` fill

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:106-110` Reader.tint
- `sw/tint.py:123-126` apply_tint
- `sw/tint.py:103-109` schemes_for
- `sw/tint.py:18-22` hue_for
- `sw/tint.py:69-88` tinted_schemes
- `sw/tint.py:37-46` load_base_scheme
- `sw/tint.py:29-34` tint_color
- `sw/tint.py:49-54` write_scheme
- `sw/tint.py:112-120` set_schemes
- `sw/tint.py:91-100` when_indexed

## 7. Measuring (10 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/reader.py:112-117` Reader.draw_gaps
- `sw/views.py:202-209` draw_gap
- `sw/reader.py:119-127` Reader.make_items
- `sw/line_one.py:16-17` line_top
- `sw/views.py:157-158` header_top
- `sw/reader.py:129-134` Reader.calibrate
- `sw/reader.py:136-141` Reader.measure_full
- `sw/reader.py:143-147` Reader.measure_half
- `sw/reader.py:149-152` Reader.start
- `sw/plan.py:34-38` stack

## 8. The layout (10 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:313-318` Reader.scroll_to
- `sw/plan.py:41-48` max_offset
- `sw/reader.py:288-296` Reader.render
- `sw/reader.py:221-235` Reader.column_rects
- `sw/reader.py:187-191` Reader.column
- `sw/reader.py:237-251` Reader.sight_cells
- `sw/line_one.py:43-55` LineOne.rects
- `sw/reader.py:253-259` Reader.layout
- `sw/views.py:62-77` reader_layout
- `sw/views.py:52-59` to_layout

## 9. Arranging the views (9 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:298-309` Reader.arrange
- `sw/reader.py:269-272` Reader.place
- `sw/reader.py:274-286` Reader.assign_groups
- `sw/views.py:39-42` hide_chrome
- `sw/reader.py:332-337` Reader.scroll_views
- `sw/reader.py:320-330` Reader.places
- `sw/line_one.py:38-41` LineOne.places
- `sw/views.py:103-105` anchor
- `sw/views.py:161-172` draw_edit_button

## 10. Polling and the wheel (9 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:358-369` Reader.poll
- `sw/chat.py:137-151` keep_at_bottom
- `sw/reader.py:154-168` Reader.measure_gutter
- `sw/line_one.py:29-33` LineOne.misalignment
- `sw/reader.py:371-378` Reader.poll_wheel
- `sw/reader.py:355-356` Reader.alive
- `sw/reader.py:339-351` Reader.read_wheel
- `sw/reader.py:320-330` Reader.places
- `sw/reader.py:313-318` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:119-125` point
- `sw/bridge.py:93-95` op_point
- `sw/state.py:36-42` require_ready
- `sw/reader.py:392-400` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (8 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:402-415` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:177-186` draw_icons
- `sw/line_one.py:61-62` LineOne.draw_icons
- `sw/reader.py:417-424` Reader.draw_outlines
- `sw/views.py:189-199` draw_outlines
- `sw/line_one.py:64-66` LineOne.draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:108-116` say
- `sw/bridge.py:82-90` op_say
- `sw/reader.py:514-520` Reader.say
- `sw/reader.py:492-494` Reader.show_headers
- `sw/chat.py:91-102` show_header
- `sw/header.py:11-21` title_lines
- `sw/chat.py:112-118` say
- `sw/commands.py:21-22` SightWalkInsertCommand.run
- `sw/chat.py:50-67` Guard.on_text_changed
- `sw/chat.py:32-40` protected_end
- `sw/commands.py:99-101` SightWalkChatListener.on_modified

## 14. The user sends a message (9 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:28-36` SightWalkSendCommand.run
- `sw/state.py:27-28` reader_for
- `sw/reader.py:522-531` Reader.context
- `sw/plan.py:51-59` focus_sight
- `sw/plan.py:62-65` visible_specs
- `sw/chat.py:121-134` take_draft
- `sw/reader.py:485-488` Reader.take_edits
- `sw/bridge.py:154-168` wait_for_user
- `mcp_server/sight_walk_mcp.py:150-153` wait_for_user

## 15. Opening the editor (9 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:54-61` SightWalkEditCommand.run
- `sw/reader.py:444-449` Reader.sight_of
- `sw/plan.py:29-31` Sight.code_views
- `sw/reader.py:433-442` Reader.open_editor
- `sw/editor.py:26-37` Editor.__init__
- `sw/editor.py:13-22` clone_for_editing
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/reader.py:211-219` Reader.editor_geometry

## 16. Closing the editor (9 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:67-70` SightWalkCloseEditorCommand.run
- `sw/reader.py:451-452` Reader.close_editor
- `sw/editor.py:74-84` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:454-475` Reader.editor_closed
- `sw/reader.py:477-483` Reader.move_range
- `sw/line_one.py:68-70` LineOne.refill
- `sw/twin.py:32-38` fill

## 17. Window events (10 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:380-388` Reader.follow_resize
- `sw/reader.py:261-267` Reader.keep_bench_width
- `sw/reader.py:178-185` Reader.spans
- `sw/state.py:54-58` render_all
- `sw/bridge.py:121-128` op_settings
- `sw/bridge.py:111-118` check_setting
- `sw/commands.py:105-106` SightWalkWindowListener.on_activated
- `sw/commands.py:84-88` SightWalkScrollCommand.run
- `sw/commands.py:78-80` SightWalkHeaderListener.on_hover
- `sw/chat.py:105-109` show_help

## 18. Moving the focus (2 views)

primary+g in a trip: from the sights to the bench and back.

- `sw/commands.py:126-129` SightWalkToggleGuideCommand.run
- `sw/reader.py:496-503` Reader.toggle_focus

## 19. How Claude comes to listen to Sublime (10 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:90-94` await_answer
- `sw/guide.py:48-58` ensure
- `sw/guide.py:31-33` listening
- `sw/guide.py:36-37` running
- `sw/guide.py:40-45` find_claude
- `sw/guide.py:61-69` start
- `mcp_server/sight_walk_mcp.py:150-153` wait_for_user
- `mcp_server/sight_walk_mcp.py:86-97` call
- `sw/bridge.py:179-188` dispatch
- `sw/bridge.py:154-168` wait_for_user

## 20. Talking on the bench (5 views)

A question goes to the inbox with what is selected; the answer comes back to the bench.

- `sw/commands.py:42-48` SightWalkAskCommand.run
- `sw/state.py:61-63` owner
- `sw/views.py:212-216` selected_text
- `sw/views.py:219-225` bench_button
- `sw/chat.py:154-162` catch_up

## 21. Endings (9 views)

The guide is stopped, windows close.

- `sw/commands.py:115-116` SightWalkStopGuideCommand.run
- `sw/commands.py:118-119` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:84-87` stop
- `sw/guide.py:72-81` stop_when_idle
- `sw/commands.py:108-109` SightWalkWindowListener.on_pre_close_window
- `sw/state.py:21-24` forget
- `mcp_server/sight_walk_mcp.py:134-137` close
- `sw/bridge.py:103-108` op_close
- `sw/state.py:31-33` current_reader

## 22. Names and room (12 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-49` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:52-57` matches
- `sw/reader.py:172-176` Reader.share
- `sw/reader.py:193-201` Reader.conversation_rows
- `sw/reader.py:203-205` Reader.head
- `sw/reader.py:207-209` Reader.room
- `sw/reader.py:428-431` Reader.draw_edit_buttons
- `sw/bridge.py:98-100` op_state
- `sw/reader.py:509-512` Reader.folder
- `sw/reader.py:505-507` Reader.note_waiting

## 23. Building blocks (10 views)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-12` Item.__init__
- `sw/plan.py:18-27` Sight.__init__
- `sw/line_one.py:26-27` LineOne.first_line
- `sw/line_one.py:35-36` LineOne.views
- `sw/line_one.py:57-59` LineOne.draw_gaps
- `sw/line_one.py:72-75` LineOne.close
- `sw/twin.py:41-43` content_top
- `sw/chat.py:46-48` Guard.__init__
- `sw/commands.py:74-76` SightWalkHeaderListener.is_applicable
- `sw/commands.py:95-97` SightWalkChatListener.is_applicable

## 24. Settings and the rest of the colours (7 views)

The agent's view of the settings, and colour helpers.

- `mcp_server/sight_walk_mcp.py:140-147` settings
- `mcp_server/sight_walk_mcp.py:128-131` state
- `sw/commands.py:90-91` SightWalkScrollCommand.is_enabled
- `sw/tint.py:57-59` band_amount
- `sw/tint.py:62-66` scheme_stem
- `sw/tint.py:25-26` hex_rgb
- `sw/tint.py:129-134` apply_grey

## 25. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/reader.py:88-104` Reader.build
- `sw/asked.py:32-44` draw
- `sw/asked.py:19-29` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 26. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/asked.py:47-57` mark
- `sw/asked.py:73-80` popup_html
- `sw/asked.py:83-84` escape
- `sw/commands.py:135-137` SightWalkSightListener.is_applicable
- `sw/commands.py:139-141` SightWalkSightListener.on_hover
- `sw/asked.py:87-92` show_popup
- `sw/asked.py:60-62` paint
- `sw/asked.py:65-70` toggle
- `sw/commands.py:147-148` SightWalkToggleSentinelsCommand.run
