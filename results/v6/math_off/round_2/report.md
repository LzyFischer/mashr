# Diagnostic report (dev-A)

Organization: acc 88.7%, cost 5892/question, of which the HR 792 (HR prompt 8603 chars). 29 distinct architectures, 2.7 nodes per question. HR outputs: repaired 1, written again 2, fallback 2.

## By category
| category | n | acc | full acc | cost | full cost | architectures |
|---|---|---|---|---|---|---|
| Algebra L4 | 17 | 100% | - | 2843 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 10, solver.off[S] 3, coder.off[T][S],geometer.off[S]>verifier.off[T]? 2 |
| Algebra L5 | 18 | 94% | - | 3951 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 9, solver.off[S] 2, algebraist.off[S],coder.off[T][S]>verifier.off[T]? 2 |
| Counting & Probability L4 | 8 | 100% | - | 4104 | 0 | coder.off[T][S],combinator.off[S]>verifier.off[T]? 4, coder.off[T][S],solver.off[S]>verifier.off[T]? 2, solver.off[T][S] 1 |
| Counting & Probability L5 | 9 | 89% | - | 6460 | 0 | coder.off[T][S],combinator.off[S]>verifier.off[T]? 4, coder.off[T][S]>verifier.off[T]? 2, coder.off[T][S],solver.off[S]>verifier.off[T]? 1 |
| Geometry L4 | 5 | 80% | - | 3982 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 2, coder.off[T][S],geometer.off[S]>verifier.off[T]? 2, geometer.off[T][S],solver.off[T][S],verifier.off[T][S] 1 |
| Geometry L5 | 7 | 57% | - | 9280 | 0 | coder.off[T][S],geometer.off[T][S]>verifier.off[T]? 4, coder.off[T][S],geometer.off[S]>verifier.off[T]? 2, solver.off[T] 1 |
| Intermediate Algebra L4 | 14 | 100% | - | 5941 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 8, solver.off[S] 2, combinator.off[T][S] 1 |
| Intermediate Algebra L5 | 17 | 65% | - | 11521 | 0 | algebraist.off[S],coder.off[T][S]>verifier.off[T]? 6, coder.off[T][S],solver.off[S]>verifier.off[T]? 6, algebraist.off[S],algebraist.off[S]>verifier.off[T]? 1 |
| Number Theory L4 | 9 | 100% | - | 4348 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 4, combinator.off[T][S],solver.off[T][S]>verifier.off[T]? 1, coder.off[T][S],combinator.off[S]>verifier.off[T]? 1 |
| Number Theory L5 | 16 | 94% | - | 5474 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 10, coder.off[T][S],combinator.off[S]>verifier.off[T]? 3, combinator.off[T][S],combinator.off[T][S]>verifier.off[T]? 1 |
| Prealgebra L4 | 12 | 100% | - | 2125 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 6, solver.off[S] 3, coder.off[T][S]>verifier.off[T]? 1 |
| Prealgebra L5 | 9 | 89% | - | 6814 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 3, coder.off[T][S],geometer.off[T][S]>verifier.off[T]? 2, coder.off[T][S],combinator.off[S]>verifier.off[T]? 1 |
| Precalculus L4 | 3 | 100% | - | 8020 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 2, algebraist.off[T][S],coder.off[T][S],geometer.off[T][S]>verifier.off[T]? 1 |
| Precalculus L5 | 6 | 50% | - | 11973 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 2, coder.off[T][S],coder.off[T][S]>verifier.off[T]? 1, coder.off[T][S],geometer.off[T][S]>verifier.off[T]? 1 |

## Architectures the HR wrote
| architecture | uses | acc | mean cost |
|---|---|---|---|
| coder.off[T][S],solver.off[S]>verifier.off[T]? | 65 | 92% | 5211 |
| coder.off[T][S],combinator.off[S]>verifier.off[T]? | 13 | 100% | 5477 |
| solver.off[S] | 12 | 100% | 1672 |
| algebraist.off[S],coder.off[T][S]>verifier.off[T]? | 9 | 89% | 7211 |
| coder.off[T][S],geometer.off[T][S]>verifier.off[T]? | 9 | 67% | 8664 |
| coder.off[T][S],geometer.off[S]>verifier.off[T]? | 7 | 57% | 7963 |
| coder.off[T][S]>verifier.off[T]? | 4 | 100% | 3702 |
| combinator.off[S] | 4 | 100% | 1916 |
| coder.off[T][S] | 4 | 100% | 2152 |
| coder.off[T][S],coder.off[T][S]>verifier.off[T]? | 2 | 100% | 13819 |
| solver.off[T] | 2 | 0% | 7022 |
| coder.off[T][S],combinator.off[T][S]>verifier.off[T]? | 2 | 50% | 9227 |
| solver.off[S]>verifier.off[T]? | 1 | 100% | 1373 |
| combinator.off[T][S],combinator.off[T][S]>verifier.off[T]? | 1 | 100% | 6948 |
| combinator.off[T][S],solver.off[T][S]>verifier.off[T]? | 1 | 100% | 5295 |

## Nodes (employee.thinking)
answer correct = the node's own answer; hit budget = the reasoning was cut at the thinking budget; for nodes with inputs: changed = its answer differs from its inputs' majority.
| node | uses | answer correct | hit budget | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| coder.off | 127 | 76% | 0% | 2396 | - | - | - |
| verifier.off (with inputs) | 126 | 87% | 0% | 1070 | 30 | 17 | 1 |
| solver.off | 90 | 83% | 0% | 1846 | - | - | - |
| combinator.off | 23 | 87% | 0% | 2281 | - | - | - |
| geometer.off | 21 | 52% | 0% | 2860 | - | - | - |
| algebraist.off | 15 | 47% | 0% | 3014 | - | - | - |
| verifier.off | 2 | 100% | 0% | 1024 | - | - | - |

## Leave-one-out on 60 questions with 2+ nodes
Remove the node (its consumers lose that input; a removed output hands over to its first input) and re-run: 'needed' = right becomes wrong; 'harmful' = wrong becomes right.
| removed | uses | needed | harmful | no effect | mean cost saved |
|---|---|---|---|---|---|
| verifier.off (output) | 59 | 10 | 0 | 49 | 843 |
| coder.off (input) | 56 | 10 | 0 | 46 | 2854 |
| solver.off (input) | 35 | 2 | 0 | 33 | 2278 |
| combinator.off (input) | 12 | 2 | 0 | 10 | 2869 |
| algebraist.off (input) | 7 | 2 | 0 | 5 | 5271 |
| geometer.off (input) | 7 | 0 | 0 | 7 | 3855 |

## Residual harness (what the HR gave each node)
| item | nodes given it | node answer correct when given | node answer correct otherwise |
|---|---|---|---|
| note | 397 | 75% | 33% |
| skill:exact_algebra | 149 | 72% | 76% |
| tool:python | 149 | 70% | 78% |
| tool:check_answer | 130 | 66% | 76% |
| no tools (no Python) | 118 | 81% | 70% |
| skill:case_split | 94 | 76% | 74% |
| tool:exact_solve | 77 | 64% | 78% |
| skill:substitute_back | 63 | 75% | 74% |
| skill:number_theory | 52 | 88% | 72% |
| tool:simplify_exact | 50 | 73% | 75% |
| skill:small_cases | 32 | 78% | 74% |
| skill:counting_constraints | 26 | 85% | 74% |
| skill:minimal_polynomial | 19 | 53% | 76% |
| tool:number_theory | 16 | 88% | 74% |
| skill:geometric_counting | 9 | 33% | 76% |
| skill:proportion_units | 8 | 100% | 74% |
| tool:coord_geometry | 8 | 25% | 76% |
| skill:inverse_function | 4 | 100% | 74% |
| skill:functional_equation | 2 | 50% | 75% |
| tool:brute_force | 2 | 100% | 74% |

only_if="disagree": 126 nodes, skipped 86 (inputs agreed); question correct when skipped 98%, when run 62%.
Notes: 397 nodes got one, mean 137 chars. Example: Solve algebraically by equating exponents of 2. Express 16 as 2^4 and simplify radicals to find Q.

HR output problems: syntax error: invalid syntax (line 1) (1); line 1: expected `x = employee("thinking", inputs..., tools=[...], skills=[...])` (1); line 2: expected `x = employee("thinking", inputs..., tools=[...], skills=[...])` (1); syntax error: unterminated string literal (detected at line 3) (line 2) (1); minor: line 13: only_if must be "disagree" on a node with inputs; ignored (1)

## Organization wrong (17)
- [Prealgebra L5] The area of the shaded region is 78 square inches. All angles are right angles and all measurements are given in inches. What is the perimeter of the non-shaded region?

[asy]size(101);
filldraw(((0,0)--(0,8)--(10,8)--(10,-2)--(6,-2)--(6,0)--cycle^^(2.5,3)--(2.5,5)--(7.5,5)--(7.5
  architecture: g = geometer("off", tools=['coord_geometry', 'python'], skills=['case_split', 'exact_algebra'])  # note: Extract coordinates from Asymptote. Define outer boundary (L-shape) and inner ho; c = coder("off", tools=['python', 'exact_solve'], skills=['exact_algebra', 'substitute_back'])  # note: Implement formula for perimeter of non-shaded region (outer boundary + inner hol; v = verifier("off", g, c, tools=['check_answer'], only_if="disagree")  # note: Re-calculate area and perimeter independently. Verify hole side length is 2 inch; return v; answered 54, correct 14
- [Intermediate Algebra L5] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver("off", skills=['functional_equation', 'exact_algebra'])  # note: Deduce that $f(2^n) = n^2$. Use $a=b=2^{n-1}$ to find $f(2^{n-1})$. Show $f(x) =; b = coder("off", tools=['python', 'exact_solve'], skills=['case_split', 'exact_algebra']); v = verifier("off", a, b, tools=['check_answer'], only_if="disagree"); return v; answered 2, correct 96
- [Intermediate Algebra L5] Find the sum of all complex numbers $z$ that satisfy
\[z^3 + z^2 - |z|^2 + 2z = 0.\]
  architecture: a = solver("off", skills=['case_split', 'exact_algebra'])  # note: Split by cases |z|=0 and |z|!=0. Solve algebraic equations exactly. Check extran; b = coder("off", tools=['python', 'exact_solve'], skills=['exact_algebra'])  # note: Verify solutions using Python algebraic solver and summing.; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Confirm sum satisfies original equation and check arithmetic.; return v; answered 3, correct -2
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: s = solver("off", skills=['case_split', 'substitute_back'])  # note: Identify sphere center (r,r,r) and radius r. Set up distance equations for point; c = coder("off", tools=['python', 'exact_solve'], skills=['exact_algebra'])  # note: Implement the equation (50-r)^2 + (29-r)^2 + (41-r)^2 = r^2. Solve the resulting; v = verifier("off", s, c, tools=['check_answer'], only_if="disagree")  # note: Re-derive quadratic manually. Check both roots. Verify they are positive. Check ; return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver("off", tools=['python']); return a; answered 4, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = algebraist("off", skills=['exact_algebra', 'minimal_polynomial'])  # note: Use Vieta and symmetric sums for cubic equations to relate coefficients to roots; b = coder("off", tools=['python', 'exact_solve'], skills=['substitute_back'])  # note: Implement the system of symmetric equations derived by a; solve for b exactly us; v = verifier("off", a, b, tools=['check_answer', 'python'], only_if="disagree")  # note: Verify the derived b values by checking if the original root conditions hold for; return v; answered 59, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = geometer("off", skills=['case_split', 'geometric_counting'])  # note: Map the family of lines to a triangular lattice in the plane. Identify the unit ; b = coder("off", tools=['python', 'exact_solve'], skills=['exact_algebra'])  # note: Compute the exact number of unit triangles in the large equilateral triangle for; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Confirm the side length of the large triangle and the counting formula by checki; return v; answered 12, correct 660
- [Precalculus L5] Three unit circles are drawn so they are mutually tangent, as shown below.  A blue circle that is externally tangent to all three unit circles is drawn.  Finally, three red circles are drawn, so that each red circle is externally tangent to two unit circles and externally tangent
  architecture: g = geometer("off", tools=['python'], skills=['exact_algebra', 'case_split'])  # note: Identify the radius of the blue circle (inner Soddy circle) tangent to three uni; c = coder("off", tools=['python', 'exact_solve'], skills=['exact_algebra', 'substitute_back'])  # note: Model the distances between centers. Let the unit circles be at distance 2 from ; v = verifier("off", g, c, tools=['python', 'check_answer', 'simplify_exact'], only_if="disagree")  # note: Compare r from g and c. Simplify r to the form (a - b*sqrt(c))/d. Ensure a,b,c,d; return v; answered 33, correct 49
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: g1 = geometer("off", tools=['coord_geometry'], skills=['case_split', 'geometric_counting'])  # note: Enumerate all 30 pairs. For each pair, check intersection of parabolas sharing f; c1 = coder("off", tools=['python', 'exact_solve', 'simplify_exact'], skills=['exact_algebra', 'substitute_back'])  # note: Implement the geometric intersection logic for parabolas. Compute intersections ; v1 = verifier("off", g1, c1, tools=['check_answer'], only_if="disagree")  # note: Verify the set of intersection points satisfies the parabola equations and count; a1 = algebraist("off", tools=['exact_solve'], skills=['case_split', 'exact_algebra'])  # note: Derive the algebraic condition for a point (x,y) to lie on two parabolas with fo; c2 = coder("off", tools=['python', 'number_theory'], skills=['counting_constraints', 'substitute_back'])  # note: Iterate through all pairs of directrix parameters. Solve the resulting system of; v2 = verifier("off", a1, c2, tools=['check_answer'], only_if="disagree")  # note: Cross-check the count from Method 1 and 2. Ensure no double counting of points l; final = verifier("off", v1, v2, tools=['check_answer'], only_if="disagree")  # note: If both methods agree, confirm the final count. If they disagree, perform an ind; return final; answered 2, correct 810
- [Geometry L4] A line with slope of $-2$ intersects the positive $x$-axis at $A$ and the positive $y$-axis at $B$. A second line intersects the $x$-axis at $C(8,0)$ and the $y$-axis at $D$. The lines intersect at $E(4,4)$. What is the area of the shaded quadrilateral $OBEC$? [asy]
draw((0,-1)--
  architecture: g = geometer("off", skills=['case_split', 'geometric_counting'])  # note: Compute coordinates of B and D from line equations; identify vertices O(0,0), B,; c = coder("off", tools=['python'], skills=['exact_algebra', 'substitute_back'])  # note: Calculate areas of triangles OBC and ODC (or use polygon formula) to find Area(O; v = verifier("off", g, c, tools=['check_answer'], only_if="disagree")  # note: Verify coordinates satisfy line equations and check area calculation logic.; return v; answered 80, correct 40

## Most expensive correct questions (possible waste)
- [Number Theory L5, cost 16272] Let $N$ be the number of ways to write $2010$ in the form $2010 = a_3 \cdot 10^3 + a_2 \cdot 10^2 + a_1 \cdot 10 + a_0$, where the $a_i$'s are integers, and $0 \le a_i \le 99$. An 
  architecture: a = coder("off", tools=['python'], skills=['counting_constraints'])  # note: Count solutions to a3*1000 + a2*100 + a1*10 + a0 = 2010 with 0<=ai<=99 by iterat; b = coder("off", tools=['python'], skills=['case_split'])  # note: Split by a3 value (0, 1, 2). For each, count valid (a2, a1, a0) triples satisfyi; v = verifier("off", a, b, tools=['check_answer', 'python'], only_if="disagree")  # note: Verify the sum of counts from both methods matches the manual calculation for ea; return v
- [Precalculus L4, cost 14719] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\
  architecture: g = geometer("off", tools=['coord_geometry'], skills=['case_split', 'geometric_counting'])  # note: Convert roots of unity (excluding 1) to coordinates in the plane. The roots are ; a = algebraist("off", tools=['exact_solve'], skills=['exact_algebra', 'minimal_polynomial'])  # note: Verify the roots are the primitive 7th roots of unity by checking the polynomial; c = coder("off", tools=['python'], skills=['substitute_back'])  # note: Compute the exact area using Python's complex number arithmetic or coordinate ge; v = verifier("off", g, a, c, tools=['check_answer'], only_if="disagree")  # note: Re-calculate area using two different methods (e.g., geometric decomposition vs.; return v
- [Prealgebra L5, cost 13403] Triangle $ABC$ is a right triangle. If the measure of angle $PAB$ is $x^\circ$ and the measure of angle $ACB$ is expressed in the form $(Mx+N)^\circ$ with $M=1$, what is the value 
  architecture: a = solver("off", skills=['case_split', 'minimal_polynomial'])  # note: Use coordinate geometry to find exact coordinates of C based on the 30-60-90 tri; b = coder("off", tools=['python', 'exact_solve', 'simplify_exact'], skills=['exact_algebra', 'substitute_back'])  # note: Implement the geometric derivation in Python using sympy to solve for M and N ex; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify the derived linear relationship M=1, N=2 by substituting back into the an; return v
- [Geometry L5, cost 12895] Square $ABCD$ has center $O,\ AB=900,\ E$ and $F$ are on $AB$ with $AE<BF$ and $E$ between $A$ and $F, m\angle EOF =45^\circ,$ and $EF=400.$ Given that $BF=p+q\sqrt{r},$ where $p,q
  architecture: g = geometer("off", tools=['coord_geometry', 'exact_solve', 'python'], skills=['case_split', 'exact_algebra'])  # note: Set A=(0,900), B=(900,900), O=(450,450). E=(x,900), F=(y,900). Solve constraints; c = coder("off", tools=['python', 'exact_solve', 'simplify_exact'], skills=['exact_algebra', 'substitute_back'])  # note: Solve the quadratic for x derived from the 45-degree condition. Compute BF = 900; v = verifier("off", g, c, tools=['check_answer', 'python'], only_if="disagree")  # note: Verify angle is 45 degrees and EF=400 with the found coordinates. Confirm BF mat; return v
- [Intermediate Algebra L4, cost 12851] Find the largest constant $m,$ so that for any positive real numbers $a,$ $b,$ $c,$ and $d,$
\[\sqrt{\frac{a}{b + c + d}} + \sqrt{\frac{b}{a + c + d}} + \sqrt{\frac{c}{a + b + d}} 
  architecture: a = solver("off", skills=['case_split', 'small_cases', 'exact_algebra'])  # note: Analyze symmetry, test a=b=c=d=1 to guess m=1. Prove m=1 by reducing to sum of s; c = coder("off", tools=['python', 'exact_solve', 'check_answer'], skills=['substitute_back'])  # note: Implement numerical check for random points and symbolic verification of the ine; v = verifier("off", a, c, tools=['check_answer'], only_if="disagree")  # note: Check if both methods yield m=1. If disagree, re-derive using standard inequalit; return v