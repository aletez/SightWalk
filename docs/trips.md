# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:44-51` plugin_loaded
- `sw/subl_mcp_http.py:142-145` start
- `sw/subl_executor.py:239-243` load_config
- `sw/subl_mcp_http.py:118-122` start_server
- `sw/subl_mcp_http.py:133-139` settings_changed
- `sw/subl_mcp_http.py:125-130` stop_server
- `sight_walk.py:61-67` plugin_unloaded
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
- `sw/subl_reader.py:75-104` Reader.__init__
- `sw/subl_reader.py:106-157` Reader.make_side_views
- `sw/subl_views.py:179-188` bench_font
- `sw/subl_views.py:191-195` match_font
- `sw/subl_views.py:139-146` make_blank_view
- `sw/subl_views.py:115-122` make_side_view
- `sw/subl_chat.py:72-78` start
- `sw/subl_chat.py:81-91` make_header
- `sw/subl_chat.py:146-155` make_status
- `sw/subl_vetting.py:29-36` make_tool
- `sw/state.py:23-26` register

## 5. Loading the sights (22 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/subl_reader.py:161-178` Reader.load
- `sw/subl_chat.py:238-246` catch_up
- `sw/subl_reader.py:224-234` Reader.close_sights
- `sw/subl_reader.py:236-251` Reader.build
- `sw/subl_views.py:157-161` FileCopy.__init__
- `sw/subl_views.py:164-176` make_copy
- `sw/subl_reader.py:253-273` Reader.surround
- `sw/spec.py:162-177` elided
- `sw/spec.py:190-194` block_name
- `sw/spec.py:180-187` body_indent
- `sw/words.py:133-138` lines_of
- `sw/subl_reader.py:275-282` Reader.ellipses
- `sw/subl_reader.py:284-295` Reader.draw_ellipsis
- `sw/subl_views.py:303-311` draw_ellipsis
- `sw/subl_reader.py:369-377` Reader.room_px
- `sw/subl_reader.py:297-306` Reader.grow_ellipses
- `sw/spec.py:97-112` ancestors
- `sw/spec.py:84-85` indent
- `sw/spec.py:88-94` opens_block
- `sw/spec.py:197-204` breathing
- `sw/subl_views.py:213-220` make_header
- `sw/subl_views.py:223-228` write_header

## 6. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/subl_reader.py:325-330` Reader.tint
- `sw/subl_tint.py:273-276` apply_tint
- `sw/subl_tint.py:233-239` schemes_for
- `sw/subl_tint.py:22-26` hue_for
- `sw/subl_tint.py:128-155` tinted_schemes
- `sw/subl_tint.py:41-53` load_base_scheme
- `sw/subl_tint.py:33-38` tint_color
- `sw/subl_tint.py:76-81` write_scheme
- `sw/subl_tint.py:250-265` set_schemes
- `sw/subl_tint.py:221-230` when_indexed

## 7. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/subl_reader.py:332-336` Reader.draw_gaps
- `sw/subl_reader.py:56-57` line_count
- `sw/subl_views.py:314-321` draw_gap
- `sw/subl_reader.py:351-367` Reader.make_items
- `sw/subl_views.py:231-232` line_top
- `sw/subl_views.py:235-236` header_top
- `sw/subl_reader.py:379-384` Reader.calibrate
- `sw/subl_reader.py:386-391` Reader.measure_full
- `sw/subl_reader.py:393-397` Reader.measure_half
- `sw/subl_reader.py:399-413` Reader.start
- `sw/subl_reader.py:524-527` Reader.centred_lead
- `sw/plan.py:85-90` lead
- `sw/plan.py:79-82` free_room
- `sw/plan.py:50-66` stack
- `sw/plan.py:69-76` sight_groups
- `sw/subl_reader.py:630-636` Reader.write_strip

## 8. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/subl_reader.py:529-535` Reader.scroll_to
- `sw/plan.py:93-101` offset_range
- `sw/subl_geometry.py:60-63` Geometry.bench_floor
- `sw/subl_reader.py:490-500` Reader.render
- `sw/subl_geometry.py:91-122` Geometry.column_rects
- `sw/subl_geometry.py:40-44` Geometry.column
- `sw/subl_geometry.py:139-150` Geometry.sight_cells
- `sw/subl_geometry.py:135-137` Geometry.floor_height
- `sw/subl_reader.py:417-424` Reader.layout
- `sw/subl_views.py:86-110` reader_layout
- `sw/subl_views.py:76-83` to_layout

## 9. Arranging the views (16 views)

After a new layout: every view into its group, then back at its place.

- `sw/subl_reader.py:502-520` Reader.arrange
- `sw/subl_reader.py:452-457` Reader.place
- `sw/subl_reader.py:426-441` Reader.strip_in_front
- `sw/subl_geometry.py:124-133` Geometry.strip_rows
- `sw/subl_reader.py:338-349` Reader.clone
- `sw/subl_reader.py:459-488` Reader.assign_groups
- `sw/subl_views.py:63-66` hide_chrome
- `sw/subl_reader.py:567-578` Reader.scroll_views
- `sw/subl_reader.py:537-545` Reader.places
- `sw/subl_reader.py:624-628` Reader.strip_place
- `sw/subl_views.py:149-151` anchor
- `sw/subl_reader.py:873-880` Reader.draw_strip_buttons
- `sw/subl_reader.py:882-884` Reader.strip_button
- `sw/subl_reader.py:729-738` Reader.draw_edit_buttons
- `sw/subl_reader.py:724-727` Reader.title
- `sw/subl_views.py:239-251` draw_edit_button

## 10. Polling and the wheel (12 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/subl_reader.py:643-651` Reader.poll
- `sw/subl_chat.py:207-217` keep_at_bottom
- `sw/subl_chat.py:226-229` bottom_place
- `sw/subl_chat.py:220-223` kept_place
- `sw/subl_reader.py:653-660` Reader.poll_wheel
- `sw/subl_reader.py:640-641` Reader.alive
- `sw/subl_reader.py:580-607` Reader.read_wheel
- `sw/subl_reader.py:609-617` Reader.clamp_bench
- `sw/subl_reader.py:619-622` Reader.bench_edited
- `sw/subl_reader.py:547-559` Reader.wheel_places
- `sw/subl_reader.py:561-565` Reader.pinned_places
- `sw/subl_reader.py:68-71` item_top

## 11. Pointing (25 views)

The marks an answer places with its own tags, resolved to sights and lines, framed in its words, the reader scrolled to show them.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:264-296` read_marks
- `sw/marks.py:233-241` mark_attributes
- `sw/marks.py:244-261` tag_marks
- `sw/marks.py:401-412` frame_scopes
- `sw/subl_reader.py:676-685` Reader.point
- `sw/marks.py:91-117` resolve_marks
- `sw/marks.py:80-88` jump
- `sw/marks.py:18-37` resolve_target
- `sw/marks.py:46-53` sight_target
- `sw/marks.py:56-62` icon_for
- `sw/marks.py:14-15` line_y
- `sw/subl_chat.py:255-271` outline_refs
- `sw/marks.py:186-189` sight_refs
- `sw/marks.py:40-43` sight_number
- `sw/spec.py:58-64` sight_index
- `sw/spec.py:50-55` sight_name
- `sw/marks.py:386-398` trip_place
- `sw/subl_reader.py:1163-1190` Reader.follow_frame
- `sw/subl_reader.py:1267-1281` Reader.frame_regions
- `sw/subl_chat.py:249-252` blanks
- `sw/subl_reader.py:1192-1203` Reader.show_places
- `sw/subl_reader.py:1283-1300` Reader.add_to_answer
- `sw/subl_reader.py:1096-1105` Reader.follow_label
- `sw/subl_reader.py:1020-1029` Reader.show_answer

## 12. Drawing the marks (10 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/subl_reader.py:687-703` Reader.draw_gutter
- `sw/subl_reader.py:705-710` Reader.draw_strip_marks
- `sw/marks.py:153-164` strip_icons
- `sw/subl_views.py:268-277` draw_strip_icons
- `sw/marks.py:120-132` visible_lines
- `sw/marks.py:135-150` gutter_icons
- `sw/subl_views.py:256-265` draw_icons
- `sw/subl_reader.py:712-720` Reader.draw_outlines
- `sw/marks.py:71-77` icon_colour
- `sw/subl_views.py:283-296` draw_outlines

## 13. The agent says something (19 views)

A reply reaches the Vetting Bench past the transcript guard; the status line follows the topic.

- `sw/subl_executor.py:67-75` op_say
- `sw/marks.py:199-214` untag
- `sw/marks.py:426-428` line_refs
- `sw/validator.py:14-17` MARK_FIRST
- `sw/marks.py:170-172` speaks_of_code
- `sw/marks.py:167-167` CODE_TALK
- `sw/subl_reader.py:1252-1265` Reader.say
- `sw/subl_reader.py:797-811` Reader.show_headers
- `sw/subl_chat.py:98-120` show_header
- `sw/header.py:12-20` title_lines
- `sw/subl_chat.py:158-167` show_status
- `sw/subl_chat.py:177-187` say
- `sw/subl_commands.py:28-29` SightWalkInsertCommand.run
- `sw/subl_chat.py:52-69` Guard.on_text_changed
- `sw/subl_chat.py:34-42` protected_end
- `sw/subl_commands.py:249-256` SightWalkChatListener.on_modified
- `sw/subl_commands.py:264-274` SightWalkChatListener.on_post_text_command
- `sw/marks.py:415-417` clean
- `sw/subl_chat.py:274-279` shade_variables

## 14. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/subl_commands.py:363-366` SightWalkStopAnswerCommand.run
- `sw/subl_reader.py:1231-1238` Reader.stop_answer
- `sw/subl_reader.py:1240-1243` Reader.withdraw_unread_messages

## 15. The Tools pane's tabs (12 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/subl_reader.py:898-905` Reader.select_tool
- `sw/subl_vetting.py:73-101` show_tabs
- `sw/subl_vetting.py:66-70` toggle_html
- `sw/subl_vetting.py:104-120` align_mark
- `sw/subl_commands.py:455-458` SightWalkTogglePanningCommand.run
- `sw/subl_reader.py:907-917` Reader.toggle_panning
- `sw/subl_vetting.py:39-47` set_panning
- `sw/subl_vetting.py:50-52` content_point
- `sw/subl_reader.py:888-890` Reader.tools
- `sw/subl_reader.py:892-893` Reader.tool_view
- `sw/subl_reader.py:895-896` Reader.hidden_tools
- `sw/subl_reader.py:1139-1151` Reader.draw_map

## 16. The Map's nodes (13 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/subl_reader.py:1139-1151` Reader.draw_map
- `sw/subl_reader.py:1153-1161` Reader.answer_transitions
- `sw/subl_reader.py:1353-1360` map_style
- `sw/subl_reader.py:1205-1219` Reader.map_nodes
- `sw/subl_reader.py:49-53` fragment_of
- `sw/subl_reader.py:1221-1225` Reader.owner
- `sw/subl_reader.py:60-65` defined_name
- `sw/callmap.py:33-39` first_definition
- `sw/callmap.py:42-49` node_at
- `sw/callmap.py:28-30` Node.__init__
- `sw/callmap.py:52-59` edges
- `sw/callmap.py:42-49` node_at
- `sw/subl_vetting.py:132-140` draw_map

## 17. Drawing the Map (17 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/subl_vetting.py:132-140` draw_map
- `sw/subl_vetting.py:125-129` find_dot
- `sw/callmap.py:120-141` dot_source
- `sw/callmap.py:93-99` file_block
- `sw/callmap.py:70-73` cluster
- `sw/callmap.py:76-78` node_line
- `sw/callmap.py:81-90` sight_blocks
- `sw/callmap.py:62-63` node_id
- `sw/callmap.py:66-67` quote
- `sw/callmap.py:102-106` arrow
- `sw/callmap.py:109-117` legend
- `sw/subl_vetting.py:143-155` render
- `sw/subl_vetting.py:158-160` png_size
- `sw/subl_vetting.py:169-184` show_image
- `sw/subl_vetting.py:187-192` zoom
- `sw/subl_commands.py:448-449` SightWalkZoomMapCommand.run
- `sw/subl_vetting.py:195-198` show_note

## 18. The user sends a message (9 views)

The draft becomes a message, with here, the visible sights and the edits, and the agent receives it.

- `sw/subl_commands.py:46-53` SightWalkSendCommand.run
- `sw/subl_chat.py:190-204` take_draft
- `sw/subl_commands.py:32-40` send
- `sw/state.py:37-38` reader_for
- `sw/subl_reader.py:1302-1321` Reader.context
- `sw/subl_views.py:324-328` selected_text
- `sw/plan.py:121-124` visible_specs
- `sw/subl_reader.py:790-793` Reader.take_edits
- `sw/subl_executor.py:220-234` wait_for_user

## 19. Linking words to code (38 views)

primary+p joins words of the draft to selections in the sights, from either side; the words go out as a <here> tag, and a click on them shows their place.

- `sw/subl_commands.py:197-204` SightWalkLinkCommand.run
- `sw/subl_links.py:19-30` Links.__init__
- `sw/subl_commands.py:258-262` SightWalkChatListener.on_selection_modified
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
- `sw/subl_reader.py:851-862` Reader.show_place
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
- `sw/subl_commands.py:311-317` SightWalkWindowListener.on_post_text_command

## 20. Opening the editor (11 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/subl_commands.py:210-220` SightWalkEditCommand.run
- `sw/subl_reader.py:757-762` Reader.sight_of
- `sw/subl_reader.py:740-755` Reader.open_editor
- `sw/subl_editor.py:24-32` Editor.__init__
- `sw/subl_views.py:69-73` wait_until_loaded
- `sw/subl_editor.py:16-20` open_live
- `sw/subl_editor.py:34-44` Editor.start
- `sw/subl_editor.py:46-58` Editor.track
- `sw/subl_editor.py:60-65` Editor.hold
- `sw/subl_geometry.py:69-78` Geometry.editor_geometry
- `sw/subl_geometry.py:80-89` Geometry.text_left

## 21. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/subl_commands.py:226-229` SightWalkCloseEditorCommand.run
- `sw/subl_reader.py:764-765` Reader.close_editor
- `sw/subl_editor.py:81-92` Editor.close
- `sw/subl_editor.py:74-79` Editor.read_back
- `sw/subl_editor.py:67-72` Editor.rows
- `sw/subl_reader.py:767-781` Reader.editor_closed
- `sw/subl_reader.py:783-788` Reader.move_range

## 22. Window events (12 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/subl_reader.py:662-672` Reader.follow_resize
- `sw/subl_reader.py:443-450` Reader.keep_bench_width
- `sw/subl_geometry.py:18-25` Geometry.spans
- `sw/subl_geometry.py:27-31` Geometry.strip_span
- `sw/subl_geometry.py:33-35` Geometry.strip_share
- `sw/subl_geometry.py:37-38` Geometry.bench_side
- `sw/state.py:55-60` render_all
- `sw/subl_executor.py:99-106` op_settings
- `sw/validator.py:174-182` check_settings
- `sw/subl_commands.py:278-280` SightWalkWindowListener.on_activated
- `sw/subl_commands.py:237-241` SightWalkHeaderListener.on_hover
- `sw/subl_chat.py:170-174` show_help

## 23. One colour scheme for the trips (17 views)

SightWalk: Select Colour Scheme: general, light or dark, only schemes of that kind, previewed live in every trip; the files' hues derived from it again, the other views take it as it is.

- `sw/subl_commands.py:61-63` SightWalkSelectColourSchemeCommand.run
- `sw/subl_commands.py:65-76` SightWalkSelectColourSchemeCommand.pick_kind
- `sw/subl_commands.py:91-94` all_schemes
- `sw/subl_tint.py:203-207` is_dark
- `sw/subl_commands.py:97-99` scheme_item
- `sw/subl_commands.py:78-80` SightWalkSelectColourSchemeCommand.preview
- `sw/subl_tint.py:242-247` refresh_all
- `sw/subl_reader.py:308-314` Reader.refresh_schemes
- `sw/subl_tint.py:100-110` chosen_scheme
- `sw/subl_tint.py:158-168` scheme_colours
- `sw/subl_tint.py:176-185` resolve_colour
- `sw/subl_tint.py:268-270` base_name
- `sw/subl_tint.py:188-200` plain_colour
- `sw/subl_tint.py:171-173` luminance
- `sw/subl_reader.py:316-323` Reader.plain_views
- `sw/subl_tint.py:210-218` apply_plain
- `sw/subl_commands.py:82-88` SightWalkSelectColourSchemeCommand.done

## 24. ctrl+tab (5 views)

The focus round the sights on screen, top to bottom, ctrl+shift+tab the other way.

- `sw/subl_commands.py:105-108` SightWalkCycleSightsCommand.run
- `sw/subl_commands.py:285-297` SightWalkWindowListener.on_window_command
- `sw/subl_reader.py:832-849` Reader.cycle
- `sw/plan.py:104-108` visible_indices
- `sw/plan.py:111-118` cycled

## 25. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/subl_commands.py:476-487` SightWalkToggleGuideCommand.run
- `sw/subl_reader.py:813-823` Reader.toggle_focus
- `sw/subl_commands.py:489-494` SightWalkToggleGuideCommand.folder
- `sw/subl_reader.py:180-184` Reader.open_empty
- `sw/subl_reader.py:186-205` Reader.empty_layout
- `sw/subl_reader.py:207-212` Reader.close_hijacker
- `sw/subl_commands.py:320-324` SightWalkWindowListener.offer_to_browser
- `sw/subl_commands.py:282-283` SightWalkWindowListener.on_load
- `sw/subl_reader.py:214-222` Reader.take_file
- `sw/subl_executor.py:88-96` op_browse
- `sw/subl_views.py:125-136` make_browser

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

- `sw/subl_commands.py:299-309` SightWalkWindowListener.on_selection_modified
- `sw/subl_reader.py:825-830` Reader.note_selection

## 31. Words in two languages (9 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/subl_commands.py:439-442` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:54-58` settings_changed
- `sw/words.py:128-130` set_language
- `sw/state.py:55-60` render_all
- `sw/words.py:124-125` word
- `sw/subl_chat.py:28-31` help_html
- `sw/subl_views.py:33-35` button_html
- `sw/subl_commands.py:524-536` SightWalkCompareFontsCommand.run
- `sw/subl_commands.py:539-547` kept_conversation

## 32. Endings (17 views, survey)

The guide is stopped, windows close.

- `sw/subl_commands.py:464-465` SightWalkStopGuideCommand.run
- `sw/subl_commands.py:467-468` SightWalkStopGuideCommand.is_enabled
- `sw/subl_guide.py:90-94` stop
- `sw/subl_guide.py:78-87` stop_when_idle
- `sw/subl_commands.py:326-330` SightWalkWindowListener.on_pre_close_window
- `sw/subl_commands.py:333-335` clear_schemes_if_unused
- `sw/subl_tint.py:291-295` first_load
- `sw/subl_tint.py:298-327` clear_schemes
- `sw/subl_tint.py:72-73` scheme_folder
- `sw/subl_commands.py:285-297` SightWalkWindowListener.on_window_command
- `sw/subl_commands.py:370-372` SightWalkCloseTripCommand.run
- `sw/subl_commands.py:350-353` SightWalkResetSightsCommand.run
- `sw/subl_reader.py:864-871` Reader.reset_sights
- `sw/subl_commands.py:355-357` SightWalkResetSightsCommand.is_enabled
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
- `sw/subl_geometry.py:46-54` Geometry.conversation_rows
- `sw/subl_geometry.py:56-58` Geometry.head
- `sw/subl_geometry.py:65-67` Geometry.room
- `sw/subl_views.py:204-209` smaller
- `sw/subl_executor.py:78-80` op_state
- `sw/subl_reader.py:1245-1250` Reader.folder
- `sw/subl_reader.py:1227-1229` Reader.note_waiting

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
- `sw/subl_chat.py:48-50` Guard.__init__
- `sw/subl_commands.py:233-235` SightWalkHeaderListener.is_applicable
- `sw/subl_commands.py:245-247` SightWalkChatListener.is_applicable

## 35. Settings and the rest of the colours (6 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/subl_tint.py:84-86` band_amount
- `sw/subl_tint.py:59-69` from_tm_theme
- `sw/subl_tint.py:113-125` resolved_scheme
- `sw/subl_tint.py:89-93` scheme_stem
- `sw/subl_tint.py:29-30` hex_rgb
- `sw/subl_tint.py:279-284` apply_grey

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

- `sw/subl_commands.py:380-386` SightWalkOpenTourCommand.run
- `sw/subl_commands.py:395-408` tour_choices
- `sw/subl_commands.py:411-421` found_files
- `sw/subl_commands.py:424-425` read_name
- `sw/subl_commands.py:428-433` read_field
- `sw/subl_commands.py:388-392` SightWalkOpenTourCommand.open
- `sw/words.py:141-148` trips_count
- `sw/subl_reader.py:921-935` Reader.open_tour
- `sw/subl_reader.py:1344-1346` read_json
- `sw/ontology.py:303-309` tour_from
- `sw/ontology.py:282-286` informator_from
- `sw/ontology.py:266-269` trip_from
- `sw/ontology.py:249-257` transition_from
- `sw/ontology.py:212-227` tour
- `sw/ontology.py:230-238` visit
- `sw/subl_vetting.py:222-228` read_walked
- `sw/subl_reader.py:937-951` Reader.tour_link
- `sw/subl_reader.py:981-991` Reader.keep_transcript
- `sw/subl_reader.py:993-1001` Reader.kept_marks
- `sw/subl_reader.py:1003-1005` Reader.line_text
- `sw/subl_reader.py:1007-1018` Reader.restore_marks
- `sw/subl_reader.py:1324-1328` kept_frame
- `sw/subl_reader.py:1331-1333` transcripts_path
- `sw/subl_reader.py:1336-1341` read_transcripts
- `sw/subl_chat.py:232-235` set_transcript
- `sw/ontology.py:289-293` dumps
- `sw/subl_vetting.py:231-240` save_walked
- `sw/subl_reader.py:1107-1109` Reader.draw_tour
- `sw/subl_vetting.py:203-219` show_tour

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

- `sw/subl_reader.py:236-251` Reader.build
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
- `sw/subl_commands.py:500-502` SightWalkSightListener.is_applicable
- `sw/subl_commands.py:504-506` SightWalkSightListener.on_hover
- `sw/subl_asked.py:87-92` show_popup
- `sw/subl_asked.py:60-62` paint
- `sw/subl_asked.py:65-70` toggle
- `sw/subl_commands.py:512-513` SightWalkToggleSentinelsCommand.run

## 42. The guide's permissions (14 views)

The Permissions tab: a field ticked, remembered or not, and the guide SightWalk started restarted while it waits with the tools allowed now.

- `sw/subl_reader.py:1111-1114` Reader.draw_permissions
- `sw/subl_vetting.py:248-268` show_permissions
- `sw/subl_reader.py:1116-1131` Reader.permission_link
- `sw/subl_vetting.py:271-273` show_tip
- `sw/subl_guide.py:126-132` toggle
- `sw/permissions.py:37-39` remembered
- `sw/subl_guide.py:135-146` restart
- `sw/subl_guide.py:107-111` chosen
- `sw/subl_guide.py:114-116` folders
- `sw/permissions.py:23-34` allowed_tools
- `sw/permissions.py:42-44` reminders
- `sw/subl_guide.py:149-151` ours
- `sw/subl_reader.py:1133-1137` Reader.add_folder
- `sw/subl_guide.py:119-123` set_folders

## 43. Back and forward through trips (14 views)

◀ ▶ in the Sights' header, primary+[ and primary+]: each trip the guide shows goes into the window's history with its own conversation, starting from the question that called it; a step keeps the conversation shown and brings the other trip's back.

- `sw/subl_reader.py:955-959` Reader.visit
- `sw/history.py:38-44` last_exchange
- `sw/history.py:7-9` History.__init__
- `sw/history.py:20-25` History.visit
- `sw/subl_reader.py:967-970` Reader.leave
- `sw/history.py:14-18` History.keep
- `sw/history.py:11-12` History.current
- `sw/subl_reader.py:972-979` Reader.enter
- `sw/subl_chat.py:135-140` nav_phantom
- `sw/subl_commands.py:341-344` SightWalkStepCommand.run
- `sw/subl_reader.py:961-965` Reader.step
- `sw/history.py:27-28` History.can
- `sw/history.py:30-35` History.go
- `sw/subl_chat.py:123-127` help_or_link

## 44. Driving a trip from the terminal (7 views)

Tests without mouse or keys, in the guide's notation: sight_walk_fill sets the draft, whose <here> tags become links, sight_walk_select selects places, (>) the draft, and sight_walk_send_draft sends it.

- `sw/subl_commands.py:121-138` SightWalkFillCommand.run
- `sw/marks.py:348-366` read_here
- `sw/subl_commands.py:168-180` place_region
- `sw/marks.py:332-345` parse_place
- `sw/subl_commands.py:145-156` SightWalkSelectCommand.run
- `sw/subl_commands.py:183-190` note_selection
- `sw/subl_commands.py:162-165` SightWalkSendDraftCommand.run

## 45. The bench's answers listed (9 views)

The Answers tab: the bench's questions and answers by their first words; a click shows one's icons or places and brings it into the bench, a second click hides them.

- `sw/subl_reader.py:1067-1069` Reader.draw_answers
- `sw/subl_reader.py:1050-1065` Reader.bench_rows
- `sw/answers.py:9-19` entries
- `sw/subl_reader.py:1031-1041` Reader.answer_marks
- `sw/subl_vetting.py:278-293` show_answers
- `sw/subl_vetting.py:296-297` html_escape
- `sw/subl_reader.py:1071-1087` Reader.answer_link
- `sw/subl_reader.py:1043-1046` Reader.hide_answer
- `sw/subl_reader.py:1089-1094` Reader.scroll_bench
