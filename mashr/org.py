"""The organization (v7): task agents and the meta-harness.

A task agent's full harness = its self harness (role; evolved, the same on every problem) + the
residual harness the meta-agent gives it on each problem: tools (Python functions preloaded in its
sandbox; no tools = no Python) and skills (how-to texts). The meta-agent's own harness is the
meta-harness, a numbered list of rules.

The evolver edits three layers: the task agents (add / remove / edit a role = self harness), the
meta-harness (add / edit / remove a rule) and the libraries the residual harness is drawn from (add /
edit / remove a skill or a tool). The libraries start from the task's hand-written ones
(tasks/<name>.py) and live in the organization (pool["skills"], pool["tools"]).

Meta-agent output (code, parsed, never executed):

    ```python
    a = solver(tools=["number_theory"], skills=["modular"])
    v = verifier(a, tools=["check_answer"])
    return v
    ```
The meta-agent does not solve the task; the task agents do.
"""
import ast
import copy
import json
import re

NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,30}$")
LIMITS = {"agents": 8, "rules": 20, "nodes": 8, "skills_per_node": 3, "tools_per_node": 3, "skills": 40,
          "tools": 24}     # counts only; no length limits on roles, rules, skills or tools
TASK_OPS, META_OPS = ("add_agent", "remove_agent", "edit_agent"), ("add_rule", "edit_rule", "remove_rule")
SKILL_OPS, TOOL_OPS = ("add_skill", "edit_skill"), ("add_tool", "edit_tool")   # libraries only grow
LIB_OPS = SKILL_OPS + TOOL_OPS


def skills_of(task, pool):
    return pool.get("skills", task.SKILLS)


def tools_of(task, pool):
    return pool.get("tools", task.TOOLS)


def with_libs(task, pool):
    """A copy of the organization that carries its own skill and tool libraries (the task's, if it has
    none yet), so the evolver can edit them."""
    o = copy.deepcopy(pool)
    o.setdefault("skills", copy.deepcopy(task.SKILLS))
    o.setdefault("tools", copy.deepcopy(task.TOOLS))
    return o


def _strs(node):
    if isinstance(node, (ast.List, ast.Tuple)):
        return [x.value for x in node.elts if isinstance(x, ast.Constant) and isinstance(x.value, str)]
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    return None


def parse_program(task, pool, text):
    """Meta-agent output -> (plan, problems) or (None, problems). A plan is {"nodes": [...], "output":
    id} with nodes {id, agent, inputs, tools, skills}."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    src = m.group(1) if m else text
    lines = [l for l in src.strip().splitlines() if l.strip() and not l.strip().startswith("#")]
    try:
        tree = ast.parse("def _plan():\n" + "\n".join("    " + l.strip() for l in lines))
    except SyntaxError as e:
        return None, [f"syntax error: {e.msg} (line {(e.lineno or 2) - 1})"]
    nodes, cur, out, probs = [], {}, None, []
    for st in tree.body[0].body:
        final = isinstance(st, ast.Return) and isinstance(st.value, ast.Call)
        if final:
            st = ast.Assign(targets=[ast.Name(id="out")], value=st.value, lineno=st.lineno)
        if isinstance(st, ast.Return):
            if isinstance(st.value, ast.Name) and st.value.id in cur:
                out = cur[st.value.id]
            else:
                probs.append("return must name a node defined above")
            break
        if not (isinstance(st, ast.Assign) and len(st.targets) == 1
                and isinstance(st.targets[0], ast.Name) and isinstance(st.value, ast.Call)
                and isinstance(st.value.func, ast.Name)):
            probs.append(f"line {st.lineno - 1}: expected `x = agent(inputs..., tools=[...], skills=[...])`")
            continue
        var, agent = st.targets[0].id, st.value.func.id
        if agent not in pool["agents"]:
            probs.append(f"line {st.lineno - 1}: unknown agent {agent!r}")
            continue
        inputs = []
        for x in st.value.args:
            if isinstance(x, ast.Name) and x.id in cur:
                inputs.append(cur[x.id])
            elif isinstance(x, ast.Name):
                probs.append(f"line {st.lineno - 1}: input {x.id!r} is not a node defined above")
            else:
                probs.append(f"minor: line {st.lineno - 1}: non-node argument ignored")
        kw = {k.arg: k.value for k in st.value.keywords}
        tools, skills = _strs(kw["tools"]) if "tools" in kw else [], \
            _strs(kw["skills"]) if "skills" in kw else []
        if tools is None or skills is None:
            probs.append(f"minor: line {st.lineno - 1}: tools/skills must be lists of names")
            tools, skills = tools or [], skills or []
        T, S = tools_of(task, pool), skills_of(task, pool)
        bad = [t for t in tools if t not in T] + [k for k in skills if k not in S]
        if bad:
            probs.append(f"minor: line {st.lineno - 1}: unknown tools/skills {bad} dropped")
        tools = [t for t in tools if t in T][:LIMITS["tools_per_node"]]
        skills = [k for k in skills if k in S][:LIMITS["skills_per_node"]]
        if len(nodes) == LIMITS["nodes"]:
            probs.append(f"more than {LIMITS['nodes']} nodes")
            break
        nid = var if var not in cur and all(n["id"] != var for n in nodes) else f"{var}_{len(nodes)}"
        nodes.append({"id": nid, "agent": agent, "inputs": inputs, "tools": tools, "skills": skills})
        cur[var] = nid
        if final:
            out = nid
            break
    if not nodes:
        return None, probs + ["no node"]
    if out is None:
        probs.append("no return; using the last node")
        out = nodes[-1]["id"]
    return {"nodes": nodes, "output": out}, probs


def fallback_plan(task, pool):
    """Fixed, not editable: the first task agent alone with the task's fallback tools."""
    a = next(iter(pool["agents"]))
    return {"nodes": [{"id": "a", "agent": a, "inputs": [], "tools": list(task.FALLBACK_TOOLS),
                       "skills": []}], "output": "a"}


def program_str(p):
    def one(n):
        args = list(n["inputs"])
        if n["tools"]:
            args.append(f"tools={n['tools']}")
        if n["skills"]:
            args.append(f"skills={n['skills']}")
        return f"{n['id']} = {n['agent']}({', '.join(args)})"
    return "; ".join([one(n) for n in p["nodes"]] + [f"return {p['output']}"])


def shape(p):
    """Canonical architecture: 'coder[T]>verifier[T]' ([T] tools, [S] skills)."""
    depth = {}
    for n in p["nodes"]:
        depth[n["id"]] = 1 + max((depth[i] for i in n["inputs"]), default=-1)
    layers = {}
    for n in p["nodes"]:
        tag = ("[T]" if n["tools"] else "") + ("[S]" if n["skills"] else "")
        layers.setdefault(depth[n["id"]], []).append(f"{n['agent']}{tag}")
    return ">".join(",".join(sorted(layers[d])) for d in sorted(layers))


def _check_lib(pool, errs):
    if "skills" in pool:
        if not isinstance(pool["skills"], dict) or len(pool["skills"]) > LIMITS["skills"]:
            errs.append(f"skills: at most {LIMITS['skills']}")
        else:
            for k, v in pool["skills"].items():
                if not NAME.match(k):
                    errs.append(f"bad skill name {k!r}")
                elif not isinstance(v, dict) or not {"when", "text"} <= set(v) \
                        or not all(isinstance(v[f], str) and v[f].strip() for f in ("when", "text")):
                    errs.append(f"skill {k!r}: {{\"when\": str, \"text\": str}} required")
    if "tools" in pool:
        if not isinstance(pool["tools"], dict) or len(pool["tools"]) > LIMITS["tools"]:
            errs.append(f"tools: at most {LIMITS['tools']}")
        else:
            for k, v in pool["tools"].items():
                if not NAME.match(k):
                    errs.append(f"bad tool name {k!r}")
                elif not isinstance(v, dict) or not isinstance(v.get("doc"), str) or not v["doc"].strip():
                    errs.append(f"tool {k!r}: a \"doc\" string is required")


def validate(pool):
    errs = [f"missing key {k!r}" for k in ("agents", "rules") if k not in pool]
    if errs:
        return errs
    _check_lib(pool, errs)
    if not pool["agents"] or len(pool["agents"]) > LIMITS["agents"]:
        errs.append(f"1..{LIMITS['agents']} task agents required")
    for name, a in pool["agents"].items():
        if not NAME.match(name):
            errs.append(f"bad agent name {name!r}")
        if not isinstance(a, dict) or set(a) != {"role"} or not isinstance(a["role"], str) \
                or not a["role"].strip():
            errs.append(f"{name!r}: {{\"role\": a non-empty string}}")
    if not isinstance(pool["rules"], list) or len(pool["rules"]) > LIMITS["rules"]:
        errs.append(f"rules must be a list of at most {LIMITS['rules']}")
    else:
        for i, r in enumerate(pool["rules"], 1):
            if not isinstance(r, str) or not r.strip():
                errs.append(f"rule {i}: a non-empty string")
    return errs


def apply_ops(pool, ops, layers=("task-agent", "meta-agent", "library"), code_tools=True):
    """Evolver edits. Rule numbers refer to the meta-harness as shown (before this edit); new rules
    are appended. layers: the layers this edit may touch. Skills and tools are added or edited, never
    removed. code_tools: whether tools are Python code the evolver may add or edit.
    Returns (organization, errors, changed tool names)."""
    o = copy.deepcopy(pool)
    errs, changed_tools = [], set()
    if not isinstance(ops, list) or not ops:
        return o, ["ops must be a non-empty list"], changed_tools
    n_rules = len(pool["rules"])
    rules = {i: r for i, r in enumerate(pool["rules"], 1)}
    added = []
    for i, op in enumerate(ops):
        try:
            kind = op["op"]
            layer = ("task-agent" if kind in TASK_OPS else "meta-agent" if kind in META_OPS
                     else "library" if kind in LIB_OPS else None)
            if layer is None:
                raise ValueError(f"unknown op {kind!r}")
            if layer not in layers:
                raise ValueError(f"this edit may change only the {' and '.join(layers)} layer")
            if kind == "add_agent":
                if op["name"] in o["agents"]:
                    raise ValueError(f"agent {op['name']!r} exists")
                o["agents"][op["name"]] = {"role": op["role"]}
            elif kind == "remove_agent":
                del o["agents"][op["name"]]
            elif kind == "edit_agent":
                o["agents"][op["name"]]["role"] = op["role"]
            elif kind == "add_rule":
                added.append(op["text"])
            elif kind in META_OPS:
                k = int(op["rule"])
                if k not in rules:
                    raise ValueError(f"rule {k} does not exist (1..{n_rules}) or was removed")
                if kind == "edit_rule":
                    rules[k] = op["text"]
                else:
                    del rules[k]
            elif kind == "add_skill":
                if op["name"] in o["skills"]:
                    raise ValueError(f"skill {op['name']!r} exists")
                o["skills"][op["name"]] = {"when": op["when"], "text": op["text"]}
            elif kind == "edit_skill":
                sk = o["skills"][op["name"]]
                sk.update({f: op[f] for f in ("when", "text") if f in op})
            else:                                            # tools
                name = op["name"]
                if not code_tools:
                    raise ValueError("the tools of this task are fixed aids")
                if kind == "add_tool":
                    if name in o["tools"]:
                        raise ValueError(f"tool {name!r} exists")
                    if not str(op.get("test", "")).strip():
                        raise ValueError("a new tool needs a test (Python asserts)")
                    o["tools"][name] = {"doc": op["doc"], "code": op["code"], "test": op["test"]}
                    changed_tools.add(name)
                else:
                    t = o["tools"][name]
                    t.update({f: op[f] for f in ("doc", "code", "test") if f in op})
                    if "code" in op or "test" in op:
                        if not str(t.get("test", "")).strip():
                            raise ValueError("an edited tool needs a test (Python asserts)")
                        changed_tools.add(name)
        except (KeyError, TypeError, ValueError, AttributeError) as e:
            errs.append(f"op {i} ({json.dumps(op)[:120]}): {type(e).__name__} {e}")
    o["rules"] = [rules[k] for k in sorted(rules)] + added
    for name in set(pool["agents"]) - set(o["agents"]):
        if any(re.search(rf"\b{re.escape(name)}\b", r) for r in o["rules"]):
            errs.append(f"a rule still mentions removed agent {name!r}")
    return o, errs + validate(o), changed_tools


def minimal_seed(task):
    """The default starting organization: one task agent (the hand seed's first, so that the fixed
    fallback and baselines keep working) with a one-sentence role and no meta-harness rules; the skill
    and tool libraries are the task's hand-written ones (with_libs). Agents, rules and the libraries are
    left to RSI."""
    name = next(iter(task.SEED["agents"]))
    return {"agents": {name: {"role": f"You {task.META['team']}."}}, "rules": []}


def example(task, pool):
    """The team example shown to the meta-agent and the evolver: the task's own if all of its agents exist
    in this organization, else one built from the organization's first agent and library."""
    if all(re.match(r"\s*(?:\w+\s*=\s*)?(\w+)\(", l) is None or re.match(r"\s*(?:\w+\s*=\s*)?(\w+)\(", l).group(1)
           in pool["agents"] for l in task.EXAMPLE if not l.strip().startswith("return")):
        return list(task.EXAMPLE)
    a = next(iter(pool["agents"]))
    t = [x for x in tools_of(task, pool)][:1]
    k = [x for x in skills_of(task, pool)][:1]
    return [f"x = {a}(tools={json.dumps(t)}, skills={json.dumps(k)})", f"y = {a}(x, tools={json.dumps(t)})", "return y"]


def meta_prompt(task, pool):
    m = task.META
    L = [f"You are the meta-agent of a team of task agents that {m['team']}. For each {m['item']} you "
         "build the team and give each task agent its residual harness: tools and skills.", "",
         "Write only a code block (read, not executed):", "```python", *example(task, pool), "```",
         f"- `x = agent(inputs..., tools=[...], skills=[...])` adds a node: {m['node']}",
         f"- Nodes without inputs run in parallel; a node can take only nodes above it. {m['final']}",
         f"- Do not solve the {m['item']}: {m['no_solve']} Only design the team; the task agents do "
         "the work.",
         f"- tools: {m['tools']}. skills: how-to texts.",
         f"- At most {LIMITS['nodes']} nodes, {LIMITS['tools_per_node']} tools and "
         f"{LIMITS['skills_per_node']} skills per node.",
         "- The task agents' roles are general: the same on every " + m['item'] + ". You make each agent "
         "fit this " + m['item'] + " by choosing its tools and skills: give the ones whose description "
         "matches it, not every one that might help.",
         "", "## Task agents"]
    L += [f"- {n}: {a['role']}" for n, a in pool["agents"].items()]
    L += ["", "## Tools"] + [f"- {t}: {v['doc']}" for t, v in tools_of(task, pool).items()]
    L += ["", "## Skills (give one when it fits)"] + [f"- {k}: {v['when']}" for k, v in skills_of(task, pool).items()]
    L += ["", "## Meta-harness"] + [f"{i}. {r}" for i, r in enumerate(pool["rules"], 1)]
    return "\n".join(L)
