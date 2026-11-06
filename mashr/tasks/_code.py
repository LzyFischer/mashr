"""Code generation from specifications: HumanEval+ and MBPP+ (EvalPlus). A node writes the complete
function; with tools it may run Python up to MAX_RUNS times first. Graded with the official EvalPlus
checker (evalplus.eval.untrusted_check): correct = passes the base and the plus tests (pass@1).

Data: data/_download/evalplus/{HumanEvalPlus,MbppPlus}.jsonl (scripts/prepare_data.py) and the splits
in data/code/splits.json. Needs evalplus (pip install --no-deps evalplus==0.3.1; pip install tempdir
wget appdirs psutil numpy). Expected outputs are computed once per problem and cached next to the data.
"""
import functools
import json
import os
import pickle
import re
import threading

from .. import ROOT
from ..sandbox import CODE, run_python

DL = os.path.join(ROOT, "data", "_download", "evalplus")
RAW = {"humaneval_plus": ("humaneval", "HumanEvalPlus.jsonl"), "mbpp_plus": ("mbpp", "MbppPlus.jsonl")}
os.environ.setdefault("HUMANEVAL_OVERRIDE_PATH", os.path.join(DL, "HumanEvalPlus.jsonl"))
os.environ.setdefault("MBPP_OVERRIDE_PATH", os.path.join(DL, "MbppPlus.jsonl"))
MAX_TOKENS = 3072    # per task-agent call
MAX_RUNS = 3
N_CHECKERS = int(os.environ.get("MASHR_CODE_CHECKS", 8))   # grader processes
FINAL = "Final solution:"
ANSWER_FMT = (f"End your response with the line '{FINAL}' and then one ```python``` block with the "
              "complete function (with the imports and helpers it needs).")

_lock = threading.Lock()
_probs, _graded = {}, {}


def problems(name):
    with _lock:
        if name not in _probs:
            ds, f = RAW[name]
            if not os.path.exists(os.path.join(DL, f)):
                raise SystemExit(f"{os.path.join(DL, f)} is missing: run scripts/prepare_data.py")
            try:
                from evalplus.data import get_human_eval_plus, get_mbpp_plus
            except ImportError:
                raise SystemExit("the code tasks grade with EvalPlus: pip install --no-deps evalplus==0.3.1 "
                                 "&& pip install tempdir wget appdirs psutil numpy")
            _probs[name] = get_human_eval_plus() if ds == "humaneval" else get_mbpp_plus()
    return _probs[name]


def _oracle(name, p):
    """The canonical solution's outputs and times on the base and plus inputs."""
    from evalplus.eval._special_oracle import MBPP_OUTPUT_NOT_NONE_TASKS
    from evalplus.gen.util import trusted_exec
    nn = p["entry_point"] in MBPP_OUTPUT_NOT_NONE_TASKS
    out = {}
    for k in ("base", "plus"):
        out[k], out[f"{k}_time"] = trusted_exec(p["prompt"] + p["canonical_solution"], p[f"{k}_input"],
                                                p["entry_point"], record_time=True, output_not_none=nn)
    return out


@functools.lru_cache(maxsize=16)
def expected(name, tid):
    """The canonical solution's outputs on problem tid, cached one file per problem in
    data/_download/evalplus/expected_<task>/ (a few problems have outputs of tens of MB, so a worker
    loads only the problems it grades)."""
    path = os.path.join(DL, f"expected_{name}", tid.replace("/", "_") + ".pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    exp = _oracle(name, problems(name)[tid])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.part"
    with open(tmp, "wb") as f:
        pickle.dump(exp, f)
    os.replace(tmp, path)
    return exp


# Grading runs in spawned worker processes. EvalPlus forks a child per check and caps its address space
# (RLIMIT_AS, 4 GB); a child forked from the RSI process (128 threads, ~12 GB of virtual memory) fails
# every check, even the canonical solution's. A fresh, small worker keeps the children small.
_pool = None


def _executor():
    global _pool
    with _lock:
        if _pool is None:
            import multiprocessing as mp
            from concurrent.futures import ProcessPoolExecutor
            import atexit
            _pool = ProcessPoolExecutor(N_CHECKERS, mp_context=mp.get_context("spawn"))
            atexit.register(_pool.shutdown, wait=False, cancel_futures=True)
    return _pool


def check(name, p, code):
    """(passed, detail) of a complete program on the base and the plus tests of problem p."""
    return _executor().submit(_check, name, p["task_id"], code).result()


def canonical_ok(name, tid, tries=3):
    """Whether the canonical solution passes (any of `tries` checks); run in a fresh worker per problem
    (scripts/prepare_data.py)."""
    import resource
    lim = 6 * 1024 ** 3      # a canonical solution with huge outputs (Mbpp/255) fails instead of killing the worker
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))
    p = problems(name)[tid]
    try:
        exp = expected(name, tid)
    except MemoryError:
        return False
    return any(_check(name, tid, p["prompt"] + p["canonical_solution"], exp)[0] for _ in range(tries))


def _check(name, tid, code, exp=None):
    """In a worker. Time limits are EvalPlus's (max(1 s, 4 x the canonical solution's time) per input); a
    timeout is re-checked once, since a loaded machine can push a solution as fast as the reference
    over its limit."""
    from evalplus.eval import PASS, TIMEOUT, untrusted_check
    ds, p = RAW[name][0], problems(name)[tid]
    exp = exp or expected(name, tid)
    for k in ("base", "plus"):
        for attempt in range(2):
            status, det = untrusted_check(ds, code, p[f"{k}_input"], p["entry_point"], expected=exp[k],
                                          atol=p["atol"], ref_time=exp[f"{k}_time"], fast_check=True)
            if status != TIMEOUT:
                break
        if status != PASS:
            msg = f"fails the {k} tests ({status})"
            i = next((i for i, ok in enumerate(det) if not ok), None) if det is not None else None
            if i is not None and i < len(p[f"{k}_input"]):
                msg += (f" on input {repr(tuple(p[f'{k}_input'][i]))[:300]}; expected output "
                        f"{repr(exp[k][i])[:200]}")
            return False, msg
    return True, "passes the base and plus tests"


def extract_code(text, entry):
    """The final function: the last ```python``` block after the last 'Final solution:' (else in the
    whole text) that defines the entry point, else the last block."""
    if text is None:
        return None
    i = text.lower().rfind(FINAL.lower())
    blocks = CODE.findall(text[i:] if i >= 0 else text) or CODE.findall(text)
    if not blocks:
        return None
    defs = [b for b in blocks if re.search(rf"\bdef\s+{re.escape(entry)}\s*\(", b)]
    return (defs or blocks)[-1].strip()


TOOLS = {
    "python": {
        "doc": "Run Python (standard library, numpy) to test code: define the function, call it, print results.",
        "code": "",
        "test": "assert 2 + 2 == 4",
    },
    "run_examples": {
        "doc": "run_examples(func=None) -> prints PASS/FAIL for every example in the problem statement (the "
               "'>>>' lines with their expected output, or the 'assert' lines) run against func (default: "
               "the function with the problem's name, defined in your code).",
        "code": '''
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
''',
        "test": "def add(a, b):\n    return a + b\nimport io, contextlib\nbuf = io.StringIO()\n"
                "with contextlib.redirect_stdout(buf):\n    run_examples()\nassert '1/1 examples pass' in buf.getvalue(), buf.getvalue()",
    },
    "compare": {
        "doc": "compare(f, g, inputs) -> runs f(*x) and g(*x) for each tuple x in inputs and prints the "
               "mismatches (first 5) and their count; e.g. a fast solution against a brute-force one.",
        "code": '''
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
''',
        "test": "import io, contextlib\nbuf = io.StringIO()\nwith contextlib.redirect_stdout(buf):\n"
                "    compare(lambda a: a * 2, lambda a: a + a, [(1,), (2,), (3,)])\n"
                "assert '0/3 mismatches' in buf.getvalue(), buf.getvalue()",
    },
    "timed": {
        "doc": "timed(func, *args) -> prints how long func(*args) takes (stops after 5 s); hidden tests use "
               "large inputs, so check the speed of your solution on a large one.",
        "code": '''
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
''',
        "test": "import io, contextlib\nbuf = io.StringIO()\nwith contextlib.redirect_stdout(buf):\n"
                "    timed(sum, range(1000))\nassert ' s' in buf.getvalue(), buf.getvalue()",
    },
}

SKILLS = {
    "read_spec": {
        "when": "any problem",
        "text": "1. Restate the input types, the output type and every rule in the specification before "
                "coding. 2. The examples are part of the specification: your function must reproduce them "
                "exactly, including the output type (list vs tuple, int vs float, True/False). 3. Return "
                "the value; do not print and do not read input. 4. Keep the given function name and "
                "parameter order.",
    },
    "edge_cases": {
        "when": "inputs are lists, strings or numbers whose size or sign can vary",
        "text": "Hidden tests probe the corners. Check before answering: empty list/string, one element, "
                "all equal elements, duplicates, negative numbers, zero, unsorted input, very large values, "
                "and None-like cases the specification mentions. Decide what each must return from the "
                "specification (not from a guess), and make sure the code does not crash on them.",
    },
    "examples_check": {
        "when": "the problem statement contains examples",
        "text": "Before the final answer, run every example (run_examples, or by hand if you have no "
                "tools: trace the code line by line on each example). If one fails, find the rule you "
                "misread instead of special-casing the example.",
    },
    "string_rules": {
        "when": "string manipulation (case, words, characters, formatting)",
        "text": "1. Case: does the comparison or output keep, lower or upper case? 2. Whitespace: split() "
                "vs split(' ') (multiple spaces, leading/trailing spaces). 3. Which characters count "
                "(letters only, vowels incl. 'y'?, digits, punctuation)? 4. Keep the original order unless "
                "told to sort. 5. Return the exact format of the examples (quotes, separators).",
    },
    "numeric_rules": {
        "when": "arithmetic, rounding, division or number formats",
        "text": "1. Return type: int vs float, as in the examples. 2. // and % with negative numbers round "
                "towards minus infinity in Python. 3. round() rounds halves to even; use the rule the "
                "problem states. 4. Compare floats with a tolerance. 5. Large numbers: use integers, not "
                "floats, to stay exact.",
    },
    "efficiency": {
        "when": "inputs can be large (primes, divisors, sequences, nested loops, recursion)",
        "text": "The plus tests use large inputs and a time limit of a few times the reference solution. "
                "Avoid exponential recursion (memoize or iterate), quadratic loops over long lists when a "
                "set/dict/sort works, and trial division beyond sqrt(n). Check the speed on a large input "
                "(timed) before answering.",
    },
    "assert_signature": {
        "when": "the problem gives an assert line (the MBPP style)",
        "text": "The assert fixes the function name, the number and order of arguments and the exact "
                "return value: match its type (tuple vs list vs set, int vs float, bool) and format. If it "
                "wraps the call (e.g. set(...)), the order of elements does not matter; otherwise it does.",
    },
}

SEED = {
    "agents": {
        "coder": {"role": "You write correct, complete Python functions that meet the specification exactly."},
        "tester": {"role": "You test the solution your teammates wrote: derive test cases from the "
                           "specification (including edge cases), run them, fix every bug you find, and give "
                           "the corrected complete function."},
        "reviewer": {"role": "You review the solutions you are given against the specification: find any "
                             "bug or misread requirement and give the complete function you believe is correct."},
    },
    "rules": [
        "Simple, clearly specified function: one coder with python.",
        "Tricky specification or many edge cases: a coder with python and run_examples, then a tester with "
        "run_examples that reads its work.",
        "Give skills that match the problem.",
    ],
}

BASELINES = {
    "single": "a = coder()\nreturn a",
    "coder_tools": 'a = coder(tools=["python", "run_examples"])\nreturn a',
    "code_test": 'a = coder(tools=["python", "run_examples"])\nb = tester(a, tools=["python", "run_examples"])\nreturn b',
}
META = {"team": "write Python functions from specifications", "item": "problem",
        "node": "the agent reads the problem, its skills and the full work of its inputs, then writes the "
                "complete function.",
        "final": "`return x`: x's function is the answer.",
        "no_solve": "write no code.",
        "tools": f"Python functions (no tools = no Python; up to {MAX_RUNS} runs)"}
EXAMPLE = ['a = coder(tools=["python", "run_examples"], skills=["edge_cases"])',
           'b = tester(a, tools=["run_examples", "compare"])', "return b"]
SYSTEM_NOTE = (f"A node with tools may run Python up to {MAX_RUNS} times (tools preloaded), then writes its "
               "final function. It reads the problem, its skills and the full work of its inputs.")
TOOL_ENV = ("Tool code runs in a sandbox (Python 3, numpy, no network, 20 s) with PROBLEM (the problem "
            "statement) and ENTRY (the function name) defined; the code of a node's tools is preloaded "
            "before the code the agent writes. Tools print their results.")


def build(name):
    """Module attributes of the task `name` (humaneval_plus | mbpp_plus)."""
    splits_path = os.path.join(ROOT, "data", "code", "splits.json")

    def load(split, n=None):
        if not os.path.exists(splits_path):
            raise SystemExit(f"{splits_path} is missing: run scripts/prepare_data.py")
        ids = json.load(open(splits_path))[name][split]
        probs = problems(name)
        items = []
        for tid in ids[:n] if n else ids:
            p = probs[tid]
            items.append({"id": tid, "question": p["prompt"].strip(), "entry": p["entry_point"],
                          "gold": "(hidden base and plus tests)", "bucket": name,
                          "hard": len(p["canonical_solution"].strip().splitlines()) >= 8})
        return items

    def meta_view(item):
        return f"Problem:\n{item['question']}"

    def grade(pred, item):
        return feedback(pred, item)[0]

    def feedback(pred, item):
        """(correct, what the grader saw); cached per (problem, program)."""
        if not pred:
            return False, "no function"
        key = (item["id"], pred)
        if key not in _graded:
            p = problems(name)[item["id"]]
            _graded[key] = check(name, p, p["prompt"] + "\n\n" + pred)
        return _graded[key]

    def tool_prelude(item=None):
        if item is None:
            return 'PROBLEM = "def add(a, b):\\n    \\"\\"\\"\\n    >>> add(1, 2)\\n    3\\n    \\"\\"\\"\\n"\nENTRY = "add"\n'
        return f"PROBLEM = {item['question']!r}\nENTRY = {item['entry']!r}\n"

    def run_node(eng, pool, node, item, work, is_output):
        S, T = pool.get("skills", SKILLS), pool.get("tools", TOOLS)
        user = f"Problem:\n```python\n{item['question']}\n```"
        if work:
            user += f"\n\nWork from your teammates:\n{work}\n\nGive your own final function."
        user += f"\n\n{ANSWER_FMT}"
        system = pool["agents"][node["agent"]]["role"]
        if node["skills"]:
            system += "\n\nSkills to apply:\n" + "\n".join(f"- {k}: {S[k]['text']}" for k in node["skills"])
        if node["tools"]:
            helpers = [t for t in node["tools"] if T[t].get("code", "").strip()]
            system += (f"\n\nYou can run Python up to {MAX_RUNS} times: write one ```python``` block that "
                       f"prints what you need, then stop and wait for its output (do not write '{FINAL}' "
                       "in that turn).")
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
            if not node["tools"] or not code or FINAL.lower() in r.text.lower() or k == MAX_RUNS:
                break
            out, _ = run_python(pre + "\n" + code[-1], timeout=20)
            shown.append(f"[Python output]\n{out}")
            more = (f"You may run code again ({MAX_RUNS - k - 1} runs left) or give the final function."
                    if k + 1 < MAX_RUNS else "No more runs. Give the final function now.")
            msgs += [{"role": "assistant", "content": r.text},
                     {"role": "user", "content": f"Output:\n{out}\n\n{more} {ANSWER_FMT}"}]
        return {"text": "\n\n".join(shown), "answer": extract_code(r.text, item["entry"]), "calls": calls,
                "cut": any(c["gen_tokens"] >= MAX_TOKENS for c in calls)}

    return {"NAME": name, "MAX_TOKENS": MAX_TOKENS, "VOTE_ON_MISSING": False, "FALLBACK_TOOLS": ("python",),
            "TOOLS_ARE_CODE": True, "TOOL_ENV": TOOL_ENV, "META": META, "EXAMPLE": EXAMPLE,
            "SYSTEM_NOTE": SYSTEM_NOTE, "TOOLS": TOOLS, "SKILLS": SKILLS, "SEED": SEED, "BASELINES": BASELINES,
            "load": load, "meta_view": meta_view, "grade": grade, "feedback": feedback,
            "tool_prelude": tool_prelude, "run_node": run_node}


if __name__ == "__main__":      # python -m mashr.tasks._code canonical <task> <problem id>: prints OK or FAIL
    import sys
    print("OK" if canonical_ok(sys.argv[2], sys.argv[3]) else "FAIL")
