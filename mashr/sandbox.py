"""Model-written Python runs in a separate interpreter without network (unshare -rn when available),
with memory, CPU-time and file-size limits, in a temporary directory."""
import os
import re
import shutil
import subprocess
import tempfile
import threading

PY = os.environ.get("MASHR_PY", "/usr/bin/python3")   # needs numpy/sympy; the tinker env has none
CODE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.S)
_ISOLATE = (["unshare", "-rn"] if shutil.which("unshare") and subprocess.run(
    ["unshare", "-rn", "true"], capture_output=True).returncode == 0 else [])
_py_cache: dict = {}
_py_lock = threading.Lock()


def run_python(code: str, timeout: int = 10) -> tuple[str, bool]:
    """Run code; returns (stdout tail plus error, ok). Results are memoized per code string."""
    with _py_lock:
        if code in _py_cache:
            return _py_cache[code]
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "main.py")
        with open(path, "w") as f:
            f.write(code)
        cmd = ["prlimit", "--as=2000000000", f"--cpu={timeout}", "--fsize=10000000", "--",
               *_ISOLATE, PY, "-I", path]
        try:
            r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=timeout + 5,
                               env={"PATH": "/usr/bin:/bin", "HOME": d})
            out, err, ok = r.stdout, r.stderr, r.returncode == 0
        except subprocess.TimeoutExpired:
            out, err, ok = "", "timed out", False
    text = out[-1500:].strip()
    if not ok:
        text += "\n[error] " + err.strip()[-800:]
    res = (text.strip() or "(no output)", ok)
    with _py_lock:
        _py_cache[code] = res
    return res
