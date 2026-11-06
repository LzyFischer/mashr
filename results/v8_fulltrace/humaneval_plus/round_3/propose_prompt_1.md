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
- At most 6 operations in this candidate (all changes together).

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
This candidate may edit only the residual side: the meta-agent and library layers.

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
- edge_cases (when: inputs are lists, strings or numbers whose size or sign can vary): Test the boundaries the spec implies: empty input, single element, and values at the stated limits. Verify no crash and correct return for each.
- examples_check (when: the problem statement contains examples): Before the final answer, run every example (run_examples, or by hand if you have no tools: trace the code line by line on each example). If one fails, find the rule you misread instead of special-casing the example.
- string_rules (when: string manipulation (case, words, characters, formatting)): Check: (1) Are non-letter characters (spaces, digits, punctuation) preserved unchanged? (2) Does the spec change case, and for which characters? (3) Match the exact output format from the examples.
- numeric_rules (when: arithmetic, rounding, division or number formats): 1. Return type: int vs float, as in the examples. 2. // and % with negative numbers round towards minus infinity in Python. 3. round() rounds halves to even; use the rule the problem states. 4. Compare floats with a tolerance. 5. Large numbers: use integers, not floats, to stay exact.
- efficiency (when: inputs can be large (primes, divisors, sequences, nested loops, recursion)): The plus tests use large inputs and a time limit of a few times the reference solution. Avoid exponential recursion (memoize or iterate), quadratic loops over long lists when a set/dict/sort works, and trial division beyond sqrt(n). Check the speed on a large input (timed) before answering.
- assert_signature (when: the problem gives an assert line (the MBPP style)): The assert fixes the function name, the number and order of arguments and the exact return value: match its type (tuple vs list vs set, int vs float, bool) and format. If it wraps the call (e.g. set(...)), the order of elements does not matter; otherwise it does.

# Current organization
Task agents:
- coder: You write correct, complete Python functions that meet the specification exactly. Write the function, then run run_examples to verify. Do not trace examples by hand. Keep explanations to 2-3 lines.
- tester: You verify and fix the solution from your teammates. (1) Run run_examples on the function. (2) If all pass, write 1-2 quick tests for a boundary the examples do not cover (extra whitespace, empty input, type edge). (3) Fix any bug found. (4) Output the complete function. Do not re-derive the algorithm. Keep reasoning brief.
- reviewer: You review the solutions you are given against the specification: find any bug or misread requirement and give the complete function you believe is correct.
Meta-harness:
1. Simple, clearly specified function: one coder with python.
2. Tricky specification or many edge cases: a coder with python and run_examples, then a tester with run_examples that reads its work.
3. Give at most 2 skills per node, chosen for the specific risk in the problem (e.g. string_rules for case/character problems, numeric_rules for rounding/division). Skip a skill if the problem's examples already demonstrate its guidance.

# Report
# Report (dev-A)

Organization: acc 86.0% (meta-agent prompt 3517 chars; roles 678 chars). 3 distinct architectures, 1.8 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| humaneval_plus | 50 | 86% | coder[T][S]>tester[T][S] 28, coder[T][S]>tester[T] 11, coder[T][S] 11 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| coder[T][S]>tester[T][S] | 28 | 86% |
| coder[T][S]>tester[T] | 11 | 73% |
| coder[T][S] | 11 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| coder | 50 | 82% | 6% | - | - | - |
| tester (with inputs) | 39 | 82% | 3% | 23 | 19 | 17 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_examples | 88 | 83% | 0% |
| skill:edge_cases | 56 | 80% | 85% |
| tool:python | 52 | 83% | 81% |
| skill:read_spec | 26 | 85% | 81% |
| skill:examples_check | 21 | 95% | 78% |
| skill:string_rules | 16 | 75% | 84% |
| skill:numeric_rules | 10 | 70% | 84% |
| tool:compare | 10 | 100% | 80% |
| skill:efficiency | 1 | 0% | 83% |
Never given: timed, assert_signature.

## Wrong (7)
- A1 [humaneval_plus] answered def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # It is a vowel: shift by 2, then swap case
            shifted =; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'edge_cases']); b = tester(a, tools=['run_examples']); return b
- A2 [humaneval_plus] answered def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
- A10 [humaneval_plus] answered def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    betwee; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'examples_check', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
- A23 [humaneval_plus] answered def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
     ; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']); b = tester(a, tools=['run_examples']); return b
- A24 [humaneval_plus] answered def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5)); correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
- A26 [humaneval_plus] answered import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
  ; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['edge_cases', 'efficiency']); b = tester(a, tools=['run_examples']); return b
- A30 [humaneval_plus] answered def check_dict_case(d):
    if not d:
        return False
    
    keys = list(d.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower(); correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b

## Traces of the wrong problems (7 of 7; node outputs over 6000 chars are cut in the middle)
### A1 [humaneval_plus]
Problem:
def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
    Examples:
    >>> encode('test')
    'TGST'
    >>> encode('This is a message')
    'tHKS KS C MGSSCGG'
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the base tests (fail) on input ('TEST',); expected output 'tgst'
Team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'edge_cases']); b = tester(a, tools=['run_examples']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'edge_cases']) -> None (wrong, cut at the token limit)
```
read_spec:
1. Input: string `message`.
2. Output: string.
3. Rules:
   - Swap case of all letters (upper -> lower, lower -> upper).
   - Replace vowels (a, e, i, o, u) with the letter 2 positions ahead in the alphabet.
   - Preserve non-letter characters (spaces, etc.) unchanged.
   - The examples show spaces are preserved. The docstring says "Assume only letters", but the example contains spaces, so we must handle non-letters by leaving them alone.
4. Vowel mapping (based on standard English alphabet order):
   - a -> c
   - e -> g
   - i -> k
   - o -> q
   - u -> w
   - Case sensitivity: Since we swap case first, then replace, or replace then swap?
     Let's trace `This is a message`:
     - T -> t (swap)
     - h -> H (swap)
     - i -> k (swap to I? then replace? or replace then swap?)
       Example output: `tHKS`.
       Input: `This`
       T -> t
       h -> H
       i -> k (if i->k and swap case of k? k is lower, so K? No, output has K).
       Wait, output is `tHKS`.
       T -> t
       h -> H
       i -> k (vowel replacement: i -> k). Then swap case? k -> K.
       s -> S.
       Result: `tHKS`. Matches.
       So order: Swap case -> Replace vowel -> Swap case again?
       Or: Replace vowel (preserving original case?) then swap case?
       Let's try: `i` (lower) -> `k` (lower). Then swap case -> `K`. Correct.
       `A` (upper) in `a`? Input `a` is lower. `a` -> `c`. Swap -> `C`.
       Input `message`: `m`->`M`, `e`->`g`->`G`, `s`->`S`, `s`->`S`, `a`->`c`->`C
[... 3912 chars omitted ...]
is lower case in input. Output has 'C'.
       # We don't have an example with uppercase vowel like 'A'.
       # Let's look at the wording: "swaps case of all letters, replaces all vowels...".
       # Usually, operations are applied in order or as a transformation function.
       # If I say "Swap case of all letters", that applies to EVERY letter.
       # Then "replaces all vowels".
       # If order is Swap THEN Replace:
       #   'A' -> 'a' (swap). 'a' is vowel -> 'c'. Result 'c'.
       #   'a' -> 'A' (swap). 'A' is vowel -> 'C'. Result 'C'.
       # If order is Replace THEN Swap:
       #   'A' -> 'C' (replace). 'C' is not vowel -> Swap 'C' -> 'c'.
       #   'a' -> 'c' (replace). 'c' is not vowel -> Swap 'c' -> 'C'.
       # In the example `This is a message`, 'a' becomes 'C'.
       # If we use Swap-then-Replace: 'a' -> 'A' -> 'C'. Matches.
       # If we use Replace-then-Swap: 'a' -> 'c' -> 'C'. Matches.
       # Both yield 'C' for 'a'.
       # What about 'A'?
       # Swap-then-Replace: 'A' -> 'a' -> 'c'.
       # Replace-then-Swap: 'A' -> 'C' -> 'c'.
       # Both yield 'c' for 'A'.
       # Wait, why did I think they were different?
       # Swap-then-Replace: 'A' -> 'a' (lower). 'a' is vowel. 'a'+2 = 'c'. Result 'c'.
       # Replace-then-Swap: 'A' (upper). 'A'+2 = 'C' (upper). Swap 'C' -> 'c'. Result 'c'.
       # They yield the same result!
       # Let's check 'i'.
       # Swap-then-Replace: 'I' -> 'i' -> 'k'. Result 'k'.
       # Replace-then-Swap: 'I' -> 'K' -> 'k'. Result 'k'.
       # It seems they are equivalent because the +2 shift preserves case relative to the starting case, and then the final swap flips it.
       # Start Upper -> Shift Upper -> Swap Lower.
       # Start Lower -> Shift Lower -> Swap Upper.
       # Start Upper -> Swap Lower -> Shift Lower -> Swap Upper.
       # Yes, mathematically:
       # Let c be char.
       # Method 1 (Replace then Swap):
       #   c_v = c + 2 (preserving case).
       #   return swap(c_v).
       # Method 2 (Swap then Replace):
       #   c_s = swap(c).
       #   c_v = c_s + 2 (preserving case).
       #   return c_v? No, the problem says "replaces...". If we swap first, we swap the vowel. Then replace the vowel.
       #   If I swap 'I' to 'i', then replace 'i' with 'k'. Result 'k'.
       #   If I replace 'I' with 'K', then swap 'K' to 'k'. Result 'k'.
       #   It seems the result is always the opposite case of the vowel's +2 letter.
       #   Vowel + 2 letter always has the same case as the input vowel.
       #   Then swapping case flips it.
       #   So regardless of order, the final character is the +2 letter with the FLIPPED case of the original vowel.
       #   Example: 'a' (lower) -> 'c' (upper). 'A' (upper) -> 'c' (lower).
       #   This is consistent.
       #   So logic:
       #   If char is vowel: return opposite case of (char + 2).
       #   Else if char is letter: return opposite case of char.
       #   Else: return char.
       
       Let's double check non-vowel letters.
       't' -> swap -> 'T'.
       'T' -> swap -> 't'.
       Correct.
       
       So the algorithm is:
       For each char:
         If char is vowel:
            target_char = chr(ord(char.lower()) + 2)
            if char.isupper(): return target_char.upper()
            else: return target_char.lower()
         Elif char is letter:
            return char.swapcase()
         Else:
            return char

Wait, `ord(char.lower()) + 2` works for 'a'->'c', 'e'->'g', etc.
Does it work for 'y'? 'y' is not a vowel in this context (usually).
The problem says "vowels". Standard vowels are a, e, i, o, u.
What about 'y'? Usually not considered a vowel in simple puzzles unless specified. Given examples don't show 'y', assume standard 5.

Let's write the code.

```python
def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # It is a vowel
            # Find the letter 2 places ahead
            base = ord(char.lower())
            new_char_code = base + 2
            new_char = chr(new_char_code)
            # Swap case
            if char.isupper():
                result.append(new_char.upper())
            else:
                result.append(new_char.lower())
        elif char.isalpha():
            # It is a letter but not a vowel
            result.append(char.swapcase())
        else:
            # Not a letter
            result.append(char)
    return "".join(result)
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=[]) -> def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # It is a vowel: shift by 2, then swap case
            shifted = chr(ord(char.lower()) + 2)
            if char.isupper():
                result.append(shifted.upp (wrong)
```
```python
def encode(message):
    vowels = set('aeiouAEIOU')
    result = []
    for char in message:
        if char in vowels:
            # It is a vowel, replace with letter 2 places ahead, then swap case.
            # Since we need the opposite case of the original, and the shift preserves case relative to the base:
            # 'a' -> 'c' (lower) -> swap -> 'C' (upper)
            # 'A' -> 'C' (upper) -> swap -> 'c' (lower)
            # We can just shift the lower case version and flip the case of the result to match the input's flip.
            # Actually, simpler: calculate the shifted char in the same case as input, then swapcase.
            shifted_char = chr(ord(char.lower()) + 2)
            if char.isupper():
                result.append(shifted_char.upper())
            else:
                result.append(shifted_char.lower())
        elif char.isalpha():
            result.append(char.swapcase())
        else:
            result.append(char)
    return "".join(result)
```

[Python output]
(no output)

```python
def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # Shift the lowercase vowel by 2
            shifted = chr(ord(char.lower()) + 2)
            # Swap case of the original character to determine output case
            if char.isupper():
                result.append(shifted.upper())
            else:
                result.append(shifted.lower())
        elif char.isalpha():
            result.append(char.swapcase())
        else:
            # Problem says "Assume only letters", but handle non-letters just in case
            result.append(char)
    return "".join(result)
```

[Python output]
(no output)

```python
def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # Shift the lowercase vowel by 2
            shifted = chr(ord(char.lower()) + 2)
            # Swap case of the original character to determine output case
            if char.isupper():
                result.append(shifted.upper())
            else:
                result.append(shifted.lower())
        elif char.isalpha():
            result.append(char.swapcase())
        else:
            # Problem says "Assume only letters", but handle non-letters just in case
            result.append(char)
    return "".join(result)
```

[Python output]
(no output)

Final solution:
```python
def encode(message):
    vowels = set('aeiou')
    result = []
    for char in message:
        if char.lower() in vowels:
            # It is a vowel: shift by 2, then swap case
            shifted = chr(ord(char.lower()) + 2)
            if char.isupper():
                result.append(shifted.upper())
            else:
                result.append(shifted.lower())
        elif char.isalpha():
            # It is a consonant: swap case
            result.append(char.swapcase())
        else:
            # Keep non-letters as is (though problem assumes only letters)
            result.append(char)
    return "".join(result)
```
```
### A2 [humaneval_plus]
Problem:
def valid_date(date):
    """You have to write a function which validates a given date string and
    returns True if the date is valid otherwise False.
    The date is valid if all of the following rules are satisfied:
    1. The date string is not empty.
    2. The number of days is not less than 1 or higher than 31 days for months 1,3,5,7,8,10,12. And the number of days is not less than 1 or higher than 30 days for months 4,6,9,11. And, the number of days is not less than 1 or higher than 29 for the month 2.
    3. The months should not be less than 1 or higher than 12.
    4. The date should be in the format: mm-dd-yyyy

    for example: 
    valid_date('03-11-2000') => True

    valid_date('15-01-2012') => False

    valid_date('04-0-2040') => False

    valid_date('06-04-2020') => True

    valid_date('06/04/2020') => False
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the plus tests (fail) on input ('06-04-202',); expected output False
Team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['string_rules', 'numeric_rules']) -> def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month (wrong)
```
```python
def valid_date(date):
    """You have to write a function which validates a given date string and
    returns True if the date is valid otherwise False.
    The date is valid if all of the following rules are satisfied:
    1. The date string is not empty.
    2. The number of days is not less than 1 or higher than 31 days for months 1,3,5,7,8,10,12. And the number of days is not less than 1 or higher than 30 days for months 4,6,9,11. And, the number of days is not less than 1 or higher than 29 for the month 2.
    3. The months should not be less than 1 or higher than 12.
    4. The date should be in the format: mm-dd-yyyy

    for example: 
    valid_date('03-11-2000') => True

    valid_date('15-01-2012') => False

    valid_date('04-0-2040') => False

    valid_date('06-04-2020') => True

    valid_date('06/04/2020') => False
    """
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # month == 2
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```

[Python output]
(no output)

```python
def run_examples(func=None):
    examples = [
        ("valid_date('03-11-2000')", True),
        ("valid_date('15-01-2012')", False),
        ("valid_date('04-0-2040')", False),
        ("valid_date('06-04-2020')", True),
        ("valid_date('06/04/2020')", False),
    ]
    if func is None:
        func = valid_date
    for ex, expected in examples:
        # Extract the argument string from the example call like 'valid_date("...")'
        arg = ex.strip().strip("'").strip('"')
        if arg.startswith('valid_date('):
            arg = arg[10:-1]
        result = func(arg)
        status = "PASS" if result == expected else "FAIL"
        print(f"{ex} => {result} | Expected: {expected} | {status}")

def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```

[Python output]
(no output)

```python
def run_examples(func=None):
    examples = [
        ("valid_date('03-11-2000')", True),
        ("valid_date('15-01-2012')", False),
        ("valid_date('04-0-2040')", False),
        ("valid_date('06-04-2020')", True),
        ("valid_date('06/04/2020')", False),
    ]
    if func is None:
        func = valid_date
    for ex, expected in examples:
        # Extract the argument string from the example call like 'valid_date("...")'
        arg = ex.strip().strip("'").strip('"')
        if arg.startswith('valid_date('):
            arg = arg[10:-1]
        result = func(arg)
        status = "PASS" if result == expected else "FAIL"
        print(f"{ex} => {result} | Expected: {expected} | {status}")

def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```
Final solution:
```python
def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=['edge_cases']) -> def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month (wrong)
```
```python
def run_examples(func=None):
    examples = [
        ("valid_date('03-11-2000')", True),
        ("valid_date('15-01-2012')", False),
        ("valid_date('04-0-2040')", False),
        ("valid_date('06-04-2020')", True),
        ("valid_date('06/04/2020')", False),
    ]
    if func is None:
        func = valid_date
    for ex, expected in examples:
        # Extract the argument string from the example call like 'valid_date("...")'
        arg = ex.strip().strip("'").strip('"')
        if arg.startswith('valid_date('):
            arg = arg[10:-1]
        result = func(arg)
        status = "PASS" if result == expected else "FAIL"
        print(f"{ex} => {result} | Expected: {expected} | {status}")

def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    # Check max days based on month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # month == 2
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```

[Python output]
(no output)

```python
def run_examples(func=None):
    examples = [
        ("valid_date('03-11-2000'
[... 2654 chars omitted ...]
with whitespace.
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # month == 2
        max_day = 29
    
    if day > max_day:
        return False
    
    return True

# Run examples
run_examples()

# Run boundary tests
print("--- Boundary Tests ---")
tests = [
    ("", False, "Empty input"),
    (" 03-11-2000 ", False, "Whitespace around date (strict format violation if not stripped, but problem says format is mm-dd-yyyy, usually implies no space unless specified. However, int() handles whitespace. Let's see what happens. 03-11-2000 with spaces around: split gives [' 03', '11', '2000']. int(' 03') works. But is it valid? The spec says format mm-dd-yyyy. Usually strict. Let's assume strict first. If it returns True, maybe we need to strip. But the example '04-0-2040' fails because day is 0. '06/04/2020' fails because split is wrong. 
    # Let's test strictness on whitespace.
    ("03 -11 -2000", False, "Spaces inside"),
    ("03-11-2000", True, "Normal"),
    ("00-11-2000", False, "Month 0"),
    ("03-00-2000", False, "Day 0"),
    ("03-32-2000", False, "Day > 31"),
    ("02-29-2000", True, "Leap year Feb 29 (allowed max 29 per spec)"),
    ("02-30-2000", False, "Feb 30"),
    ("13-01-2000", False, "Month 13"),
    ("01-01-0000", True, "Year 0 (int allows it, spec doesn't forbid)"),
]

for date_str, expected, desc in tests:
    result = valid_date(date_str)
    status = "PASS" if result == expected else "FAIL"
    print(f"{desc}: '{date_str}' => {result} (Expected {expected}) | {status}")
```

```python
def run_examples(func=None):
    examples = [
        ("valid_date('03-11-2000')", True),
        ("valid_date('15-01-2012')", False),
        ("valid_date('04-0-2040')", False),
        ("valid_date('06-04-2020')", True),
        ("valid_date('06/04/2020')", False),
    ]
    if func is None:
        func = valid_date
    for ex, expected in examples:
        arg = ex.strip().strip("'").strip('"')
        if arg.startswith('valid_date('):
            arg = arg[10:-1]
        result = func(arg)
        status = "PASS" if result == expected else "FAIL"
        print(f"{ex} => {result} | Expected: {expected} | {status}")

def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # month == 2
        max_day = 29
    
    if day > max_day:
        return False
    
    return True

# Run examples
run_examples()

# Run boundary tests
print("--- Boundary Tests ---")
tests = [
    ("", False, "Empty input"),
    ("03 -11 -2000", False, "Spaces inside"),
    ("03-11-2000", True, "Normal"),
    ("00-11-2000", False, "Month 0"),
    ("03-00-2000", False, "Day 0"),
    ("03-32-2000", False, "Day > 31"),
    ("02-29-2000", True, "Feb 29 max allowed"),
    ("02-30-2000", False, "Feb 30 invalid"),
    ("13-01-2000", False, "Month 13"),
]

for date_str, expected, desc in tests:
    result = valid_date(date_str)
    status = "PASS" if result == expected else "FAIL"
    print(f"{desc}: '{date_str}' => {result} (Expected {expected}) | {status}")
```

Final solution:
```python
def valid_date(date):
    if not date:
        return False
    
    parts = date.split('-')
    if len(parts) != 3:
        return False
    
    try:
        month = int(parts[0])
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return False
    
    if month < 1 or month > 12:
        return False
    
    if day < 1:
        return False
    
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month in [4, 6, 9, 11]:
        max_day = 30
    else:  # month == 2
        max_day = 29
    
    if day > max_day:
        return False
    
    return True
```
```
### A10 [humaneval_plus]
Problem:
def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged elements between lst1 and lst2.
    If it is possible to exchange elements between the lst1 and lst2 to make
    all the elements of lst1 to be even, return "YES".
    Otherwise, return "NO".
    For example:
    exchange([1, 2, 3, 4], [1, 2, 3, 4]) => "YES"
    exchange([1, 2, 3, 4], [1, 5, 3, 4]) => "NO"
    It is assumed that the input lists will be non-empty.
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the base tests (fail) on input ([1, 2, 3, 4], [1, 5, 3, 4]); expected output 'NO'
Team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'examples_check', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['read_spec', 'examples_check', 'numeric_rules']) -> def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged el (wrong)
```
### 1. Restate the input types, the output type and every rule in the specification before coding

- **Input types**: Two lists of integers, `lst1` and `lst2`.
- **Output type**: A string, either `"YES"` or `"NO"`.
- **Rules**:
  - We can exchange any number of elements between `lst1` and `lst2`.
  - The goal is to make all elements in `lst1` even after the exchange.
  - If `lst1` already contains only even numbers, return `"YES"`.
  - If there are odd numbers in `lst1`, we can replace them with even numbers from `lst2`.
  - If `lst2` has at least one even number, we can use it to replace an odd number in `lst1`.
  - If `lst2` has no even numbers, and `lst1` has any odd numbers, it's impossible to make `lst1` all even -> return `"NO"`.
  - Otherwise (if `lst2` has at least one even number, or `lst1` has no odds), return `"YES"`.

### 2. The examples are part of the specification:

- `exchange([1, 2, 3, 4], [1, 2, 3, 4])` -> `"YES"` (lst2 has evens)
- `exchange([1, 2, 3, 4], [1, 5, 3, 4])` -> `"NO"` (lst2 has no evens, lst1 has odds)

### 3. Return the value; do not print and do not read input.

### 4. Keep the given function name and parameter order.

### 5. Numeric rules: Not directly applicable here, but we'll use integer comparison.

### 6. Examples check:

- Example 1: `lst1` has odds, `lst2` has evens (2, 4) -> `"YES"`
- Example 2: `lst1` has odds, `lst2` has no evens -> `"NO"`

### 7. Logic:

- If `lst1` has no odd numbers -> `"YES"`.
- Else if `lst2` has at least one even number -> `"YES"`.
- Else -> `"NO"`.

```python
def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged elements between lst1 and lst2.
    If it is possible to exchange elements between the lst1 and lst2 to make
    all the elements of lst1 to be even, return "YES".
    Otherwise, return "NO".
    For example:
    exchange([1, 2, 3, 4], [1, 2, 3, 4]) => "YES"
    exchange([1, 2, 3, 4], [1, 5, 3, 4]) => "NO"
    It is assumed that the input lists will be non-empty.
    """
    # Check if lst1 has any odd numbers
    has_odd_in_lst1 = any(x % 2 != 0 for x in lst1)
    
    # Check if lst2 has any even numbers
    has_even_in_lst2 = any(x % 2 == 0 for x in lst2)
    
    if has_odd_in_lst1:
        if has_even_in_lst2:
            return "YES"
        else:
            return "NO"
    else:
        # lst1 already has no odd numbers
        return "YES"
```

[Python output]
(no output)

```python
def run_examples(func=None):
    if func is None:
        from problem import exchange
        func = exchange
    
    tests = [
        (exchange, ([1, 2, 3, 4], [1, 2, 3, 4]), "YES"),
        (exchange, ([1, 2, 3, 4], [1, 5, 3, 4]), "NO"),
    ]
    
    for f, inp, expected in tests:
        res = f(*inp)
        status = "PASS" if res == expected else "FAIL"
        print(f"{status}: {inp} => {res} (expected {expected})")

# Run verification
run_examples()
```

Final solution:
```python
def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged elements between lst1 and lst2.
    If it is possible to exchange elements between the lst1 and lst2 to make
    all the elements of lst1 to be even, return "YES".
    Otherwise, return "NO".
    For example:
    exchange([1, 2, 3, 4], [1, 2, 3, 4]) => "YES"
    exchange([1, 2, 3, 4], [1, 5, 3, 4]) => "NO"
    It is assumed that the input lists will be non-empty.
    """
    # Check if lst1 contains any odd numbers
    has_odd = any(x % 2 != 0 for x in lst1)
    # Check if lst2 contains any even numbers
    has_even = any(x % 2 == 0 for x in lst2)
    
    # If lst1 has no odds, it's already valid -> YES
    # If lst1 has odds but lst2 has no evens to swap -> NO
    # Otherwise -> YES
    return "NO" if (has_odd and not has_even) else "YES"
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=['edge_cases']) -> def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged el (wrong)
```
```python
def run_examples(func=None):
    if func is None:
        from problem import exchange
        func = exchange
    
    tests = [
        (exchange, ([1, 2, 3, 4], [1, 2, 3, 4]), "YES"),
        (exchange, ([1, 2, 3, 4], [1, 5, 3, 4]), "NO"),
    ]
    
    for f, inp, expected in tests:
        res = f(*inp)
        status = "PASS" if res == expected else "FAIL"
        print(f"{status}: {inp} => {res} (expected {expected})")

# Run verification
run_examples()
```

Final solution:
```python
def exchange(lst1, lst2):
    """In this problem, you will implement a function that takes two lists of numbers,
    and determines whether it is possible to perform an exchange of elements
    between them to make lst1 a list of only even numbers.
    There is no limit on the number of exchanged elements between lst1 and lst2.
    If it is possible to exchange elements between the lst1 and lst2 to make
    all the elements of lst1 to be even, return "YES".
    Otherwise, return "NO".
    For example:
    exchange([1, 2, 3, 4], [1, 2, 3, 4]) => "YES"
    exchange([1, 2, 3, 4], [1, 5, 3, 4]) => "NO"
    It is assumed that the input lists will be non-empty.
    """
    # Check if lst1 contains any odd numbers
    has_odd = any(x % 2 != 0 for x in lst1)
    # Check if lst2 contains any even numbers
    has_even = any(x % 2 == 0 for x in lst2)
    
    # If lst1 has no odds, it's already valid -> YES
    # If lst1 has odds but lst2 has no evens to swap -> NO
    # Otherwise -> YES
    return "NO" if (has_odd and not has_even) else "YES"
```
```
### A23 [humaneval_plus]
Problem:
def fix_spaces(text):
    """
    Given a string text, replace all spaces in it with underscores, 
    and if a string has more than 2 consecutive spaces, 
    then replace all consecutive spaces with - 
    
    fix_spaces("Example") == "Example"
    fix_spaces("Example 1") == "Example_1"
    fix_spaces(" Example 2") == "_Example_2"
    fix_spaces(" Example   3") == "_Example-3"
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the base tests (fail) on input ('Yellow Yellow  Dirty  Fellow',); expected output 'Yellow_Yellow__Dirty__Fellow'
Team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']); b = tester(a, tools=['run_examples']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']) -> def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
 (wrong)
```
```python
def fix_spaces(text):
    """
    Given a string text, replace all spaces in it with underscores, 
    and if a string has more than 2 consecutive spaces, 
    then replace all consecutive spaces with - 
    
    fix_spaces("Example") == "Example"
    fix_spaces("Example 1") == "Example_1"
    fix_spaces(" Example 2") == "_Example_2"
    fix_spaces(" Example   3") == "_Example-3"
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```

[Python output]
(no output)

```python
def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```

[Python output]
(no output)

Final solution:
```python
def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=[]) -> def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
 (wrong)
```
```python
def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```

[Python output]
(no output)

```python
def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```

[Python output]
(no output)

The teammate's solution logic is correct: it iterates through the string, counts consecutive spaces, and replaces them with `-` if the count is > 2, otherwise `_`. Single spaces become `_`.

Let's run the examples to confirm:
1. `"Example"` -> "Example" (PASS)
2. `"Example 1"` -> "Example_1" (PASS)
3. `" Example 2"` -> "_Example_2" (PASS)
4. `" Example   3"` -> "_Example-3" (PASS)

The logic handles empty strings correctly (loop doesn't run, returns empty string). It handles whitespace correctly. No bugs found.

Final solution:
```python
def fix_spaces(text):
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == ' ':
            j = i
            while j < n and text[j] == ' ':
                j += 1
            count = j - i
            if count > 2:
                result.append('-')
            else:
                result.append('_')
            i = j
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)
```
```
### A24 [humaneval_plus]
Problem:
def closest_integer(value):
    '''
    Create a function that takes a value (string) representing a number
    and returns the closest integer to it. If the number is equidistant
    from two integers, round it away from zero.

    Examples
    >>> closest_integer("10")
    10
    >>> closest_integer("15.3")
    15

    Note:
    Rounding away from zero means that if the given number is equidistant
    from two integers, the one you should return is the one that is the
    farthest from zero. For example closest_integer("14.5") should
    return 15 and closest_integer("-14.5") should return -15.
    '''
Correct: (hidden base and plus tests)
Grader on the final answer: fails the base tests (fail) on input ('10',); expected output 10
Team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'numeric_rules']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['read_spec', 'numeric_rules']) -> import math

def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5)) (correct)
```
read_spec:
1. Input: string representing a number (int or float, possibly negative).
2. Output: int.
3. Rule: Return the closest integer. If equidistant (e.g., x.5), round away from zero (14.5 -> 15, -14.5 -> -15).
4. Examples provided confirm standard rounding for non-halfs and specific "away from zero" for halves.

Plan:
1. Convert string to float.
2. Use `math.floor` and `math.ceil` to find neighbors.
3. Check distance to both. If equal, choose the one farther from zero.
4. Return as int.

```python
import math

def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5))
```

Final solution:
```python
import math

def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5))
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=['edge_cases']) -> def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5)) (wrong)
```
```python
import math

def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5))
```

[Python output]
(no output)

```python
import math

def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5))
```

Final solution:
```python
def closest_integer(value):
    num = float(value)
    if num >= 0:
        return int(math.floor(num + 0.5))
    else:
        return int(math.ceil(num - 0.5))
```
```
### A26 [humaneval_plus]
Problem:
def prime_fib(n: int):
    """
    prime_fib returns n-th number that is a Fibonacci number and it's also prime.
    >>> prime_fib(1)
    2
    >>> prime_fib(2)
    3
    >>> prime_fib(3)
    5
    >>> prime_fib(4)
    13
    >>> prime_fib(5)
    89
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the plus tests (fail) on input (12,); expected output 99194853094755497
Team: a = coder(tools=['python', 'run_examples'], skills=['edge_cases', 'efficiency']); b = tester(a, tools=['run_examples']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['edge_cases', 'efficiency']) -> import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            re (wrong)
```
```python
import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    # Check odd divisors up to sqrt(num)
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        # Check if current Fibonacci number is prime
        if is_prime(a):
            count += 1
            if count == n:
                return a
        
        # Generate next Fibonacci number
        a, b = b, a + b

# Run examples to verify
if __name__ == "__main__":
    run_examples(prime_fib)
```

[Python output]
PASS prime_fib(1)
PASS prime_fib(2)
PASS prime_fib(3)
PASS prime_fib(4)
PASS prime_fib(5)
5/5 examples pass

Final solution:
```python
import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        if is_prime(a):
            count += 1
            if count == n:
                return a
        a, b = b, a + b
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=[]) -> import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            re (wrong)
```
```python
def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        # Check if current Fibonacci number is prime
        if is_prime(a):
            count += 1
            if count == n:
                return a
        
        # Generate next Fibonacci number
        a, b = b, a + b
```

[Python output]
(no output)

```python
import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        # Check if current Fibonacci number is prime
        if is_prime(a):
            count += 1
            if count == n:
                return a
        
        # Generate next Fibonacci number
        a, b = b, a + b

# Run examples to verify
if __name__ == "__main__":
    run_examples(prime_fib)
```

[Python output]
PASS prime_fib(1)
PASS prime_fib(2)
PASS prime_fib(3)
PASS prime_fib(4)
PASS prime_fib(5)
5/5 examples pass

```python
import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        # Check if current Fibonacci number is prime
        if is_prime(a):
            count += 1
            if count == n:
                return a
        
        # Generate next Fibonacci number
        a, b = b, a + b
```

Final solution:
```python
import sys

def is_prime(num: int) -> bool:
    """Check if a number is prime."""
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    limit = int(num**0.5) + 1
    for i in range(3, limit, 2):
        if num % i == 0:
            return False
    return True

def prime_fib(n: int) -> int:
    """
    Returns the n-th number that is both a Fibonacci number and prime.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    
    count = 0
    a, b = 0, 1
    
    while True:
        if is_prime(a):
            count += 1
            if count == n:
                return a
        a, b = b, a + b
```
```
### A30 [humaneval_plus]
Problem:
def check_dict_case(dict):
    """
    Given a dictionary, return True if all keys are strings in lower 
    case or all keys are strings in upper case, else return False.
    The function should return False is the given dictionary is empty.
    Examples:
    check_dict_case({"a":"apple", "b":"banana"}) should return True.
    check_dict_case({"a":"apple", "A":"banana", "B":"banana"}) should return False.
    check_dict_case({"a":"apple", 8:"banana", "a":"apple"}) should return False.
    check_dict_case({"Name":"John", "Age":"36", "City":"Houston"}) should return False.
    check_dict_case({"STATE":"NC", "ZIP":"12345" }) should return True.
    """
Correct: (hidden base and plus tests)
Grader on the final answer: fails the base tests (fail) on input ({'p': 'pineapple', '5': 'banana', 'a': 'apple'},); expected output False
Team: a = coder(tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']); b = tester(a, tools=['run_examples'], skills=['edge_cases']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['string_rules', 'edge_cases']) -> def check_dict_case(dict):
    if not dict:
        return False
    
    keys = list(dict.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower (wrong)
```
```python
def check_dict_case(dict):
    """
    Given a dictionary, return True if all keys are strings in lower 
    case or all keys are strings in upper case, else return False.
    The function should return False is the given dictionary is empty.
    """
    if not dict:
        return False
    
    keys = list(dict.keys())
    all_strings = all(isinstance(k, str) for k in keys)
    
    if not all_strings:
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_upper
```

[Python output]
(no output)

```python
def check_dict_case(dict):
    if not dict:
        return False
    
    keys = list(dict.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_upper
```

Final solution:
```python
def check_dict_case(dict):
    if not dict:
        return False
    
    keys = list(dict.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_upper
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=['edge_cases']) -> def check_dict_case(d):
    if not d:
        return False
    
    keys = list(d.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_u (wrong)
```
```python
def check_dict_case(d):
    """
    Given a dictionary, return True if all keys are strings in lower 
    case or all keys are strings in upper case, else return False.
    The function should return False if the given dictionary is empty.
    """
    if not d:
        return False

    keys = list(d.keys())
    
    # Check if all keys are strings
    if not all(isinstance(k, str) for k in keys):
        return False

    # Check if all keys are lowercase or all keys are uppercase
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)

    return all_lower or all_upper
```

[Python output]
(no output)

```python
def check_dict_case(d):
    if not d:
        return False
    
    keys = list(d.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_upper
```

Final solution:
```python
def check_dict_case(d):
    if not d:
        return False
    
    keys = list(d.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    
    all_lower = all(k == k.lower() for k in keys)
    all_upper = all(k == k.upper() for k in keys)
    
    return all_lower or all_upper
```
```

# History (held-out dev-B)
round 0 (starting organization): acc 90.0%
round 1 [task-agent, rejected]: dev-B acc 86.7%, cost 3554 (against the incumbent: fixed 2, broke 3)
  change 1 [cites A1]: Coder writes extensive analysis and re-derivations before the code, hitting the token limit and producing a solution whose logic does not match its own trace (vowel-shifted within the vowel list inste
    rationale: In A1 the coder's python tool returned '(no output)' twice, meaning the examples were never actually executed against the code. The coder traced by hand with the wrong indices (full-alphabet positions) while the code used vowel-list positions, and no tool run caught the mismatch. The root cause is t
    ops: {"op": "edit_agent", "name": "coder", "role": "You write correct, complete Python functions that meet the specification exactly. Run your code against every example in the problem (run_examples or a d
  change 2 [cites A2 A23 A30]: Tester reviews the teammate's code by reading alone, misses subtle bugs that hidden tests probe (regex $ matching before a trailing newline; key==key.lower() passing for digit-only strings), and on am
    rationale: In A2 the tester never tested an input with trailing whitespace, so the Python-regex $-before-newline bug survived. In A30 the tester never tested a digit-only string key, so the key==key.lower() vs key.islower() bug survived; it also renamed the parameter. In A23 the tester spent its entire token b
    ops: {"op": "edit_agent", "name": "tester", "role": "You test the solution your teammates wrote: run it against the problem's examples, then against edge cases (empty input, boundary values, unusual or mix
round 1 [meta-agent+library, rejected]: dev-B acc 93.3%, cost 4111 (against the incumbent: fixed 2, broke 1)
  change 1 [cites A23 A30]: Tester with no skills can loop on an ambiguous spec point and hit the token limit, producing no function (A23), or miss the correct idiom because no domain skill was given (A30).
    rationale: Rule 3 ('Give skills that match the problem') is too vague: the meta-agent gave the tester zero skills in A23 (fix_spaces) and A30 (check_dict_case). In A23 the tester deliberated endlessly on 'more than 2' vs '2 or more' and was cut with output None; in A30 neither node had string_rules so both use
    ops: {"op": "edit_rule", "rule": 3, "text": "Give skills matching the problem type. The tester must always receive read_spec; also give string_rules for string/case/format problems, numeric_rules for arith
  change 2 [cites A30 A2]: Using s==s.lower() instead of s.islower() returns True for strings with no cased characters (digits, symbols), giving wrong results on case-checking problems; regex $ in Python matches before a traili
    rationale: A30: both coder and tester used key==key.lower() which is True for '5', so a dict with a digit key passed the all-lower check. A2: the regex ^…$ matched '06-04-2020\n' because $ matches before a trailing newline. Both are general Python string pitfalls that the string_rules skill should warn about. 
    ops: {"op": "edit_skill", "name": "string_rules", "when": "string manipulation (case, words, characters, formatting, validation)", "text": "1. Case: does the comparison or output keep, lower or upper case?
  change 3 [cites A23]: A tester (or coder) can loop indefinitely on an ambiguous spec detail, consuming the token budget and producing no output.
    rationale: In A23 the tester spent its entire output budget re-deliberating whether 'more than 2 consecutive spaces' means >2 or >=2, never writing a final function. The read_spec skill already says to restate rules and match examples, but it lacks an explicit 'resolve and move on' directive. Adding point 5 gi
    ops: {"op": "edit_skill", "name": "read_spec", "when": "any problem", "text": "1. Restate the input types, the output type and every rule in the specification before coding. 2. The examples are part of the
round 1 [task-agent+meta-agent+library, ACCEPTED]: dev-B acc 93.3%, cost 3198 (against the incumbent: fixed 2, broke 1)
  change 1 [cites A1 A2 A23]: Agents waste tokens on manual reasoning or extended analysis instead of running code to verify, leading to token-limit cutoffs or missed subtle bugs.
    rationale: In A1 the coder traced examples by hand, never called run_examples, and was cut at the token limit. In A23 the tester spent thousands of tokens debating an ambiguity and was cut, outputting None. In A2 the tester reasoned the code was correct without running a boundary test (trailing newline exposed
    ops: {"op": "edit_agent", "name": "coder", "role": "You write correct, complete Python functions that meet the specification exactly. Write the function, then run run_examples to verify. Do not trace examp; {"op": "edit_agent", "name": "tester", "role": "You verify and fix the solution from your teammates. (1) Run run_examples on the function. (2) If all pass, write 1-2 quick tests for a boundary the exa
  change 2 [cites A1 A30]: Skills add tokens and cause the 9B model to over-analyze without preventing the core logic errors.
    rationale: edge_cases is at 84% when given vs 93% without; string_rules at 77% vs 91%. In A1 the coder had 3 skills and was cut; in A30 edge_cases did not help catch the digit-string key bug (key=='5' passes both key==key.lower() and key==key.upper() but islower()/isupper() correctly reject it). Shortening the
    ops: {"op": "edit_skill", "name": "edge_cases", "text": "Test the boundaries the spec implies: empty input, single element, and values at the stated limits. Verify no crash and correct return for each."}; {"op": "edit_skill", "name": "string_rules", "text": "Check: (1) Are non-letter characters (spaces, digits, punctuation) preserved unchanged? (2) Does the spec change case, and for which characters? (; {"op": "edit_rule", "rule": 3, "text": "Give at most 2 skills per node, chosen for the specific risk in the problem (e.g. string_rules for case/character problems, numeric_rules for rounding/division)
round 1 accepted candidate, on the next dev-A run: fixed 0, broke 3 (A10 A24 A26)
  change 1 [INEFFECTIVE: 0/3 cited fixed]: Agents waste tokens on manual reasoning or extended analysis instead of running code to verify, leading to token-limit cutoffs or missed subtle bugs.
  change 2 [INEFFECTIVE: 0/2 cited fixed]: Skills add tokens and cause the 9B model to over-analyze without preventing the core logic errors.
round 2 [task-agent, rejected]: dev-B acc 73.3%, cost 2920 (against the incumbent: fixed 0, broke 6)
  change 1 [cites A10 A23 A30 A24]: Tester fails to verify the function against the problem's actual examples when run_examples cannot parse them, misses the spec's threshold boundary between two rules, and drops necessary imports from 
    rationale: A10: examples use '=>' format that run_examples cannot parse; the tester had no fallback and never checked the function against them, missing a counting-vs-existence logic error. A23: examples show 1-space and 3-space cases but not 2; the code maps any run ≤ 2 to a single underscore, and the tester'
    ops: {"op": "edit_agent", "name": "tester", "role": "You verify and fix the solution from your teammates. (1) Run run_examples; if it finds no examples or any fail, call the function on each example in the
round 2 [meta-agent+library, rejected]: dev-B acc 86.7%, cost 3304 (against the incumbent: fixed 0, broke 2)
  change 1 [cites A24]: The final node drops import statements or helper functions when outputting the solution, causing NameError on hidden tests.
    rationale: In A24 the tester output the function without 'import math', so the grader raised NameError on the first call. The new tester role's emphasis on brevity ('Keep reasoning brief', 'Output the complete function') led the 9B model to treat 'complete function' as just the def block. A short skill that ex
    ops: {"op": "add_skill", "name": "complete_output", "when": "always give to the node whose output is returned (the final node)", "text": "Your final output must be a complete, runnable Python script. Inclu
  change 2 [cites A10]: The tester passes all given examples but misses a logic error because the examples do not exercise the algorithm's core condition at its decision boundary.
    rationale: In A10 the coder used any(even in lst2) instead of count(even in lst2) >= count(odd in lst1); both provided examples coincidentally pass with the wrong logic. The tester ran run_examples (all PASS) and wrote no test where the count matters. A skill that directs the tester to construct a boundary-cas
    ops: {"op": "add_skill", "name": "boundary_logic", "when": "the solution's core logic is a count, comparison, or threshold that the given examples may not stress at the boundary", "text": "Identify the key
  change 3 [cites A26]: The solution uses trial division for primality and times out on large inputs because the efficiency skill does not warn that sqrt(n) trial division is too slow for n > 10^12, and the timed tool is nev
    rationale: In A26 the 12th prime Fibonacci is ~10^17; trial division to sqrt(10^17) ≈ 3×10^8 iterations exceeds the time limit. The efficiency skill says to avoid trial division 'beyond sqrt(n)' but does not say sqrt(n) itself is infeasible for very large n. The timed tool was never given, so no node checked p
    ops: {"op": "edit_skill", "name": "efficiency", "text": "The plus tests use large inputs and a time limit. Avoid exponential recursion (memoize or iterate), quadratic loops when a set/dict/sort works. For ; {"op": "add_rule", "text": "When giving the efficiency skill, also give the timed tool so the agent can verify performance on a large input."}
round 2 [task-agent+meta-agent+library, rejected]: dev-B acc 73.3%, cost 4387 (against the incumbent: fixed 0, broke 6)
  change 1 [cites A10 A23 A24 A1 A2 A30]: Agents define the function in their python code but never invoke run_examples(), so the tool returns '(no output)' and no verification occurs.
    rationale: In A10, A23, A24, A1, A2, A30 the python tool shows '(no output)' because the agent only writes the def without calling run_examples(). In A26 the agent explicitly wrote 'run_examples(prime_fib)' and got PASS/FAIL output. Making the call explicit in the role ('call run_examples() at the end') ensure
    ops: {"op": "edit_agent", "name": "coder", "role": "You write correct, complete Python functions that meet the specification exactly. In your python code: define the function, then call run_examples() at t; {"op": "edit_agent", "name": "tester", "role": "You verify and fix the solution from your teammates. (1) In your python code, include the function definition and call run_examples(). (2) If all pass, 
  change 2 [cites A26]: Trial-division primality test is too slow for large numbers (e.g. prime Fibonacci ~10^17), causing timeout on hidden tests.
    rationale: In A26 the coder used trial division to sqrt(n) for n~10^17, which requires ~3*10^8 iterations. The efficiency skill says 'avoid trial division beyond sqrt(n)' but the code does go up to sqrt(n) and is still infeasible. A deterministic Miller-Rabin tool (is_prime_fast) runs in O(k log^2 n) and handl
    ops: {"op": "add_tool", "name": "is_prime_fast", "doc": "is_prime_fast(n) -> True if n is prime. Deterministic Miller-Rabin, correct for n < 3.3*10^24. Use instead of trial division for large numbers.", "c; {"op": "edit_skill", "name": "efficiency", "when": "inputs can be large (primes, divisors, sequences, nested loops, recursion)", "text": "The plus tests use large inputs and a time limit of a few time; {"op": "add_rule", "text": "Give is_prime_fast to the coder when the problem requires checking primality of numbers that can exceed 10^9 (e.g., large Fibonacci, Mersenne, or sequence elements)."}
  change 3 [cites A30]: Using s==s.lower() instead of s.islower() returns True for strings with no cased characters (digits, symbols), giving wrong results on case-checking problems.
    rationale: In A30 both nodes used k==k.lower() which is True for '5', so a dict with a digit key passed the all-lower check. The string_rules skill should explicitly warn about this distinction so the agent uses .islower()/.isupper() instead of ==.lower()/==.upper().
    ops: {"op": "edit_skill", "name": "string_rules", "when": "string manipulation (case, words, characters, formatting)", "text": "Check: (1) Are non-letter characters (spaces, digits, punctuation) preserved 

Output the JSON object between <edit> and </edit>.