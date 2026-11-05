"""Skill library (hand-written for MATH level 4-5, fixed). Each skill has a one-line `when` (shown to
the meta-agent) and a procedure `text` (given to the task agent that receives the skill): steps,
the pitfalls that cause wrong answers, and a final check."""
SKILLS = {
    "counting_setup": {
        "when": "any counting problem (arrangements, selections, paths, distributions)",
        "text": "1. Decide what one object is and when two objects count as the same: are the items "
                "distinguishable, does order matter, are rotations/reflections identified, may boxes be "
                "empty? Write these answers down first. 2. Choose one method: direct product rule, "
                "combinations, stars and bars (k identical into n distinct: C(k+n-1, n-1)), or casework. "
                "3. Pitfalls: counting ordered pairs when unordered are asked (divide by symmetry only if "
                "every object has the same number of copies), forgetting the empty/zero case, double "
                "counting when cases overlap. 4. Check: recount a smaller version of the problem by "
                "listing all objects (or with python/brute_force) and compare.",
    },
    "complement_and_pie": {
        "when": "'at least one', 'not all', 'no two adjacent', or overlapping conditions",
        "text": "1. Complement: count everything, subtract what violates the condition; both counts must "
                "use the same notion of distinct. 2. Inclusion-exclusion for sets A1..Ak: sum |Ai| - "
                "sum |Ai and Aj| + sum |Ai and Aj and Al| - ...; write each intersection size as a formula. "
                "3. For 'no two adjacent' among n in a row choose k: C(n-k+1, k); in a circle use cases on "
                "whether the first item is chosen. 4. Check with a small n by enumeration.",
    },
    "probability": {
        "when": "probability or expected value",
        "text": "1. Fix the sample space and make sure its outcomes are equally likely (use ordered "
                "outcomes for dice/cards drawn in sequence). 2. P = favorable / total with both counted "
                "in the same space; or multiply conditional probabilities along a sequence. 3. Expected "
                "value: use linearity, E[sum] = sum of E[indicator]; no independence needed. 4. Geometric "
                "probability: ratio of lengths/areas of the valid region. 5. Pitfalls: with/without "
                "replacement, 'at least' vs 'exactly', unreduced fractions. Give m/n in lowest terms if "
                "asked for m+n.",
    },
    "modular": {
        "when": "remainders, last digits, divisibility, units digit of powers",
        "text": "1. Reduce every number mod m at each step. 2. Powers: find the cycle of a^k mod m by "
                "listing a^1, a^2, ... until it repeats; then reduce the exponent mod the cycle length "
                "(careful when the remainder is 0: use the cycle length itself). Euler: a^phi(m) = 1 mod m "
                "if gcd(a, m) = 1. 3. Several moduli: solve each, combine with the Chinese remainder "
                "theorem (tool: number_theory crt). 4. Division mod m needs an inverse; it exists only if "
                "gcd = 1. 5. Check: verify the final residue with python pow(a, k, m).",
    },
    "divisors_primes": {
        "when": "number or sum of divisors, gcd/lcm, prime factorization, perfect squares/cubes",
        "text": "1. Factor n = p1^a1 ... pk^ak first (tool: number_theory factorint). 2. Number of "
                "divisors (a1+1)...(ak+1); sum of divisors prod (p^(a+1)-1)/(p-1); n is a perfect square "
                "iff all exponents are even. 3. gcd takes the minimum exponents, lcm the maximum; gcd * lcm "
                "= a * b. 4. Pitfalls: 1 and n are divisors; 'proper' divisors exclude n; 'positive' vs "
                "all integer divisors (x2). 5. Check small cases by listing divisors.",
    },
    "integer_equations": {
        "when": "equations or conditions in integers (Diophantine, digits, bases, floor)",
        "text": "1. Bound the variables first (sizes, signs, digit ranges 0-9, leading digit not 0). "
                "2. Factor: rewrite as (ax+b)(cy+d) = N (Simon's trick) and run over divisor pairs of N, "
                "including negative pairs if negatives are allowed. 3. Use parity or a modulus to cut "
                "cases. 4. Base b: digits are 0..b-1, value = sum d_i b^i. Floor: write x = n + f with "
                "0 <= f < 1. 5. Check every candidate in the original equation; once bounded, an "
                "exhaustive search with python/brute_force settles it.",
    },
    "polynomials_vieta": {
        "when": "roots and coefficients of polynomials, symmetric expressions of roots, remainders",
        "text": "1. Do not solve for the roots if a symmetric expression is asked: for a x^n + b x^(n-1) "
                "+ c x^(n-2) + ...: sum of roots -b/a, sum of pairwise products c/a, product (-1)^n * "
                "constant/a. 2. Power sums: r1^2 + r2^2 = (sum)^2 - 2 (pairwise). 3. Remainder of P(x) "
                "divided by (x - a) is P(a); for a quadratic divisor, evaluate at both roots. 4. Rational "
                "roots are p/q with p | constant, q | leading coefficient. 5. Pitfalls: multiplicity, "
                "complex roots, the sign of (-1)^n. Check with tool polynomial (poly_roots, vieta).",
    },
    "algebra_manipulation": {
        "when": "simplifying expressions, systems of equations, substitutions, x + 1/x type identities",
        "text": "1. Name the target expression and look for a substitution that produces it (e.g. t = x "
                "+ 1/x gives x^2 + 1/x^2 = t^2 - 2, x^3 + 1/x^3 = t^3 - 3t). 2. Systems: add/subtract "
                "equations to get symmetric sums; for xyz-type products multiply all equations. 3. "
                "Rationalize denominators with conjugates. 4. Pitfalls: dividing by an expression that "
                "can be 0, squaring both sides (creates extraneous roots), domain of sqrt and log. 5. "
                "Check: substitute the result back into every original equation (tool: check_answer).",
    },
    "functions_sequences": {
        "when": "functional equations, function iteration or inverses, arithmetic/geometric sequences, recursions",
        "text": "1. Functional equations: plug in special values (0, 1, -1, x = y) and solve for f at the "
                "needed points. 2. Iteration f(f(x)): compute the first values and look for a cycle. "
                "3. Sequences: arithmetic a_n = a_1 + (n-1)d, sum n(a_1 + a_n)/2; geometric a_1 r^(n-1), "
                "sum a_1 (1 - r^n)/(1 - r). 4. Recursions: list the first 10-15 terms (tool: sequence), "
                "find the period or closed form, then prove or recheck it. 5. Pitfalls: off-by-one in the "
                "index, whether the sum starts at n = 0 or 1.",
    },
    "inequalities_extrema": {
        "when": "maximum or minimum, inequalities, optimization",
        "text": "1. Find the candidate extremum: AM-GM (equality when the terms are equal), completing the "
                "square, Cauchy-Schwarz, or calculus (derivative 0, plus endpoints). 2. Show it is "
                "attained: give the values of the variables where equality holds and check they satisfy "
                "all constraints (integer, positive, distinct...). 3. For integer variables test the "
                "integers next to the real optimum. 4. Pitfall: a bound that cannot be attained is not "
                "the answer. 5. Check numerically by evaluating many points (python).",
    },
    "geometry_coordinates": {
        "when": "geometry with a diagram (Asymptote code), lengths, areas, intersections",
        "text": "1. If Asymptote code is given, read the exact coordinates of every labeled point from it; "
                "they define the figure. 2. Otherwise place the figure: a vertex at the origin, a side on "
                "the x-axis, use symmetry. 3. Compute exactly: lengths by distance, areas by the "
                "shoelace formula, intersections by solving line equations (tool: coord_geometry). 4. "
                "Identify exactly which region or segment is asked (shaded part, quadrilateral DBEF...). "
                "5. Pitfalls: unit vs scaled diagram, degrees vs radians, an area that must be "
                "subtracted. Check one known length or area from the problem against your coordinates.",
    },
    "geometry_synthetic": {
        "when": "triangles, circles, similar figures, angle chasing, area ratios",
        "text": "1. Mark all given equal lengths and angles; angle chase with the triangle sum, parallel "
                "lines, inscribed angle = half the central angle. 2. Similar triangles give length "
                "ratios; areas scale with the square. Triangles with the same height: area ratio = base "
                "ratio. 3. Useful facts: Pythagoras and common triples, angle bisector theorem, power of "
                "a point, tangent lengths from a point are equal, Heron's formula, area = (1/2)ab sin C. "
                "4. Pitfalls: assuming a figure is to scale; a ratio of the wrong pieces. 5. Check with "
                "coordinates when the configuration is simple.",
    },
    "trig_complex": {
        "when": "trigonometry, complex numbers, vectors, matrices (precalculus)",
        "text": "1. Trig: reduce angles to [0, 360) degrees and use the quadrant for the sign; identities "
                "sin^2 + cos^2 = 1, double angle, sum-to-product; exact values of 30/45/60 multiples. 2. "
                "Complex: polar form r(cos t + i sin t), De Moivre for powers, roots of unity sum to 0. 3. "
                "Vectors: dot product for angles and projections, cross product/determinant for areas. 4. "
                "Matrices: determinant, inverse, powers via a pattern or eigenvalues. 5. Pitfalls: "
                "degrees vs radians, all solutions in a given interval. Check numerically with python.",
    },
    "check_answer_form": {
        "when": "before the final answer of any problem",
        "text": "1. Re-read the question: which quantity is asked (sum of all solutions, the number of "
                "solutions, the largest value, m+n of a fraction m/n, the remainder...)? 2. Make sure "
                "every condition is used and every candidate satisfies all of them; discard extraneous "
                "roots. 3. Units and rates: chain the given ratios so the units cancel and end in the unit "
                "asked. 4. Give the answer as the integer the problem asks for. 5. If a quick "
                "independent check is possible (plug in, small case, python), do it.",
    },
}
