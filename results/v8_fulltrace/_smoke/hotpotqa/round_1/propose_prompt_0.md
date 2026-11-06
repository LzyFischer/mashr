You improve a multi-agent system whose task agents answer multi-hop questions from given paragraphs, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each question the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
    a = decomposer(tools=["search"], skills=["bridge", "answer_span"])
    c = checker(a, skills=["answer_span"])
    return c
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this question: tools (Python functions on the paragraphs (no tools = no Python; up to 3 runs)) and skills (how-to texts), chosen from the libraries
below. A node sees the question, the 10 paragraphs and the full work of its inputs; with tools it may run Python on the paragraphs up to 3 times, then answers. Nodes without inputs run in parallel. `return x`: x's answer is final. The meta-agent does not do the
question itself. Unusable output -> the first task agent alone with no tools (fixed).

# Self vs residual
A role is the same on every question, so it can hold only practices that help on every question that agent
works on. Whatever helps only some questions (a method, a check, domain knowledge, a helper function)
belongs to the residual side: a skill or a tool, plus a meta-harness rule that says when to give it.
You learn which parts are general and which vary per question; the meta-agent fills in the varying part
on each question. Before putting a sentence into a role, ask: is it right for every question this agent
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
  knowledge or a helper that only some questions need -> a skill or tool and a rule.
- Regressions first: if the last accepted change broke problems, find out why before adding more.
- If a failure persists after changes on one layer (verdict INEFFECTIVE, or the problems stay wrong),
  revert them and try another layer.
- Few, decisive changes. Remove rules and agents the evidence does not support. Skills and tools are
  never removed: an unhelpful one is fixed by editing it or by the rules that say when to give it.

# Generality (hard constraints)
- Held-out questions are different questions of the same kind. Write nothing that only fits one question in
  this report: no answers, constants, entity, table or column names, or wording copied from a report
  question. A rule must name a class of questions that can be recognized from the question text alone.
- Target patterns shared by several wrong questions (cite them in evidence), not a single failure.
- No ban lists or name lists ("never give X", "only these tools") unless the cited failures were
  caused by X.
- Prefer removing, merging or shortening rules and roles over adding; if a new rule overlaps an old
  one, edit the old one. Every role, rule and skill costs tokens on each question, and a 9B model follows long
  instructions less reliably.
- A tool is a general helper (compute, check, search, inspect) with a test. It must not contain an
  answer or a special case for one question.
- At most 8 operations in this candidate (all changes together).

# Analysis
1. Read the history: which candidates were accepted or rejected, their held-out results (fixed and
   broken against the incumbent) and, for accepted changes, which of their cited problems were fixed.
   KEEP what works, IMPROVE what is directionally right, ROLLBACK what did not work and re-approach
   that pattern on another layer.
2. Read "Since the last accepted change" in the report: regressions first.
3. Read the traces of the wrong questions: for each, find the node and the step where it went wrong.
   Group them into patterns and find each one's root cause.
4. Check which architectures, tools and skills help and which do not.

Objective: maximize accuracy on held-out problems.
This candidate may edit only the self harness: the task-agent layer.

# Output
A JSON object between <edit> and </edit>:
{"changes": [{"pattern": "<the failure pattern, one sentence>",
               "rationale": "<its root cause in the traces, and why this layer and these ops fix it>",
               "evidence": ["<labels of the wrong dev-A questions that show this pattern, e.g. A12>"],
               "ops": [<edit operations, applied in order>]}]}
One change per failure pattern. If the candidate is accepted, the next round reports which of its
cited questions were fixed.

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
Tool code runs in a sandbox (Python 3, standard library, no network, 10 s) with CONTEXT (the question's paragraphs: a list of [title, list of sentences]) defined; tests run on a small sample CONTEXT. Tools print their results. A new or edited tool is run with its test first; if the test fails, the candidate is sent back.
At most 8 task agents, 20 rules, 40 skills and 24 tools. No rule may
mention a removed agent. Names: a letter, then letters, digits or underscores.

# Tools
- python: Run Python (standard library) with CONTEXT (the paragraphs as a list of [title, sentences]) defined, to search, count or compute.
- search: search(text) -> prints every sentence that contains text (case-insensitive), with its paragraph number, title and sentence number.
```python
def search(text):
    n = 0
    for i, (title, sents) in enumerate(CONTEXT, 1):
        for j, s in enumerate(sents):
            if text.lower() in s.lower() or text.lower() in title.lower():
                print(f"[{i}] {title} ({j}): {s.strip()}"); n += 1
    print(f"{n} sentences")
```
- dates: dates(i=None) -> prints every date or year in paragraph i (all paragraphs if None), with the sentence it is in; useful for comparisons of age, time or order.
```python
def dates(i=None):
    import re
    pat = re.compile(r"\b(?:\d{1,2} )?(?:January|February|March|April|May|June|July|August|September|"
                     r"October|November|December)?(?: \d{1,2},)? ?\b(?:1[0-9]|20)\d\d\b")
    for k, (title, sents) in enumerate(CONTEXT, 1):
        if i is not None and k != i:
            continue
        for j, s in enumerate(sents):
            found = [m.group().strip() for m in pat.finditer(s)]
            if found:
                print(f"[{k}] {title} ({j}): {', '.join(found)} | {s.strip()[:200]}")
```

# Skills
- bridge (when: an entity is described through another one ('the director of film X', 'the city where Y was born')): 1. Find the inner entity first (the film X), from its paragraph. 2. Read the property you need (its director) and name the bridge entity exactly. 3. Find the bridge entity's own paragraph and read the asked property there. 4. The answer is about the last entity in the chain, not the first.
- comparison (when: two entities are compared (which / who is older, earlier, larger; do both ...; same ...)): 1. Find the compared property (birth date, release year, population, nationality) for each entity in its own paragraph; write both values. 2. Compare them carefully (earlier date = older person / earlier release). 3. Answer with the entity's name as written in the question, or yes/no for 'both' and 'same' questions.
- yes_no (when: a yes/no question (Is / Are / Were / Do / Did ... ?)): Answer only 'yes' or 'no'. For 'both' questions, check the property for each entity separately; 'same nationality' needs both nationalities written down first.
- relations (when: family or other relations (grandfather, mother-in-law, spouse, child of the director ...)): Compose relations one step at a time: paternal grandfather = father's father; mother-in-law = spouse's mother; 'the director's child' = find the director, then that person's child. Write each step with the paragraph that states it.
- dates_numbers (when: dates, ages, years, counts or quantities): 1. Copy dates exactly as written. 2. 'Who died first / was born first' compares full dates, not only years. 3. Age at an event = event year - birth year (minus one if the birthday comes later in that year). 4. Give a number or date in the form the paragraph uses.
- answer_span (when: any question): Give the shortest span that answers the question, as it appears in the paragraphs: a name, a title, a date, a number or yes/no. No explanation, no 'The answer is', no extra qualifiers; keep the original spelling.
- distractors (when: similar names, several people with one name, or paragraphs about related entities): Most paragraphs are distractors. Confirm each entity by its exact title and description (dates, profession, country) before using a fact from its paragraph; ignore facts about look-alike names.

# Current organization
Task agents:
- reader: You answer multi-hop questions using only the given paragraphs: find each fact you need and give a short answer.
- decomposer: You split the question into single-hop sub-questions, answer each from the paragraphs (cite the paragraph), and combine them into the final short answer.
- checker: You check the answers you are given against the paragraphs: verify each hop, fix any error, and give the short answer you believe is correct.
Meta-harness:
1. Comparison or yes/no question: one reader.
2. An entity described through another: a decomposer, then a checker that reads its work.
3. Give skills that match the question.

# Report
# Report (dev-A)

Organization: acc 50.0% (meta-agent prompt 2858 chars; roles 406 chars). 2 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| bridge | 7 | 57% | decomposer[T][S]>checker[T][S] 7 |
| comparison | 1 | 0% | reader[T][S] 1 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| decomposer[T][S]>checker[T][S] | 7 | 57% |
| reader[T][S] | 1 | 0% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| decomposer | 7 | 57% | 0% | - | - | - |
| checker (with inputs) | 7 | 57% | 0% | - | - | - |
| reader | 1 | 0% | 0% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:search | 15 | 53% | - |
| skill:answer_span | 15 | 53% | - |
| skill:bridge | 8 | 50% | 57% |
| tool:dates | 7 | 86% | 25% |
| skill:dates_numbers | 6 | 83% | 33% |
| skill:distractors | 3 | 0% | 67% |
| skill:comparison | 1 | 0% | 57% |
Never given: python, yes_no, relations.

## Wrong (4)
- A2 [comparison] answered 1966; correct Hey Pa! There's a Goat on the Roof; team: a = reader(tools=['search', 'dates'], skills=['comparison', 'answer_span', 'dates_numbers']); return a
- A3 [bridge] answered the Bahamian island of Great Exuma; correct Great Exuma; team: a = decomposer(tools=['search'], skills=['bridge', 'answer_span', 'distractors']); c = checker(a, tools=['search'], skills=['answer_span']); return c
- A4 [bridge] answered Claudio López; correct Claudio Javier López; team: a = decomposer(tools=['search'], skills=['bridge', 'distractors', 'answer_span']); c = checker(a, tools=['search'], skills=['answer_span']); return c
- A7 [bridge] answered India; correct Jamnagar; team: d = decomposer(tools=['search'], skills=['answer_span', 'bridge', 'distractors']); c = checker(d, tools=['search'], skills=['answer_span', 'bridge']); return c

## Traces of the wrong problems (4 of 4; node outputs over 6000 chars are cut in the middle)
### A3 [bridge]
Question: Where was the music festival Billy McFarland was charged with wire fraud for supposed to take place?
Paragraph titles: The Great Escape (festival); Frank Vennes; Billy Martin (lawyer); Pete Kott; Fyre Festival; Joint Terrorism Task Force; Pharmed Group; Ghaith Pharaon; Billy McFarland (entrepreneur); John F. Harris (political aide)
Correct: Great Exuma
Grader on the final answer: exact match 0, F1 0.57
Team: a = decomposer(tools=['search'], skills=['bridge', 'answer_span', 'distractors']); c = checker(a, tools=['search'], skills=['answer_span']); return c
#### node a = decomposer(inputs=[], tools=['search'], skills=['bridge', 'answer_span', 'distractors']) -> the Bahamian island of Great Exuma (wrong)
```
To answer the question, I need to identify the music festival Billy McFarland was charged with wire fraud for and then determine where it was supposed to take place.

1.  **Identify the festival:** Paragraph [9] states that William Z. McFarland (Billy McFarland) was "charged with wire fraud ... related to the organization of the Fyre Festival". This identifies the festival as the **Fyre Festival**.
2.  **Find the location of the festival:** Paragraph [5] describes the Fyre Festival: "The Fyre Festival was a music festival scheduled to take place on the Bahamian island of Great Exuma".

The location is the Bahamian island of Great Exuma.

#### the Bahamian island of Great Exuma
```
#### node c = checker(inputs=['a'], tools=['search'], skills=['answer_span']) -> the Bahamian island of Great Exuma (wrong)
```
The music festival Billy McFarland was charged with wire fraud for is the Fyre Festival. According to paragraph [5], the Fyre Festival was scheduled to take place on the Bahamian island of Great Exuma.

#### the Bahamian island of Great Exuma
```
### A2 [comparison]
Question: Which came to market first, "Hey Pa! There's a Goat on the Roof" or "Poleconomy"
Paragraph titles: Pashmina; Hey Pa! There's a Goat on the Roof; Poleconomy; Verão Vermelho; Ford flathead V8 engine; Friendship Hall; Vetigel; Rove goat; Chatta Bazaar; VELUX
Correct: Hey Pa! There's a Goat on the Roof
Grader on the final answer: exact match 0, F1 0.00
Team: a = reader(tools=['search', 'dates'], skills=['comparison', 'answer_span', 'dates_numbers']); return a
#### node a = reader(inputs=[], tools=['search', 'dates'], skills=['comparison', 'answer_span', 'dates_numbers']) -> 1966 (wrong)
```
Based on the text provided:
- "Hey Pa! There's a Goat on the Roof" was issued in **1966** (Paragraph [2]).
- "Poleconomy" was first published in **1980** (Paragraph [3]).

Comparing the dates, 1966 is earlier than 1980.

#### Hey Pa! There's a Goat on the Roof
#### 1966
```
### A4 [bridge]
Question: Which retired Argentine footballer who played as a forward was a main player for Valencia CF?
Paragraph titles: 1998–99 Valencia CF season; Mariano Campodónico; Luis Artime; List of Valencia CF Femenino seasons; 2002–03 Valencia CF season; Mario Kempes; Higinio Ortúzar; José Daniel Valencia; Claudio López (footballer); José Aveiro
Correct: Claudio Javier López
Grader on the final answer: exact match 0, F1 0.80
Team: a = decomposer(tools=['search'], skills=['bridge', 'distractors', 'answer_span']); c = checker(a, tools=['search'], skills=['answer_span']); return c
#### node a = decomposer(inputs=[], tools=['search'], skills=['bridge', 'distractors', 'answer_span']) -> Claudio López (wrong)
```
To answer the question, I need to identify a retired Argentine footballer who played as a forward and was a main player for Valencia CF.

1.  **Find the bridge entity (Valencia CF main player):**
    *   Paragraph [1] mentions: "Among the main players behind the success included Gaizka Mendieta, Javier Farinós and lethal striker **Claudio López**." This paragraph is about the 1998–99 Valencia CF season.
    *   I need to verify Claudio López's nationality and position.

2.  **Find the bridge entity's own paragraph and read the asked property:**
    *   Paragraph [9] is titled "Claudio López (footballer)".
    *   It states: "Claudio Javier López ... is a retired **Argentine footballer** who played as a **forward**."
    *   This matches all criteria: retired, Argentine, forward, and main player for Valencia CF (established in step 1).

3.  **Check distractors:**
    *   Paragraph [2] Mariano Campodónico: Argentine forward, but no mention of Valencia.
    *   Paragraph [3] Luis Artime: Argentine striker, but no mention of Valencia.
    *   Paragraph [6] Mario Kempes: Argentine striker who played for Valencia, but the question asks for *a* retired Argentine footballer who was a *main* player. While Kempes played for Valencia, the text in Para [1] explicitly lists "Claudio López" among the "main players behind the success" for a specific successful season where they won the Copa del Rey. However, let's re-read carefully. Para [6] says Kempes is "best known for playing for Valencia". Para [1] says López was among the "main players". The question asks "Which retired Argentine footballer who played as a forward was a main player for Valencia CF?". Both fit the description. However, looking at the phrasing "a main player", it usually refers to a specific mention in the context of a successful team or season. Para [1] explicitly groups Mendieta, Farinós, and López as "main players". Para [6] describes Kempes as a "prolific goalscorer" and "best known for playing for Valencia". Both are valid candidates based on the text. Let's look for constraints. Is there only one?
    *   Let's re-evaluate Para [6]: "Mario Alberto Kempes Chiodi... is a retired Argentine footballer who played as a striker... best known for playing for Valencia".
    *   Let's re-evaluate Para [9]: "Claudio Javier López... is a retired Argentine footballer who played as a forward." Para [1] calls him a "lethal striker" and lists him as a "main player".
    *   The prompt asks "Which...". Usually implies one specific answer derived from the chain. The chain in the instructions says "Find the inner entity first... from its paragraph... Read the property you need...".
    *   If I start with Para [1] (Valencia season), the "main players" are listed as Mendieta (Basque), Farinós (Spanish), and López (Argentine). Only López fits the "Argentine" criteria in that specific list of main players.
    *   If I start with Para [6] (Kempes), he is Argentine, a striker (forward), and played for Valencia. But was he described as a "main player" in the text? The text says he is "best known for playing for Valencia" and a "prolific goalscorer". It doesn't use the phrase "main player".
    *   Para [1] uses the exact phrase "main players" and lists López.
    *   Therefore, Claudio López is the intended answer because the text explicitly categorizes him as a "main player" in the context of Valencia CF, whereas Kempes is described by his fame and goalscoring record.

    *   Entity: Claudio López
    *   Paragraph [9] confirms: "retired Argentine footballer who played as a forward".
    *   Paragraph [1] confirms: "Among the main players... included... Claudio López."

    The answer is Claudio López.

#### Claudio López
```
#### node c = checker(inputs=['a'], tools=['search'], skills=['answer_span']) -> Claudio López (wrong)
```
Claudio López
```
### A7 [bridge]
Question: What country is the member of Gujarat Legislative Assembly and parliament representing?
Paragraph titles: Vaja Babubhai; Dhirubhai Shah; Ramanlal Vora; Ghanshyam Oza; Chhotubhai Vasava; Poonamben Maadam; Jaydrathsinh Parmar; Kundanlal Dholakia; Gujarat Legislative Assembly election, 2012; Babubhaibokhiria
Correct: Jamnagar
Grader on the final answer: exact match 0, F1 0.00
Team: d = decomposer(tools=['search'], skills=['answer_span', 'bridge', 'distractors']); c = checker(d, tools=['search'], skills=['answer_span', 'bridge']); return c
#### node d = decomposer(inputs=[], tools=['search'], skills=['answer_span', 'bridge', 'distractors']) -> India (wrong)
```
The question asks for the country represented by members of the Gujarat Legislative Assembly and parliament.

1.  **Identify the entity**: The "Gujarat Legislative Assembly" is mentioned in multiple paragraphs. Paragraph [1] states: "Vaja Babubhai is a Member of Legislative Assembly... in the Gujarat Legislative Assembly, **India**." Paragraph [3] mentions "Ramanlal Vora... from Gujarat state of **India**." Paragraph [6] mentions "Poonamben Maadam is Member of parliament... She was member of Gujarat Legislative Assembly".
2.  **Extract the country**: The country associated with Gujarat and its legislative bodies in the text is "India".

#### India
```
#### node c = checker(inputs=['d'], tools=['search'], skills=['answer_span', 'bridge']) -> India (wrong)
```
The question asks for the country represented by members of the Gujarat Legislative Assembly and parliament. Paragraph [1] states: "Vaja Babubhai is a Member of Legislative Assembly representing the Mangrol assembly constituency in the Gujarat Legislative Assembly, **India**." Paragraph [3] mentions "Ramanlal Vora... from Gujarat state of **India**." Paragraph [6] mentions "Poonamben Maadam is Member of parliament from Jamnagar seat" and was a member of the Gujarat Legislative Assembly, which is in India. The country is consistently identified as India.

#### India
```

# History (held-out dev-B)
round 0 (starting organization): acc 37.5%

Output the JSON object between <edit> and </edit>.