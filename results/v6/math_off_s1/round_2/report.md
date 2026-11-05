# Diagnostic report (dev-A)

Organization: acc 86.0%, cost 5090/question, of which the HR 674 (HR prompt 5983 chars). 22 distinct architectures, 2.2 nodes per question. HR outputs: repaired 0, written again 4, fallback 0.

## By category
| category | n | acc | full acc | cost | full cost | architectures |
|---|---|---|---|---|---|---|
| Algebra L4 | 17 | 100% | - | 2861 | 0 | solver.off>verifier.off[T] 5, solver.off[T][S]>verifier.off[T] 5, solver.off[S]>verifier.off[T] 4 |
| Algebra L5 | 18 | 94% | - | 4633 | 0 | solver.off[T][S]>verifier.off[T] 6, solver.off[S]>verifier.off[T] 3, coder.off[T][S],solver.off>verifier.off[T] 2 |
| Counting & Probability L4 | 8 | 88% | - | 3404 | 0 | counter.off[T][S]>verifier.off[T] 4, solver.off[T][S]>verifier.off[T] 2, counter.off[T][S],solver.off[T][S] 1 |
| Counting & Probability L5 | 9 | 78% | - | 5855 | 0 | counter.off[T][S]>verifier.off[T] 7, solver.off[T][S]>verifier.off[T] 1, counter.off[T][S] 1 |
| Geometry L4 | 5 | 100% | - | 4118 | 0 | solver.off>verifier.off[T] 2, coder.off[T],solver.off[T][S]>verifier.off[T] 1, coder.off,solver.off>verifier.off[T] 1 |
| Geometry L5 | 7 | 57% | - | 10704 | 0 | coder.off[T][S],solver.off[T][S]>verifier.off[T] 4, counter.off[T][S]>verifier.off[T] 1, coder.off[T],solver.off[T]>verifier.off[T] 1 |
| Intermediate Algebra L4 | 14 | 93% | - | 5219 | 0 | solver.off[T][S]>verifier.off[T] 8, counter.off[T][S]>verifier.off[T] 2, solver.off>verifier.off[T] 2 |
| Intermediate Algebra L5 | 17 | 65% | - | 7732 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T] 4, solver.off[S]>verifier.off[T] 4, solver.off[T][S]>verifier.off[T] 3 |
| Number Theory L4 | 9 | 100% | - | 4041 | 0 | counter.off[T][S]>verifier.off[T] 3, counter.off[S]>verifier.off[T] 3, counter.off[T][S],solver.off[S]>verifier.off[T] 1 |
| Number Theory L5 | 16 | 88% | - | 4433 | 0 | counter.off[T][S]>verifier.off[T] 11, counter.off[S]>verifier.off[T] 2, solver.off>verifier.off[T] 2 |
| Prealgebra L4 | 12 | 92% | - | 2338 | 0 | solver.off[T][S]>verifier.off[T] 4, solver.off>verifier.off[T] 3, coder.off[T][S],solver.off[T][S]>verifier.off[T] 2 |
| Prealgebra L5 | 9 | 89% | - | 4283 | 0 | counter.off[T][S]>verifier.off[T] 3, solver.off[T][S]>verifier.off[T] 2, solver.off[S]>verifier.off[T] 1 |
| Precalculus L4 | 3 | 100% | - | 7956 | 0 | solver.off[S]>verifier.off[T] 2, coder.off[T][S],solver.off[S]>verifier.off[T] 1 |
| Precalculus L5 | 6 | 50% | - | 8955 | 0 | solver.off[T][S]>verifier.off[T] 2, solver.off>verifier.off[T] 1, coder.off[T][S],solver.off[T][S]>verifier.off[T] 1 |

## Architectures the HR wrote
| architecture | uses | acc | mean cost |
|---|---|---|---|
| counter.off[T][S]>verifier.off[T] | 37 | 84% | 5093 |
| solver.off[T][S]>verifier.off[T] | 33 | 88% | 4354 |
| solver.off[S]>verifier.off[T] | 18 | 89% | 4733 |
| solver.off>verifier.off[T] | 17 | 94% | 3101 |
| coder.off[T][S],solver.off[T][S]>verifier.off[T] | 11 | 73% | 8548 |
| counter.off[S]>verifier.off[T] | 8 | 100% | 3666 |
| coder.off[T][S],solver.off[S]>verifier.off[T] | 5 | 80% | 10117 |
| solver.off[T]>verifier.off[T] | 3 | 100% | 3961 |
| coder.off[T][S],solver.off>verifier.off[T] | 2 | 100% | 6312 |
| coder.off[T],solver.off[T][S]>verifier.off[T] | 2 | 100% | 7750 |
| coder.off,solver.off>verifier.off[T] | 2 | 50% | 9575 |
| counter.off[T]>verifier.off[T] | 2 | 50% | 4827 |
| solver.off>coder.off[T]>verifier.off[T] | 1 | 100% | 3672 |
| counter.off[T][S],solver.off[S]>verifier.off[T] | 1 | 100% | 7594 |
| counter.off[T][S],solver.off[T][S]>verifier.off[T] | 1 | 100% | 3059 |

## Nodes (employee.thinking)
answer correct = the node's own answer; hit budget = the reasoning was cut at the thinking budget; for nodes with inputs: changed = its answer differs from its inputs' majority.
| node | uses | answer correct | hit budget | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| verifier.off (with inputs) | 148 | 86% | 0% | 1872 | 30 | 12 | - |
| solver.off | 101 | 79% | 0% | 2041 | - | - | - |
| counter.off | 52 | 77% | 0% | 2111 | - | - | - |
| coder.off | 25 | 56% | 0% | 2674 | - | - | - |
| coder.off (with inputs) | 2 | 100% | 0% | 1309 | - | - | - |

## Leave-one-out on 60 questions with 2+ nodes
Remove the node (its consumers lose that input; a removed output hands over to its first input) and re-run: 'needed' = right becomes wrong; 'harmful' = wrong becomes right.
| removed | uses | needed | harmful | no effect | mean cost saved |
|---|---|---|---|---|---|
| verifier.off (output) | 60 | 3 | 0 | 57 | 1683 |
| solver.off (input) | 38 | 2 | 0 | 36 | 1449 |
| counter.off (input) | 22 | 3 | 1 | 18 | 1012 |
| coder.off (input) | 6 | 0 | 0 | 6 | 1760 |

## Residual harness (what the HR gave each node)
| item | nodes given it | node answer correct when given | node answer correct otherwise |
|---|---|---|---|
| note | 326 | 81% | 50% |
| tool:check_answer | 150 | 86% | 76% |
| skill:sequence_series | 83 | 76% | 82% |
| no tools (no Python) | 58 | 83% | 80% |
| tool:exact_solve | 48 | 75% | 81% |
| skill:all_values | 47 | 66% | 83% |
| tool:brute_force | 31 | 71% | 81% |
| skill:functional_equation | 13 | 77% | 81% |
| tool:coord_geometry | 12 | 58% | 81% |
| tool:number_theory | 12 | 83% | 80% |
| tool:simplify_exact | 11 | 82% | 80% |
| tool:python | 6 | 50% | 81% |
Notes: 326 nodes got one, mean 150 chars. Example: Isolate Q^3 by cubing both sides of sqrt(Q^3) = 16 * 16^(1/8). Then take the 3rd root. Simplify 16 as 2^4 to find exact integer result.

HR output problems: minor: line 1: unknown tools/skills ['divisors'] dropped (4); minor: line 1: unknown tools/skills ['linear_system'] dropped (1); minor: line 2: unknown tools/skills ['shoelace_area'] dropped (1); minor: line 1: unknown tools/skills ['factorint', 'divisors'] dropped (1); minor: line 1: unknown tools/skills ['factorint'] dropped (1); minor: line 1: unknown tools/skills ['number_theory'] dropped (1)

## Organization wrong (21)
- [Prealgebra L5] The area of the shaded region is 78 square inches. All angles are right angles and all measurements are given in inches. What is the perimeter of the non-shaded region?

[asy]size(101);
filldraw(((0,0)--(0,8)--(10,8)--(10,-2)--(6,-2)--(6,0)--cycle^^(2.5,3)--(2.5,5)--(7.5,5)--(7.5
  architecture: a = solver("off", tools=['coord_geometry'], skills=['sequence_series'])  # note: Extract outer dims: 10x10. Inner hole: 5x2 centered at (5,3). Total area 100. Sh; v = verifier("off", a, tools=['check_answer']); return v; answered 4, correct 14
- [Intermediate Algebra L5] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver("off", skills=['functional_equation'])  # note: Use symmetry a=b=2^{n-1} to find f(2^k) = k^2 * 2^{k-1}? No, test a=b=2^m => 2f(; v = verifier("off", a, tools=['check_answer'])  # note: Verify f(2)=1, f(4)=2, f(8)=4, f(16)=8? Check f(2002) against derived formula. E; return v; answered 1, correct 96
- [Counting & Probability L5] The number of increasing sequences of positive integers $a_1 \le a_2 \le a_3 \le \cdots \le a_{10} \le 2007$ such that $a_i-i$ is even for $1\le i \le 10$ can be expressed as ${m \choose n}$ for some positive integers $m > n$. Compute the remainder when $m$ is divided by 1000.
  architecture: c = counter("off", tools=['brute_force'], skills=['sequence_series'])  # note: Map to disjoint cases based on parity of a_i - i. Case 1: a_i = 2k_i + (i-1). Ca; v = verifier("off", c, tools=['check_answer'])  # note: Re-derive formula: C(1004+9, 9) + C(1003+9, 9). Check parity constraints and bou; return v; answered 2006, correct 8
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver("off")  # note: Sphere center (r,r,r). Point P(x,y,z) satisfies |x|=50, |y|=29, |z|=41. P lies o; v = verifier("off", a, tools=['check_answer'])  # note: Check both roots of the quadratic. Ensure r > 0 (radius). Verify that the result; return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = counter("off", tools=['brute_force'], skills=['sequence_series'])  # note: Simulate the pass-by-pass toggle state for 1024 lockers to find the last one ope; v = verifier("off", a, tools=['check_answer'])  # note: Verify the simulation logic and the final index.; return v; answered 10, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver("off", tools=['simplify_exact'], skills=['functional_equation'])  # note: Use the shift property: if r is a root of p, then r+4 is a root of q. This impli; v = verifier("off", a, tools=['check_answer'])  # note: Verify that the found 'b' values satisfy the original polynomial definitions for; return v; answered 48, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: c = counter("off", tools=['brute_force'], skills=['sequence_series'])  # note: The lines form a lattice of equilateral triangles. The vertical lines are at x =; v = verifier("off", c, tools=['check_answer'])  # note: Verify the total count using the formula for the number of triangles in a triang; return v; answered 0, correct 660
- [Intermediate Algebra L4] Let $x,$ $y,$ and $z$ be positive real numbers such that $xyz = 32.$  Find the minimum value of
\[x^2 + 4xy + 4y^2 + 2z^2.\]
  architecture: a = solver("off", tools=['exact_solve'], skills=['sequence_series', 'functional_equation'])  # note: Recognize x^2+4xy+4y^2=(x+2y)^2. Let u=x+2y, v=z. Minimize u^2+2v^2 subject to u; v = verifier("off", a, tools=['check_answer'])  # note: Verify equality condition x=2y and u=4, v=4 satisfies xyz=32 and yields integer ; return v; answered 256, correct 96
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = counter("off", tools=['brute_force'], skills=['all_values'])  # note: Iterate all 30 pairs (a,b) and (c,d) to find intersections; filter by 'no three ; v = verifier("off", a, tools=['check_answer'])  # note: Verify subset of intersections satisfy parabola definitions and check no triple ; return v; answered 1260, correct 810
- [Counting & Probability L4] The Smith family has 4 sons and 3 daughters. In how many ways can they be seated in a row of 7 chairs such that at least 2 boys are next to each other?
  architecture: a = counter("off", tools=['brute_force'], skills=['sequence_series'])  # note: Calculate total permutations of 7 distinct people (7!). Calculate permutations w; b = solver("off", tools=['check_answer'], skills=['all_values'])  # note: Verify the arithmetic: 7! - (4! * C(4,2) * 4!). Ensure the result is an integer.; return b; answered 2, correct 4896

## Most expensive correct questions (possible waste)
- [Precalculus L4, cost 14007] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\
  architecture: a = solver("off", skills=['sequence_series'])  # note: Identify roots as 8th roots of unity excluding z=1. Use symmetry about real axis; b = coder("off", tools=['exact_solve'], skills=['sequence_series'])  # note: Calculate area using shoelace formula or sum of triangle areas from origin. Area; v = verifier("off", a, b, tools=['check_answer'])  # note: Check the area calculation. Ensure the order of vertices is correct (counter-clo; return v
- [Geometry L5, cost 13606] Square $ABCD$ has center $O,\ AB=900,\ E$ and $F$ are on $AB$ with $AE<BF$ and $E$ between $A$ and $F, m\angle EOF =45^\circ,$ and $EF=400.$ Given that $BF=p+q\sqrt{r},$ where $p,q
  architecture: a = solver("off", tools=['coord_geometry'], skills=['sequence_series'])  # note: Place A=(0,0), B=(900,0), O=(450,450). Let E=(x,0), F=(x+400,0). Use dot product; b = coder("off", tools=['exact_solve'], skills=['all_values'])  # note: Solve the quadratic equation for x exactly. Identify the two roots. Select the r; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify the chosen x satisfies AE < BF, EF=400, and angle EOF = 45 degrees. Ensur; return v
- [Intermediate Algebra L4, cost 12910] Find the largest constant $m,$ so that for any positive real numbers $a,$ $b,$ $c,$ and $d,$
\[\sqrt{\frac{a}{b + c + d}} + \sqrt{\frac{b}{a + c + d}} + \sqrt{\frac{c}{a + b + d}} 
  architecture: a = solver("off", tools=['exact_solve'], skills=['sequence_series'])  # note: Apply Cauchy-Schwarz inequality to the sum of square roots; identify the lower b; b = coder("off", tools=['exact_solve'])  # note: Algebraically verify the equality condition and compute the exact value of the b; v = verifier("off", a, b, tools=['check_answer'])  # note: Check the boundary case where a=b=c=d to confirm the strict inequality holds and; return v
- [Geometry L5, cost 10628] The grid below contains the $16$ points whose $x$- and $y$-coordinates are in the set $\{0,1,2,3\}$: [asy]
size(2.5cm);
for(int i=0; i<4; i+=1) { for(int j=0; j<4; j+=1) { dot((i,j
  architecture: a = solver("off", tools=['coord_geometry'], skills=['sequence_series'])  # note: Identify all squares by side vector (dx, dy) where dx,dy in {-3..3} excluding (0; b = coder("off", tools=['python'], skills=['all_values'])  # note: Use brute_force to iterate all pairs of points, check if they form a square with; v = verifier("off", a, b, tools=['check_answer'])  # note: Re-derive sum by listing squares: axis-aligned (areas 1,4,9) and tilted (areas 2; return v
- [Geometry L5, cost 9527] $ABCD$, a rectangle with $AB = 12$ and $BC = 16$, is the base of pyramid $P$, which has a height of $24$. A plane parallel to $ABCD$ is passed through $P$, dividing $P$ into a frus
  architecture: a = solver("off", tools=['exact_solve'], skills=['sequence_series'])  # note: Determine scale factor k from V_P = 8*V_P' => k^3 = 1/8 => k=1/2. Height of P' i; b = coder("off", tools=['exact_solve'], skills=['all_values'])  # note: Set up coordinate system: P at (0,0,24), ABCD at z=0. Circumsphere center X is o; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify X is equidistant from P and base vertices. Check final distance XT calcul; return v