# Diagnostic report (dev-A)

Organization: acc 82.7%, cost 5367/question, of which the HR 709 (HR prompt 8301 chars). 22 distinct architectures, 2.3 nodes per question. HR outputs: repaired 0, written again 5, fallback 1.

## By category
| category | n | acc | full acc | cost | full cost | architectures |
|---|---|---|---|---|---|---|
| Algebra L4 | 17 | 100% | - | 2708 | 0 | solver.off[S]>verifier.off[T] 6, solver.off[T][S]>verifier.off[T] 5, coder.off[T][S],solver.off[S]>verifier.off[T] 3 |
| Algebra L5 | 18 | 94% | - | 4316 | 0 | solver.off[T][S]>verifier.off[T] 4, coder.off[T][S],solver.off[S]>verifier.off[T] 4, coder.off[T],solver.off[S]>verifier.off[T] 2 |
| Counting & Probability L4 | 8 | 100% | - | 3929 | 0 | solver.off[S]>verifier.off[T] 4, coder.off[T][S]>verifier.off[T] 2, coder.off[T][S],coder.off[T][S]>verifier.off[T] 1 |
| Counting & Probability L5 | 9 | 67% | - | 6557 | 0 | coder.off[T][S]>verifier.off[T] 3, coder.off[T][S],solver.off>verifier.off[T] 2, coder.off[T][S],solver.off[S] 1 |
| Geometry L4 | 5 | 100% | - | 3000 | 0 | geometer.off[T][S]>verifier.off[T] 2, solver.off[T][S]>verifier.off[T] 1, coder.off[T][S],solver.off[S]>verifier.off[T] 1 |
| Geometry L5 | 7 | 43% | - | 9305 | 0 | geometer.off[T][S]>verifier.off[T] 2, coder.off[T][S],solver.off[S] 1, solver.off[T][S]>verifier.off[T] 1 |
| Intermediate Algebra L4 | 14 | 93% | - | 6002 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T] 4, solver.off[S]>verifier.off[T] 3, solver.off[T][S]>verifier.off[T] 3 |
| Intermediate Algebra L5 | 17 | 59% | - | 7868 | 0 | coder.off[T][S]>verifier.off[T] 5, coder.off[T][S],solver.off[S]>verifier.off[T] 3, solver.off[S]>verifier.off[T] 2 |
| Number Theory L4 | 9 | 100% | - | 4285 | 0 | coder.off[T][S]>verifier.off[T] 6, coder.off[T][S],solver.off[S]>verifier.off[T] 2, solver.off[S]>verifier.off[T] 1 |
| Number Theory L5 | 16 | 88% | - | 5792 | 0 | coder.off[T][S]>verifier.off[T] 7, coder.off[T][S],solver.off[S]>verifier.off[T] 3, solver.off[S]>verifier.off[T] 2 |
| Prealgebra L4 | 12 | 100% | - | 2192 | 0 | coder.off[T][S]>verifier.off[T] 3, solver.off[S]>verifier.off[T] 3, coder.off[T][S],solver.off[S]>verifier.off[T] 1 |
| Prealgebra L5 | 9 | 78% | - | 5959 | 0 | geometer.off[T][S]>verifier.off[T] 3, coder.off[T][S]>verifier.off[T] 3, coder.off[T][S],solver.off[S]>verifier.off[T] 2 |
| Precalculus L4 | 3 | 67% | - | 5678 | 0 | solver.off[S]>verifier.off[T] 1, geometer.off[T][S]>verifier.off[T] 1, coder.off[T][S]>verifier.off[T] 1 |
| Precalculus L5 | 6 | 17% | - | 10787 | 0 | coder.off[T][S]>verifier.off[T] 2, solver.off[T][S],solver.off[T][S]>verifier.off[T] 1, solver.off[S]>verifier.off[T] 1 |

## Architectures the HR wrote
| architecture | uses | acc | mean cost |
|---|---|---|---|
| coder.off[T][S]>verifier.off[T] | 35 | 91% | 5012 |
| coder.off[T][S],solver.off[S]>verifier.off[T] | 26 | 88% | 7020 |
| solver.off[S]>verifier.off[T] | 25 | 96% | 3497 |
| solver.off[T][S]>verifier.off[T] | 16 | 100% | 2764 |
| geometer.off[T][S]>verifier.off[T] | 11 | 45% | 7465 |
| solver.off[S]>verifier.off[T][S] | 8 | 88% | 3776 |
| coder.off[T][S],solver.off[T][S]>verifier.off[T] | 6 | 83% | 6334 |
| coder.off[T],solver.off[T][S]>verifier.off[T] | 3 | 100% | 5106 |
| coder.off[T][S],coder.off[T][S]>verifier.off[T] | 3 | 100% | 4620 |
| coder.off[T][S],solver.off[S] | 2 | 0% | 7972 |
| coder.off[T],solver.off[S]>verifier.off[T] | 2 | 100% | 4643 |
| solver.off[T][S],solver.off[T][S]>verifier.off[T] | 2 | 0% | 9892 |
| coder.off[T][S],solver.off>verifier.off[T] | 2 | 50% | 9058 |
| coder.off[T][S]>verifier.off[T][S] | 1 | 0% | 9275 |
| solver.off[T] | 1 | 0% | 6968 |

## Nodes (employee.thinking)
answer correct = the node's own answer; hit budget = the reasoning was cut at the thinking budget; for nodes with inputs: changed = its answer differs from its inputs' majority.
| node | uses | answer correct | hit budget | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| verifier.off (with inputs) | 144 | 85% | 0% | 1911 | 29 | 8 | 3 |
| solver.off | 100 | 80% | 0% | 1711 | - | - | - |
| coder.off | 85 | 81% | 0% | 2325 | - | - | - |
| geometer.off | 15 | 40% | 0% | 3505 | - | - | - |
| coder.off (with inputs) | 1 | 100% | 0% | 980 | - | - | - |
| solver.off (with inputs) | 1 | 0% | 0% | 1140 | - | - | - |

## Leave-one-out on 60 questions with 2+ nodes
Remove the node (its consumers lose that input; a removed output hands over to its first input) and re-run: 'needed' = right becomes wrong; 'harmful' = wrong becomes right.
| removed | uses | needed | harmful | no effect | mean cost saved |
|---|---|---|---|---|---|
| verifier.off (output) | 59 | 1 | 1 | 57 | 1729 |
| solver.off (input) | 39 | 0 | 0 | 39 | 1437 |
| coder.off (input) | 33 | 1 | 0 | 32 | 1633 |
| geometer.off (input) | 5 | 1 | 0 | 4 | 2691 |

## Residual harness (what the HR gave each node)
| item | nodes given it | node answer correct when given | node answer correct otherwise |
|---|---|---|---|
| note | 342 | 81% | 50% |
| tool:check_answer | 142 | 84% | 78% |
| skill:number_theory_counts | 72 | 85% | 79% |
| tool:python | 71 | 75% | 82% |
| no tools (no Python) | 69 | 83% | 80% |
| tool:exact_solve | 53 | 74% | 82% |
| skill:algebraic_substitution | 50 | 76% | 81% |
| skill:quadratic_methods | 42 | 83% | 80% |
| skill:exact_exponents | 29 | 79% | 80% |
| tool:simplify_exact | 29 | 79% | 80% |
| skill:diagram_geometry | 26 | 54% | 82% |
| tool:number_theory | 24 | 83% | 80% |
| tool:coord_geometry | 9 | 33% | 82% |
| skill:sequence_sums | 9 | 89% | 80% |
| tool:brute_force | 5 | 40% | 81% |
| skill:functional_equation | 3 | 33% | 81% |
| skill:minimal_polynomial | 3 | 100% | 80% |
| skill:roots_of_unity_polygon | 3 | 33% | 81% |
| skill:inverse_functions | 2 | 100% | 80% |
| skill:parity_digit_counting | 2 | 50% | 81% |
Notes: 342 nodes got one, mean 168 chars. Example: Rewrite 16 as 2^4 and 16^(1/8) as 2^(4/8)=2^(1/2), then equate exponents of Q^(3/2) = 2^(1/2) to find Q.

HR output problems: minor: line 2: unknown tools/skills ['number_theory'] dropped (1); minor: line 1: unknown tools/skills ['diagram_geometry'] dropped (1); minor: line 1: unknown tools/skills ['matrix_power_sum'] dropped (1); minor: line 1: unknown tools/skills ['number_theory_counts'] dropped (1); syntax error: invalid syntax (line 1) (1)

## Organization wrong (26)
- [Prealgebra L5] The area of the shaded region is 78 square inches. All angles are right angles and all measurements are given in inches. What is the perimeter of the non-shaded region?

[asy]size(101);
filldraw(((0,0)--(0,8)--(10,8)--(10,-2)--(6,-2)--(6,0)--cycle^^(2.5,3)--(2.5,5)--(7.5,5)--(7.5
  architecture: g = geometer("off", tools=['python', 'coord_geometry'], skills=['diagram_geometry'])  # note: Extract all coordinates from Asymptote: Outer boundary vertices (0,0), (0,8), (1; v = verifier("off", g, tools=['check_answer'])  # note: Re-calculate outer perimeter using distances between consecutive outer vertices.; return v; answered 78, correct 14
- [Intermediate Algebra L5] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver("off", skills=['functional_equation'])  # note: Deduce f(2^n) = n^2 and f(2^k * m) = k^2 + f(m) for odd m. Show f(x) = 0 for all; b = coder("off", tools=['python', 'number_theory'], skills=['number_theory_counts'])  # note: Verify 2002 = 2 * 1001, check 1001 is odd, and confirm the derived formula f(2 *; v = verifier("off", a, b, tools=['check_answer'])  # note: Check if f(1) + f(2^n - 1) = n^2 holds with f(1)=0 and f(2^n-1)=0. Verify f(2) +; return v; answered 2, correct 96
- [Counting & Probability L5] The number of increasing sequences of positive integers $a_1 \le a_2 \le a_3 \le \cdots \le a_{10} \le 2007$ such that $a_i-i$ is even for $1\le i \le 10$ can be expressed as ${m \choose n}$ for some positive integers $m > n$. Compute the remainder when $m$ is divided by 1000.
  architecture: a = solver("off", skills=['exact_exponents', 'sequence_sums'])  # note: Transform $a_i$ by $b_i = (a_i - i)/2$. The condition $a_i \le a_{i+1}$ with par; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute $N$ exactly, calculate the binomial coefficient $\binom{N+9}{9}$, and fi; return b; answered 2, correct 8
- [Prealgebra L5] Triangle $ABC$ is a right triangle. If the measure of angle $PAB$ is $x^\circ$ and the measure of angle $ACB$ is expressed in the form $(Mx+N)^\circ$ with $M=1$, what is the value of $M+N$?

[asy]
draw((-10,0)--(20,0),linewidth(1),Arrows);
draw((0,0)--(10,10/sqrt(3))--(10+10/3,0)
  architecture: a = geometer("off", tools=['exact_solve', 'coord_geometry'], skills=['diagram_geometry', 'exact_exponents'])  # note: Extract coordinates from Asymptote: A=(0,0), B=(10, 10/sqrt(3)), C=(10+10/3, 0).; v = verifier("off", a, tools=['check_answer'])  # note: Verify the calculated angle ACB is exactly 90. Re-calculate angle PAB. Ensure N ; return v; answered 1, correct -89
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver("off", tools=['exact_solve'], skills=['diagram_geometry'])  # note: Let radius be r. Center is (r,r,r). Distances are |x-r|, |y-r|, |z-r|. Point (x,; b = solver("off", tools=['exact_solve'], skills=['diagram_geometry'])  # note: Same setup. Check if the system of equations yields valid geometric configuratio; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify both candidate values of r by substituting back into the sphere equation ; return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = coder("off", tools=['exact_solve', 'brute_force'], skills=['sequence_sums'])  # note: Model the state as a binary string of length 1024. Simulate the process of walki; v = verifier("off", a, tools=['check_answer'], skills=['number_theory_counts'])  # note: Verify the simulation logic by checking a smaller case (e.g., 4 or 8 lockers) ma; return v; answered 4, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver("off", tools=['exact_solve'], skills=['algebraic_substitution'])  # note: Use Vieta's formulas on p(x) to express sum and product of roots r, s, and the t; b = solver("off", tools=['exact_solve'], skills=['algebraic_substitution'])  # note: Apply the same logic to q(x) with roots r+4, s-3, and a third root u. Use the co; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify that the found values of b satisfy the condition that r, s are real by ch; return v; answered 90, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = solver("off", skills=['quadratic_methods', 'diagram_geometry'])  # note: Identify the grid structure formed by the lines. The lines form a triangular lat; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute the exact count using Python to simulate the grid or apply the derived f; return b; answered 10, correct 660
- [Precalculus L5] Three unit circles are drawn so they are mutually tangent, as shown below.  A blue circle that is externally tangent to all three unit circles is drawn.  Finally, three red circles are drawn, so that each red circle is externally tangent to two unit circles and externally tangent
  architecture: a = solver("off", skills=['exact_exponents'])  # note: Use Descartes' Circle Theorem to relate curvatures of the two unit circles, the ; v = verifier("off", a, tools=['check_answer'])  # note: Verify r = (9 - 4*sqrt(3))/33 by substituting into the curvature equation k_red ; return v; answered 33, correct 49
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = solver("off", tools=['python']); return a; answered 2, correct 810

## Most expensive correct questions (possible waste)
- [Geometry L5, cost 12587] The grid below contains the $16$ points whose $x$- and $y$-coordinates are in the set $\{0,1,2,3\}$: [asy]
size(2.5cm);
for(int i=0; i<4; i+=1) { for(int j=0; j<4; j+=1) { dot((i,j
  architecture: a = solver("off", skills=['diagram_geometry'])  # note: Identify all squares by considering the vector (dx, dy) between adjacent vertice; b = coder("off", tools=['exact_solve', 'python'], skills=['number_theory_counts'])  # note: Use python to iterate through all pairs of points in the 4x4 grid, calculate the; v = verifier("off", a, b, tools=['check_answer'])  # note: Re-derive the condition for a square on a grid (area = dx^2 + dy^2). Manually li; return v
- [Intermediate Algebra L4, cost 12193] The equations $x^3 + Ax + 10 = 0$ and $x^3 + Bx^2 + 50 = 0$ have two roots in common.  Then the product of these common roots can be expressed in the form $a \sqrt[b]{c},$ where $a
  architecture: a = solver("off", skills=['algebraic_substitution', 'quadratic_methods'])  # note: Let common roots be u, v. Subtract equations to get B*t^2 - A*t - 40 = 0 with ro; b = coder("off", tools=['python'], skills=['exact_exponents'])  # note: Solve the derived system k*u^3 - 40*u^2 - 30*k = 0 and k*v^3 - 40*v^2 + 50*k = 0; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify that the computed k satisfies the original cubic equations for the corres; return v
- [Algebra L5, cost 10401] What is the sum of all values of $k$ such that the equation $2x^2-kx+8=0$ has two distinct integer solutions?
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Use Vieta's formulas to express sum and product of roots; derive that product 8 ; b = coder("off", tools=['number_theory'], skills=['number_theory_counts'])  # note: Independently list integer factor pairs (d1, d2) of 8, calculate k = d1+d2 for e; v = verifier("off", a, b, tools=['check_answer'])  # note: Check that the sum of k values matches the manual enumeration in notes; ensure n; return v
- [Intermediate Algebra L5, cost 10234] During the car ride home, Michael looks back at his recent math exams. A problem on Michael's calculus mid-term gets him starting thinking about a particular quadratic,\[x^2-sx+p,\
  architecture: a = solver("off", tools=['exact_solve'], skills=['algebraic_substitution', 'quadratic_methods'])  # note: Use $s=r_1+r_2, p=r_1r_2$. Given $S_k = r_1^k+r_2^k$ is constant for $k \ge 1$, ; b = coder("off", tools=['python'])  # note: For valid $(s,p)$, compute max of $1/r_1^{2008} + 1/r_2^{2008} = (r_1^{2008}+r_2; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify the derivation of the recurrence constraint. Check that the computed maxi; return v
- [Counting & Probability L5, cost 9953] My three-digit code is 023. Reckha can't choose a code that is the same as mine in two or more of the three digit-positions, nor that is the same as mine except for switching the p
  architecture: a = solver("off", skills=['algebraic_substitution', 'number_theory_counts'])  # note: Total codes = 1000. Forbidden set S = {023} ∪ {swaps of 023}. Identify unique el; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute |S| using Python set logic to ensure exact count of unique forbidden cod; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify that the count of unique forbidden codes matches the manual deduction of ; return v