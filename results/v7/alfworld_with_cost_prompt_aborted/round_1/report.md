# Report (dev-A)

Organization: acc 83.3%, cost 10144/problem, of which the meta-agent 1472 (its prompt 2423 chars). 5 distinct architectures, 1.8 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | cost | architectures |
|---|---|---|---|---|
| look_at_obj_in_light | 13 | 92% | 5655 | planner[S]>actor[T][S] 9, actor[T][S] 4 |
| pick_and_place_simple | 38 | 97% | 5139 | actor[T][S] 20, planner[S]>actor[T][S] 17, planner[T][S]>actor[T][S] 1 |
| pick_clean_then_place_in_recep | 22 | 64% | 16098 | planner[S]>actor[T][S] 19, planner[T][S]>actor[T][S] 2, actor[T][S],planner[T][S] 1 |
| pick_cool_then_place_in_recep | 19 | 63% | 12273 | planner[S]>actor[T][S] 18, actor[T][S],planner[S] 1 |
| pick_heat_then_place_in_recep | 15 | 73% | 14821 | planner[S]>actor[T][S] 13, planner[T][S]>actor[T][S] 1, actor[T][S],planner[S] 1 |
| pick_two_obj_and_place | 43 | 91% | 10307 | planner[S]>actor[T][S] 35, actor[T][S],planner[S] 5, planner[T][S]>actor[T][S] 2 |

## Architectures
| architecture | uses | acc | mean cost |
|---|---|---|---|
| planner[S]>actor[T][S] | 111 | 81% | 11028 |
| actor[T][S] | 24 | 96% | 5732 |
| actor[T][S],planner[S] | 7 | 86% | 9199 |
| planner[T][S]>actor[T][S] | 6 | 67% | 14062 |
| actor[T][S],planner[T][S] | 2 | 100% | 5642 |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| planner | 126 | 0% | 0% | 172 | - | - | - |
| actor (with inputs) | 117 | 80% | 20% | 9617 | 117 | 94 | - |
| actor | 33 | 94% | 6% | 4669 | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| skill:search_order | 170 | 25% | 78% |
| tool:valid_actions | 158 | 79% | 0% |
| tool:memory | 129 | 78% | 17% |
| no tools (no Python) | 118 | 0% | 79% |
| skill:pick_place | 90 | 63% | 37% |
| tool:goal_reminder | 55 | 84% | 36% |
| skill:action_syntax | 40 | 65% | 42% |
| skill:pick_two | 40 | 80% | 39% |
| skill:clean_task | 38 | 34% | 47% |
| skill:cool_task | 31 | 39% | 46% |
| skill:heat_task | 25 | 44% | 45% |
| skill:look_in_light | 14 | 86% | 43% |
Never given: stuck_recovery.

## Wrong (25)
- [pick_and_place_simple] You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, a towelholder 2
  architecture: a = actor(tools=['valid_actions', 'memory'], skills=['search_order', 'pick_place', 'action_syntax']); return a; answered False, correct True
- [pick_two_obj_and_place] You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a
  architecture: p = planner(skills=['search_order', 'pick_place']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_place']); return a; answered False, correct True
- [pick_heat_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 4, a c
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['heat_task', 'action_syntax']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a c
  architecture: p = planner(skills=['search_order', 'clean_task']); a = actor(p, tools=['valid_actions', 'memory'], skills=['clean_task']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabi
  architecture: p = planner(skills=['search_order', 'clean_task', 'pick_place']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['search_order', 'clean_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a diningtable
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory'], skills=['cool_task']); return a; answered False, correct True
- [pick_heat_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a
  architecture: p = planner(tools=['valid_actions', 'memory'], skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['search_order', 'heat_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory'], skills=['cool_task']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 1, a diningtable 3, a diningtable 2, a diningtable 1, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sidetable 1, a s
  architecture: p = planner(skills=['search_order']); a = actor(p, tools=['valid_actions'], skills=['clean_task']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a
  architecture: p = planner(skills=['search_order']); a = actor(p, tools=['valid_actions', 'memory'], skills=['cool_task', 'pick_place']); return a; answered False, correct True

## Most expensive correct problems (possible waste)
- [pick_heat_then_place_in_recep, cost 20690] You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a c
  architecture: p = planner(skills=['search_order', 'heat_task']); a = actor(tools=['valid_actions', 'memory', 'goal_reminder'], skills=['heat_task', 'pick_place']); return a
- [pick_two_obj_and_place, cost 19601] You are in the middle of a room. Looking quickly around you, you see a bed 1, a desk 1, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer
  architecture: p = planner(skills=['search_order', 'pick_two']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_two']); return a
- [pick_two_obj_and_place, cost 19319] You are in the middle of a room. Looking quickly around you, you see a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cab
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_two']); return a
- [pick_two_obj_and_place, cost 18951] You are in the middle of a room. Looking quickly around you, you see a bathtubbasin 1, a drawer 1, a garbagecan 1, a handtowelholder 1, a sidetable 1, a sinkbasin 1, a toilet 1, a 
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_two', 'action_syntax']); return a
- [pick_and_place_simple, cost 17984] You are in the middle of a room. Looking quickly around you, you see a armchair 1, a bed 1, a drawer 16, a drawer 15, a drawer 14, a drawer 13, a drawer 12, a drawer 11, a drawer 1
  architecture: p = planner(skills=['search_order']); a = actor(p, tools=['valid_actions'], skills=['pick_place']); return a