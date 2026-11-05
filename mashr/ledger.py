"""Per-stage time and token ledger for experiment runs (uses LLM.usage).

  led = Ledger(llm, log)                      # log: callable(str)
  with led.stage("round 1 / dev-A eval"):
      ...
  led.dump(path)                              # costs.json: one entry per stage + totals

Billed tokens are what the sampler actually processed (cache hits cost nothing). Optional prices via
MASHR_PRICES='{"Qwen/Qwen3.5-9B": [prompt_usd_per_M, gen_usd_per_M], ...}' add a USD estimate.
"""
import json
import os
import time
from contextlib import contextmanager

PRICES = json.loads(os.environ.get("MASHR_PRICES", "{}"))
SHORT = lambda m: m.split("/")[-1]


def delta(a, b):
    out = {}
    for m in set(a) | set(b):
        d = {k: b.get(m, {}).get(k, 0) - a.get(m, {}).get(k, 0)
             for k in ("calls", "cached", "prompt", "gen", "billed_prompt", "billed_gen")}
        if d["calls"]:
            if m in PRICES:
                d["usd"] = round(d["billed_prompt"] / 1e6 * PRICES[m][0]
                                 + d["billed_gen"] / 1e6 * PRICES[m][1], 2)
            out[m] = d
    return out


def describe(d):
    parts = []
    for m, u in sorted(d.items()):
        parts.append(f"{SHORT(m)}: {u['billed_gen'] / 1e6:.2f}M gen + {u['billed_prompt'] / 1e6:.2f}M "
                     f"prompt billed, {u['calls']} calls ({u['cached'] / max(1, u['calls']):.0%} cached)"
                     + (f", ${u['usd']}" if "usd" in u else ""))
    return "; ".join(parts) or "no model calls"


class Ledger:
    def __init__(self, llm, log=print):
        self.llm, self.log, self.rows, self.t0, self.u0 = llm, log, [], time.time(), llm.snapshot()

    @contextmanager
    def stage(self, name):
        t, u = time.time(), self.llm.snapshot()
        try:
            yield
        finally:
            d = delta(u, self.llm.snapshot())
            row = {"stage": name, "seconds": round(time.time() - t, 1), "models": d}
            self.rows.append(row)
            self.log(f"[cost] {name}: {row['seconds'] / 60:.1f} min; {describe(d)}")

    def dump(self, path, quiet=False):
        total = {"seconds": round(time.time() - self.t0, 1),
                 "models": delta(self.u0, self.llm.snapshot())}
        with open(path, "w") as f:
            json.dump({"stages": self.rows, "total": total}, f, indent=1)
        if not quiet:
            self.log(f"[cost] TOTAL: {total['seconds'] / 3600:.2f} h; "
                     f"{describe(total['models'])}")
