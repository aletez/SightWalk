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
- `sw/commands.py:14-21` SightWalkReplaceCommand.run
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
- `sw/reader.py:29-43` Reader.__init__
- `sw/reader.py:45-58` Reader.make_side_views
- `sw/views.py:83-91` make_blank_view
- `sw/views.py:73-80` make_side_view
- `sw/chat.py:63-69` start
- `sw/chat.py:72-81` make_header
- `sw/vetting.py:9-14` make
- `sw/state.py:14-16` register

## 5. Loading the sights (10 views)

Files opened, each sight's views made; a sight at line 1 gets its two extra views.

- `sw/reader.py:62-72` Reader.load
- `sw/reader.py:74-84` Reader.close_sights
- `sw/views.py:36-40` wait_until_loaded
- `sw/reader.py:86-101` Reader.build
- `sw/views.py:99-107` prepare_code_view
- `sw/views.py:127-133` make_header
- `sw/views.py:136-141` write_header
- `sw/line_one.py:21-24` LineOne.__init__
- `sw/twin.py:18-29` make
- `sw/twin.py:32-38` fill

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/reader.py:103-107` Reader.tint
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

- `sw/reader.py:109-114` Reader.draw_gaps
- `sw/views.py:189-196` draw_gap
- `sw/reader.py:116-124` Reader.make_items
- `sw/line_one.py:16-17` line_top
- `sw/views.py:144-145` header_top
- `sw/reader.py:126-131` Reader.calibrate
- `sw/reader.py:133-138` Reader.measure_full
- `sw/reader.py:140-144` Reader.measure_half
- `sw/reader.py:146-149` Reader.start
- `sw/plan.py:34-38` stack

## 8. The layout (10 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/reader.py:310-315` Reader.scroll_to
- `sw/plan.py:41-48` max_offset
- `sw/reader.py:285-293` Reader.render
- `sw/reader.py:218-232` Reader.column_rects
- `sw/reader.py:184-188` Reader.column
- `sw/reader.py:234-248` Reader.sight_cells
- `sw/line_one.py:43-55` LineOne.rects
- `sw/reader.py:250-256` Reader.layout
- `sw/views.py:53-68` reader_layout
- `sw/views.py:43-50` to_layout

## 9. Arranging the views (9 views)

After a new layout: every view into its group, then back at its place.

- `sw/reader.py:295-306` Reader.arrange
- `sw/reader.py:266-269` Reader.place
- `sw/reader.py:271-283` Reader.assign_groups
- `sw/views.py:30-33` hide_chrome
- `sw/reader.py:329-334` Reader.scroll_views
- `sw/reader.py:317-327` Reader.places
- `sw/line_one.py:38-41` LineOne.places
- `sw/views.py:94-96` anchor
- `sw/views.py:148-159` draw_edit_button

## 10. Polling and the wheel (9 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/reader.py:355-366` Reader.poll
- `sw/chat.py:130-143` keep_at_bottom
- `sw/reader.py:151-165` Reader.measure_gutter
- `sw/line_one.py:29-33` LineOne.misalignment
- `sw/reader.py:368-375` Reader.poll_wheel
- `sw/reader.py:352-353` Reader.alive
- `sw/reader.py:336-348` Reader.read_wheel
- `sw/reader.py:317-327` Reader.places
- `sw/reader.py:310-315` Reader.scroll_to

## 11. Pointing (10 views)

The agent's marks resolved to sights and lines, the reader scrolled to show them.

- `mcp_server/sight_walk_mcp.py:110-116` point
- `sw/bridge.py:93-95` op_point
- `sw/state.py:34-40` require_ready
- `sw/reader.py:389-397` Reader.point
- `sw/marks.py:66-81` resolve_marks
- `sw/marks.py:56-63` jump
- `sw/marks.py:16-35` resolve_target
- `sw/marks.py:38-44` sight_target
- `sw/marks.py:47-53` icon_for
- `sw/marks.py:12-13` line_y

## 12. Drawing the marks (8 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/reader.py:399-412` Reader.draw_gutter
- `sw/marks.py:84-96` visible_lines
- `sw/marks.py:99-110` gutter_icons
- `sw/views.py:164-173` draw_icons
- `sw/line_one.py:61-62` LineOne.draw_icons
- `sw/reader.py:414-421` Reader.draw_outlines
- `sw/views.py:176-186` draw_outlines
- `sw/line_one.py:64-66` LineOne.draw_outlines

## 13. The agent says something (11 views)

A reply reaches the Vetting Bench past the transcript guard.

- `mcp_server/sight_walk_mcp.py:103-107` say
- `sw/bridge.py:85-90` op_say
- `sw/reader.py:493-497` Reader.say
- `sw/reader.py:489-491` Reader.show_headers
- `sw/chat.py:84-95` show_header
- `sw/header.py:11-21` title_lines
- `sw/chat.py:105-111` say
- `sw/commands.py:25-26` SightWalkInsertCommand.run
- `sw/chat.py:49-60` Guard.on_text_changed
- `sw/chat.py:31-39` protected_end
- `sw/commands.py:101-103` SightWalkChatListener.on_modified

## 14. The user sends a message (9 views)

The draft becomes a message, with the focus and the visible sights, and the agent receives it.

- `sw/commands.py:32-39` SightWalkSendCommand.run
- `sw/state.py:25-26` reader_for
- `sw/reader.py:499-504` Reader.context
- `sw/plan.py:51-59` focus_sight
- `sw/plan.py:62-65` visible_specs
- `sw/chat.py:114-127` take_draft
- `sw/reader.py:482-485` Reader.take_edits
- `sw/bridge.py:154-165` wait_for_user
- `mcp_server/sight_walk_mcp.py:141-144` wait_for_user

## 15. Opening the editor (9 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/commands.py:56-63` SightWalkEditCommand.run
- `sw/reader.py:441-446` Reader.sight_of
- `sw/plan.py:29-31` Sight.code_views
- `sw/reader.py:430-439` Reader.open_editor
- `sw/editor.py:26-37` Editor.__init__
- `sw/editor.py:13-22` clone_for_editing
- `sw/editor.py:39-51` Editor.track
- `sw/editor.py:53-58` Editor.hold
- `sw/reader.py:208-216` Reader.editor_geometry

## 16. Closing the editor (9 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/commands.py:69-72` SightWalkCloseEditorCommand.run
- `sw/reader.py:448-449` Reader.close_editor
- `sw/editor.py:74-84` Editor.close
- `sw/editor.py:67-72` Editor.read_back
- `sw/editor.py:60-65` Editor.rows
- `sw/reader.py:451-472` Reader.editor_closed
- `sw/reader.py:474-480` Reader.move_range
- `sw/line_one.py:68-70` LineOne.refill
- `sw/twin.py:32-38` fill

## 17. Window events (10 views)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/reader.py:377-385` Reader.follow_resize
- `sw/reader.py:258-264` Reader.keep_bench_width
- `sw/reader.py:175-182` Reader.spans
- `sw/state.py:55-59` render_all
- `sw/bridge.py:121-128` op_settings
- `sw/bridge.py:111-118` check_setting
- `sw/commands.py:107-108` SightWalkWindowListener.on_activated
- `sw/commands.py:86-90` SightWalkScrollCommand.run
- `sw/commands.py:80-82` SightWalkHeaderListener.on_hover
- `sw/chat.py:98-102` show_help

## 18. Asking the guide on a selection (10 views)

The Vetting strip opens on the selection's side, with the conversation so far.

- `sw/commands.py:117-123` SightWalkAskGuideCommand.run
- `sw/commands.py:132-133` SightWalkAskGuideCommand.is_enabled
- `sw/strip.py:64-75` GuideStrip.__init__
- `sw/strip.py:33-38` strip_side
- `sw/strip.py:41-49` selection_x
- `sw/strip.py:52-60` selection_spec
- `sw/strip.py:77-89` GuideStrip.make_views
- `sw/views.py:110-115` bench_font
- `sw/views.py:118-122` match_font
- `sw/commands.py:125-130` SightWalkAskGuideCommand.folder

## 19. The strip glides (10 views)

Eased frames: the window's own cells shift aside while the strip comes in.

- `sw/strip.py:125-137` GuideStrip.glide
- `sw/strip.py:22-24` ease
- `sw/strip.py:139-144` GuideStrip.place
- `sw/strip.py:101-113` GuideStrip.rects
- `sw/strip.py:27-30` cell_rects
- `sw/strip.py:115-123` GuideStrip.header_share
- `sw/strip.py:95-96` GuideStrip.views
- `sw/strip.py:91-93` GuideStrip.opened
- `sw/strip.py:177-180` GuideStrip.poll
- `sw/strip.py:98-99` GuideStrip.is_open

## 20. How Claude comes to listen to Sublime (10 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/guide.py:44-54` ensure
- `sw/guide.py:27-29` listening
- `sw/guide.py:32-33` running
- `sw/guide.py:36-41` find_claude
- `sw/guide.py:57-63` start
- `mcp_server/sight_walk_mcp.py:141-144` wait_for_user
- `mcp_server/sight_walk_mcp.py:81-92` call
- `sw/bridge.py:176-185` dispatch
- `sw/bridge.py:154-165` wait_for_user
- `sw/state.py:67-69` listener

## 21. Talking in the strip (10 views)

A question goes to the inbox, the answer comes back to the strip; the strip glides out.

- `sw/commands.py:45-50` SightWalkAskCommand.run
- `sw/state.py:72-77` owner
- `sw/state.py:62-64` current_bench
- `sw/strip.py:195-196` GuideStrip.context
- `sw/strip.py:198-199` GuideStrip.take_edits
- `sw/strip.py:184-189` GuideStrip.say
- `sw/strip.py:191-193` GuideStrip.say_status
- `sw/commands.py:139-142` SightWalkCloseStripCommand.run
- `sw/strip.py:146-152` GuideStrip.close
- `sw/chat.py:146-154` catch_up

## 22. Endings (10 views)

A trip hides the strip, the guide is stopped, windows close.

- `sw/strip.py:154-163` GuideStrip.vanish_later
- `sw/strip.py:165-175` GuideStrip.closed
- `sw/commands.py:148-149` SightWalkStopGuideCommand.run
- `sw/commands.py:151-152` SightWalkStopGuideCommand.is_enabled
- `sw/guide.py:66-69` stop
- `sw/commands.py:110-111` SightWalkWindowListener.on_pre_close_window
- `sw/state.py:19-22` forget
- `mcp_server/sight_walk_mcp.py:125-128` close
- `sw/bridge.py:103-108` op_close
- `sw/state.py:29-31` current_reader

## 23. Names and room (10 views)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:46-49` sight_title
- `sw/spec.py:36-43` display_path
- `sw/spec.py:25-33` repo_root
- `sw/spec.py:52-57` matches
- `sw/reader.py:169-173` Reader.share
- `sw/reader.py:190-198` Reader.conversation_rows
- `sw/reader.py:200-202` Reader.head
- `sw/reader.py:204-206` Reader.room
- `sw/reader.py:425-428` Reader.draw_edit_buttons
- `sw/bridge.py:98-100` op_state

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
- `sw/commands.py:76-78` SightWalkHeaderListener.is_applicable
- `sw/commands.py:97-99` SightWalkChatListener.is_applicable

## 25. Settings and the rest of the colours (7 views)

The agent's view of the settings, and colour helpers.

- `mcp_server/sight_walk_mcp.py:131-138` settings
- `mcp_server/sight_walk_mcp.py:119-122` state
- `sw/commands.py:92-93` SightWalkScrollCommand.is_enabled
- `sw/tint.py:57-59` band_amount
- `sw/tint.py:62-66` scheme_stem
- `sw/tint.py:25-26` hex_rgb
- `sw/tint.py:129-134` apply_grey
