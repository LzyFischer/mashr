You improve a multi-agent system whose task agents write Python functions from specifications, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each problem the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
    a = coder(tools=["python", "run_examples"], skills=["edge_cases"])
    b = tester(a, tools=["run_examples", "compare"])
    return b
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this problem: tools (Python functions (no tools = no Python; up to 3 runs)) and skills (how-to texts), chosen from the libraries
below. A node with tools may run Python up to 3 times (tools preloaded), then writes its final function. It reads the problem, its skills and the full work of its inputs. Nodes without inputs run in parallel. `return x`: x's function is the answer. The meta-agent does not do the
problem itself. Unusable output -> the first task agent alone with python (fixed).

# Self vs residual
A role is the same on every problem, so it can hold only practices that help on every problem that agent
works on. Whatever helps only some problems (a method, a check, domain knowledge, a helper function)
belongs to the residual side: a skill or a tool, plus a meta-harness rule that says when to give it.
You learn which parts are general and which vary per problem; the meta-agent fills in the varying part
on each problem. Before putting a sentence into a role, ask: is it right for every problem this agent
sees? If not, make it a skill or a tool and a rule. Conversely, a skill the meta-agent gives to nearly
every node of an agent can move into that agent's role.

# What you edit: three layers
| layer | side | what | effect |
|---|---|---|---|
| task-agent | self | add, remove or edit a task agent (its role) | always on for that agent |
| meta-agent | residual | add, edit or remove a rule of the meta-harness | how the meta-agent staffs, wires and equips teams |
| library | residual | add or edit a skill or a tool (never removed) | what the meta-agent can give; a new item has no effect until the meta-agent gives it |
The model, the answer format and the grader are fixed.

# Principles
- Evidence first: each change targets a failure pattern you see in the traces below (which problems,
  which node, which step went wrong, why), not a general best practice.
- Choose the layer that fits the root cause (see Self vs residual): a practice an agent should always
  follow -> its role; whom to staff, how to wire, which tools and skills -> a meta-harness rule;
  knowledge or a helper that only some problems need -> a skill or tool and a rule.
- Regressions first: if the last accepted change broke problems, find out why before adding more.
- If a failure persists after changes on one layer (verdict INEFFECTIVE, or the problems stay wrong),
  revert them and try another layer.
- Few, decisive changes. Remove rules and agents the evidence does not support. Skills and tools are
  never removed: an unhelpful one is fixed by editing it or by the rules that say when to give it.

# Generality (hard constraints)
- Held-out problems are different problems of the same kind. Write nothing that only fits one problem in
  this report: no answers, constants, entity, table or column names, or wording copied from a report
  problem. A rule must name a class of problems that can be recognized from the problem text alone.
- Target patterns shared by several wrong problems (cite them in evidence), not a single failure.
- No ban lists or name lists ("never give X", "only these tools") unless the cited failures were
  caused by X.
- Prefer removing, merging or shortening rules and roles over adding; if a new rule overlaps an old
  one, edit the old one. Every role, rule and skill costs tokens on each problem, and a 9B model follows long
  instructions less reliably.
- A tool is a general helper (compute, check, search, inspect) with a test. It must not contain an
  answer or a special case for one problem.
- At most 8 operations in this candidate (all changes together).

# Analysis
1. Read the history: which candidates were accepted or rejected, their held-out results (fixed and
   broken against the incumbent) and, for accepted changes, which of their cited problems were fixed.
   KEEP what works, IMPROVE what is directionally right, ROLLBACK what did not work and re-approach
   that pattern on another layer.
2. Read "Since the last accepted change" in the report: regressions first.
3. Read the traces of the wrong problems: for each, find the node and the step where it went wrong.
   Group them into patterns and find each one's root cause.
4. Check which architectures, tools and skills help and which do not.

Objective: maximize accuracy on held-out problems.
This candidate may edit all three layers.

# Output
A JSON object between <edit> and </edit>:
{"changes": [{"pattern": "<the failure pattern, one sentence>",
               "rationale": "<its root cause in the traces, and why this layer and these ops fix it>",
               "evidence": ["<labels of the wrong dev-A problems that show this pattern, e.g. A12>"],
               "ops": [<edit operations, applied in order>]}]}
One change per failure pattern. If the candidate is accepted, the next round reports which of its
cited problems were fixed.

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
{"op": "add_tool", "name": "<name>", "doc": "<signature and what it prints or returns>", "code": "<Python source defining it>", "test": "<Python asserts; must pass>"}
{"op": "edit_tool", "name": "<name>", "doc": "<optional>", "code": "<optional>", "test": "<optional>"}
Tool code runs in a sandbox (Python 3, numpy, no network, 20 s) with PROBLEM (the problem statement) and ENTRY (the function name) defined; the code of a node's tools is preloaded before the code the agent writes. Tools print their results. A new or edited tool is run with its test first; if the test fails, the candidate is sent back.
At most 8 task agents, 20 rules, 40 skills and 24 tools. No rule may
mention a removed agent. Names: a letter, then letters, digits or underscores.

# Tools
- python: Run Python (standard library, numpy) to test code: define the function, call it, print results.
- run_examples: run_examples(func=None) -> prints PASS/FAIL for every example in the problem statement (the '>>>' lines with their expected output, or the 'assert' lines) run against func (default: the function with the problem's name, defined in your code).
```python
def run_examples(func=None):
    g = globals()
    f = func or g.get(ENTRY)
    if f is None:
        print(f"define {ENTRY} first"); return
    env = dict(g); env[ENTRY] = f
    lines = PROBLEM.splitlines()
    checks = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("assert "):
            checks.append((s[7:], None))
        elif s.startswith(">>> "):
            nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
            checks.append((s[4:], nxt))
    if not checks:
        print("no examples found in the problem"); return
    n = 0
    for expr, exp in checks:
        try:
            got = eval(expr, env)
            if exp is None:
                ok = bool(got)
            else:
                try:
                    ok = got == eval(exp, env)
                except Exception:
                    ok = repr(got) == exp
        except Exception as e:
            ok, got = False, f"{type(e).__name__}: {e}"
        n += bool(ok)
        print(("PASS " if ok else "FAIL ") + expr[:200] + ("" if ok else f"  -> got {got!r:.200}"
              + (f", expected {exp}" if exp else "")))
    print(f"{n}/{len(checks)} examples pass")
```
- compare: compare(f, g, inputs) -> runs f(*x) and g(*x) for each tuple x in inputs and prints the mismatches (first 5) and their count; e.g. a fast solution against a brute-force one.
```python
def compare(f, g, inputs):
    import copy
    bad = []
    for x in inputs:
        x = tuple(x) if isinstance(x, (list, tuple)) else (x,)
        try:
            a = f(*copy.deepcopy(x))
        except Exception as e:
            a = f"{type(e).__name__}: {e}"
        try:
            b = g(*copy.deepcopy(x))
        except Exception as e:
            b = f"{type(e).__name__}: {e}"
        if a != b:
            bad.append((x, a, b))
    for x, a, b in bad[:5]:
        print(f"input {x!r:.200}: {a!r:.150} vs {b!r:.150}")
    print(f"{len(bad)}/{len(inputs)} mismatches")
```
- timed: timed(func, *args) -> prints how long func(*args) takes (stops after 5 s); hidden tests use large inputs, so check the speed of your solution on a large one.
```python
def timed(func, *args):
    import signal, time
    def _stop(*_):
        raise TimeoutError("over 5 s")
    old = signal.signal(signal.SIGALRM, _stop)
    signal.alarm(5)
    t = time.time()
    try:
        func(*args)
        print(f"{time.time() - t:.3f} s")
    except TimeoutError:
        print("too slow: over 5 s")
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
```

# Skills
- read_spec (when: any problem): 1. Restate the input types, the output type and every rule in the specification before coding. 2. The examples are part of the specification: your function must reproduce them exactly, including the output type (list vs tuple, int vs float, True/False). 3. Return the value; do not print and do not read input. 4. Keep the given function name and parameter order.
- edge_cases (when: inputs are lists, strings or numbers whose size or sign can vary): Hidden tests probe the corners. Check before answering: empty list/string, one element, all equal elements, duplicates, negative numbers, zero, unsorted input, very large values, and None-like cases the specification mentions. Decide what each must return from the specification (not from a guess), and make sure the code does not crash on them.
- examples_check (when: the problem statement contains examples): Before the final answer, run every example (run_examples, or by hand if you have no tools: trace the code line by line on each example). If one fails, find the rule you misread instead of special-casing the example.
- string_rules (when: string manipulation (case, words, characters, formatting)): 1. Case: does the comparison or output keep, lower or upper case? 2. Whitespace: split() vs split(' ') (multiple spaces, leading/trailing spaces). 3. Which characters count (letters only, vowels incl. 'y'?, digits, punctuation)? 4. Keep the original order unless told to sort. 5. Return the exact format of the examples (quotes, separators).
- numeric_rules (when: arithmetic, rounding, division or number formats): 1. Return type: int vs float, as in the examples. 2. // and % with negative numbers round towards minus infinity in Python. 3. round() rounds halves to even; use the rule the problem states. 4. Compare floats with a tolerance. 5. Large numbers: use integers, not floats, to stay exact.
- efficiency (when: inputs can be large (primes, divisors, sequences, nested loops, recursion)): The plus tests use large inputs and a time limit of a few times the reference solution. Avoid exponential recursion (memoize or iterate), quadratic loops over long lists when a set/dict/sort works, and trial division beyond sqrt(n). Check the speed on a large input (timed) before answering.
- assert_signature (when: the problem gives an assert line (the MBPP style)): The assert fixes the function name, the number and order of arguments and the exact return value: match its type (tuple vs list vs set, int vs float, bool) and format. If it wraps the call (e.g. set(...)), the order of elements does not matter; otherwise it does.

# Current organization
Task agents:
- coder: You write correct, complete Python functions that meet the specification exactly.
- tester: You test the solution your teammates wrote: derive test cases from the specification (including edge cases), run them, fix every bug you find, and give the corrected complete function.
- reviewer: You review the solutions you are given against the specification: find any bug or misread requirement and give the complete function you believe is correct.
Meta-harness:
1. Simple, clearly specified function: one coder with python.
2. Tricky specification or many edge cases: a coder with python and run_examples, then a tester with run_examples that reads its work.
3. Give skills that match the problem.

# Report
# Report (dev-A)

Organization: acc 100.0% (meta-agent prompt 3061 chars; roles 421 chars). 2 distinct architectures, 1.5 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| mbpp_plus | 8 | 100% | coder[T][S]>tester[T][S] 4, coder[T][S] 4 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| coder[T][S]>tester[T][S] | 4 | 100% |
| coder[T][S] | 4 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| coder | 8 | 100% | 0% | - | - | - |
| tester (with inputs) | 4 | 100% | 0% | 2 | 2 | 2 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_examples | 11 | 100% | 100% |
| tool:python | 8 | 100% | 100% |
| skill:examples_check | 6 | 100% | 100% |
| skill:read_spec | 5 | 100% | 100% |
| skill:edge_cases | 5 | 100% | 100% |
| skill:assert_signature | 4 | 100% | 100% |
| skill:string_rules | 3 | 100% | 100% |
| skill:numeric_rules | 2 | 100% | 100% |
| tool:compare | 1 | 100% | 100% |
Never given: timed, efficiency.

## Wrong (0)

## Traces of the wrong problems (0 of 0; node outputs over 6000 chars are cut in the middle)

# History (held-out dev-B)
round 0 (starting organization): acc 87.5%

Output the JSON object between <edit> and </edit>.