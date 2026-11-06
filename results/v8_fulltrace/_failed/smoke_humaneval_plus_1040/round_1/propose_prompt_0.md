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
This candidate may edit only the self harness: the task-agent layer.

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

Organization: acc 75.0% (meta-agent prompt 3061 chars; roles 421 chars). 2 distinct architectures, 1.8 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| humaneval_plus | 8 | 75% | coder[T][S]>tester[T][S] 6, coder[T][S] 2 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| coder[T][S]>tester[T][S] | 6 | 67% |
| coder[T][S] | 2 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| coder | 8 | 75% | 12% | - | - | - |
| tester (with inputs) | 6 | 67% | 0% | 4 | 2 | 2 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_examples | 11 | 64% | 100% |
| skill:edge_cases | 10 | 70% | 75% |
| tool:python | 9 | 78% | 60% |
| skill:read_spec | 9 | 67% | 80% |
| skill:examples_check | 8 | 75% | 67% |
| skill:string_rules | 3 | 33% | 82% |
| skill:numeric_rules | 2 | 100% | 67% |
| tool:compare | 1 | 0% | 77% |
Never given: timed, efficiency, assert_signature.

## Wrong (2)
- A1 [humaneval_plus] answered def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that a; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'examples_check']); b = tester(a, tools=['run_examples'], skills=['edge_cases', 'read_spec']); return b
- A2 [humaneval_plus] answered import re

def valid_date(date):
    # Check if the input is a string and not empty
    if not isinstance(date, str):
        return False
    if not date:
        return False

    # Define the regul; correct (hidden base and plus tests); team: a = coder(tools=['python', 'run_examples'], skills=['edge_cases', 'string_rules', 'examples_check']); b = tester(a, tools=['run_examples', 'compare'], skills=['edge_cases', 'read_spec']); return b

## Traces of the wrong problems (2 of 2; node outputs over 6000 chars are cut in the middle)
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
Team: a = coder(tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'examples_check']); b = tester(a, tools=['run_examples'], skills=['edge_cases', 'read_spec']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['read_spec', 'string_rules', 'examples_check']) -> def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
   (wrong, cut at the token limit)
```
```python
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
    vowels = 'aeiouAEIOU'
    result = []
    
    for char in message:
        if char in vowels:
            # Swap case first
            swapped = char.lower() if char.isupper() else char.upper()
            # Find position in lowercase vowels
            idx = vowels.index(swapped)
            # Move 2 places ahead
            new_char = vowels[(idx + 2) % 26]
            # Swap case again to match the swapped version's case
            if swapped.isupper():
                new_char = new_char.upper()
            result.append(new_char)
        else:
            # Swap case for non-vowels
            result.append(char.lower() if char.isupper() else char.upper())
    
    return ''.join(result)
```

[Python output]
(no output)

Let's trace the examples to verify the logic.

**Example 1:** `encode('test')`
- 't' (lowercase vowel? No, 't' is a consonant). Swap case -> 'T'.
- 'e' (lowercase vowel). Swap case -> 'E'. Move 2 ahead in alphabet: 'e' (5) -> 'g' (7). Swap case back to upper -> 'G'.
- 's' (consonant). Swap case -> 'S'.
- 't' (consonant). Swap case 
[... 8071 chars omitted ...]
*after* the swap operation.
  So if 'i' -> 'I', the result of the vowel replacement must be 'K' (upper).
  My code: `if original_is_upper` (False) -> `shifted_char.lower()`.
  `shifted_char` is 'k'. 'k'.lower() is 'k'.
  I need it to be 'K'.
  So the condition should be: if the *swapped* char is upper, result is upper.
  `swapped` is 'I' (upper). So result should be upper.
  My variable `original_is_upper` tracks if the *original* was upper.
  If original was 'i' (lower), `original_is_upper` is False.
  But `swapped` is 'I' (upper).
  So I should check `swapped.isupper()` or `not original_is_upper`.
  
  Correction:
  If `original_is_upper` is True (e.g. 'A'), `swapped` is 'a' (lower). Result should be lower.
  If `original_is_upper` is False (e.g. 'i'), `swapped` is 'I' (upper). Result should be upper.
  So:
  `if original_is_upper: result.append(shifted_char.lower())`
  `else: result.append(shifted_char.upper())`
  
  Let's re-verify 'test':
  'e' (lower). swapped='E'. orig_upper=False.
  'e' is vowel. idx=4 ('e'). shifted='g'.
  orig_upper=False -> append 'g'.upper() -> 'G'. Correct.
  
  'This':
  'i' (lower). swapped='I'. orig_upper=False.
  'i' is vowel. idx=1. shifted='k'.
  orig_upper=False -> append 'k'.upper() -> 'K'. Correct.
  
  'A' (upper). swapped='a'. orig_upper=True.
  'a' is vowel. idx=0. shifted='c'.
  orig_upper=True -> append 'c'.lower() -> 'c'. Correct.
  
  Okay, the logic is:
  Case

[Python output]
(no output)

The `run_examples` function is not provided in the current environment to execute the checks, but I have manually traced the logic against the provided examples in the problem description.

**Logic Verification:**
1.  **Input:** `'test'`
    *   `t` (consonant) -> swap case -> `T`
    *   `e` (vowel) -> swap case -> `E` -> shift 2 (`E`->`F`->`G`) -> `G`
    *   `s` (consonant) -> swap case -> `S`
    *   `t` (consonant) -> swap case -> `T`
    *   Result: `'TGST'`. Matches example.

2.  **Input:** `'This is a message'`
    *   `T` -> `t`
    *   `h` -> `H`
    *   `i` -> `I` -> shift 2 (`I`->`J`->`K`) -> `K`
    *   `s` -> `S`
    *   ` ` -> ` ` (preserved)
    *   `i` -> `K`
    *   `s` -> `S`
    *   ` ` -> ` `
    *   `a` -> `A` -> shift 2 (`A`->`B`->`C`) -> `C`
    *   ` ` -> ` `
    *   `m` -> `M`
    *   `e` -> `E` -> shift 2 -> `G`
    *   `s` -> `S`
    *   `s` -> `S`
    *   `a` -> `C`
    *   `g` -> `G`
    *   `e` -> `G`
    *   Result: `'tHKS KS C MGSSCGG'`. Matches example.

The implementation below handles case swapping, vowel shifting (2 places ahead in the alphabet, wrapping if necessary, though standard vowels don't wrap past 'u' with +2 unless we consider 'u'->'w' which is fine, or 'z' isn't a vowel), and preserves non-alphabetic characters like spaces.

Final solution:
```python
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
    vowels_lower = 'aeiou'
    result = []
    
    for char in message:
        # If the character is not a letter, keep it as is (e.g., spaces)
        if not char.isalpha():
            result.append(char)
            continue
        
        # Step 1: Swap the case of the letter
        if char.isupper():
            swapped = char.lower()
            swapped_is_upper = False
        else:
            swapped = char.upper()
            swapped_is_upper = True
        
        # Step 2: Check if the original character was a vowel (case-insensitive)
        if char.lower() in vowels_lower:
            # It is a vowel. We need to replace it with the letter 2 places ahead.
            # We perform the shift on the lowercase version to find the target letter.
            idx = vowels_lower.index(swapped.lower())
            shifted_char_lower = vowels_lower[(idx + 2) % 5]
            
            # Apply the case that was swapped in Step 1
            if swapped_is_upper:
                shifted_char = shifted_char_lower.upper()
            else:
                shifted_char = shifted_char_lower
            result.append(shifted_char)
        else:
            # It is a consonant, just use the swapped version
            result.append(swapped)
            
    return ''.join(result)
```
```
#### node b = tester(inputs=['a'], tools=['run_examples'], skills=['edge_cases', 'read_spec']) -> def encode(message):
    """
    Write a function that takes a message, and encodes in such a 
    way that it swaps case of all letters, replaces all vowels in 
    the message with the letter that appears 2 places ahead of that 
    vowel in the english alphabet. 
    Assume only letters. 
    
   (wrong)
```
The specification requires two operations for each character in the message:
1.  **Swap Case**: Upper becomes lower, lower becomes upper.
2.  **Vowel Shift**: If the *original* character was a vowel (case-insensitive), replace it with the letter 2 positions ahead in the alphabet. This replacement must respect the case determined by step 1.
    *   Example: Original 'a' (lower) -> Swap -> 'A' (upper). 'a' is a vowel. 'a' + 2 = 'c'. Result: 'C'.
    *   Example: Original 'A' (upper) -> Swap -> 'a' (lower). 'A' is a vowel. 'a' + 2 = 'c'. Result: 'c'.

The specification states "Assume only letters", but the examples contain spaces. Standard practice for such problems is to preserve non-letter characters (like spaces) as they are, applying no transformation to them.

Edge cases to consider:
- Empty string: Returns empty string.
- String with only spaces: Returns same spaces.
- Vowels at the end of the alphabet (u, y?): 'u' + 2 = 'w'. 'y' is usually not considered a vowel in these puzzles unless specified; standard vowels are a, e, i, o, u.
- Case sensitivity logic: The shift amount is based on the vowel's position in the standard lowercase alphabet (a=0, e=4, etc.), but the output case follows the swapped case.

Let's trace `encode('test')`:
- 't' (consonant): Swap -> 'T'.
- 'e' (vowel): Swap -> 'E'. 'e' is vowel. 'e' index 4. 4+2=6 ('g'). Apply swapped case (upper) -> 'G'.
- 's' (consonant): Swap -> 'S'.
- 't' (consonant): Swap -> 'T'.
Result: 'TGST'. Matches.

Let's trace `encode('This is a message')`:
- 'T' -> 't'.
- 'h' -> 'H'.
- 'i' -> 'I'. 'i' is vowel. 'i' index 8. 8+2=10 ('k'). Upper -> 'K'.
- 's' -> 'S'.
- ' ' -> ' '.
- 'i' -> 'K'.
- 's' -> 'S'.
- ' ' -> ' '.
- 'a' -> 'A'. 'a' is vowel. 'a' index 0. 0+2=2 ('c'). Upper -> 'C'.
- ' ' -> ' '.
- 'm' -> 'M'.
- 'e' -> 'E'. 'e' is vowel. 'e' index 4. 4+2=6 ('g'). Upper -> 'G'.
- 's' -> 'S'.
- 's' -> 'S'.
- 'a' -> 'C'.
- 'g' -> 'G'.
- 'e' -> 'G'.
Result: 'tHKS KS C MGSSCGG'. Matches.

The logic holds. I will implement this cleanly.

Final solution:
```python
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
    vowels = "aeiou"
    result = []
    
    for char in message:
        if not char.isalpha():
            # Non-alphabetic characters (like spaces) are preserved as-is
            result.append(char)
            continue
        
        # Step 1: Determine the swapped case
        if char.isupper():
            swapped_char = char.lower()
            is_swapped_upper = False
        else:
            swapped_char = char.upper()
            is_swapped_upper = True
            
        # Step 2: Check if original character is a vowel
        if char.lower() in vowels:
            # Find index of the vowel (case-insensitive)
            vowel_idx = vowels.index(char.lower())
            # Calculate new vowel index (wrapping not strictly needed for 'u' -> 'w' but good practice)
            new_vowel_idx = (vowel_idx + 2) % 5
            new_vowel_char = vowels[new_vowel_idx]
            
            # Apply the swapped case to the new vowel
            if is_swapped_upper:
                result.append(new_vowel_char.upper())
            else:
                result.append(new_vowel_char)
        else:
            # Consonant: just use the swapped character
            result.append(swapped_char)
            
    return ''.join(result)
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
Grader on the final answer: fails the plus tests (fail) on input ('06-04-2020\n',); expected output False
Team: a = coder(tools=['python', 'run_examples'], skills=['edge_cases', 'string_rules', 'examples_check']); b = tester(a, tools=['run_examples', 'compare'], skills=['edge_cases', 'read_spec']); return b
#### node a = coder(inputs=[], tools=['python', 'run_examples'], skills=['edge_cases', 'string_rules', 'examples_check']) -> import re

def valid_date(date):
    # Check if the date string is empty
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date)

    if not match:
        return False

    month (wrong)
```
To solve this problem, we need to validate a date string based on specific rules. The function should return `True` if the date is valid and `False` otherwise.

Here are the key steps:
1. Check if the input string is empty.
2. Verify the format of the date string using a regular expression to ensure it matches `mm-dd-yyyy`.
3. Extract the month, day, and year from the string.
4. Validate the month to ensure it is between 1 and 12.
5. Validate the day based on the month:
   - Months with 31 days: 1, 3, 5, 7, 8, 10, 12.
   - Months with 30 days: 4, 6, 9, 11.
   - Month 2: 29 days (as per the problem statement, no leap year logic is mentioned).
6. Ensure all components are within the valid ranges.

Let's implement the solution:

```python
import re

def valid_date(date):
    # Check if the date string is empty
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date)

    if not match:
        return False

    month_str, day_str, year_str = match.groups()

    # Convert the extracted parts to integers
    try:
        month = int(month_str)
        day = int(day_str)
        year = int(year_str)
    except ValueError:
        return False

    # Validate the month
    if month < 1 or month > 12:
        return False

    # Validate the day based on the month
    if month in [4, 6, 9, 11]:
        if day < 1 or day > 30:
            return False
    elif month in [1, 3, 5, 7, 8, 10, 12]:
        if day < 1 or day > 31:
            return False
    elif month == 2:
        if day < 1 or day > 29:
            return False
    else:
        return False

    return True
```

### Explanation:
1. **Empty Check**: The function first checks if the input string is empty.
2. **Regular Expression**: A regex pattern is used to ensure the date string matches the `mm-dd-yyyy` format.
3. **Conversion to Integers**: The matched groups are converted to integers, handling any potential `ValueError`.
4. **Month Validation**: The month is checked to ensure it is between 1 and 12.
5. **Day Validation**: The day is validated based on the month, considering the number of days in each month.

This implementation ensures that all the specified rules are followed, and the function returns `True` only if the date is valid.

Final solution:
```python
import re

def valid_date(date):
    # Check if the date string is empty
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date)

    if not match:
        return False

    month_str, day_str, year_str = match.groups()

    # Convert the extracted parts to integers
    try:
        month = int(month_str)
        day = int(day_str)
        year = int(year_str)
    except ValueError:
        return False

    # Validate the month
    if month < 1 or month > 12:
        return False

    # Validate the day based on the month
    if month in [4, 6, 9, 11]:
        if day < 1 or day > 30:
            return False
    elif month in [1, 3, 5, 7, 8, 10, 12]:
        if day < 1 or day > 31:
            return False
    elif month == 2:
        if day < 1 or day > 29:
            return False
    else:
        return False

    return True
```
```
#### node b = tester(inputs=['a'], tools=['run_examples', 'compare'], skills=['edge_cases', 'read_spec']) -> import re

def valid_date(date):
    # Check if the input is a string and not empty
    if not isinstance(date, str):
        return False
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    # Ensures exactly 2 digits for month, 2 for day, 4 for year (wrong)
```
To evaluate the solution, I will:
1.  **Restate the specification**:
    *   **Input**: A string `date`.
    *   **Output**: Boolean (`True` or `False`).
    *   **Rules**:
        1.  String must not be empty.
        2.  Format must be strictly `mm-dd-yyyy` (regex check).
        3.  Month: 1-12.
        4.  Day ranges:
            *   31 days: 1, 3, 5, 7, 8, 10, 12.
            *   30 days: 4, 6, 9, 11.
            *   29 days: 2 (No leap year logic required per spec).
        5.  Days must be >= 1 and <= max_days for that month.
    *   **Examples**:
        *   `'03-11-2000'` -> True
        *   `'15-01-2012'` -> False (Month 15 invalid)
        *   `'04-0-2040'` -> False (Day '0' is 0, invalid)
        *   `'06-04-2020'` -> True
        *   `'06/04/2020'` -> False (Wrong separator)

2.  **Analyze Teammate's Code**:
    *   **Empty Check**: `if not date:` handles `None`, `""`, etc. Correct.
    *   **Regex**: `r'^(\d{2})-(\d{2})-(\d{4})$'` enforces exactly 2 digits for month, 2 for day, 4 for year.
        *   *Edge Case*: `'04-0-2040'`. Day is `'0'`. Regex `\d{2}` requires two digits. This string has only one digit for the day. The regex will fail to match. Returns `False`. **Correct**.
        *   *Edge Case*: `'1-1-2000'`. Month has 1 digit. Regex fails. Returns `False`. **Correct**.
    *   **Conversion**: Converts groups to int.
    *   **Validation Logic**:
        *   Month 1-12 check.
        *   Day check based on month lists.
        *   Returns `True` only if 
[... 3181 chars omitted ...]
amples are strings, and the rule "The date string is not empty" implies the existence of a string, handling non-strings as invalid (False) is safer.
    *   However, the teammate's code *crashes* on `valid_date(123)`.
    *   Let's check if the provided examples cover this. No.
    *   Let's check the instruction: "Check before answering: ... None-like cases". `None` is handled. What about other types?
    *   I will add `isinstance(date, str)` check to be safe and robust, returning `False` for non-strings, as a date validation function should not crash.

    Another subtle point: The regex `\d{2}` ensures the string length is exactly 9 characters (2+1+2+1+4).
    Is it possible to have valid logic but wrong format? `re.match` handles this.

    Let's re-read the day logic.
    "number of days is not less than 1 or higher than 31... not less than 1 or higher than 29".
    The code: `if day < 1 or day > 29: return False`. Correct.

    One tiny detail: `valid_date('00-01-2000')`.
    Regex matches. `month=0`. `month < 1` check fails. Returns False. Correct.

    Is there any case where the regex passes but the logic fails?
    `02-30-2020`. Regex matches. `month=2`. `day=30`. `30 > 29`. Returns False. Correct.
    `02-29-2020`. Regex matches. `month=2`. `day=29`. `1<=29<=29`. Returns True. Correct (Spec doesn't care about leap years).

    The teammate's solution seems solid. I will add the `isinstance` check just to be perfectly robust against non-string inputs (like integers or lists) which might be tested as "edge cases" for type safety, ensuring no crash.

    Final check on constraints:
    - Input: `date` (string).
    - Output: `bool`.
    - Format: `mm-dd-yyyy`.

    I will refine the solution to include `isinstance(date, str)` check to prevent `TypeError` on non-string inputs, which is a common edge case in "robustness" tests.

```python
import re

def valid_date(date):
    # Check if input is a string and not empty
    if not isinstance(date, str):
        return False
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    # Ensures exactly 2 digits, dash, 2 digits, dash, 4 digits
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date)

    if not match:
        return False

    month_str, day_str, year_str = match.groups()

    # Convert the extracted parts to integers
    try:
        month = int(month_str)
        day = int(day_str)
        year = int(year_str)
    except ValueError:
        return False

    # Validate the month
    if month < 1 or month > 12:
        return False

    # Validate the day based on the month
    # Months with 31 days: 1, 3, 5, 7, 8, 10, 12
    if month in [1, 3, 5, 7, 8, 10, 12]:
        if day < 1 or day > 31:
            return False
    # Months with 30 days: 4, 6, 9, 11
    elif month in [4, 6, 9, 11]:
        if day < 1 or day > 30:
            return False
    # Month 2: 29 days (no leap year logic per spec)
    elif month == 2:
        if day < 1 or day > 29:
            return False
    else:
        # This case is covered by month < 1 or > 12, but good for completeness
        return False

    return True
```

Final solution:
```python
import re

def valid_date(date):
    # Check if the input is a string and not empty
    if not isinstance(date, str):
        return False
    if not date:
        return False

    # Define the regular expression pattern for mm-dd-yyyy
    # Ensures exactly 2 digits for month, 2 for day, 4 for year, separated by dashes
    pattern = r'^(\d{2})-(\d{2})-(\d{4})$'
    match = re.match(pattern, date)

    if not match:
        return False

    month_str, day_str, year_str = match.groups()

    # Convert the extracted parts to integers
    try:
        month = int(month_str)
        day = int(day_str)
        year = int(year_str)
    except ValueError:
        return False

    # Validate the month range (1-12)
    if month < 1 or month > 12:
        return False

    # Validate the day based on the month
    # Months with 31 days: 1, 3, 5, 7, 8, 10, 12
    if month in [1, 3, 5, 7, 8, 10, 12]:
        if day < 1 or day > 31:
            return False
    # Months with 30 days: 4, 6, 9, 11
    elif month in [4, 6, 9, 11]:
        if day < 1 or day > 30:
            return False
    # Month 2: 29 days (spec does not require leap year logic)
    elif month == 2:
        if day < 1 or day > 29:
            return False
    else:
        return False

    return True
```
```

# History (held-out dev-B)
round 0 (starting organization): acc 75.0%

Output the JSON object between <edit> and </edit>.