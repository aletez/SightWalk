# Trips through SightWalk's own code

Each trip follows one stretch of a run, in run order, one view per function; a survey shows all the places about one thing. Written by `tools/trips.py`; run it again after the code changes. `python3 tools/trips.py N` prints trip N for show, with the calls between its sights.

## 1. Registering the guide (5 views)

The setup command keeps a token, writes it for poke, and puts Claude Code's registration line on the clipboard.

- `sw/subl_setup.py:32-38` SightWalkSetupCommand.run
- `sw/subl_setup.py:41-48` ensure_token
- `sw/subl_setup.py:51-57` write_config
- `sw/subl_setup.py:60-63` show_instructions
- `sw/subl_commands.py:17-24` SightWalkReplaceCommand.run

## 2. The manual (5 views, survey)

What every guide reads at its start: how to compose trips, show code, talk and mark.

- `sw/manual.py:6-24` MANUAL: opening
- `sw/manual.py:26-54` MANUAL: Showing code
- `sw/manual.py:56-59` MANUAL: Writing code that fits the reader
- `sw/manual.py:61-124` MANUAL: Conversation
- `sw/manual.py:126-173` MANUAL: Indicators

## 3. The tools' schemas (5 views, survey)

The tools a guide may call, their parameters, and the fields that permit its other work.

- `sw/manual.py:176-179` tool
- `sw/manual.py:187-226` TOOLS
- `sw/manual.py:182-185` TRANSITION
- `sw/validator.py:11-13` TRANSITION_FORM
- `sw/permissions.py:8-19` FIELDS

## 4. A guide started from Sublime (5 views)

When no agent listens, asking the guide starts one.

- `sw/subl_guide.py:97-102` await_answer
- `sw/subl_guide.py:51-60` ensure
- `sw/subl_guide.py:34-36` listening
- `sw/subl_guide.py:39-40` running
- `sw/subl_guide.py:43-48` find_claude

## 5. The guide's first words (3 views)

The guide starts with a prompt and calls wait_for_user, which takes the message waiting.

- `sw/subl_guide.py:63-75` start
- `sw/subl_guide.py:20-25` PROMPT
- `sw/subl_executor.py:248-262` wait_for_user

## 6. An MCP request over HTTP (5 views)

A JSON-RPC message posted to the plugin, its token checked, answered.

- `sw/subl_mcp_http.py:94-105` Handler.do_POST
- `sw/subl_mcp_http.py:78-81` Handler.authorized
- `sw/subl_mcp_http.py:65-74` reply
- `sw/subl_mcp_http.py:50-62` answer
- `sw/subl_mcp_http.py:83-92` Handler.send

## 7. The other HTTP verbs (3 views, survey)

What the server says to GET and DELETE, and the log it keeps quiet.

- `sw/subl_mcp_http.py:107-108` Handler.do_GET
- `sw/subl_mcp_http.py:110-112` Handler.do_DELETE
- `sw/subl_mcp_http.py:114-115` Handler.log_message

## 8. A tool call reaches Sublime's thread (5 views)

From the HTTP thread to Sublime's main thread and back with the result.

- `sw/subl_mcp_http.py:23-35` call_tool
- `sw/subl_mcp_http.py:38-47` tool_result
- `sw/subl_executor.py:237-245` wait_until_ready
- `sw/subl_executor.py:208-215` execute
- `sw/subl_executor.py:218-234` run_on_main

## 9. `show`: the files and functions (5 views)

The facts show is judged by: each sight's file and the functions in its lines.

- `sw/subl_executor.py:149-163` facts
- `sw/subl_executor.py:166-175` sight_files
- `sw/subl_executor.py:31-33` file_lines
- `sw/subl_executor.py:178-189` sight_functions
- `sw/validator.py:73-86` files

## 10. `show`: one function a sight (5 views)

How the functions and classes in a sight are found, and the rule that a sight holds one.

- `sw/spec.py:118-123` functions_in
- `sw/spec.py:126-130` units_in
- `sw/spec.py:136-149` blocks_in
- `sw/spec.py:152-159` open_above
- `sw/validator.py:89-101` one_function

## 11. `show`: the trip judged (5 views)

The validator's entry, show's checks, and the trip's places read.

- `sw/validator.py:26-31` check
- `sw/validator.py:123-127` check_show
- `sw/validator.py:56-59` not_stopped
- `sw/validator.py:34-53` trip_of
- `sw/marks.py:386-398` trip_place

## 12. `show`: the trip made (5 views)

The sights parsed and the trip built as a network whose transitions fit it.

- `sw/spec.py:10-23` parse_spec
- `sw/ontology.py:129-137` Sight.parse
- `sw/ontology.py:160-164` Trip.__init__
- `sw/ontology.py:93-100` Network.__init__
- `sw/ontology.py:109-119` Network.problem

## 13. `show`: the window opens (4 views)

show runs on the main thread: the trip visited in its window, its sights named.

- `sw/subl_executor.py:218-234` run_on_main
- `sw/subl_executor.py:49-65` op_show
- `sw/subl_executor.py:36-46` new_reader
- `sw/subl_executor.py:82-84` named

## 14. `wait_for_user`: a message sent (5 views)

The draft becomes a message in the shared inbox, and the guide's wait returns it.

- `sw/subl_commands.py:47-54` SightWalkSendCommand.run
- `sw/subl_chat.py:210-223` take_draft
- `sw/subl_commands.py:32-41` send
- `sw/state.py:37-38` reader_for
- `sw/subl_executor.py:248-262` wait_for_user

## 15. What a message carries (4 views)

Here, the selection, the visible sights and the edits that go with every message.

- `sw/subl_reader.py:1474-1495` Reader.context
- `sw/subl_views.py:327-331` selected_text
- `sw/plan.py:121-124` visible_specs
- `sw/subl_reader.py:808-811` Reader.take_edits

## 16. `say`: the words checked (6 views)

An answer's words before they reach the bench: tags removed, no line numbers, names marked.

- `sw/subl_executor.py:91-99` op_say
- `sw/marks.py:199-214` untag
- `sw/marks.py:426-428` line_refs
- `sw/marks.py:170-172` speaks_of_code
- `sw/marks.py:167-167` CODE_TALK
- `sw/validator.py:14-17` MARK_FIRST

## 17. `say`: on the bench (5 views)

The answer appended to the bench, the headers and status line updated.

- `sw/subl_reader.py:1424-1437` Reader.say
- `sw/subl_chat.py:198-207` say
- `sw/subl_commands.py:28-29` SightWalkInsertCommand.run
- `sw/subl_reader.py:815-831` Reader.show_headers
- `sw/subl_chat.py:167-176` show_status

## 18. The headers follow (4 views)

A header's title and status cut to its width, and the bench's names shaded.

- `sw/subl_chat.py:106-129` show_header
- `sw/header.py:12-20` title_lines
- `sw/marks.py:415-417` clean
- `sw/subl_chat.py:292-297` shade_variables

## 19. The transcript guard (4 views)

What was said cannot be edited: only the draft after the prompt may change.

- `sw/subl_chat.py:55-72` Guard.on_text_changed
- `sw/subl_chat.py:37-45` protected_end
- `sw/subl_commands.py:265-272` SightWalkChatListener.on_modified
- `sw/subl_commands.py:280-290` SightWalkChatListener.on_post_text_command

## 20. Stopping an answer (3 views)

Esc or [Stop (Esc)]: the agent's next tool call is refused, the unread messages withdrawn.

- `sw/subl_commands.py:391-394` SightWalkStopAnswerCommand.run
- `sw/subl_reader.py:1403-1410` Reader.stop_answer
- `sw/subl_reader.py:1412-1415` Reader.withdraw_unread_messages

## 21. `say`: marks read (5 views)

The answer's tags read into marks and the frames around their words.

- `sw/marks.py:264-296` read_marks
- `sw/marks.py:233-241` mark_attributes
- `sw/marks.py:244-261` tag_marks
- `sw/marks.py:401-412` frame_scopes
- `sw/marks.py:386-398` trip_place

## 22. `say`: marks resolved (5 views)

Each mark resolved to a sight and a line, a jump to its two ends, an icon chosen.

- `sw/marks.py:91-117` resolve_marks
- `sw/marks.py:80-88` jump
- `sw/marks.py:18-37` resolve_target
- `sw/marks.py:46-53` sight_target
- `sw/marks.py:56-62` icon_for

## 23. Sight names (5 views)

(a), (b), (c): the names the user reads, and the guide writes.

- `sw/marks.py:186-189` sight_refs
- `sw/marks.py:40-43` sight_number
- `sw/spec.py:58-64` sight_index
- `sw/spec.py:50-55` sight_name
- `sw/marks.py:14-15` line_y

## 24. `say`: marks drawn (5 views)

The marks drawn in the gutter and as frames on the bench, kept with their answer.

- `sw/subl_reader.py:694-703` Reader.point
- `sw/subl_chat.py:273-289` outline_refs
- `sw/subl_chat.py:267-270` blanks
- `sw/subl_reader.py:1455-1472` Reader.add_to_answer
- `sw/subl_reader.py:1439-1453` Reader.frame_regions

## 25. A frame clicked (4 views)

A click on framed words shows their places; on an answer's label, its marks.

- `sw/subl_reader.py:1335-1362` Reader.follow_frame
- `sw/subl_reader.py:1364-1375` Reader.show_places
- `sw/subl_reader.py:1246-1255` Reader.follow_label
- `sw/subl_reader.py:1170-1179` Reader.show_answer

## 26. `state` (2 views)

What the guide may ask at any time: the sights, the visible ones, here.

- `sw/validator.py:178-179` check_state
- `sw/subl_executor.py:102-104` op_state

## 27. `close` (2 views)

The guide closes the trip's window.

- `sw/validator.py:182-184` check_close
- `sw/subl_executor.py:107-109` op_close

## 28. `settings` (2 views)

The settings the guide may read and change.

- `sw/validator.py:193-201` check_settings
- `sw/subl_executor.py:127-134` op_settings

## 29. `browse` (4 views)

A trip with no sights: the folder's files in their place.

- `sw/validator.py:187-190` check_browse
- `sw/subl_executor.py:112-124` op_browse
- `sw/subl_reader.py:192-196` Reader.open_empty
- `sw/subl_reader.py:198-218` Reader.empty_layout

## 30. `open_trip` (4 views)

A trip opened from its file instead of composed with show.

- `sw/validator.py:130-135` check_open_trip
- `sw/subl_executor.py:192-201` trip_file
- `sw/subl_executor.py:137-144` op_open_trip
- `sw/ontology.py:266-269` trip_from

## 31. Writing an informator (4 views)

Trips, transitions, the informator and its tours written to files.

- `sw/ontology.py:260-263` trip_data
- `sw/ontology.py:244-246` transition_data
- `sw/ontology.py:272-279` informator_data
- `sw/ontology.py:296-300` tour_data

## 32. Plugin start and stop (11 views)

Sublime loads the plugin, which starts its MCP server; a new port restarts it; on unload, trips close and the server stops. The Restart command makes Sublime reload the plugin.

- `sight_walk.py:45-52` plugin_loaded
- `sw/subl_mcp_http.py:142-145` start
- `sw/subl_executor.py:267-271` load_config
- `sw/subl_mcp_http.py:118-122` start_server
- `sw/subl_mcp_http.py:133-139` settings_changed
- `sw/subl_mcp_http.py:125-130` stop_server
- `sight_walk.py:62-68` plugin_unloaded
- `sw/subl_scrollbars.py:13-25` reader_focused
- `sw/state.py:45-52` close_all
- `sw/subl_mcp_http.py:148-150` stop
- `sw/subl_setup.py:70-72` SightWalkRestartCommand.run

## 33. A new reader window (12 views)

The window and every view but the sights.

- `sw/subl_executor.py:36-46` new_reader
- `sw/subl_reader.py:75-109` Reader.__init__
- `sw/subl_reader.py:111-169` Reader.make_side_views
- `sw/subl_views.py:182-191` bench_font
- `sw/subl_views.py:194-198` match_font
- `sw/subl_views.py:142-149` make_blank_view
- `sw/subl_views.py:118-125` make_side_view
- `sw/subl_chat.py:79-86` start
- `sw/subl_chat.py:89-99` make_header
- `sw/subl_chat.py:155-164` make_status
- `sw/subl_vetting.py:30-37` make_tool
- `sw/state.py:23-26` register

## 34. Loading the sights (22 views)

Files read, each sight's copy, header and frozen lines made.

- `sw/subl_reader.py:173-190` Reader.load
- `sw/subl_chat.py:256-264` catch_up
- `sw/subl_reader.py:237-247` Reader.close_sights
- `sw/subl_reader.py:249-264` Reader.build
- `sw/subl_views.py:160-164` FileCopy.__init__
- `sw/subl_views.py:167-179` make_copy
- `sw/subl_reader.py:266-286` Reader.surround
- `sw/spec.py:162-177` elided
- `sw/spec.py:190-194` block_name
- `sw/spec.py:180-187` body_indent
- `sw/words.py:145-150` lines_of
- `sw/subl_reader.py:288-295` Reader.ellipses
- `sw/subl_reader.py:297-308` Reader.draw_ellipsis
- `sw/subl_views.py:306-314` draw_ellipsis
- `sw/subl_reader.py:383-391` Reader.room_px
- `sw/subl_reader.py:310-319` Reader.grow_ellipses
- `sw/spec.py:97-112` ancestors
- `sw/spec.py:84-85` indent
- `sw/spec.py:88-94` opens_block
- `sw/spec.py:197-204` breathing
- `sw/subl_views.py:216-223` make_header
- `sw/subl_views.py:226-231` write_header

## 35. Colours (10 views)

Every file in its own hue, schemes written and set once Sublime has indexed them.

- `sw/subl_reader.py:339-344` Reader.tint
- `sw/subl_tint.py:282-285` apply_tint
- `sw/subl_tint.py:242-248` schemes_for
- `sw/subl_tint.py:22-26` hue_for
- `sw/subl_tint.py:128-156` tinted_schemes
- `sw/subl_tint.py:41-53` load_base_scheme
- `sw/subl_tint.py:33-38` tint_color
- `sw/subl_tint.py:76-81` write_scheme
- `sw/subl_tint.py:259-274` set_schemes
- `sw/subl_tint.py:230-239` when_indexed

## 36. Measuring (16 views)

The gap phantoms, the cells of the virtual document, and the window's height measured with two layouts.

- `sw/subl_reader.py:346-350` Reader.draw_gaps
- `sw/subl_reader.py:56-57` line_count
- `sw/subl_views.py:317-324` draw_gap
- `sw/subl_reader.py:365-381` Reader.make_items
- `sw/subl_views.py:234-235` line_top
- `sw/subl_views.py:238-239` header_top
- `sw/subl_reader.py:393-398` Reader.calibrate
- `sw/subl_reader.py:400-405` Reader.measure_full
- `sw/subl_reader.py:407-411` Reader.measure_half
- `sw/subl_reader.py:413-430` Reader.start
- `sw/subl_reader.py:543-546` Reader.centred_lead
- `sw/plan.py:85-90` lead
- `sw/plan.py:79-82` free_room
- `sw/plan.py:50-66` stack
- `sw/plan.py:69-76` sight_groups
- `sw/subl_reader.py:645-651` Reader.write_strip

## 37. The layout (11 views)

From an offset to Sublime's layout: every sight's cells at its place, shifted.

- `sw/subl_reader.py:548-554` Reader.scroll_to
- `sw/plan.py:93-101` offset_range
- `sw/subl_geometry.py:64-67` Geometry.bench_floor
- `sw/subl_reader.py:507-519` Reader.render
- `sw/subl_geometry.py:95-126` Geometry.column_rects
- `sw/subl_geometry.py:44-48` Geometry.column
- `sw/subl_geometry.py:143-154` Geometry.sight_cells
- `sw/subl_geometry.py:139-141` Geometry.floor_height
- `sw/subl_reader.py:434-441` Reader.layout
- `sw/subl_views.py:86-113` reader_layout
- `sw/subl_views.py:76-83` to_layout

## 38. Arranging the views (16 views)

After a new layout: every view into its group, then back at its place.

- `sw/subl_reader.py:521-539` Reader.arrange
- `sw/subl_reader.py:469-474` Reader.place
- `sw/subl_reader.py:443-458` Reader.strip_in_front
- `sw/subl_geometry.py:128-137` Geometry.strip_rows
- `sw/subl_reader.py:352-363` Reader.clone
- `sw/subl_reader.py:476-505` Reader.assign_groups
- `sw/subl_views.py:63-66` hide_chrome
- `sw/subl_reader.py:586-597` Reader.scroll_views
- `sw/subl_reader.py:556-564` Reader.places
- `sw/subl_reader.py:639-643` Reader.strip_place
- `sw/subl_views.py:152-154` anchor
- `sw/subl_reader.py:908-915` Reader.draw_strip_buttons
- `sw/subl_reader.py:917-919` Reader.strip_button
- `sw/subl_reader.py:747-756` Reader.draw_edit_buttons
- `sw/subl_reader.py:742-745` Reader.title
- `sw/subl_views.py:242-254` draw_edit_button

## 39. Polling and the wheel (12 views)

The two loops: the gutter measured once, the reader opening at the top; the wheel read and taken over.

- `sw/subl_reader.py:658-666` Reader.poll
- `sw/subl_chat.py:226-236` keep_at_bottom
- `sw/subl_chat.py:245-248` bottom_place
- `sw/subl_chat.py:239-242` kept_place
- `sw/subl_reader.py:668-675` Reader.poll_wheel
- `sw/subl_reader.py:655-656` Reader.alive
- `sw/subl_reader.py:599-622` Reader.read_wheel
- `sw/subl_reader.py:624-632` Reader.clamp_bench
- `sw/subl_reader.py:634-637` Reader.bench_edited
- `sw/subl_reader.py:566-578` Reader.wheel_places
- `sw/subl_reader.py:580-584` Reader.pinned_places
- `sw/subl_reader.py:68-71` item_top

## 40. Drawing the marks (10 views)

Icons on screen, eyes for marks off it, outlines on marked lines.

- `sw/subl_reader.py:705-721` Reader.draw_gutter
- `sw/subl_reader.py:723-728` Reader.draw_strip_marks
- `sw/marks.py:153-164` strip_icons
- `sw/subl_views.py:271-280` draw_strip_icons
- `sw/marks.py:120-132` visible_lines
- `sw/marks.py:135-150` gutter_icons
- `sw/subl_views.py:259-268` draw_icons
- `sw/subl_reader.py:730-738` Reader.draw_outlines
- `sw/marks.py:71-77` icon_colour
- `sw/subl_views.py:286-299` draw_outlines

## 41. The Tools pane's tabs (15 views, survey)

Map and Scroll: the tab links, and the tab shown in the pane.

- `sw/subl_reader.py:933-941` Reader.select_tool
- `sw/subl_vetting.py:71-87` show_tabs
- `sw/subl_vetting.py:64-68` toggle_html
- `sw/subl_vetting.py:90-92` tab_at
- `sw/subl_vetting.py:104-119` show_buttons
- `sw/subl_commands.py:250-257` SightWalkHeaderListener.on_selection_modified
- `sw/subl_geometry.py:18-20` Geometry.buttons_share
- `sw/subl_commands.py:486-489` SightWalkTogglePanningCommand.run
- `sw/subl_reader.py:990-1000` Reader.toggle_panning
- `sw/subl_vetting.py:40-48` set_panning
- `sw/subl_vetting.py:51-53` content_point
- `sw/subl_reader.py:923-925` Reader.tools
- `sw/subl_reader.py:927-928` Reader.tool_view
- `sw/subl_reader.py:930-931` Reader.hidden_tools
- `sw/subl_reader.py:1311-1323` Reader.draw_map

## 42. The Map's nodes (13 views)

The trip's definitions and the calls its author named, as nodes for the graph.

- `sw/subl_reader.py:1311-1323` Reader.draw_map
- `sw/subl_reader.py:1325-1333` Reader.answer_transitions
- `sw/subl_reader.py:1527-1534` map_style
- `sw/subl_reader.py:1377-1391` Reader.map_nodes
- `sw/subl_reader.py:49-53` fragment_of
- `sw/subl_reader.py:1393-1397` Reader.owner
- `sw/subl_reader.py:60-65` defined_name
- `sw/callmap.py:33-39` first_definition
- `sw/callmap.py:42-49` node_at
- `sw/callmap.py:28-30` Node.__init__
- `sw/callmap.py:52-59` edges
- `sw/callmap.py:42-49` node_at
- `sw/subl_vetting.py:131-139` draw_map

## 43. Drawing the Map (17 views)

The graph in dot's language, drawn by Graphviz off the main thread, shown as an image.

- `sw/subl_vetting.py:131-139` draw_map
- `sw/subl_vetting.py:124-128` find_dot
- `sw/callmap.py:120-141` dot_source
- `sw/callmap.py:93-99` file_block
- `sw/callmap.py:70-73` cluster
- `sw/callmap.py:76-78` node_line
- `sw/callmap.py:81-90` sight_blocks
- `sw/callmap.py:62-63` node_id
- `sw/callmap.py:66-67` quote
- `sw/callmap.py:102-106` arrow
- `sw/callmap.py:109-117` legend
- `sw/subl_vetting.py:142-154` render
- `sw/subl_vetting.py:157-159` png_size
- `sw/subl_vetting.py:168-183` show_image
- `sw/subl_vetting.py:186-191` zoom
- `sw/subl_commands.py:479-480` SightWalkZoomMapCommand.run
- `sw/subl_vetting.py:194-197` show_note

## 44. Linking words to code (40 views)

primary+p joins words of the draft to selections in the sights, from either side; the words go out as a <here> tag, and a click on them shows their place.

- `sw/subl_commands.py:198-205` SightWalkLinkCommand.run
- `sw/subl_links.py:19-30` Links.__init__
- `sw/subl_commands.py:274-278` SightWalkChatListener.on_selection_modified
- `sw/subl_links.py:32-37` Links.note_bench
- `sw/subl_links.py:39-53` Links.note_code
- `sw/subl_links.py:55-61` Links.link_from_code
- `sw/subl_links.py:72-83` Links.link_from_bench
- `sw/subl_links.py:63-70` Links.link_either
- `sw/subl_links.py:85-103` Links.add
- `sw/subl_links.py:325-329` carets
- `sw/subl_links.py:139-149` Links.tagged
- `sw/subl_links.py:227-231` Links.places
- `sw/subl_links.py:312-322` ends
- `sw/marks.py:315-324` place_text
- `sw/subl_links.py:233-239` Links.code
- `sw/subl_links.py:300-302` Links.draft_start
- `sw/subl_links.py:241-266` Links.follow
- `sw/subl_links.py:332-338` repaint
- `sw/subl_reader.py:881-892` Reader.show_place
- `sw/subl_links.py:304-309` Links.clear
- `sw/subl_links.py:105-110` Links.show_made
- `sw/subl_links.py:112-117` Links.remove
- `sw/subl_links.py:119-124` Links.prune
- `sw/subl_links.py:126-127` Links.draft_keys
- `sw/subl_links.py:129-131` Links.bench_region
- `sw/subl_links.py:133-137` Links.by_sight
- `sw/marks.py:299-312` span_relation
- `sw/marks.py:369-383` here_tags
- `sw/subl_links.py:268-287` Links.follow_code
- `sw/subl_links.py:289-294` Links.repaint_bench
- `sw/subl_links.py:151-160` Links.ask
- `sw/subl_links.py:162-165` Links.frame_question
- `sw/subl_links.py:201-212` Links.follow_question
- `sw/subl_links.py:214-225` Links.select
- `sw/subl_links.py:167-170` Links.kept_questions
- `sw/subl_links.py:194-199` Links.restore_questions
- `sw/subl_links.py:172-180` Links.kept_links
- `sw/subl_links.py:182-192` Links.restore_links
- `sw/subl_links.py:296-298` Links.forget_shown
- `sw/subl_commands.py:327-333` SightWalkWindowListener.on_post_text_command

## 45. Opening the editor (11 views)

Enter or the header's button: the editor laid over the sights, ranges and marks held.

- `sw/subl_commands.py:211-221` SightWalkEditCommand.run
- `sw/subl_reader.py:775-780` Reader.sight_of
- `sw/subl_reader.py:758-773` Reader.open_editor
- `sw/subl_editor.py:24-32` Editor.__init__
- `sw/subl_views.py:69-73` wait_until_loaded
- `sw/subl_editor.py:16-20` open_live
- `sw/subl_editor.py:34-44` Editor.start
- `sw/subl_editor.py:46-58` Editor.track
- `sw/subl_editor.py:60-65` Editor.hold
- `sw/subl_geometry.py:73-82` Geometry.editor_geometry
- `sw/subl_geometry.py:84-93` Geometry.text_left

## 46. Closing the editor (7 views)

Esc: Sublime asks about changes, the reader reads back the moved ranges and marks.

- `sw/subl_commands.py:227-230` SightWalkCloseEditorCommand.run
- `sw/subl_reader.py:782-783` Reader.close_editor
- `sw/subl_editor.py:81-92` Editor.close
- `sw/subl_editor.py:74-79` Editor.read_back
- `sw/subl_editor.py:67-72` Editor.rows
- `sw/subl_reader.py:785-799` Reader.editor_closed
- `sw/subl_reader.py:801-806` Reader.move_range

## 47. Window events (12 views, survey)

Everything that reacts to the user's window: resizing, settings, focus, keys, closing.

- `sw/subl_reader.py:677-690` Reader.follow_resize
- `sw/subl_reader.py:460-467` Reader.keep_bench_width
- `sw/subl_geometry.py:22-29` Geometry.spans
- `sw/subl_geometry.py:31-35` Geometry.strip_span
- `sw/subl_geometry.py:37-39` Geometry.strip_share
- `sw/subl_geometry.py:41-42` Geometry.bench_side
- `sw/state.py:55-60` render_all
- `sw/subl_executor.py:127-134` op_settings
- `sw/validator.py:193-201` check_settings
- `sw/subl_commands.py:294-296` SightWalkWindowListener.on_activated
- `sw/subl_commands.py:238-248` SightWalkHeaderListener.on_hover
- `sw/subl_chat.py:179-183` show_help

## 48. One colour scheme for the trips (17 views)

SightWalk: Select Colour Scheme: general, light or dark, only schemes of that kind, previewed live in every trip; the files' hues derived from it again, the other views take it as it is.

- `sw/subl_commands.py:62-64` SightWalkSelectColourSchemeCommand.run
- `sw/subl_commands.py:66-77` SightWalkSelectColourSchemeCommand.pick_kind
- `sw/subl_commands.py:92-95` all_schemes
- `sw/subl_tint.py:212-216` is_dark
- `sw/subl_commands.py:98-100` scheme_item
- `sw/subl_commands.py:79-81` SightWalkSelectColourSchemeCommand.preview
- `sw/subl_tint.py:251-256` refresh_all
- `sw/subl_reader.py:321-328` Reader.refresh_schemes
- `sw/subl_tint.py:100-110` chosen_scheme
- `sw/subl_tint.py:167-177` scheme_colours
- `sw/subl_tint.py:185-194` resolve_colour
- `sw/subl_tint.py:277-279` base_name
- `sw/subl_tint.py:197-209` plain_colour
- `sw/subl_tint.py:180-182` luminance
- `sw/subl_reader.py:330-337` Reader.plain_views
- `sw/subl_tint.py:219-227` apply_plain
- `sw/subl_commands.py:83-89` SightWalkSelectColourSchemeCommand.done

## 49. ctrl+tab (5 views)

The focus round the sights on screen, top to bottom, ctrl+shift+tab the other way.

- `sw/subl_commands.py:106-109` SightWalkCycleSightsCommand.run
- `sw/subl_commands.py:301-313` SightWalkWindowListener.on_window_command
- `sw/subl_reader.py:862-879` Reader.cycle
- `sw/plan.py:104-108` visible_indices
- `sw/plan.py:111-118` cycled

## 50. primary+g (11 views)

In a trip: from the sights to the bench and back. Elsewhere: to the open trip, or a new trip with no sights, the repository's files in their place.

- `sw/subl_commands.py:507-518` SightWalkToggleGuideCommand.run
- `sw/subl_reader.py:843-853` Reader.toggle_focus
- `sw/subl_commands.py:520-525` SightWalkToggleGuideCommand.folder
- `sw/subl_reader.py:192-196` Reader.open_empty
- `sw/subl_reader.py:198-218` Reader.empty_layout
- `sw/subl_reader.py:220-225` Reader.close_hijacker
- `sw/subl_commands.py:336-340` SightWalkWindowListener.offer_to_browser
- `sw/subl_commands.py:298-299` SightWalkWindowListener.on_load
- `sw/subl_reader.py:227-235` Reader.take_file
- `sw/subl_executor.py:112-124` op_browse
- `sw/subl_views.py:128-139` make_browser

## 51. What the validator refuses (16 views, survey)

Every refusal of the guide's calls, judged before the executor acts, with the facts it is given; each message says what to do instead.

- `sw/validator.py:26-31` check
- `sw/validator.py:56-59` not_stopped
- `sw/validator.py:62-64` trip_open
- `sw/validator.py:67-70` ready
- `sw/validator.py:73-86` files
- `sw/validator.py:123-127` check_show
- `sw/validator.py:130-135` check_open_trip
- `sw/subl_executor.py:192-201` trip_file
- `sw/validator.py:138-159` check_say
- `sw/validator.py:162-166` mask
- `sw/validator.py:169-175` crowded_lines
- `sw/validator.py:178-179` check_state
- `sw/validator.py:182-184` check_close
- `sw/validator.py:187-190` check_browse
- `sw/validator.py:193-201` check_settings
- `sw/validator.py:204-205` check_wait

## 52. Here (2 views)

The caret or a selection in a sight becomes here.

- `sw/subl_commands.py:315-325` SightWalkWindowListener.on_selection_modified
- `sw/subl_reader.py:855-860` Reader.note_selection

## 53. Words in two languages (9 views)

Switch Language: the setting changes, the words follow at once, in every open trip.

- `sw/subl_commands.py:470-473` SightWalkSwitchLanguageCommand.run
- `sight_walk.py:55-59` settings_changed
- `sw/words.py:140-142` set_language
- `sw/state.py:55-60` render_all
- `sw/words.py:136-137` word
- `sw/subl_chat.py:31-34` help_html
- `sw/subl_views.py:33-35` button_html
- `sw/subl_commands.py:555-568` SightWalkCompareFontsCommand.run
- `sw/subl_commands.py:571-579` kept_conversation

## 54. Endings (17 views, survey)

The guide is stopped, windows close.

- `sw/subl_commands.py:495-496` SightWalkStopGuideCommand.run
- `sw/subl_commands.py:498-499` SightWalkStopGuideCommand.is_enabled
- `sw/subl_guide.py:90-94` stop
- `sw/subl_guide.py:78-87` stop_when_idle
- `sw/subl_commands.py:342-349` SightWalkWindowListener.on_pre_close_window
- `sw/subl_commands.py:352-354` clear_schemes_if_unused
- `sw/subl_tint.py:300-304` first_load
- `sw/subl_tint.py:307-336` clear_schemes
- `sw/subl_tint.py:72-73` scheme_folder
- `sw/subl_commands.py:301-313` SightWalkWindowListener.on_window_command
- `sw/subl_commands.py:398-400` SightWalkCloseTripCommand.run
- `sw/subl_commands.py:378-381` SightWalkResetSightsCommand.run
- `sw/subl_reader.py:894-906` Reader.reset_sights
- `sw/subl_commands.py:383-385` SightWalkResetSightsCommand.is_enabled
- `sw/state.py:29-34` forget
- `sw/subl_executor.py:107-109` op_close
- `sw/state.py:41-42` current_reader

## 55. Names and room (12 views, survey)

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
- `sw/subl_executor.py:102-104` op_state
- `sw/subl_reader.py:1417-1422` Reader.folder
- `sw/subl_reader.py:1399-1401` Reader.note_waiting

## 56. Building blocks (11 views, survey)

The small classes and hooks the trips above stand on.

- `sw/plan.py:8-15` Item.__init__
- `sw/plan.py:22-35` Pane.__init__
- `sw/plan.py:37-39` Pane.spec
- `sw/plan.py:41-43` Pane.items
- `sw/plan.py:45-47` Pane.all_views
- `sw/subl_views.py:45-46` kept
- `sw/subl_views.py:49-54` phantoms
- `sw/subl_views.py:57-58` forget
- `sw/subl_chat.py:51-53` Guard.__init__
- `sw/subl_commands.py:234-236` SightWalkHeaderListener.is_applicable
- `sw/subl_commands.py:261-263` SightWalkChatListener.is_applicable

## 57. Settings and the rest of the colours (6 views, survey)

The agent's view of the settings, and colour helpers.

- `sw/subl_tint.py:84-86` band_amount
- `sw/subl_tint.py:59-69` from_tm_theme
- `sw/subl_tint.py:113-125` resolved_scheme
- `sw/subl_tint.py:89-93` scheme_stem
- `sw/subl_tint.py:29-30` hex_rgb
- `sw/subl_tint.py:288-293` apply_grey

## 58. The ontology: collections and sights (15 views, survey)

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

## 59. The ontology: networks (17 views, survey)

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

## 60. An informator and its tour (29 views)

Open Tour: an informator's tours to choose from, the informator read from its files, its trips in the tour's order in the Tour tab, a trip opened from it, its conversation kept, a box ticked by hand.

- `sw/subl_commands.py:408-417` SightWalkOpenTourCommand.run
- `sw/subl_commands.py:426-439` tour_choices
- `sw/subl_commands.py:442-452` found_files
- `sw/subl_commands.py:455-456` read_name
- `sw/subl_commands.py:459-464` read_field
- `sw/subl_commands.py:419-423` SightWalkOpenTourCommand.open
- `sw/words.py:153-160` trips_count
- `sw/subl_reader.py:1004-1018` Reader.open_tour
- `sw/subl_reader.py:1518-1520` read_json
- `sw/ontology.py:303-309` tour_from
- `sw/ontology.py:282-286` informator_from
- `sw/ontology.py:266-269` trip_from
- `sw/ontology.py:249-257` transition_from
- `sw/ontology.py:212-227` tour
- `sw/ontology.py:230-238` visit
- `sw/subl_vetting.py:326-332` read_walked
- `sw/subl_reader.py:1020-1040` Reader.tour_link
- `sw/subl_reader.py:1130-1140` Reader.keep_transcript
- `sw/subl_reader.py:1142-1150` Reader.kept_marks
- `sw/subl_reader.py:1152-1154` Reader.line_text
- `sw/subl_reader.py:1156-1168` Reader.restore_marks
- `sw/subl_reader.py:1498-1502` kept_frame
- `sw/subl_reader.py:1505-1507` transcripts_path
- `sw/subl_reader.py:1510-1515` read_transcripts
- `sw/subl_chat.py:251-253` set_transcript
- `sw/ontology.py:289-293` dumps
- `sw/subl_vetting.py:335-344` save_walked
- `sw/subl_reader.py:1257-1266` Reader.draw_tour
- `sw/subl_vetting.py:202-209` show_tour

## 61. Questions the code already asks (10 views)

Guards found in the code itself, carried to the sights that use the same objects without them.

- `sw/subl_reader.py:249-264` Reader.build
- `sw/subl_asked.py:33-44` draw
- `sw/subl_asked.py:20-30` sources
- `sw/questions.py:62-77` catalogue
- `sw/questions.py:58-59` functions
- `sw/questions.py:48-55` conditions
- `sw/questions.py:34-45` asked_in
- `sw/questions.py:19-31` subject
- `sw/questions.py:92-109` unasked
- `sw/questions.py:80-89` uses

## 62. Seeing where the code asks (9 views)

The underline and the popup that says where the code asks the question.

- `sw/subl_asked.py:47-57` mark
- `sw/subl_asked.py:73-80` popup_html
- `sw/subl_asked.py:83-84` escape
- `sw/subl_commands.py:531-533` SightWalkSightListener.is_applicable
- `sw/subl_commands.py:535-537` SightWalkSightListener.on_hover
- `sw/subl_asked.py:87-92` show_popup
- `sw/subl_asked.py:60-62` paint
- `sw/subl_asked.py:65-70` toggle
- `sw/subl_commands.py:543-544` SightWalkToggleSentinelsCommand.run

## 63. The guide's permissions (14 views)

The Permissions tab: a field ticked, remembered or not, and the guide SightWalk started restarted while it waits with the tools allowed now.

- `sw/subl_reader.py:1283-1286` Reader.draw_permissions
- `sw/subl_vetting.py:365-385` show_permissions
- `sw/subl_reader.py:1288-1303` Reader.permission_link
- `sw/subl_vetting.py:388-390` show_tip
- `sw/subl_guide.py:126-132` toggle
- `sw/permissions.py:37-39` remembered
- `sw/subl_guide.py:135-146` restart
- `sw/subl_guide.py:107-111` chosen
- `sw/subl_guide.py:114-116` folders
- `sw/permissions.py:23-34` allowed_tools
- `sw/permissions.py:42-44` reminders
- `sw/subl_guide.py:149-151` ours
- `sw/subl_reader.py:1305-1309` Reader.add_folder
- `sw/subl_guide.py:119-123` set_folders

## 64. Cutting a PNG (5 views)

Graphviz's PNG read, unfiltered, cropped and written again, in pure Python.

- `sw/pngcut.py:10-27` read
- `sw/pngcut.py:30-40` unfilter
- `sw/pngcut.py:43-54` predict
- `sw/pngcut.py:69-71` crop
- `sw/pngcut.py:57-66` write

## 65. The tour map's source (5 views)

The Tour tab asks for the tour map: each trip a row of its sights named file:function, the arrows between trips taken from the informator.

- `sw/subl_reader.py:1257-1266` Reader.draw_tour
- `sw/subl_reader.py:1268-1281` Reader.tour_sight
- `sw/tourmap.py:53-66` cross_arrows
- `sw/tourmap.py:33-50` tour_dot
- `sw/tourmap.py:22-30` column

## 66. Each sight's box (5 views)

A box's hue, drawn once for the whole tour so neighbours differ, its height hinting at its lines, and the list of trips the map stands under.

- `sw/tourmap.py:17-19` height
- `sw/tourmap.py:13-14` node
- `sw/subl_vetting.py:212-215` show_tour_page
- `sw/subl_vetting.py:218-229` tour_rows
- `sw/subl_vetting.py:232-237` code_words

## 67. The tour map in tiles (6 views)

dot lays the map out once to find each trip's frame; the picture is cut into tiles, each a link that opens the trip it lies in.

- `sw/subl_vetting.py:243-250` draw_tour_map
- `sw/subl_vetting.py:253-269` render_tiles
- `sw/subl_vetting.py:272-291` cut_tiles
- `sw/tourmap.py:69-91` tiles
- `sw/subl_vetting.py:299-304` run_dot
- `sw/subl_vetting.py:307-323` tour_map_html

## 68. An adventure opens (4 views)

show with aside: the trip recorded with its mother and opened in a window of its own, starting from the question that called it and the guide's reason.

- `sw/subl_reader.py:1074-1082` Reader.go_on_adventure
- `sw/subl_executor.py:73-79` open_adventure
- `sw/subl_reader.py:1084-1094` Reader.adventure
- `sw/subl_chat.py:75-76` transcript

## 69. Back from an adventure (4 views)

Its window closing keeps its conversation in its record; the Adventures tab opens it again.

- `sw/subl_reader.py:1096-1102` Reader.leave_adventure
- `sw/subl_reader.py:1104-1105` Reader.draw_adventures
- `sw/subl_vetting.py:349-357` show_adventures
- `sw/subl_reader.py:1107-1114` Reader.adventure_link

## 70. The tools over the window (5 views)

[⤢] in the Tools header lays the tools over almost the whole window under the top headers, kept apart; [Restore size] in the trip's header brings them back. Hovering a button says what it does.

- `sw/subl_reader.py:943-957` Reader.toggle_maximized
- `sw/subl_commands.py:360-363` SightWalkToggleMaximizedCommand.run
- `sw/subl_reader.py:959-988` Reader.arrange_maximized
- `sw/subl_vetting.py:98-101` buttons_help
- `sw/subl_chat.py:186-195` show_trip_help

## 71. Back and forward through trips (17 views)

◀ ▶ in the Sights' header, primary+[ and primary+]: each trip the guide shows goes into the window's history with its own conversation, starting from the question that called it; a step keeps the conversation shown and brings the other trip's back.

- `sw/subl_reader.py:1044-1050` Reader.visit
- `sw/history.py:38-44` last_exchange
- `sw/subl_reader.py:1058-1070` Reader.tell_story
- `sw/validator.py:104-116` check_story
- `sw/subl_reader.py:833-841` Reader.trip_title
- `sw/history.py:7-9` History.__init__
- `sw/history.py:20-25` History.visit
- `sw/subl_reader.py:1116-1119` Reader.leave
- `sw/history.py:14-18` History.keep
- `sw/history.py:11-12` History.current
- `sw/subl_reader.py:1121-1128` Reader.enter
- `sw/subl_chat.py:144-149` nav_phantom
- `sw/subl_commands.py:369-372` SightWalkStepCommand.run
- `sw/subl_reader.py:1052-1056` Reader.step
- `sw/history.py:27-28` History.can
- `sw/history.py:30-35` History.go
- `sw/subl_chat.py:132-136` help_or_link

## 72. Driving a trip from the terminal (7 views)

Tests without mouse or keys, in the guide's notation: sight_walk_fill sets the draft, whose <here> tags become links, sight_walk_select selects places, (>) the draft, and sight_walk_send_draft sends it.

- `sw/subl_commands.py:122-139` SightWalkFillCommand.run
- `sw/marks.py:348-366` read_here
- `sw/subl_commands.py:169-181` place_region
- `sw/marks.py:332-345` parse_place
- `sw/subl_commands.py:146-157` SightWalkSelectCommand.run
- `sw/subl_commands.py:184-191` note_selection
- `sw/subl_commands.py:163-166` SightWalkSendDraftCommand.run

## 73. The bench's answers listed (9 views)

The Answers tab: the bench's questions and answers by their first words; a click shows one's icons or places and brings it into the bench, a second click hides them.

- `sw/subl_reader.py:1217-1219` Reader.draw_answers
- `sw/subl_reader.py:1200-1215` Reader.bench_rows
- `sw/answers.py:9-19` entries
- `sw/subl_reader.py:1181-1191` Reader.answer_marks
- `sw/subl_vetting.py:395-410` show_answers
- `sw/subl_vetting.py:413-414` html_escape
- `sw/subl_reader.py:1221-1237` Reader.answer_link
- `sw/subl_reader.py:1193-1196` Reader.hide_answer
- `sw/subl_reader.py:1239-1244` Reader.scroll_bench
