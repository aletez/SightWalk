# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function. Written by `tools/trips.py`; run it again after the code changes.

## 1. Plugin start and stop (9 views)

Sublime loads the plugin, the bridge starts listening; on unload, readers close and the bridge stops.

- `sight_walk.py:30-33` plugin_loaded
- `sw/bridge.py:233-237` start
- `sw/bridge.py:209-216` load_config
- `sw/bridge.py:219-222` start_server
- `sight_walk.py:36-41` plugin_unloaded
- `sw/scrollbars.py:13-25` reader_focused
- `sw/state.py:43-52` close_all
- `sw/bridge.py:240-242` stop
- `sw/bridge.py:225-230` stop_server

## 2. Setting up the agent bridge (8 views)

The setup command writes the token and the MCP server; the server reads them and calls Sublime.

- `sw/setup.py:37-44` SightWalkSetupCommand.run
- `sw/setup.py:47-54` ensure_token
- `sw/setup.py:57-67` install_server
- `sw/setup.py:70-73` show_instructions
- `sw/commands.py:11-18` SightWalkReplaceCommand.run
- `mcp_server/sight_walk_mcp.py:72-75` load_config
- `mcp_server/sight_walk_mcp.py:95-100` show
- `mcp_server/sight_walk_mcp.py:81-92` call

## 3. A request arrives (9 views)

From the socket to the show operation, with every check on the way.

- `sw/bridge.py:189-199` Handler.handle
- `sw/bridge.py:176-185` dispatch
- `sw/bridge.py:170-173` authorized
- `sw/bridge.py:135-151` run_on_main
- `sw/bridge.py:72-82` op_show
- `sw/bridge.py:60-69` check_show
- `sw/bridge.py:33-45` check_sights
- `sw/spec.py:9-22` parse_spec
- `sw/bridge.py:28-30` line_count

## 4. A new reader window (9 views)

The window and every view but the sights.

- `sw/bridge.py:48-57` new_reader
- `sw/reader.py:30-44` Reader.__init__
- `sw/reader.py:46-59` Reader.make_side_views
- `sw/views.py:83-91` make_blank_view
- `sw/views.py:73-80` make_side_view
- `sw/chat.py:63-69` start
- `sw/chat.py:72-81` make_header
- `sw/vetting.py:9-14` make
- `sw/state.py:14-16` register

## 5. Loading the sights (10 views)

Files opened, each sight's views made; a sight at line 1 gets its two extra views.

- `sw/reader.py:63-73` Reader.load
- `sw/reader.py:75-85` Reader.close_sights
- `sw/views.py:36-40` wait_until_loaded
- `sw/reader.py:87-102` Reader.build
- `sw/views.py:99-107` prepare_code_view
- `sw/views.py:127-133` make_header
- `sw/views.py:136-141` write_header
- `sw/line_one.py:21-24` LineOne.__init__
- `sw/twin.py:18-29` make
- `sw/twin.py:32-38` fill

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:104-108` Reader.tint
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

- `sw/reader.py:110-115` Reader.draw_gaps
- `sw/views.py:189-196` draw_gap
- `sw/reader.py:117-125` Reader.make_items
- `sw/line_one.py:16-17` line_top
- `sw/views.py:144-145` header_top
- `sw/reader.py:127-132` Reader.calibrate
- `sw/reader.py:134-139` Reader.measure_full
- `sw/reader.py:141-145` Reader.measure_half
- `sw/reader.py:147-150` Reader.start
- `sw/plan.py:34-38` stack

## 8. The layout (10 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:311-316` Reader.scroll_to
- `sw/plan.py:41-48` max_offset
- `sw/reader.py:286-294` Reader.render
- `sw/reader.py:219-233` Reader.column_rects
- `sw/reader.py:185-189` Reader.column
- `sw/reader.py:235-249` Reader.sight_cells
- `sw/line_one.py:43-55` LineOne.rects
- `sw/reader.py:251-257` Reader.layout
- `sw/views.py:53-68` reader_layout
- `sw/views.py:43-50` to_layout

## 9. Arranging the views (9 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:296-307` Reader.arrange
- `sw/reader.py:267-270` Reader.place
- `sw/reader.py:272-284` Reader.assign_groups
- `sw/views.py:30-33` hide_chrome
- `sw/reader.py:330-335` Reader.scroll_views
- `sw/reader.py:318-328` Reader.places
- `sw/line_one.py:38-41` LineOne.places
- `sw/views.py:94-96` anchor
- `sw/views.py:148-159` draw_edit_button

## 10. Polling and the wheel (9 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:356-367` Reader.poll
- `sw/chat.py:130-143` keep_at_bottom
- `sw/reader.py:152-166` Reader.measure_gutter
- `sw/line_one.py:29-33` LineOne.misalignment
- `sw/reader.py:369-376` Reader.poll_wheel
- `sw/reader.py:353-354` Reader.alive
- `sw/reader.py:337-349` Reader.read_wheel
- `sw/reader.py:318-328` Reader.places
- `sw/reader.py:311-316` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:114-120` point
- `sw/bridge.py:93-95` op_point
- `sw/state.py:34-40` require_ready
- `sw/reader.py:390-398` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (8 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:400-413` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:164-173` draw_icons
- `sw/line_one.py:61-62` LineOne.draw_icons
- `sw/reader.py:415-422` Reader.draw_outlines
- `sw/views.py:176-186` draw_outlines
- `sw/line_one.py:64-66` LineOne.draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:103-111` say
- `sw/bridge.py:85-90` op_say
- `sw/reader.py:503-509` Reader.say
- `sw/reader.py:490-492` Reader.show_headers
- `sw/chat.py:84-95` show_header
- `sw/header.py:11-21` title_lines
- `sw/chat.py:105-111` say
- `sw/commands.py:22-23` SightWalkInsertCommand.run
- `sw/chat.py:49-60` Guard.on_text_changed
- `sw/chat.py:31-39` protected_end
- `sw/commands.py:100-102` SightWalkChatListener.on_modified

## 14. The user sends a message (9 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:29-37` SightWalkSendCommand.run
- `sw/state.py:25-26` reader_for
- `sw/reader.py:511-516` Reader.context
- `sw/plan.py:51-59` focus_sight
- `sw/plan.py:62-65` visible_specs
- `sw/chat.py:114-127` take_draft
- `sw/reader.py:483-486` Reader.take_edits
- `sw/bridge.py:154-165` wait_for_user
- `mcp_server/sight_walk_mcp.py:145-148` wait_for_user

## 15. Opening the editor (9 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:55-62` SightWalkEditCommand.run
- `sw/reader.py:442-447` Reader.sight_of
- `sw/plan.py:29-31` Sight.code_views
- `sw/reader.py:431-440` Reader.open_editor
- `sw/editor.py:26-37` Editor.__init__
- `sw/editor.py:13-22` clone_for_editing
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/reader.py:209-217` Reader.editor_geometry

## 16. Closing the editor (9 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:68-71` SightWalkCloseEditorCommand.run
- `sw/reader.py:449-450` Reader.close_editor
- `sw/editor.py:74-84` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:452-473` Reader.editor_closed
- `sw/reader.py:475-481` Reader.move_range
- `sw/line_one.py:68-70` LineOne.refill
- `sw/twin.py:32-38` fill

## 17. Window events (10 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:378-386` Reader.follow_resize
- `sw/reader.py:259-265` Reader.keep_bench_width
- `sw/reader.py:176-183` Reader.spans
- `sw/state.py:55-59` render_all
- `sw/bridge.py:121-128` op_settings
- `sw/bridge.py:111-118` check_setting
- `sw/commands.py:106-107` SightWalkWindowListener.on_activated
- `sw/commands.py:85-89` SightWalkScrollCommand.run
- `sw/commands.py:79-81` SightWalkHeaderListener.on_hover
- `sw/chat.py:98-102` show_help

## 18. Asking the guide on a selection (10 views)

The Vetting strip opens on the selection's side, with the conversation so far.

- `sw/commands.py:116-122` SightWalkAskGuideCommand.run
- `sw/commands.py:124-125` SightWalkAskGuideCommand.is_enabled
- `sw/strip.py:65-76` GuideStrip.__init__
- `sw/strip.py:34-39` strip_side
- `sw/strip.py:42-50` selection_x
- `sw/strip.py:53-61` selection_spec
- `sw/strip.py:78-90` GuideStrip.make_views
- `sw/views.py:110-115` bench_font
- `sw/views.py:118-122` match_font
- `sw/strip.py:200-205` GuideStrip.folder

## 19. The strip glides (10 views)

Eased frames: the window's own cells shift aside while the strip comes in.

- `sw/strip.py:126-138` GuideStrip.glide
- `sw/strip.py:23-25` ease
- `sw/strip.py:140-145` GuideStrip.place
- `sw/strip.py:102-114` GuideStrip.rects
- `sw/strip.py:28-31` cell_rects
- `sw/strip.py:116-124` GuideStrip.header_share
- `sw/strip.py:96-97` GuideStrip.views
- `sw/strip.py:92-94` GuideStrip.opened
- `sw/strip.py:178-181` GuideStrip.poll
- `sw/strip.py:99-100` GuideStrip.is_open

## 20. How Claude comes to listen to Sublime (12 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:74-77` await_answer
- `sw/strip.py:193-195` GuideStrip.note_waiting
- `sw/guide.py:46-56` ensure
- `sw/guide.py:29-31` listening
- `sw/guide.py:34-35` running
- `sw/guide.py:38-43` find_claude
- `sw/guide.py:59-65` start
- `mcp_server/sight_walk_mcp.py:145-148` wait_for_user
- `mcp_server/sight_walk_mcp.py:81-92` call
- `sw/bridge.py:176-185` dispatch
- `sw/bridge.py:154-165` wait_for_user
- `sw/state.py:67-69` listener

## 21. Talking in the strip (10 views)

A question goes to the inbox, the answer comes back to the strip; the strip glides out.

- `sw/commands.py:43-49` SightWalkAskCommand.run
- `sw/state.py:72-77` owner
- `sw/state.py:62-64` current_bench
- `sw/strip.py:207-208` GuideStrip.context
- `sw/strip.py:210-211` GuideStrip.take_edits
- `sw/strip.py:185-191` GuideStrip.say
- `sw/strip.py:197-198` GuideStrip.show_header
- `sw/commands.py:131-134` SightWalkCloseStripCommand.run
- `sw/strip.py:147-153` GuideStrip.close
- `sw/chat.py:146-154` catch_up

## 22. Endings (10 views)

A trip hides the strip, the guide is stopped, windows close.

- `sw/strip.py:155-164` GuideStrip.vanish_later
- `sw/strip.py:166-176` GuideStrip.closed
- `sw/commands.py:140-141` SightWalkStopGuideCommand.run
- `sw/commands.py:143-144` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:68-71` stop
- `sw/commands.py:109-110` SightWalkWindowListener.on_pre_close_window
- `sw/state.py:19-22` forget
- `mcp_server/sight_walk_mcp.py:129-132` close
- `sw/bridge.py:103-108` op_close
- `sw/state.py:29-31` current_reader

## 23. Names and room (12 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-49` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:52-57` matches
- `sw/reader.py:170-174` Reader.share
- `sw/reader.py:191-199` Reader.conversation_rows
- `sw/reader.py:201-203` Reader.head
- `sw/reader.py:205-207` Reader.room
- `sw/reader.py:426-429` Reader.draw_edit_buttons
- `sw/bridge.py:98-100` op_state
- `sw/reader.py:498-501` Reader.folder
- `sw/reader.py:494-496` Reader.note_waiting

## 24. Building blocks (10 views)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-12` Item.__init__
- `sw/plan.py:18-27` Sight.__init__
- `sw/line_one.py:26-27` LineOne.first_line
- `sw/line_one.py:35-36` LineOne.views
- `sw/line_one.py:57-59` LineOne.draw_gaps
- `sw/line_one.py:72-75` LineOne.close
- `sw/twin.py:41-43` content_top
- `sw/chat.py:45-47` Guard.__init__
- `sw/commands.py:75-77` SightWalkHeaderListener.is_applicable
- `sw/commands.py:96-98` SightWalkChatListener.is_applicable

## 25. Settings and the rest of the colours (7 views)

The agent's view of the settings, and colour helpers.

- `mcp_server/sight_walk_mcp.py:135-142` settings
- `mcp_server/sight_walk_mcp.py:123-126` state
- `sw/commands.py:91-92` SightWalkScrollCommand.is_enabled
- `sw/tint.py:57-59` band_amount
- `sw/tint.py:62-66` scheme_stem
- `sw/tint.py:25-26` hex_rgb
- `sw/tint.py:129-134` apply_grey
