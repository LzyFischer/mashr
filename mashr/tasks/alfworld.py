"""Task: ALFWorld (text household tasks, TextWorld engine). One environment per game: only the returned
node acts in it (up to MAX_STEPS actions); the other nodes are advisers that read the task and their
inputs' work and write advice. Tools are aids the acting agent sees at every step. Success = the
game is won. Test = valid_unseen (134 games, the standard out-of-distribution split); dev = train.
Needs the alfworld package and data (ALFWORLD_DATA, default ~/.cache/alfworld)."""
import glob
import json
import os
import random
import re
import threading

NAME = "alfworld"
DATA = os.path.expanduser(os.environ.get("ALFWORLD_DATA", "~/.cache/alfworld"))
MAX_STEPS = 40
MAX_TOKENS = 300          # per acting step
VOTE_ON_MISSING = False
FALLBACK_TOOLS = ("valid_actions",)
TOOLS_ARE_CODE = False   # tools are built-in aids: the evolver may only remove them
TOOL_ENV = ""


def tool_prelude():
    return ""
SPLITS = {"dev_a": 150, "dev_b": 50, "test": 134}
META = {"team": "complete household tasks in a text environment", "item": "task",
        "node": "the agent reads the task, its skills and the full work of its inputs. Only the returned "
                "node acts in the environment; the other nodes write advice for it.",
        "final": "`return x`: x acts in the environment.",
        "no_solve": "write no plan and no actions.",
        "tools": "aids the acting agent sees at every step (no effect on advisers)"}
EXAMPLE = ['p = planner(skills=["heat_task", "search_order"])',
           'a = actor(p, tools=["valid_actions", "memory"], skills=["heat_task"])', "return a"]
SYSTEM_NOTE = (f"The returned node acts in the environment for up to {MAX_STEPS} steps; nodes it takes as "
               "inputs are advisers whose written advice it reads before acting.")

TOOLS = {
    "valid_actions": {"doc": "after every observation, the list of commands that are valid right now."},
    "memory": {"doc": "after every observation, a summary of the places visited so far and what was "
                      "seen in each (closed/empty receptacles included)."},
    "goal_reminder": {"doc": "after every observation, the task again and the number of steps left."},
}

SKILLS = {
    "action_syntax": {
        "when": "any task (exact command forms)",
        "text": "Commands: go to {recep}; open {recep}; close {recep}; take {obj} from {recep}; put "
                "{obj} in/on {recep}; clean {obj} with {sinkbasin}; heat {obj} with {microwave}; cool "
                "{obj} with {fridge}; use {lamp}; examine {obj or recep}; inventory; look. Use the exact "
                "names with numbers as they appear ('mug 1', 'countertop 2'). You can hold one object; "
                "you must be at a receptacle to take from or put on it. 'Nothing happens' means the "
                "command was invalid: change it.",
    },
    "search_order": {
        "when": "the target object is not in view (most tasks)",
        "text": "Search likely places first and never revisit a place you have checked. Typical: food "
                "(apple, potato, tomato, egg, lettuce, bread) -> fridge, countertop, diningtable, "
                "sinkbasin, garbagecan; dishes (mug, cup, plate, bowl, pan, pot) -> countertop, "
                "cabinet, diningtable, sinkbasin, shelf, drawer; small items (keychain, creditcard, "
                "pen, pencil, cd, cellphone) -> desk, drawer, sidetable, dresser, shelf; towels/soap -> "
                "towelholder, countertop, toilet, cabinet; books/laptops -> desk, bed, sofa, "
                "sidetable. Open closed cabinets, drawers, fridges and safes to see inside.",
    },
    "pick_place": {
        "when": "put an object in/on a receptacle",
        "text": "1. Find the object (search_order), take it. 2. Go to the target receptacle; open it if "
                "closed. 3. put {obj} in/on {recep}. The task is done when the object is placed. "
                "Pitfall: placing a similar but different object type (a cup is not a mug).",
    },
    "pick_two": {
        "when": "put two objects of a type in/on a receptacle",
        "text": "1. Find the first object, take it, put it in/on the target. 2. Go back to searching "
                "for the second one (it may be elsewhere; remember where you saw others). 3. Put the "
                "second in/on the same target. You can carry only one object at a time.",
    },
    "clean_task": {
        "when": "put a clean object somewhere",
        "text": "1. Find and take the object. 2. go to sinkbasin 1 (or the sinkbasin), then 'clean "
                "{obj} with sinkbasin 1'. 3. Go to the target, open it if needed, put the object. Do "
                "not put the object in the sink to clean it; use the clean command.",
    },
    "heat_task": {
        "when": "put a hot or heated object somewhere",
        "text": "1. Find and take the object. 2. go to microwave 1, then 'heat {obj} with microwave 1' "
                "(no need to open it or put the object inside). 3. Go to the target, open it if needed, "
                "put the object.",
    },
    "cool_task": {
        "when": "put a cool or cold object somewhere",
        "text": "1. Find and take the object. 2. go to fridge 1, then 'cool {obj} with fridge 1' (no "
                "need to put it inside). 3. Go to the target, open it if needed, put the object. If the "
                "target is the fridge itself this is a plain placement.",
    },
    "look_in_light": {
        "when": "examine or look at an object with/under a lamp",
        "text": "1. Find and take the object. 2. Find a desklamp or floorlamp (often on a desk, "
                "sidetable or dresser). 3. Go to the lamp while holding the object and 'use {lamp}'. "
                "Using the lamp while holding the object completes the task.",
    },
    "stuck_recovery": {
        "when": "long or tricky tasks",
        "text": "If an action fails twice or you are repeating yourself: stop, check what you hold "
                "(inventory), list unvisited places, and pick a different command. Do not repeat the "
                "same failing command. Prefer going to a new place over examining.",
    },
}

SEED = {
    "agents": {
        "actor": {"role": "You act in a household text environment to complete the task. Each turn, "
                          "write one short line 'Think: ...' and then 'Action: <one command>'."},
        "planner": {"role": "You read the task and the room, and write a short plan for the teammate "
                            "who will act: where to look first and the steps to finish. You do not act."},
    },
    "rules": [
        "Every task: an actor with valid_actions.",
        "Tasks with two objects or with cleaning, heating or cooling: a planner, then the actor reading "
        "its plan.",
        "Give the skill for the task type.",
    ],
}

BASELINES = {
    "react": 'a = actor(tools=["valid_actions"])\nreturn a',
    "react_no_tools": "a = actor()\nreturn a",
    "plan_act": 'p = planner()\na = actor(p, tools=["valid_actions"])\nreturn a',
}

TASK_TYPES = ["pick_and_place_simple", "pick_two_obj_and_place", "look_at_obj_in_light",
              "pick_clean_then_place_in_recep", "pick_heat_then_place_in_recep",
              "pick_cool_then_place_in_recep"]
HARD = {"pick_two_obj_and_place", "pick_clean_then_place_in_recep", "pick_heat_then_place_in_recep",
        "pick_cool_then_place_in_recep"}


def _games(split_dir):
    out = []
    for g in sorted(glob.glob(os.path.join(DATA, "json_2.1.1", split_dir, "*", "*", "game.tw-pddl"))):
        if "movable" in g or "Sliced" in g:
            continue
        with open(g) as f:
            if json.load(f).get("solvable"):
                out.append(g)
    return out


def load(split, n=None):
    if split == "test":
        games = _games("valid_unseen")
    else:
        games = _games("train")
        random.Random(0).shuffle(games)
        a, b = SPLITS["dev_a"], SPLITS["dev_b"]
        games = games[:a] if split == "dev_a" else games[a:a + b]
    out = []
    for g in games:
        t = os.path.basename(os.path.dirname(os.path.dirname(g))).split("-")[0]
        out.append({"id": "alfworld/" + os.path.relpath(g, DATA), "game": g, "bucket": t,
                    "hard": t in HARD, "gold": True})
    return out[:n] if n else out


_lock = threading.RLock()     # TextWorld's PDDL parsing (tatsu) is not thread-safe: one env op at a time
_first = {}


_libs = []                    # fast-downward library instances free for reuse
_lib_stats = {"loaded": 0}
MAX_LIVE_ENVS = 96            # at most this many library copies (35 MB of disk each) exist at once
_live = threading.BoundedSemaphore(MAX_LIVE_ENVS)


def _pool_libs():
    """textworld's PddlEnv copies the 35 MB libdownward.so to a temp dir and loads it for every new
    environment; the deleted copies stay mapped, so disk fills up over a run. Reuse instances: one
    per live environment, returned on close (each reset reloads the game into its library)."""
    from textworld.envs.pddl import pddl
    if getattr(pddl.PddlEnv, "_pooled", False):
        return
    load, close = pddl.fast_downward.load_lib, pddl.PddlEnv.close

    def init(self, infos=None):
        pddl.textworld.core.Environment.__init__(self, infos)
        with _lock:
            if _libs:
                self.downward_lib = _libs.pop()
            else:
                self.downward_lib = load()
                _lib_stats["loaded"] += 1

    def close_(self):
        close(self)
        lib = self.__dict__.pop("downward_lib", None)
        if lib is not None:
            with _lock:
                _libs.append(lib)
            _live.release()
    pddl.PddlEnv.__init__, pddl.PddlEnv.close, pddl.PddlEnv._pooled = init, close_, True


def _env(game):
    import textworld
    import textworld.gym
    from alfworld.agents.environment.alfred_tw_env import AlfredDemangler, AlfredInfos
    _pool_libs()
    infos = textworld.EnvInfos(won=True, admissible_commands=True, extras=["gamefile"])
    with _lock:
        eid = textworld.gym.register_games([game], infos, batch_size=1, asynchronous=False,
                                           max_episode_steps=MAX_STEPS + 5,
                                           wrappers=[AlfredDemangler(), AlfredInfos])
        return textworld.gym.make(eid)


def _start(item):
    _live.acquire()               # released when the environment is closed (PddlEnv.close)
    with _lock:
        env = _env(item["game"])
        obs, info = env.reset()
    text = obs[0].replace("-= Welcome to TextWorld, ALFRED! =-", "").strip()
    _first[item["id"]] = text
    return env, text, info


def first_obs(item):
    if item["id"] not in _first:
        env, text, _ = _start(item)
        with _lock:
            env.close()
    return _first[item["id"]]


def meta_view(item):
    return first_obs(item)


def grade(pred, item):
    return pred is True


class Memory:
    """Places visited and what was seen there, parsed from observations."""
    def __init__(self):
        self.seen = {}

    def update(self, obs):
        m = re.match(r"You arrive at (.+?)\. (.*)", obs)
        place = m.group(1).strip() if m else None
        rest = m.group(2) if m else obs
        m2 = re.search(r"(?:On|In) (?:the|it,) ?(.*?)you see (.+?)\.", rest)
        if place and "is closed" in rest:
            self.seen[place] = "closed"
        elif place and m2:
            self.seen[place] = m2.group(2)
        m3 = re.match(r"You open the (.+?)\. The .+? is open\. In it, you see (.+?)\.", obs)
        if m3:
            self.seen[m3.group(1)] = m3.group(2)

    def text(self):
        return "; ".join(f"{k}: {v}" for k, v in self.seen.items()) or "nothing yet"


def _aids(tools, info, memory, goal, step):
    out = []
    if "goal_reminder" in tools:
        out.append(f"Task: {goal} ({MAX_STEPS - step} steps left)")
    if "memory" in tools:
        out.append(f"Seen so far: {memory.text()}")
    if "valid_actions" in tools:
        out.append("Valid actions: " + ", ".join(info["admissible_commands"][0]))
    return "\n".join(out)


def _system(pool, node):
    system = pool["agents"][node["agent"]]["role"]
    if node["skills"]:
        S = pool.get("skills", SKILLS)
        system += "\n\nSkills to apply:\n" + "\n".join(f"- {k}: {S[k]['text']}" for k in node["skills"])
    return system


def run_node(eng, pool, node, item, work, is_output):
    system = _system(pool, node)
    if not is_output:                                  # an adviser writes advice once
        user = f"{first_obs(item)}"
        if work:
            user += f"\n\nWork from your teammates:\n{work}"
        user += "\n\nWrite concise advice for the teammate who will act. Do not act yourself."
        r = eng.chat([{"role": "system", "content": system}, {"role": "user", "content": user}], 1024)
        return {"text": r.text, "answer": None, "cut": False,
                "calls": [{"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
                           "gen_tokens": r.gen_tokens}]}
    env, obs, info = _start(item)
    goal = obs.split("Your task is to:")[-1].strip()
    memory = Memory()
    memory.update(obs)
    user = obs + (f"\n\nAdvice from your teammates:\n{work}" if work else "")
    aids = _aids(node["tools"], info, memory, goal, 0)
    history, calls, won, trace = [], [], False, [obs]
    try:
        for step in range(MAX_STEPS):
            msgs = [{"role": "system", "content": system + "\n\nEach turn, end with one line 'Action: <command>'."},
                    {"role": "user", "content": user + (f"\n\n{aids}" if not history and aids else "")}]
            for i, (said, seen) in enumerate(history):
                last = i == len(history) - 1
                msgs += [{"role": "assistant", "content": said},
                         {"role": "user", "content": f"Observation: {seen}" + (f"\n{aids}" if last and aids else "")}]
            r = eng.chat(msgs, MAX_TOKENS)
            calls.append({"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
                          "gen_tokens": r.gen_tokens})
            acts = re.findall(r"Action:\s*(.+)", r.text)
            action = (acts[-1] if acts else (r.text.strip().splitlines() or ["look"])[-1]).strip().strip("`'\". ")
            with _lock:
                obs_, _, done, info = env.step([action])
            seen = obs_[0].strip()
            memory.update(seen)
            history.append((r.text.strip(), seen))
            trace.append(f"> {action}\n{seen}")
            if info["won"][0]:
                won = True
                break
            aids = _aids(node["tools"], info, memory, goal, step + 1)
    finally:
        with _lock:
            env.close()
    return {"text": "\n".join(trace), "answer": won, "calls": calls,
            "cut": not won and len(history) >= MAX_STEPS}
