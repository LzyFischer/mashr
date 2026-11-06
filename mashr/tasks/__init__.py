"""Tasks (math, bird, alfworld, humaneval_plus, mbpp_plus, hotpotqa, twowiki): each module gives the
tool and skill libraries, the seed organization, baselines, data
splits, what the meta-agent sees, how a node runs (run_node) and the grader."""
import importlib


def get(name):
    return importlib.import_module(f".{name}", __name__)
