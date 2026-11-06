You improve a multi-agent system whose task agents complete household tasks in a text environment, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each task the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
    p = planner(skills=["heat_task", "search_order"])
    a = actor(p, tools=["valid_actions", "memory"], skills=["heat_task"])
    return a
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this task: tools (aids the acting agent sees at every step (no effect on advisers)) and skills (how-to texts), chosen from the libraries
below. The returned node acts in the environment for up to 40 steps; nodes it takes as inputs are advisers whose written advice it reads before acting. Nodes without inputs run in parallel. `return x`: x acts in the environment. The meta-agent does not do the
task itself. Unusable output -> the first task agent alone with valid_actions (fixed).

# Self vs residual
A role is the same on every task, so it can hold only practices that help on every task that agent
works on. Whatever helps only some tasks (a method, a check, domain knowledge, a helper function)
belongs to the residual side: a skill or a tool, plus a meta-harness rule that says when to give it.
You learn which parts are general and which vary per task; the meta-agent fills in the varying part
on each task. Before putting a sentence into a role, ask: is it right for every task this agent
sees? If not, make it a skill or a tool and a rule. Conversely, a skill the meta-agent gives to nearly
every node of an agent can move into that agent's role.

# What you edit: three layers
| layer | side | what | effect |
|---|---|---|---|
| task-agent | self | add, remove or edit a task agent (its role) | always on for that agent |
| meta-agent | residual | add, edit or remove a rule of the meta-harness | how the meta-agent staffs, wires and equips teams |
| library | residual | add or edit a skill (never removed) | what the meta-agent can give; a new item has no effect until the meta-agent gives it |
The model, the answer format and the grader are fixed.

# Principles
- Evidence first: each change targets a failure pattern you see in the traces below (which problems,
  which node, which step went wrong, why), not a general best practice.
- Choose the layer that fits the root cause (see Self vs residual): a practice an agent should always
  follow -> its role; whom to staff, how to wire, which tools and skills -> a meta-harness rule;
  knowledge or a helper that only some tasks need -> a skill or tool and a rule.
- Regressions first: if the last accepted change broke problems, find out why before adding more.
- If a failure persists after changes on one layer (verdict INEFFECTIVE, or the problems stay wrong),
  revert them and try another layer.
- Few, decisive changes. Remove rules and agents the evidence does not support. Skills and tools are
  never removed: an unhelpful one is fixed by editing it or by the rules that say when to give it.

# Generality (hard constraints)
- Held-out tasks are different tasks of the same kind. Write nothing that only fits one task in
  this report: no answers, constants, entity, table or column names, or wording copied from a report
  task. A rule must name a class of tasks that can be recognized from the task text alone.
- Target patterns shared by several wrong tasks (cite them in evidence), not a single failure.
- No ban lists or name lists ("never give X", "only these tools") unless the cited failures were
  caused by X.
- Prefer removing, merging or shortening rules and roles over adding; if a new rule overlaps an old
  one, edit the old one. Every role, rule and skill costs tokens on each task, and a 9B model follows long
  instructions less reliably.
- A tool is a general helper (compute, check, search, inspect) with a test. It must not contain an
  answer or a special case for one task.
- At most 8 operations in this candidate (all changes together).

# Analysis
1. Read the history: which candidates were accepted or rejected, their held-out results (fixed and
   broken against the incumbent) and, for accepted changes, which of their cited problems were fixed.
   KEEP what works, IMPROVE what is directionally right, ROLLBACK what did not work and re-approach
   that pattern on another layer.
2. Read "Since the last accepted change" in the report: regressions first.
3. Read the traces of the wrong tasks: for each, find the node and the step where it went wrong.
   Group them into patterns and find each one's root cause.
4. Check which architectures, tools and skills help and which do not.

Objective: maximize accuracy on held-out problems.
This candidate may edit only the self harness: the task-agent layer.

# Output
A JSON object between <edit> and </edit>:
{"changes": [{"pattern": "<the failure pattern, one sentence>",
               "rationale": "<its root cause in the traces, and why this layer and these ops fix it>",
               "evidence": ["<labels of the wrong dev-A tasks that show this pattern, e.g. A12>"],
               "ops": [<edit operations, applied in order>]}]}
One change per failure pattern. If the candidate is accepted, the next round reports which of its
cited tasks were fixed.

# Edit operations
task-agent layer:
{"op": "add_agent", "name": "<name>", "role": "<role>"}
{"op": "remove_agent", "name": "<name>"}
{"op": "edit_agent", "name": "<name>", "role": "<new role>"}
meta-agent layer (rule numbers as shown below; new rules are appended):
{"op": "add_rule", "text": "<rule>"}
{"op": "edit_rule", "rule": <number>, "text": "<new rule>"}
{"op": "remove_rule", "rule": <number>}
library layer:
{"op": "add_skill", "name": "<name>", "when": "<when to give it (shown to the meta-agent)>", "text": "<the procedure (shown to the task agent)>"}
{"op": "edit_skill", "name": "<name>", "when": "<optional>", "text": "<optional>"}
(The tools of this task are built-in aids: they cannot be added or edited.)
At most 8 task agents, 20 rules, 40 skills and 24 tools. No rule may
mention a removed agent. Names: a letter, then letters, digits or underscores.

# Tools
- valid_actions: after every observation, the list of commands that are valid right now.
- memory: after every observation, a summary of the places visited so far and what was seen in each (closed/empty receptacles included).
- goal_reminder: after every observation, the task again and the number of steps left.

# Skills
- action_syntax (when: any task (exact command forms)): Commands: go to {recep}; open {recep}; close {recep}; take {obj} from {recep}; put {obj} in/on {recep}; clean {obj} with {sinkbasin}; heat {obj} with {microwave}; cool {obj} with {fridge}; use {lamp}; examine {obj or recep}; inventory; look. Use the exact names with numbers as they appear ('mug 1', 'countertop 2'). You can hold one object; you must be at a receptacle to take from or put on it. 'Nothing happens' means the command was invalid: change it.
- search_order (when: the target object is not in view (most tasks)): Search likely places first and never revisit a place you have checked. Typical: food (apple, potato, tomato, egg, lettuce, bread) -> fridge, countertop, diningtable, sinkbasin, garbagecan; dishes (mug, cup, plate, bowl, pan, pot) -> countertop, cabinet, diningtable, sinkbasin, shelf, drawer; small items (keychain, creditcard, pen, pencil, cd, cellphone) -> desk, drawer, sidetable, dresser, shelf; towels/soap -> towelholder, countertop, toilet, cabinet; books/laptops -> desk, bed, sofa, sidetable. Open closed cabinets, drawers, fridges and safes to see inside.
- pick_place (when: put an object in/on a receptacle): 1. Find the object (search_order), take it. 2. Go to the target receptacle; open it if closed. 3. put {obj} in/on {recep}. The task is done when the object is placed. Pitfall: placing a similar but different object type (a cup is not a mug).
- pick_two (when: put two objects of a type in/on a receptacle): 1. Find the first object, take it, put it in/on the target. 2. Go back to searching for the second one (it may be elsewhere; remember where you saw others). 3. Put the second in/on the same target. You can carry only one object at a time.
- clean_task (when: put a clean object somewhere): 1. Find and take the object. 2. go to sinkbasin 1 (or the sinkbasin), then 'clean {obj} with sinkbasin 1'. 3. Go to the target, open it if needed, put the object. Do not put the object in the sink to clean it; use the clean command.
- heat_task (when: put a hot or heated object somewhere): 1. Find and take the object. 2. go to microwave 1, then 'heat {obj} with microwave 1' (no need to open it or put the object inside). 3. Go to the target, open it if needed, put the object.
- cool_task (when: put a cool or cold object somewhere): 1. Find and take the object. 2. go to fridge 1, then 'cool {obj} with fridge 1' (no need to put it inside). 3. Go to the target, open it if needed, put the object. If the target is the fridge itself this is a plain placement.
- look_in_light (when: examine or look at an object with/under a lamp): 1. Find and take the object. 2. Find a desklamp or floorlamp (often on a desk, sidetable or dresser). 3. Go to the lamp while holding the object and 'use {lamp}'. Using the lamp while holding the object completes the task.
- stuck_recovery (when: long or tricky tasks): If an action fails twice or you are repeating yourself: stop, check what you hold (inventory), list unvisited places, and pick a different command. Do not repeat the same failing command. Prefer going to a new place over examining.

# Current organization
Task agents:
- actor: You act in a household text environment to complete the task. Each turn, write one short line 'Think: ...' and then 'Action: <one command>'.
- planner: You read the task and the room, and write a short plan for the teammate who will act: where to look first and the steps to finish. You do not act.
Meta-harness:
1. Every task: an actor with valid_actions.
2. Tasks with two objects or with cleaning, heating or cooling: a planner, then the actor reading its plan.
3. Give the skill for the task type.

# Report
# Report (dev-A)

Organization: acc 75.0% (meta-agent prompt 2529 chars; roles 286 chars). 3 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| pick_and_place_simple | 3 | 67% | planner[T][S]>actor[T][S] 1, planner[S]>actor[T][S] 1, actor[T][S] 1 |
| pick_clean_then_place_in_recep | 3 | 100% | planner[S]>actor[T][S] 3 |
| pick_heat_then_place_in_recep | 1 | 100% | planner[T][S]>actor[T][S] 1 |
| pick_two_obj_and_place | 1 | 0% | planner[T][S]>actor[T][S] 1 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| planner[S]>actor[T][S] | 4 | 100% |
| planner[T][S]>actor[T][S] | 3 | 33% |
| actor[T][S] | 1 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| planner | 7 | 0% | 0% | - | - | - |
| actor (with inputs) | 7 | 71% | 29% | 7 | 5 | - |
| actor | 1 | 100% | 0% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| skill:search_order | 10 | 20% | 80% |
| tool:valid_actions | 9 | 67% | 0% |
| tool:memory | 9 | 56% | 17% |
| skill:clean_task | 6 | 50% | 33% |
| skill:pick_place | 6 | 50% | 33% |
| tool:goal_reminder | 6 | 67% | 22% |
| skill:action_syntax | 5 | 80% | 20% |
| no tools (no Python) | 4 | 0% | 55% |
| skill:pick_two | 2 | 0% | 46% |
| skill:heat_task | 2 | 50% | 38% |
Never given: cool_task, look_in_light, stuck_recovery.

## Wrong (2)
- A2 [pick_and_place_simple] answered False; correct True; team: p = planner(tools=['goal_reminder'], skills=['search_order']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_place', 'search_order']); return a
- A3 [pick_two_obj_and_place] answered False; correct True; team: p = planner(tools=['memory', 'goal_reminder'], skills=['search_order', 'pick_two']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_two', 'action_syntax']); return a

## Traces of the wrong problems (2 of 2; node outputs over 6000 chars are cut in the middle)
### A2 [pick_and_place_simple]
You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, a towelholder 2, and a towelholder 1.

Your task is to: put a cloth in drawer.
Correct: True
Team: p = planner(tools=['goal_reminder'], skills=['search_order']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_place', 'search_order']); return a
#### node p = planner(inputs=[], tools=['goal_reminder'], skills=['search_order']) -> None (wrong)
```
1. **Search Towels First**: Check `towelholder 1`, `towelholder 2`, `handtowelholder 1`, and `handtowelholder 2` for a cloth.
2. **Retrieve Cloth**: Once found, pick up the cloth.
3. **Open Drawers**: Open `drawer 1` through `drawer 6` in order until you find an empty one.
4. **Place Cloth**: Put the cloth inside the open drawer.
5. **Close Drawer**: Ensure the drawer is closed after placing the item.
```
#### node a = actor(inputs=['p'], tools=['valid_actions', 'memory'], skills=['pick_place', 'search_order']) -> False (wrong, cut at the token limit)
```
You are in the middle of a room. Looking quickly around you, you see a countertop 1, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a garbagecan 1, a handtowelholder 2, a handtowelholder 1, a sinkbasin 1, a toilet 1, a toiletpaperhanger 1, a towelholder 2, and a towelholder 1.

Your task is to: put a cloth in drawer.
> go to towelholder 1
You arrive at towelholder 1. On the towelholder 1, you see a towel 1.
> take towel 1 from towelholder 1
You pick up the towel 1 from the towelholder 1.
> go to drawer 1
You arrive at drawer 1. The drawer 1 is closed.
> open drawer 1
You open the drawer 1. The drawer 1 is open. In it, you see nothing.
> put towel 1 in drawer 1
Nothing happens.
> put towel 1 in drawer 1
Nothing happens.
> Think: The 'put' command is not working, and 'towel 1' is not in the list of valid actions or available objects in the current context (only 'towel 1' was seen earlier, but maybe the system expects a generic name or the object was dropped). However, looking at the valid actions, 'examine towel 1' is there, implying I might still have it or need to interact with it differently. Wait, the valid actions list doesn't include 'take' or 'put' for 'towel 1'. This suggests the object might not be in my inventory anymore or the syntax is restricted. Let's re-evaluate. The planner said to put a "cloth". Maybe "towel 1" isn't the right object name for the 'put' command, or I need to check my inventory. But I don't have an inventory command in the valid actions list. Let's try to go to another drawer in case the first one is the wrong one or the command simply doesn't work there. Actually, looking closely at the valid actions, there is no 'put' command listed at all! This is strange. Perhaps I need to go to the drawer and the system will handle it, or I need to check if the towel is actually a "cloth". Let's try going to drawer 2 to see if the logic holds or if I missed something about the object. Wait, the valid actions are strictly limited. If
Nothing happens.
> inventory
You are carrying: a towel 1.
> go to drawer 2
You arrive at drawer 2. The drawer 2 is closed.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
> inventory
You are carrying: a towel 1.
```
### A3 [pick_two_obj_and_place]
You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a diningtable 1, a drawer 12, a drawer 11, a drawer 10, a drawer 9, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.

Your task is to: put two spatula in drawer.
Correct: True
Team: p = planner(tools=['memory', 'goal_reminder'], skills=['search_order', 'pick_two']); a = actor(p, tools=['valid_actions', 'memory'], skills=['pick_two', 'action_syntax']); return a
#### node p = planner(inputs=[], tools=['memory', 'goal_reminder'], skills=['search_order', 'pick_two']) -> None (wrong)
```
1. Start searching for **spatula** in **countertop 1** and **countertop 2**, as cooking utensils are typically stored there.
2. If not found on countertops, check **cabinet** units (prioritize those near the stove or countertops) and **drawer** units.
3. Once the first spatula is found, **pick it up** and place it directly into any available **drawer**.
4. Return to searching for the **second spatula** (re-check countertops, cabinets, or other drawers if missed).
5. After finding the second spatula, **pick it up** and place it into the same **drawer** with the first one.
```
#### node a = actor(inputs=['p'], tools=['valid_actions', 'memory'], skills=['pick_two', 'action_syntax']) -> False (wrong, cut at the token limit)
```
You are in the middle of a room. Looking quickly around you, you see a cabinet 27, a cabinet 26, a cabinet 25, a cabinet 24, a cabinet 23, a cabinet 22, a cabinet 21, a cabinet 20, a cabinet 19, a cabinet 18, a cabinet 17, a cabinet 16, a cabinet 15, a cabinet 14, a cabinet 13, a cabinet 12, a cabinet 11, a cabinet 10, a cabinet 9, a cabinet 8, a cabinet 7, a cabinet 6, a cabinet 5, a cabinet 4, a cabinet 3, a cabinet 2, a cabinet 1, a coffeemachine 1, a countertop 2, a countertop 1, a diningtable 1, a drawer 12, a drawer 11, a drawer 10, a drawer 9, a drawer 8, a drawer 7, a drawer 6, a drawer 5, a drawer 4, a drawer 3, a drawer 2, a drawer 1, a fridge 1, a garbagecan 1, a microwave 1, a sinkbasin 1, a stoveburner 4, a stoveburner 3, a stoveburner 2, a stoveburner 1, and a toaster 1.

Your task is to: put two spatula in drawer.
> go to countertop 1
You arrive at countertop 1. On the countertop 1, you see a bowl 1, a dishsponge 1, a houseplant 2, a houseplant 1, a ladle 1, a papertowelroll 1, a peppershaker 3, a plate 1, a potato 1, a soapbottle 3, a spatula 2, a spoon 1, and a winebottle 2.
> take spatula 2 from countertop 1
You pick up the spatula 2 from the countertop 1.
> go to drawer 1
You arrive at drawer 1. The drawer 1 is closed.
> open drawer 1
You open the drawer 1. The drawer 1 is open. In it, you see nothing.
> move spatula 2 to drawer 1
You move the spatula 2 to the drawer 1.
> go to countertop 2
You arrive at countertop 2. On the countertop 2, you see a apple 1, a cup 1, a mug 1, a saltshaker 2, and a winebottle 3.
> go to cabinet 2
You arrive at cabinet 2. The cabinet 2 is closed.
> open cabinet 2
You open the cabinet 2. The cabinet 2 is open. In it, you see nothing.
> go to cabinet 3
You arrive at cabinet 3. The cabinet 3 is closed.
> open cabinet 3
You open the cabinet 3. The cabinet 3 is open. In it, you see nothing.
> go to cabinet 4
You arrive at cabinet 4. The cabinet 4 is closed.
> open cabinet 4
You open the cabinet 4. The cabinet 4 is open. In it, you see nothing.
> go to cabinet 5
You arrive at cabinet 5. The cabinet 5 is closed.
> open cabinet 5
You open the cabinet 5. The cabinet 5 is open. In it, you see nothing.
> go to cabinet 6
You arrive at cabinet 6. The cabinet 6 is closed.
> open cabinet 6
You open the cabinet 6. The cabinet 6 is open. In it, you see nothing.
> go to cabinet 7
You arrive at cabinet 7. On the cabinet 7, you see nothing.
> go to cabinet 8
You arrive at cabinet 8. The cabinet 8 is closed.
> open cabinet 8
You open the cabinet 8. The cabinet 8 is open. In it, you see a pan 1.
> go to cabinet 9
You arrive at cabinet 9. The cabinet 9 is closed.
> open cabinet 9
You open the cabinet 9. The cabinet 9 is open. In it, you see nothing.
> go to cabinet 10
You arrive at cabinet 10. The cabinet 10 is closed.
> open cabinet 10
You open the cabinet 10. The cabinet 10 is open. In it, you see nothing.
> go to cabinet 11
You arrive at cabinet 11. The cabinet 11 is closed.
> open cabinet 11
You open the cabinet 11. The cabinet 11 is open. In it, you see a peppershaker 2.
> go to cabinet 12
You arrive at cabinet 12. On the cabinet 12, you see nothing.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
> go to cabinet 13
Nothing happens.
```

# History (held-out dev-B)
round 0 (starting organization): acc 75.0%

Output the JSON object between <edit> and </edit>.