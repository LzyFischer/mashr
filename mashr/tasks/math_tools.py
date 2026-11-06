"""Tool library (hand-written, fixed). A tool is Python code preloaded into the sandbox of
an agent that is given it, plus a one-line doc shown to that agent and to the HR. Every tool carries a
test that must pass in the sandbox before it can be used. Any tool implies Python access; "python" is
plain Python (numpy, sympy) with nothing preloaded.
"""
TOOLS = {
    "python": {
        "doc": "Run Python (numpy, sympy available) to compute or check anything.",
        "code": "",
        "test": "assert 2 + 2 == 4",
    },
    "exact_solve": {
        "doc": "exact_solve(equations, unknowns) -> list of exact solutions. Equations are strings "
               "like 'x + 2*y = 7'; unknowns a string like 'x y'.",
        "code": '''
def exact_solve(equations, unknowns):
    import sympy as sp
    syms = sp.symbols(unknowns)
    syms = list(syms) if isinstance(syms, (tuple, list)) else [syms]
    loc = {str(s): s for s in syms}
    eqs = []
    for e in ([equations] if isinstance(equations, str) else equations):
        if "=" in e and "==" not in e:
            l, r = e.split("=", 1)
            eqs.append(sp.Eq(sp.sympify(l, locals=loc), sp.sympify(r, locals=loc)))
        else:
            eqs.append(sp.sympify(e.replace("==", "-(") + (")" if "==" in e else ""), locals=loc))
    return sp.solve(eqs, syms, dict=True)
''',
        "test": "s = exact_solve(['x + y = 5', 'x - y = 1'], 'x y'); assert s == [{__import__('sympy').Symbol('x'): 3, __import__('sympy').Symbol('y'): 2}], s",
    },
    "brute_force": {
        "doc": "brute_force(predicate, *ranges) -> count of tuples in the product of the ranges for "
               "which predicate(*t) is true; brute_list(...) returns them (first 50).",
        "code": '''
def brute_force(predicate, *ranges):
    import itertools
    return sum(1 for t in itertools.product(*ranges) if predicate(*t))

def brute_list(predicate, *ranges, limit=50):
    import itertools
    out = []
    for t in itertools.product(*ranges):
        if predicate(*t):
            out.append(t)
            if len(out) >= limit:
                break
    return out
''',
        "test": "assert brute_force(lambda a, b: a + b == 4, range(5), range(5)) == 5; assert brute_list(lambda a: a % 2 == 0, range(5)) == [(0,), (2,), (4,)]",
    },
    "check_answer": {
        "doc": "check_answer(conditions, **values) -> {condition: True/False}. Conditions are strings "
               "such as 'a + b == 10', 'a > 0', 'a**2 - 3*a + 2 == 0' evaluated exactly at the values.",
        "code": '''
def check_answer(conditions, **values):
    import sympy as sp
    loc = {k: sp.nsimplify(v) if isinstance(v, float) else sp.sympify(v) for k, v in values.items()}
    out = {}
    for c in ([conditions] if isinstance(conditions, str) else conditions):
        try:
            for op in ("==", ">=", "<=", "!=", ">", "<"):
                if op in c:
                    l, r = c.split(op, 1)
                    lv = sp.simplify(sp.sympify(l, locals=loc))
                    rv = sp.simplify(sp.sympify(r, locals=loc))
                    out[c] = bool({"==": sp.simplify(lv - rv) == 0, ">=": lv >= rv,
                                   "<=": lv <= rv, "!=": sp.simplify(lv - rv) != 0,
                                   ">": lv > rv, "<": lv < rv}[op])
                    break
            else:
                out[c] = bool(sp.sympify(c, locals=loc))
        except Exception as e:
            out[c] = f"error: {e}"
    return out
''',
        "test": "r = check_answer(['a + b == 10', 'a > b', 'a*b == 21'], a=7, b=3); assert r == {'a + b == 10': True, 'a > b': True, 'a*b == 21': True}, r",
    },
    "simplify_exact": {
        "doc": "simplify_exact(expr) -> (simplest exact form as a string, LaTeX, float value). Use it to "
               "put a final answer in exact simplest form.",
        "code": '''
def simplify_exact(expr):
    import sympy as sp
    e = sp.nsimplify(sp.sympify(expr), [sp.pi, sp.E], rational=False) if isinstance(expr, (int, float)) \\
        else sp.simplify(sp.sympify(expr))
    return str(e), sp.latex(e), float(sp.N(e))
''',
        "test": "s, l, v = simplify_exact('sqrt(8) + 2/4'); assert s in ('1/2 + 2*sqrt(2)', '2*sqrt(2) + 1/2'), s; assert abs(v - 3.3284) < 1e-3",
    },
    "number_theory": {
        "doc": "factorint(n), divisors(n), totient(n), isprime(n), mod_inverse(a, m), crt(moduli, "
               "residues) -> (x, M), digit_sum(n, base=10): exact number-theory helpers (sympy).",
        "code": '''
from sympy import factorint, divisors, totient, isprime, mod_inverse
from sympy.ntheory.modular import crt

def digit_sum(n, base=10):
    n, s = abs(int(n)), 0
    while n:
        s, n = s + n % base, n // base
    return s
''',
        "test": "assert factorint(360) == {2: 3, 3: 2, 5: 1}; assert len(divisors(36)) == 9; assert crt([3, 5], [2, 3])[0] == 8; assert digit_sum(1234) == 10; assert mod_inverse(3, 7) == 5",
    },
    "coord_geometry": {
        "doc": "dist(p, q), shoelace_area(points), line_intersection(p1, p2, q1, q2), "
               "angle_deg(a, b, c) (angle at b): exact coordinate-geometry helpers (sympy).",
        "code": '''
def dist(p, q):
    import sympy as sp
    return sp.sqrt(sum((sp.nsimplify(a) - sp.nsimplify(b)) ** 2 for a, b in zip(p, q)))

def shoelace_area(points):
    import sympy as sp
    pts = [(sp.nsimplify(x), sp.nsimplify(y)) for x, y in points]
    s = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
            for i in range(len(pts)))
    return sp.Abs(s) / 2

def line_intersection(p1, p2, q1, q2):
    import sympy as sp
    return sp.Line(sp.Point(*p1), sp.Point(*p2)).intersection(sp.Line(sp.Point(*q1), sp.Point(*q2)))

def angle_deg(a, b, c):
    import sympy as sp
    v1 = sp.Matrix([sp.nsimplify(a[0]) - b[0], sp.nsimplify(a[1]) - b[1]])
    v2 = sp.Matrix([sp.nsimplify(c[0]) - b[0], sp.nsimplify(c[1]) - b[1]])
    return sp.simplify(sp.acos(v1.dot(v2) / (v1.norm() * v2.norm())) * 180 / sp.pi)
''',
        "test": "assert dist((0, 0), (3, 4)) == 5; assert shoelace_area([(0, 0), (4, 0), (0, 3)]) == 6; assert angle_deg((1, 0), (0, 0), (0, 1)) == 90",
    },
    "counting": {
        "doc": "comb(n, k), perm(n, k), multinomial(*ks), count_if(predicate, iterable), "
               "inclusion_exclusion(sizes_by_level) -> exact counts (sizes_by_level[i] = sum of the "
               "sizes of all (i+1)-wise intersections).",
        "code": '''
from math import comb, perm, factorial

def multinomial(*ks):
    out = factorial(sum(ks))
    for k in ks:
        out //= factorial(k)
    return out

def count_if(predicate, iterable):
    return sum(1 for x in iterable if predicate(x))

def inclusion_exclusion(sizes_by_level):
    return sum((-1) ** i * s for i, s in enumerate(sizes_by_level))
''',
        "test": "assert comb(5, 2) == 10 and perm(5, 2) == 20 and multinomial(2, 1, 1) == 12; assert count_if(lambda x: x % 3 == 0, range(1, 31)) == 10; assert inclusion_exclusion([50 + 33, 16]) == 67",
    },
    "polynomial": {
        "doc": "poly_roots(expr, x='x') -> exact roots with multiplicity, vieta(expr, x='x') -> "
               "elementary symmetric sums of the roots, expand(expr), factor(expr) (strings in, sympy out).",
        "code": '''
def poly_roots(expr, x="x"):
    import sympy as sp
    return sp.roots(sp.Poly(sp.sympify(expr), sp.Symbol(x)))

def vieta(expr, x="x"):
    import sympy as sp
    c = sp.Poly(sp.sympify(expr), sp.Symbol(x)).all_coeffs()
    return [sp.Rational((-1) ** (i + 1)) * c[i + 1] / c[0] for i in range(len(c) - 1)]

def expand(expr):
    import sympy as sp
    return sp.expand(sp.sympify(expr))

def factor(expr):
    import sympy as sp
    return sp.factor(sp.sympify(expr))
''',
        "test": "r = poly_roots('x**2 - 5*x + 6'); assert r == {2: 1, 3: 1}, r; assert vieta('2*x**2 - 6*x + 4') == [3, 2]; assert str(factor('x**2 - 1')) == '(x - 1)*(x + 1)'",
    },
    "sequence": {
        "doc": "terms(f, n, start=1) -> [f(start), ..., ] (n terms), recurrence(rule, init, n) -> first "
               "n terms where rule(prev_terms_list) gives the next, partial_sums(xs).",
        "code": '''
def terms(f, n, start=1):
    return [f(i) for i in range(start, start + n)]

def recurrence(rule, init, n):
    xs = list(init)
    while len(xs) < n:
        xs.append(rule(xs))
    return xs[:n]

def partial_sums(xs):
    out, s = [], 0
    for x in xs:
        s += x
        out.append(s)
    return out
''',
        "test": "assert terms(lambda i: i * i, 3) == [1, 4, 9]; assert recurrence(lambda xs: xs[-1] + xs[-2], [1, 1], 6) == [1, 1, 2, 3, 5, 8]; assert partial_sums([1, 2, 3]) == [1, 3, 6]",
    },
}


def tool_code(ids, tools=None):
    """Source preloaded for a node given these tools (tools: the organization's library)."""
    tools = tools or TOOLS
    return "\n".join(tools[t].get("code", "") for t in ids if tools[t].get("code", "").strip())


def test_tools(run_python, tools=None):
    """{tool: (ok, output)} running each tool's test in the sandbox."""
    tools = tools or TOOLS
    out = {}
    for name, t in tools.items():
        res, ok = run_python(t["code"] + "\n" + t["test"] + "\nprint('TEST OK')")
        out[name] = (ok and "TEST OK" in res, res[-300:])
    return out
