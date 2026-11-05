# Report (dev-A)

Organization: acc 86.7% (meta-agent prompt 3002 chars). 3 distinct architectures, 2.0 nodes per problem. Fallback (unusable meta-agent output): 2.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| look_at_obj_in_light | 13 | 100% | planner[S]>actor[T][S] 11, actor[T][S],planner[S] 2 |
| pick_and_place_simple | 38 | 97% | planner[S]>actor[T][S] 32, actor[T][S],planner[S] 6 |
| pick_clean_then_place_in_recep | 22 | 77% | planner[S]>actor[T][S] 17, actor[T][S],planner[S] 4, actor[T] 1 |
| pick_cool_then_place_in_recep | 19 | 68% | planner[S]>actor[T][S] 17, actor[T][S],planner[S] 2 |
| pick_heat_then_place_in_recep | 15 | 73% | planner[S]>actor[T][S] 13, actor[T][S],planner[S] 1, actor[T] 1 |
| pick_two_obj_and_place | 43 | 91% | planner[S]>actor[T][S] 38, actor[T][S],planner[S] 5 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| planner[S]>actor[T][S] | 128 | 88% |
| actor[T][S],planner[S] | 20 | 80% |
| actor[T] | 2 | 50% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| planner | 148 | 0% | 0% | - | - | - |
| actor (with inputs) | 128 | 88% | 12% | 128 | 113 | - |
| actor | 22 | 77% | 23% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| skill:action_syntax | 154 | 84% | 1% |
| skill:search_order | 153 | 3% | 86% |
| tool:valid_actions | 150 | 87% | 0% |
| no tools (no Python) | 148 | 0% | 87% |
| tool:memory | 148 | 87% | 1% |
| tool:goal_reminder | 148 | 87% | 1% |
| skill:pick_place | 137 | 57% | 32% |
| skill:pick_two | 86 | 45% | 43% |
| skill:clean_task | 40 | 38% | 45% |
| skill:cool_task | 38 | 34% | 45% |
| skill:heat_task | 28 | 39% | 44% |
| skill:look_in_light | 26 | 50% | 43% |
Never given: stuck_recovery.

Meta-agent output problems: line 1: unknown agent 'agent' (2); line 2: unknown agent 'agent' (2); return must name a node defined above (2); no node (2)

## Wrong (20)
- [pick_and_place_simple] You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, a towelholder 2
  architecture: p = planner(skills=['search_order', 'pick_place']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'pick_place']); return a; answered False, correct True
- [pick_two_obj_and_place] You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a
  architecture: p = planner(skills=['search_order', 'pick_two']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'pick_two', 'pick_place']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a c
  architecture: p = planner(skills=['search_order', 'clean_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'clean_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a diningtable
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'cool_task', 'pick_place']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a bathtubbasin 1, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a garbagecan 1, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.

Y
  architecture: p = planner(skills=['search_order', 'clean_task']); a = actor(tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'clean_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cab
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'cool_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a drawer 13, a drawer 12, a drawer 11, a dr
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'cool_task', 'pick_place']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a drawer 13, a drawer 12, a drawer 11, a dr
  architecture: p = planner(skills=['search_order', 'clean_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'clean_task', 'pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cab
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'cool_task', 'pick_place']); return a; answered False, correct True
- [pick_heat_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabi
  architecture: p = planner(skills=['search_order', 'heat_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['action_syntax', 'heat_task', 'pick_place']); return a; answered False, correct True