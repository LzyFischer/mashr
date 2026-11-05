# Report (dev-A)

Organization: acc 82.0% (meta-agent prompt 2324 chars). 5 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| look_at_obj_in_light | 13 | 92% | planner[S]>actor[T][S] 12, planner[T][S]>actor[T][S] 1 |
| pick_and_place_simple | 38 | 87% | planner[S]>actor[T][S] 23, actor[T][S] 12, actor[T][S],planner[T][S] 1 |
| pick_clean_then_place_in_recep | 22 | 59% | planner[S]>actor[T][S] 19, actor[T][S] 1, actor[T][S],planner[T][S] 1 |
| pick_cool_then_place_in_recep | 19 | 74% | planner[S]>actor[T][S] 16, planner[T][S]>actor[T][S] 2, actor[T][S],planner[S] 1 |
| pick_heat_then_place_in_recep | 15 | 80% | planner[S]>actor[T][S] 12, planner[T][S]>actor[T][S] 3 |
| pick_two_obj_and_place | 43 | 91% | planner[S]>actor[T][S] 34, planner[T][S]>actor[T][S] 6, actor[T][S],planner[S] 3 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| planner[S]>actor[T][S] | 116 | 84% |
| planner[T][S]>actor[T][S] | 14 | 86% |
| actor[T][S] | 13 | 77% |
| actor[T][S],planner[S] | 5 | 60% |
| actor[T][S],planner[T][S] | 2 | 50% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| planner | 137 | 0% | 0% | - | - | - |
| actor (with inputs) | 130 | 84% | 16% | 130 | 109 | - |
| actor | 20 | 70% | 30% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| skill:search_order | 167 | 14% | 82% |
| tool:valid_actions | 163 | 75% | 0% |
| tool:memory | 151 | 75% | 7% |
| no tools (no Python) | 121 | 0% | 74% |
| tool:goal_reminder | 117 | 74% | 21% |
| skill:action_syntax | 113 | 58% | 33% |
| skill:pick_place | 102 | 62% | 32% |
| skill:pick_two | 46 | 76% | 37% |
| skill:clean_task | 32 | 41% | 43% |
| skill:cool_task | 30 | 43% | 43% |
| skill:heat_task | 29 | 41% | 43% |
| skill:look_in_light | 12 | 83% | 41% |
Never given: stuck_recovery.

## Wrong (27)
- [pick_and_place_simple] You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, a towelholder 2
  architecture: p = planner(skills=['search_order', 'pick_place']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['pick_place', 'action_syntax']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a c
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['clean_task', 'pick_place']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabi
  architecture: p = planner(skills=['search_order', 'pick_place']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 3, a countertop 2, a countertop 1, a diningtable
  architecture: p = planner(skills=['search_order', 'cool_task', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory'], skills=['cool_task', 'action_syntax']); return a; answered False, correct True
- [pick_and_place_simple] You are in the middle of a room. Looking quickly around you, you see a armchair 1, a bed 1, a drawer 16, a drawer 15, a drawer 14, a drawer 13, a drawer 12, a drawer 11, a drawer 10, a drawer 9, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['pick_place', 'action_syntax']); return a; answered False, correct True
- [pick_clean_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a bathtubbasin 1, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a countertop 1, a garbagecan 1, a handtowelholder 1, a sinkbasin 2, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, and a towelholder 1.

Y
  architecture: p = planner(skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory'], skills=['clean_task']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cab
  architecture: p = planner(tools=['valid_actions', 'memory', 'goal_reminder'], skills=['search_order', 'action_syntax']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['cool_task', 'pick_place', 'action_syntax']); return a; answered False, correct True
- [pick_heat_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a
  architecture: p = planner(skills=['search_order', 'heat_task']); a = actor(p, tools=['valid_actions', 'memory', 'goal_reminder'], skills=['heat_task', 'pick_place']); return a; answered False, correct True
- [pick_and_place_simple] You are in the middle of a room. Looking quickly around you, you see a bed 1, a desk 1, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a dresser 1, a garbagecan 1, a laundryhamper 1, and a shelf 1.

Your task is to: put some pen on drawer.
  architecture: a = actor(tools=['valid_actions'], skills=['pick_place']); return a; answered False, correct True
- [pick_cool_then_place_in_recep] You are in the middle of a room. Looking quickly around you, you see a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cab
  architecture: p = planner(skills=['search_order', 'cool_task']); a = actor(p, tools=['valid_actions', 'memory'], skills=['cool_task', 'pick_place']); return a; answered False, correct True