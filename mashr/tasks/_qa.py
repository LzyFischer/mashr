"""Multi-hop QA over given paragraphs (the distractor setting): HotpotQA and 2WikiMultihopQA. A node
reads the question and the 10 paragraphs (2 or more supporting, the rest distractors) and gives a short
answer; with tools it may run Python on the paragraphs up to MAX_RUNS times first. Correct = exact
match after the official normalization (lower case, no punctuation, no articles, single spaces); the
grader also reports token F1.

Data: data/qa/{hotpotqa,twowiki}_{dev_a,dev_b,test}.jsonl (scripts/prepare_data.py).
"""
import json
import os
import re
import string
from collections import Counter

from .. import ROOT
from ..sandbox import CODE, run_python

MAX_TOKENS = 1536    # per task-agent call
MAX_RUNS = 3
DEFAULT_N = {"dev_a": 150, "dev_b": 50, "test": 500}
ANSWER_FMT = ("End your response with a final line of the form '#### <answer>': a short answer (an entity, "
              "a date, a number, or yes/no) written as in the paragraphs, with no explanation.")


def normalize(s):
    s = str(s).lower()
    s = "".join(ch for ch in s if ch not in set(string.punctuation))
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def f1(pred, gold):
    p, g = normalize(pred).split(), normalize(gold).split()
    if normalize(pred) in ("yes", "no", "noanswer") or normalize(gold) in ("yes", "no", "noanswer"):
        return float(normalize(pred) == normalize(gold))
    common = sum((Counter(p) & Counter(g)).values())
    if not common:
        return 0.0
    prec, rec = common / len(p), common / len(g)
    return 2 * prec * rec / (prec + rec)


def extract(text):
    if not text:
        return None
    m = re.findall(r"####\s*(.+)", text)
    a = m[-1] if m else (text.strip().splitlines() or [""])[-1]
    a = a.strip().strip("*").strip().strip('"').strip()
    return a.rstrip(".").strip() or None


def paragraphs(item):
    return "\n\n".join(f"[{i}] {t}\n" + " ".join(f"({j}) {s.strip()}" for j, s in enumerate(ss))
                       for i, (t, ss) in enumerate(item["context"], 1))


TOOLS = {
    "python": {
        "doc": "Run Python (standard library) with CONTEXT (the paragraphs as a list of [title, sentences]) "
               "defined, to search, count or compute.",
        "code": "",
        "test": "assert isinstance(CONTEXT, list)",
    },
    "search": {
        "doc": "search(text) -> prints every sentence that contains text (case-insensitive), with its "
               "paragraph number, title and sentence number.",
        "code": '''
def search(text):
    n = 0
    for i, (title, sents) in enumerate(CONTEXT, 1):
        for j, s in enumerate(sents):
            if text.lower() in s.lower() or text.lower() in title.lower():
                print(f"[{i}] {title} ({j}): {s.strip()}"); n += 1
    print(f"{n} sentences")
''',
        "test": "import io, contextlib\nbuf = io.StringIO()\nwith contextlib.redirect_stdout(buf):\n"
                "    search('paris')\nassert '1 sentences' in buf.getvalue(), buf.getvalue()",
    },
    "dates": {
        "doc": "dates(i=None) -> prints every date or year in paragraph i (all paragraphs if None), with "
               "the sentence it is in; useful for comparisons of age, time or order.",
        "code": '''
def dates(i=None):
    import re
    pat = re.compile(r"\\b(?:\\d{1,2} )?(?:January|February|March|April|May|June|July|August|September|"
                     r"October|November|December)?(?: \\d{1,2},)? ?\\b(?:1[0-9]|20)\\d\\d\\b")
    for k, (title, sents) in enumerate(CONTEXT, 1):
        if i is not None and k != i:
            continue
        for j, s in enumerate(sents):
            found = [m.group().strip() for m in pat.finditer(s)]
            if found:
                print(f"[{k}] {title} ({j}): {', '.join(found)} | {s.strip()[:200]}")
''',
        "test": "import io, contextlib\nbuf = io.StringIO()\nwith contextlib.redirect_stdout(buf):\n"
                "    dates()\nassert '1889' in buf.getvalue(), buf.getvalue()",
    },
}

SKILLS = {
    "bridge": {
        "when": "an entity is described through another one ('the director of film X', 'the city where Y was born')",
        "text": "1. Find the inner entity first (the film X), from its paragraph. 2. Read the property you "
                "need (its director) and name the bridge entity exactly. 3. Find the bridge entity's own "
                "paragraph and read the asked property there. 4. The answer is about the last entity in the "
                "chain, not the first.",
    },
    "comparison": {
        "when": "two entities are compared (which / who is older, earlier, larger; do both ...; same ...)",
        "text": "1. Find the compared property (birth date, release year, population, nationality) for "
                "each entity in its own paragraph; write both values. 2. Compare them carefully (earlier "
                "date = older person / earlier release). 3. Answer with the entity's name as written in "
                "the question, or yes/no for 'both' and 'same' questions.",
    },
    "yes_no": {
        "when": "a yes/no question (Is / Are / Were / Do / Did ... ?)",
        "text": "Answer only 'yes' or 'no'. For 'both' questions, check the property for each entity "
                "separately; 'same nationality' needs both nationalities written down first.",
    },
    "relations": {
        "when": "family or other relations (grandfather, mother-in-law, spouse, child of the director ...)",
        "text": "Compose relations one step at a time: paternal grandfather = father's father; "
                "mother-in-law = spouse's mother; 'the director's child' = find the director, then that "
                "person's child. Write each step with the paragraph that states it.",
    },
    "dates_numbers": {
        "when": "dates, ages, years, counts or quantities",
        "text": "1. Copy dates exactly as written. 2. 'Who died first / was born first' compares full "
                "dates, not only years. 3. Age at an event = event year - birth year (minus one if the "
                "birthday comes later in that year). 4. Give a number or date in the form the paragraph "
                "uses.",
    },
    "answer_span": {
        "when": "any question",
        "text": "Give the shortest span that answers the question, as it appears in the paragraphs: a name, "
                "a title, a date, a number or yes/no. No explanation, no 'The answer is', no extra "
                "qualifiers; keep the original spelling.",
    },
    "distractors": {
        "when": "similar names, several people with one name, or paragraphs about related entities",
        "text": "Most paragraphs are distractors. Confirm each entity by its exact title and description "
                "(dates, profession, country) before using a fact from its paragraph; ignore facts about "
                "look-alike names.",
    },
}

SEED = {
    "agents": {
        "reader": {"role": "You answer multi-hop questions using only the given paragraphs: find each fact "
                           "you need and give a short answer."},
        "decomposer": {"role": "You split the question into single-hop sub-questions, answer each from the "
                               "paragraphs (cite the paragraph), and combine them into the final short answer."},
        "checker": {"role": "You check the answers you are given against the paragraphs: verify each hop, fix "
                            "any error, and give the short answer you believe is correct."},
    },
    "rules": [
        "Comparison or yes/no question: one reader.",
        "An entity described through another: a decomposer, then a checker that reads its work.",
        "Give skills that match the question.",
    ],
}

BASELINES = {
    "single": "a = reader()\nreturn a",
    "decompose": "a = decomposer()\nreturn a",
    "read_check": "a = reader()\nc = checker(a)\nreturn c",
}
META = {"team": "answer multi-hop questions from given paragraphs", "item": "question",
        "node": "the agent reads the question, the paragraphs, its skills and the full work of its inputs, "
                "then answers.",
        "final": "`return x`: x's answer is final.",
        "no_solve": "no answer and no reasoning about the answer.",
        "tools": f"Python functions on the paragraphs (no tools = no Python; up to {MAX_RUNS} runs)"}
EXAMPLE = ['a = decomposer(tools=["search"], skills=["bridge", "answer_span"])',
           'c = checker(a, skills=["answer_span"])', "return c"]
SYSTEM_NOTE = (f"A node sees the question, the 10 paragraphs and the full work of its inputs; with tools it "
               f"may run Python on the paragraphs up to {MAX_RUNS} times, then answers.")
TOOL_ENV = ("Tool code runs in a sandbox (Python 3, standard library, no network, 10 s) with CONTEXT "
            "(the question's paragraphs: a list of [title, list of sentences]) defined; tests run on a "
            "small sample CONTEXT. Tools print their results.")


def build(name):
    """Module attributes of the task `name` (hotpotqa | twowiki)."""
    def load(split, n=None):
        path = os.path.join(ROOT, "data", "qa", f"{name}_{split}.jsonl")
        if not os.path.exists(path):
            raise SystemExit(f"{path} is missing: run scripts/prepare_data.py")
        rows = [json.loads(l) for l in open(path) if l.strip()]
        return rows[:n or DEFAULT_N[split]]

    def meta_view(item):
        return (f"Question: {item['question']}\nParagraph titles: "
                + "; ".join(t for t, _ in item["context"]))

    def grade(pred, item):
        return pred is not None and normalize(pred) == normalize(item["gold"])

    def feedback(pred, item):
        if pred is None:
            return False, "no answer"
        return grade(pred, item), f"exact match {int(grade(pred, item))}, F1 {f1(pred, item['gold']):.2f}"

    def tool_prelude(item=None):
        ctx = item["context"] if item else [["Paris", ["Paris is the capital of France.",
                                                       "It hosted the Exposition Universelle of 1889."]]]
        return f"CONTEXT = {json.dumps(ctx, ensure_ascii=False)}\n"

    def run_node(eng, pool, node, item, work, is_output):
        S, T = pool.get("skills", SKILLS), pool.get("tools", TOOLS)
        user = f"Paragraphs:\n{paragraphs(item)}\n\nQuestion: {item['question']}"
        if work:
            user += f"\n\nWork from your teammates:\n{work}\n\nGive your own answer."
        user += f"\n\n{ANSWER_FMT}"
        system = pool["agents"][node["agent"]]["role"]
        if node["skills"]:
            system += "\n\nSkills to apply:\n" + "\n".join(f"- {k}: {S[k]['text']}" for k in node["skills"])
        if node["tools"]:
            helpers = [t for t in node["tools"] if T[t].get("code", "").strip()]
            system += (f"\n\nYou can run Python on the paragraphs up to {MAX_RUNS} times (CONTEXT holds them): "
                       "write one ```python``` block that prints what you need, then stop and wait for its "
                       "output.")
            if helpers:
                system += " These functions are already defined:\n" + "\n".join(f"- {T[t]['doc']}" for t in helpers)
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        pre = tool_prelude(item) + "\n".join(T[t].get("code", "") for t in node["tools"])
        calls, shown = [], []
        for k in range(MAX_RUNS + 1):
            r = eng.chat(msgs, MAX_TOKENS)
            calls.append({"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
                          "gen_tokens": r.gen_tokens})
            shown.append(r.text)
            code = CODE.findall(r.text)
            final = "####" in r.text.split("```")[-1]
            if not node["tools"] or not code or final or k == MAX_RUNS:
                break
            out, _ = run_python(pre + "\n" + code[-1])
            shown.append(f"[Python output]\n{out}")
            more = (f"You may run code again ({MAX_RUNS - k - 1} runs left) or answer."
                    if k + 1 < MAX_RUNS else "No more runs. Answer now.")
            msgs += [{"role": "assistant", "content": r.text},
                     {"role": "user", "content": f"Output:\n{out}\n\n{more} {ANSWER_FMT}"}]
        return {"text": "\n\n".join(shown), "answer": extract(r.text), "calls": calls,
                "cut": any(c["gen_tokens"] >= MAX_TOKENS for c in calls)}

    return {"NAME": name, "MAX_TOKENS": MAX_TOKENS, "VOTE_ON_MISSING": True, "FALLBACK_TOOLS": (),
            "TOOLS_ARE_CODE": True, "TOOL_ENV": TOOL_ENV, "META": META, "EXAMPLE": EXAMPLE,
            "SYSTEM_NOTE": SYSTEM_NOTE, "TOOLS": TOOLS, "SKILLS": SKILLS, "SEED": SEED, "BASELINES": BASELINES,
            "load": load, "meta_view": meta_view, "grade": grade, "feedback": feedback,
            "tool_prelude": tool_prelude, "run_node": run_node}
