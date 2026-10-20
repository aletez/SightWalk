# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:45-52` plugin_loaded
- `sw/subl_mcp_http.py:142-145` start
- `sw/subl_executor.py:239-243` load_config
- `sw/subl_mcp_http.py:118-122` start_server
- `sw/subl_mcp_http.py:133-139` settings_changed
- `sw/subl_mcp_http.py:125-130` stop_server
- `sight_walk.py:62-68` plugin_unloaded
- `sw/subl_scrollbars.py:13-25` reader_focused
- `sw/state.py:45-52` close_all
- `sw/subl_mcp_http.py:148-150` stop
- `sw/subl_setup.py:70-72` SightWalkRestartCommand.run

## 2. Setting up the agent bridge (5 views)

The setup command keeps a token, writes it for poke, and puts Claude Code's registration line on the clipboard.

- `sw/subl_setup.py:32-38` SightWalkSetupCommand.run
- `sw/subl_setup.py:41-48` ensure_token
- `sw/subl_setup.py:51-57` write_config
- `sw/subl_setup.py:60-63` show_instructions
- `sw/subl_commands.py:17-24` SightWalkReplaceCommand.run

## 3. A request arrives (24 views)

From the HTTP server's thread to the show operation on Sublime's, with every check on the way.

- `sw/subl_executor.py:180-187` execute
- `sw/subl_executor.py:190-206` run_on_main
- `sw/subl_executor.py:121-135` facts
- `sw/subl_executor.py:138-147` sight_files
- `sw/subl_executor.py:150-161` sight_functions
- `sw/spec.py:118-123` functions_in
- `sw/spec.py:126-130` units_in
- `sw/spec.py:136-149` blocks_in
- `sw/spec.py:152-159` open_above
- `sw/validator.py:26-31` check
- `sw/validator.py:104-108` check_show
- `sw/validator.py:89-101` one_function
- `sw/subl_executor.py:49-55` op_show
- `sw/subl_executor.py:58-60` named
- `sw/validator.py:56-59` not_stopped
- `sw/validator.py:34-53` trip_of
- `sw/marks.py:386-398` trip_place
- `sw/ontology.py:129-137` Sight.parse
- `sw/ontology.py:160-164` Trip.__init__
- `sw/ontology.py:93-100` Network.__init__
- `sw/ontology.py:109-119` Network.problem
- `sw/validator.py:73-86` files
- `sw/spec.py:10-23` parse_spec
- `sw/subl_executor.py:31-33` file_lines

## 4. A new reader window (12 views)

The window and every view but the sights.

- `sw/subl_executor.py:36-46` new_reader
- `sw/subl_reader.py:75-105` Reader.__init__
- `sw/subl_reader.py:107-163` Reader.make_side_views
- `sw/subl_views.py:182-191` bench_font
- `sw/subl_views.py:194-198` match_font
- `sw/subl_views.py:142-149` make_blank_view
- `sw/subl_views.py:118-125` make_side_view
- `sw/subl_chat.py:74-80` start
- `sw/subl_chat.py:83-93` make_header
- `sw/subl_chat.py:148-157` make_status
- `sw/subl_vetting.py:29-36` make_tool
- `sw/state.py:23-26` register

## 5. Loading the sights (22 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/subl_reader.py:167-184` Reader.load
- `sw/subl_chat.py:252-260` catch_up
- `sw/subl_reader.py:231-241` Reader.close_sights
- `sw/subl_reader.py:243-258` Reader.build
- `sw/subl_views.py:160-164` FileCopy.__init__
- `sw/subl_views.py:167-179` make_copy
- `sw/subl_reader.py:260-280` Reader.surround
- `sw/spec.py:162-177` elided
- `sw/spec.py:190-194` block_name
- `sw/spec.py:180-187` body_indent
- `sw/words.py:140-145` lines_of
- `sw/subl_reader.py:282-289` Reader.ellipses
- `sw/subl_reader.py:291-302` Reader.draw_ellipsis
- `sw/subl_views.py:306-314` draw_ellipsis
- `sw/subl_reader.py:377-385` Reader.room_px
- `sw/subl_reader.py:304-313` Reader.grow_ellipses
- `sw/spec.py:97-112` ancestors
- `sw/spec.py:84-85` indent
- `sw/spec.py:88-94` opens_block
- `sw/spec.py:197-204` breathing
- `sw/subl_views.py:216-223` make_header
- `sw/subl_views.py:226-231` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/subl_reader.py:333-338` Reader.tint
- `sw/subl_tint.py:282-285` apply_tint
- `sw/subl_tint.py:242-248` schemes_for
- `sw/subl_tint.py:22-26` hue_for
- `sw/subl_tint.py:128-156` tinted_schemes
- `sw/subl_tint.py:41-53` load_base_scheme
- `sw/subl_tint.py:33-38` tint_color
- `sw/subl_tint.py:76-81` write_scheme
- `sw/subl_tint.py:259-274` set_schemes
- `sw/subl_tint.py:230-239` when_indexed

## 7. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/subl_reader.py:340-344` Reader.draw_gaps
- `sw/subl_reader.py:56-57` line_count
- `sw/subl_views.py:317-324` draw_gap
- `sw/subl_reader.py:359-375` Reader.make_items
- `sw/subl_views.py:234-235` line_top
- `sw/subl_views.py:238-239` header_top
- `sw/subl_reader.py:387-392` Reader.calibrate
- `sw/subl_reader.py:394-399` Reader.measure_full
- `sw/subl_reader.py:401-405` Reader.measure_half
- `sw/subl_reader.py:407-421` Reader.start
- `sw/subl_reader.py:534-537` Reader.centred_lead
- `sw/plan.py:85-90` lead
- `sw/plan.py:79-82` free_room
- `sw/plan.py:50-66` stack
- `sw/plan.py:69-76` sight_groups
- `sw/subl_reader.py:636-642` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/subl_reader.py:539-545` Reader.scroll_to
- `sw/plan.py:93-101` offset_range
- `sw/subl_geometry.py:64-67` Geometry.bench_floor
- `sw/subl_reader.py:498-510` Reader.render
- `sw/subl_geometry.py:95-126` Geometry.column_rects
- `sw/subl_geometry.py:44-48` Geometry.column
- `sw/subl_geometry.py:143-154` Geometry.sight_cells
- `sw/subl_geometry.py:139-141` Geometry.floor_height
- `sw/subl_reader.py:425-432` Reader.layout
- `sw/subl_views.py:86-113` reader_layout
- `sw/subl_views.py:76-83` to_layout

## 9. Arranging the views (16 views)

After a new layout: every view into its group, then back at its place.

- `sw/subl_reader.py:512-530` Reader.arrange
- `sw/subl_reader.py:460-465` Reader.place
- `sw/subl_reader.py:434-449` Reader.strip_in_front
- `sw/subl_geometry.py:128-137` Geometry.strip_rows
- `sw/subl_reader.py:346-357` Reader.clone
- `sw/subl_reader.py:467-496` Reader.assign_groups
- `sw/subl_views.py:63-66` hide_chrome
- `sw/subl_reader.py:577-588` Reader.scroll_views
- `sw/subl_reader.py:547-555` Reader.places
- `sw/subl_reader.py:630-634` Reader.strip_place
- `sw/subl_views.py:152-154` anchor
- `sw/subl_reader.py:885-892` Reader.draw_strip_buttons
- `sw/subl_reader.py:894-896` Reader.strip_button
- `sw/subl_reader.py:738-747` Reader.draw_edit_buttons
- `sw/subl_reader.py:733-736` Reader.title
- `sw/subl_views.py:242-254` draw_edit_button

## 10. Polling and the wheel (12 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/subl_reader.py:649-657` Reader.poll
- `sw/subl_chat.py:221-231` keep_at_bottom
- `sw/subl_chat.py:240-243` bottom_place
- `sw/subl_chat.py:234-237` kept_place
- `sw/subl_reader.py:659-666` Reader.poll_wheel
- `sw/subl_reader.py:646-647` Reader.alive
- `sw/subl_reader.py:590-613` Reader.read_wheel
- `sw/subl_reader.py:615-623` Reader.clamp_bench
- `sw/subl_reader.py:625-628` Reader.bench_edited
- `sw/subl_reader.py:557-569` Reader.wheel_places
- `sw/subl_reader.py:571-575` Reader.pinned_places
- `sw/subl_reader.py:68-71` item_top

## 11. Pointing (25 views)

The marks an answer places with its own tags, resolved to sights and lines, framed in its words, the reader scrolled to show them.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:264-296` read_marks
- `sw/marks.py:233-241` mark_attributes
- `sw/marks.py:244-261` tag_marks
- `sw/marks.py:401-412` frame_scopes
- `sw/subl_reader.py:685-694` Reader.point
- `sw/marks.py:91-117` resolve_marks
- `sw/marks.py:80-88` jump
- `sw/marks.py:18-37` resolve_target
- `sw/marks.py:46-53` sight_target
- `sw/marks.py:56-62` icon_for
- `sw/marks.py:14-15` line_y
- `sw/subl_chat.py:269-285` outline_refs
- `sw/marks.py:186-189` sight_refs
- `sw/marks.py:40-43` sight_number
- `sw/spec.py:58-64` sight_index
- `sw/spec.py:50-55` sight_name
- `sw/marks.py:386-398` trip_place
- `sw/subl_reader.py:1208-1235` Reader.follow_frame
- `sw/subl_reader.py:1312-1326` Reader.frame_regions
- `sw/subl_chat.py:263-266` blanks
- `sw/subl_reader.py:1237-1248` Reader.show_places
- `sw/subl_reader.py:1328-1345` Reader.add_to_answer
- `sw/subl_reader.py:1141-1150` Reader.follow_label
- `sw/subl_reader.py:1065-1074` Reader.show_answer

## 12. Drawing the marks (10 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/subl_reader.py:696-712` Reader.draw_gutter
- `sw/subl_reader.py:714-719` Reader.draw_strip_marks
- `sw/marks.py:153-164` strip_icons
- `sw/subl_views.py:271-280` draw_strip_icons
- `sw/marks.py:120-132` visible_lines
- `sw/marks.py:135-150` gutter_icons
- `sw/subl_views.py:259-268` draw_icons
- `sw/subl_reader.py:721-729` Reader.draw_outlines
- `sw/marks.py:71-77` icon_colour
- `sw/subl_views.py:286-299` draw_outlines

## 13. The agent says something (19 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:199-214` untag
- `sw/marks.py:426-428` line_refs
- `sw/validator.py:14-17` MARK_FIRST
- `sw/marks.py:170-172` speaks_of_code
- `sw/marks.py:167-167` CODE_TALK
- `sw/subl_reader.py:1297-1310` Reader.say
- `sw/subl_reader.py:806-823` Reader.show_headers
- `sw/subl_chat.py:100-122` show_header
- `sw/header.py:12-20` title_lines
- `sw/subl_chat.py:160-169` show_status
- `sw/subl_chat.py:191-201` say
- `sw/subl_commands.py:28-29` SightWalkInsertCommand.run
- `sw/subl_chat.py:54-71` Guard.on_text_changed
- `sw/subl_chat.py:36-44` protected_end
- `sw/subl_commands.py:264-271` SightWalkChatListener.on_modified
- `sw/subl_commands.py:279-289` SightWalkChatListener.on_post_text_command
- `sw/marks.py:415-417` clean
- `sw/subl_chat.py:288-293` shade_variables

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/subl_commands.py:387-390` SightWalkStopAnswerCommand.run
- `sw/subl_reader.py:1276-1283` Reader.stop_answer
- `sw/subl_reader.py:1285-1288` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (15 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/subl_reader.py:910-917` Reader.select_tool
- `sw/subl_vetting.py:70-86` show_tabs
- `sw/subl_vetting.py:63-67` toggle_html
- `sw/subl_vetting.py:89-91` tab_at
- `sw/subl_vetting.py:103-117` show_buttons
- `sw/subl_commands.py:249-256` SightWalkHeaderListener.on_selection_modified
- `sw/subl_geometry.py:18-20` Geometry.buttons_share
- `sw/subl_commands.py:479-482` SightWalkTogglePanningCommand.run
- `sw/subl_reader.py:952-962` Reader.toggle_panning
- `sw/subl_vetting.py:39-47` set_panning
- `sw/subl_vetting.py:50-52` content_point
- `sw/subl_reader.py:900-902` Reader.tools
- `sw/subl_reader.py:904-905` Reader.tool_view
- `sw/subl_reader.py:907-908` Reader.hidden_tools
- `sw/subl_reader.py:1184-1196` Reader.draw_map

## 16. The Map's nodes (13 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/subl_reader.py:1184-1196` Reader.draw_map
- `sw/subl_reader.py:1198-1206` Reader.answer_transitions
- `sw/subl_reader.py:1398-1405` map_style
- `sw/subl_reader.py:1250-1264` Reader.map_nodes
- `sw/subl_reader.py:49-53` fragment_of
- `sw/subl_reader.py:1266-1270` Reader.owner
- `sw/subl_reader.py:60-65` defined_name
- `sw/callmap.py:33-39` first_definition
- `sw/callmap.py:42-49` node_at
- `sw/callmap.py:28-30` Node.__init__
- `sw/callmap.py:52-59` edges
- `sw/callmap.py:42-49` node_at
- `sw/subl_vetting.py:129-137` draw_map

## 17. Drawing the Map (17 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/subl_vetting.py:129-137` draw_map
- `sw/subl_vetting.py:122-126` find_dot
- `sw/callmap.py:120-141` dot_source
- `sw/callmap.py:93-99` file_block
- `sw/callmap.py:70-73` cluster
- `sw/callmap.py:76-78` node_line
- `sw/callmap.py:81-90` sight_blocks
- `sw/callmap.py:62-63` node_id
- `sw/callmap.py:66-67` quote
- `sw/callmap.py:102-106` arrow
- `sw/callmap.py:109-117` legend
- `sw/subl_vetting.py:140-152` render
- `sw/subl_vetting.py:155-157` png_size
- `sw/subl_vetting.py:166-181` show_image
- `sw/subl_vetting.py:184-189` zoom
- `sw/subl_commands.py:472-473` SightWalkZoomMapCommand.run
- `sw/subl_vetting.py:192-195` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with here, the visible sights and the edits, and the agent receives it.

- `sw/subl_commands.py:46-53` SightWalkSendCommand.run
- `sw/subl_chat.py:204-218` take_draft
- `sw/subl_commands.py:32-40` send
- `sw/state.py:37-38` reader_for
- `sw/subl_reader.py:1347-1366` Reader.context
- `sw/subl_views.py:327-331` selected_text
- `sw/plan.py:121-124` visible_specs
- `sw/subl_reader.py:799-802` Reader.take_edits
- `sw/subl_executor.py:220-234` wait_for_user

## 19. Linking words to code (38 views)

primary+p joins words of the draft to selections in the sights, from either side; the words go out as a <here> tag, and a click on them shows their place.

- `sw/subl_commands.py:197-204` SightWalkLinkCommand.run
- `sw/subl_links.py:19-30` Links.__init__
- `sw/subl_commands.py:273-277` SightWalkChatListener.on_selection_modified
- `sw/subl_links.py:32-37` Links.note_bench
- `sw/subl_links.py:39-53` Links.note_code
- `sw/subl_links.py:55-61` Links.link_from_code
- `sw/subl_links.py:72-83` Links.link_from_bench
- `sw/subl_links.py:63-70` Links.link_either
- `sw/subl_links.py:85-103` Links.add
- `sw/subl_links.py:303-307` carets
- `sw/subl_links.py:139-149` Links.tagged
- `sw/subl_links.py:205-209` Links.places
- `sw/subl_links.py:290-300` ends
- `sw/marks.py:315-324` place_text
- `sw/subl_links.py:211-217` Links.code
- `sw/subl_links.py:278-280` Links.draft_start
- `sw/subl_links.py:219-244` Links.follow
- `sw/subl_links.py:310-316` repaint
- `sw/subl_reader.py:863-874` Reader.show_place
- `sw/subl_links.py:282-287` Links.clear
- `sw/subl_links.py:105-110` Links.show_made
- `sw/subl_links.py:112-117` Links.remove
- `sw/subl_links.py:119-124` Links.prune
- `sw/subl_links.py:126-127` Links.draft_keys
- `sw/subl_links.py:129-131` Links.bench_region
- `sw/subl_links.py:133-137` Links.by_sight
- `sw/marks.py:299-312` span_relation
- `sw/marks.py:369-383` here_tags
- `sw/subl_links.py:246-265` Links.follow_code
- `sw/subl_links.py:267-272` Links.repaint_bench
- `sw/subl_links.py:151-160` Links.ask
- `sw/subl_links.py:162-165` Links.frame_question
- `sw/subl_links.py:179-190` Links.follow_question
- `sw/subl_links.py:192-203` Links.select
- `sw/subl_links.py:167-170` Links.kept_questions
- `sw/subl_links.py:172-177` Links.restore_questions
- `sw/subl_links.py:274-276` Links.forget_shown
- `sw/subl_commands.py:326-332` SightWalkWindowListener.on_post_text_command

## 20. Opening the editor (11 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/subl_commands.py:210-220` SightWalkEditCommand.run
- `sw/subl_reader.py:766-771` Reader.sight_of
- `sw/subl_reader.py:749-764` Reader.open_editor
- `sw/subl_editor.py:24-32` Editor.__init__
- `sw/subl_views.py:69-73` wait_until_loaded
- `sw/subl_editor.py:16-20` open_live
- `sw/subl_editor.py:34-44` Editor.start
- `sw/subl_editor.py:46-58` Editor.track
- `sw/subl_editor.py:60-65` Editor.hold
- `sw/subl_geometry.py:73-82` Geometry.editor_geometry
- `sw/subl_geometry.py:84-93` Geometry.text_left

## 21. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/subl_commands.py:226-229` SightWalkCloseEditorCommand.run
- `sw/subl_reader.py:773-774` Reader.close_editor
- `sw/subl_editor.py:81-92` Editor.close
- `sw/subl_editor.py:74-79` Editor.read_back
- `sw/subl_editor.py:67-72` Editor.rows
- `sw/subl_reader.py:776-790` Reader.editor_closed
- `sw/subl_reader.py:792-797` Reader.move_range

## 22. Window events (12 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/subl_reader.py:668-681` Reader.follow_resize
- `sw/subl_reader.py:451-458` Reader.keep_bench_width
- `sw/subl_geometry.py:22-29` Geometry.spans
- `sw/subl_geometry.py:31-35` Geometry.strip_span
- `sw/subl_geometry.py:37-39` Geometry.strip_share
- `sw/subl_geometry.py:41-42` Geometry.bench_side
- `sw/state.py:55-60` render_all
- `sw/subl_executor.py:99-106` op_settings
- `sw/validator.py:174-182` check_settings
- `sw/subl_commands.py:293-295` SightWalkWindowListener.on_activated
- `sw/subl_commands.py:237-247` SightWalkHeaderListener.on_hover
- `sw/subl_chat.py:172-176` show_help

## 23. One colour scheme for the trips (17 views)

SightWalk: Select Colour Scheme: general, light or dark, only schemes of that kind, previewed live in every trip; the files' hues derived from it again, the other views take it as it is.

- `sw/subl_commands.py:61-63` SightWalkSelectColourSchemeCommand.run
- `sw/subl_commands.py:65-76` SightWalkSelectColourSchemeCommand.pick_kind
- `sw/subl_commands.py:91-94` all_schemes
- `sw/subl_tint.py:212-216` is_dark
- `sw/subl_commands.py:97-99` scheme_item
- `sw/subl_commands.py:78-80` SightWalkSelectColourSchemeCommand.preview
- `sw/subl_tint.py:251-256` refresh_all
- `sw/subl_reader.py:315-322` Reader.refresh_schemes
- `sw/subl_tint.py:100-110` chosen_scheme
- `sw/subl_tint.py:167-177` scheme_colours
- `sw/subl_tint.py:185-194` resolve_colour
- `sw/subl_tint.py:277-279` base_name
- `sw/subl_tint.py:197-209` plain_colour
- `sw/subl_tint.py:180-182` luminance
- `sw/subl_reader.py:324-331` Reader.plain_views
- `sw/subl_tint.py:219-227` apply_plain
- `sw/subl_commands.py:82-88` SightWalkSelectColourSchemeCommand.done

## 24. ctrl+tab (5 views)

The focus round the sights on screen, top to bottom, ctrl+shift+tab the other way.

- `sw/subl_commands.py:105-108` SightWalkCycleSightsCommand.run
- `sw/subl_commands.py:300-312` SightWalkWindowListener.on_window_command
- `sw/subl_reader.py:844-861` Reader.cycle
- `sw/plan.py:104-108` visible_indices
- `sw/plan.py:111-118` cycled

## 25. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/subl_commands.py:500-511` SightWalkToggleGuideCommand.run
- `sw/subl_reader.py:825-835` Reader.toggle_focus
- `sw/subl_commands.py:513-518` SightWalkToggleGuideCommand.folder
- `sw/subl_reader.py:186-190` Reader.open_empty
- `sw/subl_reader.py:192-212` Reader.empty_layout
- `sw/subl_reader.py:214-219` Reader.close_hijacker
- `sw/subl_commands.py:335-339` SightWalkWindowListener.offer_to_browser
- `sw/subl_commands.py:297-298` SightWalkWindowListener.on_load
- `sw/subl_reader.py:221-229` Reader.take_file
- `sw/subl_executor.py:88-96` op_browse
- `sw/subl_views.py:128-139` make_browser

## 26. What the agent is told (11 views, survey)

The guide's manual, the tools' descriptions and schemas it gets at its start, and the prompt a guide started from Sublime is given.

- `sw/manual.py:6-20` MANUAL: opening
- `sw/manual.py:22-50` MANUAL: Showing code
- `sw/manual.py:52-55` MANUAL: Writing code that fits the reader
- `sw/manual.py:57-107` MANUAL: Conversation
- `sw/manual.py:109-156` MANUAL: Indicators
- `sw/manual.py:159-162` tool
- `sw/manual.py:165-168` TRANSITION
- `sw/manual.py:170-204` TOOLS
- `sw/validator.py:11-13` TRANSITION_FORM
- `sw/subl_guide.py:20-25` PROMPT
- `sw/permissions.py:8-19` FIELDS

## 27. What the validator refuses (16 views, survey)

Every refusal of the guide's calls, judged before the executor acts, with the facts it is given; each message says what to do instead.

- `sw/validator.py:26-31` check
- `sw/validator.py:56-59` not_stopped
- `sw/validator.py:62-64` trip_open
- `sw/validator.py:67-70` ready
- `sw/validator.py:73-86` files
- `sw/validator.py:104-108` check_show
- `sw/validator.py:111-116` check_open_trip
- `sw/subl_executor.py:164-173` trip_file
- `sw/validator.py:119-140` check_say
- `sw/validator.py:143-147` mask
- `sw/validator.py:150-156` crowded_lines
- `sw/validator.py:159-160` check_state
- `sw/validator.py:163-165` check_close
- `sw/validator.py:168-171` check_browse
- `sw/validator.py:174-182` check_settings
- `sw/validator.py:185-186` check_wait

## 28. One tool call over HTTP (13 views)

From the request to the reply: the token checked, the JSON-RPC message answered, the tool run on Sublime's thread.

- `sw/subl_mcp_http.py:94-105` Handler.do_POST
- `sw/subl_mcp_http.py:78-81` Handler.authorized
- `sw/subl_mcp_http.py:65-74` reply
- `sw/subl_mcp_http.py:50-62` answer
- `sw/manual.py:159-162` tool
- `sw/subl_mcp_http.py:38-47` tool_result
- `sw/subl_mcp_http.py:23-35` call_tool
- `sw/subl_executor.py:209-217` wait_until_ready
- `sw/subl_executor.py:190-206` run_on_main
- `sw/subl_mcp_http.py:83-92` Handler.send
- `sw/subl_mcp_http.py:107-108` Handler.do_GET
- `sw/subl_mcp_http.py:110-112` Handler.do_DELETE
- `sw/subl_mcp_http.py:114-115` Handler.log_message

## 29. How Claude comes to listen to Sublime (7 views)

When no agent listens, asking the guide starts one; it calls wait_for_user through the bridge and waits on the shared inbox.

- `sw/subl_guide.py:97-102` await_answer
- `sw/subl_guide.py:51-60` ensure
- `sw/subl_guide.py:34-36` listening
- `sw/subl_guide.py:39-40` running
- `sw/subl_guide.py:43-48` find_claude
- `sw/subl_guide.py:63-75` start
- `sw/subl_executor.py:220-234` wait_for_user

## 30. Here (2 views)

The caret or a selection in a sight becomes here.

- `sw/subl_commands.py:314-324` SightWalkWindowListener.on_selection_modified
- `sw/subl_reader.py:837-842` Reader.note_selection

## 31. Words in two languages (9 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/subl_commands.py:463-466` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:55-59` settings_changed
- `sw/words.py:135-137` set_language
- `sw/state.py:55-60` render_all
- `sw/words.py:131-132` word
- `sw/subl_chat.py:30-33` help_html
- `sw/subl_views.py:33-35` button_html
- `sw/subl_commands.py:548-560` SightWalkCompareFontsCommand.run
- `sw/subl_commands.py:563-571` kept_conversation

## 32. Endings (17 views, survey)

The guide is stopped, windows close.

- `sw/subl_commands.py:488-489` SightWalkStopGuideCommand.run
- `sw/subl_commands.py:491-492` SightWalkStopGuideCommand.is_enabled
- `sw/subl_guide.py:90-94` stop
- `sw/subl_guide.py:78-87` stop_when_idle
- `sw/subl_commands.py:341-345` SightWalkWindowListener.on_pre_close_window
- `sw/subl_commands.py:348-350` clear_schemes_if_unused
- `sw/subl_tint.py:300-304` first_load
- `sw/subl_tint.py:307-336` clear_schemes
- `sw/subl_tint.py:72-73` scheme_folder
- `sw/subl_commands.py:300-312` SightWalkWindowListener.on_window_command
- `sw/subl_commands.py:394-396` SightWalkCloseTripCommand.run
- `sw/subl_commands.py:374-377` SightWalkResetSightsCommand.run
- `sw/subl_reader.py:876-883` Reader.reset_sights
- `sw/subl_commands.py:379-381` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:29-34` forget
- `sw/subl_executor.py:83-85` op_close
- `sw/state.py:41-42` current_reader

## 33. Names and room (12 views, survey)

How files and sights are named, and how much room the Sights and the bench get.

- `sw/spec.py:67-73` sight_title
- `sw/spec.py:37-44` display_path
- `sw/spec.py:26-34` repo_root
- `sw/spec.py:76-81` matches
- `sw/subl_geometry.py:12-16` Geometry.share
- `sw/subl_geometry.py:50-58` Geometry.conversation_rows
- `sw/subl_geometry.py:60-62` Geometry.head
- `sw/subl_geometry.py:69-71` Geometry.room
- `sw/subl_views.py:207-212` smaller
- `sw/subl_executor.py:78-80` op_state
- `sw/subl_reader.py:1290-1295` Reader.folder
- `sw/subl_reader.py:1272-1274` Reader.note_waiting

## 34. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-15` Item.__init__
- `sw/plan.py:22-35` Pane.__init__
- `sw/plan.py:37-39` Pane.spec
- `sw/plan.py:41-43` Pane.items
- `sw/plan.py:45-47` Pane.all_views
- `sw/subl_views.py:45-46` kept
- `sw/subl_views.py:49-54` phantoms
- `sw/subl_views.py:57-58` forget
- `sw/subl_chat.py:50-52` Guard.__init__
- `sw/subl_commands.py:233-235` SightWalkHeaderListener.is_applicable
- `sw/subl_commands.py:260-262` SightWalkChatListener.is_applicable

## 35. Settings and the rest of the colours (6 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/subl_tint.py:84-86` band_amount
- `sw/subl_tint.py:59-69` from_tm_theme
- `sw/subl_tint.py:113-125` resolved_scheme
- `sw/subl_tint.py:89-93` scheme_stem
- `sw/subl_tint.py:29-30` hex_rgb
- `sw/subl_tint.py:288-293` apply_grey

## 36. The ontology: collections and sights (15 views, survey)

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

## 37. The ontology: networks (17 views, survey)

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

## 38. An informator and its tour (29 views)

Open Tour: an informator's tours to choose from, the informator read from its files, its trips in the tour's order in the Tour tab, a trip opened from it, its conversation kept, a box ticked by hand.

- `sw/subl_commands.py:404-410` SightWalkOpenTourCommand.run
- `sw/subl_commands.py:419-432` tour_choices
- `sw/subl_commands.py:435-445` found_files
- `sw/subl_commands.py:448-449` read_name
- `sw/subl_commands.py:452-457` read_field
- `sw/subl_commands.py:412-416` SightWalkOpenTourCommand.open
- `sw/words.py:148-155` trips_count
- `sw/subl_reader.py:966-980` Reader.open_tour
- `sw/subl_reader.py:1389-1391` read_json
- `sw/ontology.py:303-309` tour_from
- `sw/ontology.py:282-286` informator_from
- `sw/ontology.py:266-269` trip_from
- `sw/ontology.py:249-257` transition_from
- `sw/ontology.py:212-227` tour
- `sw/ontology.py:230-238` visit
- `sw/subl_vetting.py:219-225` read_walked
- `sw/subl_reader.py:982-996` Reader.tour_link
- `sw/subl_reader.py:1026-1036` Reader.keep_transcript
- `sw/subl_reader.py:1038-1046` Reader.kept_marks
- `sw/subl_reader.py:1048-1050` Reader.line_text
- `sw/subl_reader.py:1052-1063` Reader.restore_marks
- `sw/subl_reader.py:1369-1373` kept_frame
- `sw/subl_reader.py:1376-1378` transcripts_path
- `sw/subl_reader.py:1381-1386` read_transcripts
- `sw/subl_chat.py:246-249` set_transcript
- `sw/ontology.py:289-293` dumps
- `sw/subl_vetting.py:228-237` save_walked
- `sw/subl_reader.py:1152-1154` Reader.draw_tour
- `sw/subl_vetting.py:200-216` show_tour

## 39. Trip files (6 views)

A trip opened from its file by the guide, and the files written for an informator.

- `sw/subl_executor.py:109-116` op_open_trip
- `sw/ontology.py:266-269` trip_from
- `sw/ontology.py:260-263` trip_data
- `sw/ontology.py:244-246` transition_data
- `sw/ontology.py:272-279` informator_data
- `sw/ontology.py:296-300` tour_data

## 40. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/subl_reader.py:243-258` Reader.build
- `sw/subl_asked.py:33-44` draw
- `sw/subl_asked.py:20-30` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 41. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/subl_asked.py:47-57` mark
- `sw/subl_asked.py:73-80` popup_html
- `sw/subl_asked.py:83-84` escape
- `sw/subl_commands.py:524-526` SightWalkSightListener.is_applicable
- `sw/subl_commands.py:528-530` SightWalkSightListener.on_hover
- `sw/subl_asked.py:87-92` show_popup
- `sw/subl_asked.py:60-62` paint
- `sw/subl_asked.py:65-70` toggle
- `sw/subl_commands.py:536-537` SightWalkToggleSentinelsCommand.run

## 42. The guide's permissions (14 views)

The Permissions tab: a field ticked, remembered or not, and the guide SightWalk started restarted while it waits with the tools allowed now.

- `sw/subl_reader.py:1156-1159` Reader.draw_permissions
- `sw/subl_vetting.py:245-265` show_permissions
- `sw/subl_reader.py:1161-1176` Reader.permission_link
- `sw/subl_vetting.py:268-270` show_tip
- `sw/subl_guide.py:126-132` toggle
- `sw/permissions.py:37-39` remembered
- `sw/subl_guide.py:135-146` restart
- `sw/subl_guide.py:107-111` chosen
- `sw/subl_guide.py:114-116` folders
- `sw/permissions.py:23-34` allowed_tools
- `sw/permissions.py:42-44` reminders
- `sw/subl_guide.py:149-151` ours
- `sw/subl_reader.py:1178-1182` Reader.add_folder
- `sw/subl_guide.py:119-123` set_folders

## 43. The tools over the window (5 views)

[⤢] in the Tools header lays the tools over almost the whole window under the top headers, kept apart; [Restore size] in the trip's header brings them back. Hovering a button says what it does.

- `sw/subl_reader.py:919-929` Reader.toggle_maximized
- `sw/subl_commands.py:356-359` SightWalkToggleMaximizedCommand.run
- `sw/subl_reader.py:931-950` Reader.arrange_maximized
- `sw/subl_vetting.py:97-100` buttons_help
- `sw/subl_chat.py:179-188` show_trip_help

## 44. Back and forward through trips (14 views)

◀ ▶ in the Sights' header, primary+[ and primary+]: each trip the guide shows goes into the window's history with its own conversation, starting from the question that called it; a step keeps the conversation shown and brings the other trip's back.

- `sw/subl_reader.py:1000-1004` Reader.visit
- `sw/history.py:38-44` last_exchange
- `sw/history.py:7-9` History.__init__
- `sw/history.py:20-25` History.visit
- `sw/subl_reader.py:1012-1015` Reader.leave
- `sw/history.py:14-18` History.keep
- `sw/history.py:11-12` History.current
- `sw/subl_reader.py:1017-1024` Reader.enter
- `sw/subl_chat.py:137-142` nav_phantom
- `sw/subl_commands.py:365-368` SightWalkStepCommand.run
- `sw/subl_reader.py:1006-1010` Reader.step
- `sw/history.py:27-28` History.can
- `sw/history.py:30-35` History.go
- `sw/subl_chat.py:125-129` help_or_link

## 45. Driving a trip from the terminal (7 views)

Tests without mouse or keys, in the guide's notation: sight_walk_fill sets the draft, whose <here> tags become links, sight_walk_select selects places, (>) the draft, and sight_walk_send_draft sends it.

- `sw/subl_commands.py:121-138` SightWalkFillCommand.run
- `sw/marks.py:348-366` read_here
- `sw/subl_commands.py:168-180` place_region
- `sw/marks.py:332-345` parse_place
- `sw/subl_commands.py:145-156` SightWalkSelectCommand.run
- `sw/subl_commands.py:183-190` note_selection
- `sw/subl_commands.py:162-165` SightWalkSendDraftCommand.run

## 46. The bench's answers listed (9 views)

The Answers tab: the bench's questions and answers by their first words; a click shows one's icons or places and brings it into the bench, a second click hides them.

- `sw/subl_reader.py:1112-1114` Reader.draw_answers
- `sw/subl_reader.py:1095-1110` Reader.bench_rows
- `sw/answers.py:9-19` entries
- `sw/subl_reader.py:1076-1086` Reader.answer_marks
- `sw/subl_vetting.py:275-290` show_answers
- `sw/subl_vetting.py:293-294` html_escape
- `sw/subl_reader.py:1116-1132` Reader.answer_link
- `sw/subl_reader.py:1088-1091` Reader.hide_answer
- `sw/subl_reader.py:1134-1139` Reader.scroll_bench
