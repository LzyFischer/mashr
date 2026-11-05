# Diagnostic report (dev-A)

Organization: acc 88.7%, cost 5910/question, of which the HR 710 (HR prompt 7053 chars). 10 distinct architectures, 2.7 nodes per question. HR outputs: repaired 0, written again 2, fallback 0.

## By category
| category | n | acc | full acc | cost | full cost | architectures |
|---|---|---|---|---|---|---|
| Algebra L4 | 17 | 100% | - | 2870 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 12, coder.off[T][S],solver.off[T][S]>verifier.off[T]? 2, solver.off[T][S] 1 |
| Algebra L5 | 18 | 100% | - | 3795 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 15, solver.off[S] 1, coder.off[T][S],solver.off[S] 1 |
| Counting & Probability L4 | 8 | 100% | - | 4027 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 6, solver.off[S] 1, coder.off[T][S],solver.off[T][S]>verifier.off[T]? 1 |
| Counting & Probability L5 | 9 | 78% | - | 6075 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 6, solver.off[S] 2, coder.off[T][S],coder.off[T][S]>verifier.off[T]? 1 |
| Geometry L4 | 5 | 100% | - | 4380 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 3, solver.off[S] 2 |
| Geometry L5 | 7 | 57% | - | 12190 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 7 |
| Intermediate Algebra L4 | 14 | 100% | - | 6517 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 12, solver.off[S] 1, coder.off[T][S],solver.off[T][S]>verifier.off[T]? 1 |
| Intermediate Algebra L5 | 17 | 59% | - | 9504 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 16, coder.off[T][S],solver.off[S]>verifier.off[T][S]? 1 |
| Number Theory L4 | 9 | 89% | - | 5198 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 7, coder.off[T][S],solver.off[T][S]>verifier.off[T]? 1, solver.off[S] 1 |
| Number Theory L5 | 16 | 88% | - | 5767 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 13, solver.off[S] 1, coder.off[T][S],solver.off[S] 1 |
| Prealgebra L4 | 12 | 100% | - | 1976 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 7, solver.off[S] 2, coder.off[S] 1 |
| Prealgebra L5 | 9 | 100% | - | 6644 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 5, solver.off[S] 2, solver.off[T][S] 1 |
| Precalculus L4 | 3 | 100% | - | 8347 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 3 |
| Precalculus L5 | 6 | 67% | - | 12484 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T]? 6 |

## Architectures the HR wrote
| architecture | uses | acc | mean cost |
|---|---|---|---|
| coder.off[T][S],solver.off[S]>verifier.off[T]? | 118 | 88% | 6620 |
| solver.off[S] | 14 | 93% | 2074 |
| coder.off[T][S],solver.off[T][S]>verifier.off[T]? | 6 | 100% | 5567 |
| solver.off[T][S] | 4 | 100% | 1307 |
| coder.off[T][S] | 2 | 100% | 1190 |
| coder.off[T][S],solver.off[S] | 2 | 50% | 4458 |
| coder.off[T][S],solver.off[S]>verifier.off[T][S]? | 1 | 0% | 11414 |
| coder.off[S] | 1 | 100% | 1052 |
| coder.off[T][S],coder.off[T][S]>verifier.off[T]? | 1 | 100% | 12179 |
| coder.off[T][S]>verifier.off[T]? | 1 | 100% | 1820 |

## Nodes (employee.thinking)
answer correct = the node's own answer; hit budget = the reasoning was cut at the thinking budget; for nodes with inputs: changed = its answer differs from its inputs' majority.
| node | uses | answer correct | hit budget | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| solver.off | 145 | 77% | 0% | 2178 | - | - | - |
| coder.off | 133 | 77% | 0% | 2507 | - | - | - |
| verifier.off (with inputs) | 127 | 88% | 0% | 1030 | 31 | 20 | 1 |

## Leave-one-out on 60 questions with 2+ nodes
Remove the node (its consumers lose that input; a removed output hands over to its first input) and re-run: 'needed' = right becomes wrong; 'harmful' = wrong becomes right.
| removed | uses | needed | harmful | no effect | mean cost saved |
|---|---|---|---|---|---|
| coder.off (input) | 61 | 10 | 0 | 51 | 3325 |
| verifier.off (output) | 60 | 10 | 0 | 50 | 917 |
| solver.off (input) | 59 | 8 | 0 | 51 | 2988 |

## Residual harness (what the HR gave each node)
| item | nodes given it | node answer correct when given | node answer correct otherwise |
|---|---|---|---|
| note | 399 | 76% | 50% |
| tool:check_answer | 144 | 69% | 77% |
| no tools (no Python) | 136 | 76% | 75% |
| skill:case_split | 128 | 71% | 79% |
| skill:exact_algebra | 103 | 79% | 74% |
| tool:simplify_exact | 82 | 68% | 77% |
| tool:python | 57 | 79% | 75% |
| tool:exact_solve | 55 | 79% | 75% |
| skill:counting_constraints | 45 | 80% | 75% |
| skill:substitute_back | 40 | 80% | 75% |
| skill:number_theory | 35 | 80% | 75% |
| tool:number_theory | 28 | 81% | 75% |
| tool:brute_force | 26 | 58% | 77% |
| skill:geometry_diagrams | 25 | 52% | 78% |
| skill:small_cases | 21 | 67% | 76% |
| skill:roots_power_sums | 10 | 40% | 77% |
| tool:coord_geometry | 8 | 75% | 76% |
| skill:proportion_units | 3 | 100% | 75% |
| skill:sequence_recurrence | 3 | 67% | 76% |
| skill:inverse_function | 2 | 100% | 75% |

only_if="disagree": 127 nodes, skipped 85 (inputs agreed); question correct when skipped 99%, when run 67%.
Notes: 399 nodes got one, mean 144 chars. Example: Raise both sides to power 8 to clear roots, solve for Q^3, then take cube root. Check Q >= 0 domain.

HR output problems: minor: line 1: unknown tools/skills ['proportion_units'] dropped (1); minor: line 1: unknown tools/skills ['complex_numbers'] dropped (1); minor: line 1: unknown tools/skills ['arithmetic_series'] dropped (1); minor: line 2: unknown tools/skills ['sum'] dropped (1)

## Organization wrong (17)
- [Intermediate Algebra L5] During the car ride home, Michael looks back at his recent math exams. A problem on Michael's calculus mid-term gets him starting thinking about a particular quadratic,\[x^2-sx+p,\]with roots $r_1$ and $r_2$. He notices that\[r_1+r_2=r_1^2+r_2^2=r_1^3+r_2^3=\cdots=r_1^{2007}+r_2^
  architecture: a = solver("off", skills=['case_split', 'exact_algebra'])  # note: Derive s and p constraints from r1^k+r2^k=constant. Handle r1=r2 and r1=-r2 case; b = coder("off", tools=['check_answer', 'simplify_exact'], skills=['small_cases', 'substitute_back'])  # note: Compute max of 1/r1^2008 + 1/r2^2008 using derived s,p. Verify edge cases.; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify that s=0, p=-1 (roots 1, -1) or s=2, p=1 (roots 1, 1) or s=-2, p=1 (roots; return v; answered 0, correct 2
- [Intermediate Algebra L5] There is a unique polynomial $P(x)$ of degree $8$ with rational coefficients and leading coefficient $1,$ which has the number \[\sqrt{2} + \sqrt{3} + \sqrt{5}\]as a root. Compute $P(1).$
  architecture: a = solver("off", skills=['exact_algebra', 'case_split'])  # note: Find minimal poly of alpha by successive squaring to eliminate roots 2,3,5. Trac; b = coder("off", tools=['exact_solve', 'simplify_exact'], skills=['exact_algebra'])  # note: Implement squaring steps in Python to compute exact coefficients of P(x). Comput; v = verifier("off", a, b, tools=['check_answer'], skills=['substitute_back'], only_if="disagree")  # note: Verify P(alpha)=0 by substitution; check P(1) calculation; confirm monic rationa; return v; answered 2, correct -71
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver("off", skills=['case_split', 'substitute_back'])  # note: Let sphere center be (r,r,r) and point be (x,y,z). Distances to planes are coord; b = coder("off", tools=['python', 'exact_solve'], skills=['number_theory'])  # note: Implement the 6 permutations in Python. Calculate r = sqrt((x-r)^2 + (y-r)^2 + (; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify each calculated r by plugging back into distance equation. Ensure r is po; return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver("off", skills=['case_split', 'small_cases'])  # note: Model the walk as a sequence of passes. Pass 1: odd open. Pass 2: even (of remai; b = coder("off", tools=['python'], skills=['sequence_recurrence'])  # note: Write a simulation loop for N=1024 to verify the pattern found by solver. Track ; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Check if simulation matches derived formula; if agree, confirm final number.; return v; answered 1024, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver("off", skills=['case_split', 'exact_algebra'])  # note: Define p(x) and q(x) relations. Let r,s be roots of p. Then r+4, s-3 are roots o; b = coder("off", tools=['exact_solve', 'python'], skills=['exact_algebra'])  # note: Translate system of polynomial equations into algebraic constraints. Solve for b; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify both candidates satisfy original cubic root conditions. Ensure no arithme; return v; answered 1, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = coder("off", tools=['exact_solve', 'brute_force'], skills=['case_split', 'counting_constraints'])  # note: Count triangles by enumerating k from -10 to 10. Identify intersection points of; b = solver("off", skills=['geometry_diagrams', 'small_cases'])  # note: Derive the geometric structure: 3 families of parallel lines at 60 degrees. Calc; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'], only_if="disagree")  # note: Compare counts from enumeration and geometric formula. If consistent, confirm. I; return v; answered 1, correct 660
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = solver("off", skills=['case_split', 'geometry_diagrams', 'substitute_back'])  # note: Analyze the geometry. A point on two parabolas with focus (0,0) and directrices ; b = coder("off", tools=['python', 'exact_solve'], skills=['counting_constraints', 'case_split'])  # note: Code to iterate all pairs of (a1, b1) and (a2, b2). For each pair, find the numb; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify the count by checking a specific pair manually and summing up the logic.; return v; answered 9, correct 810
- [Number Theory L5] Let $\tau (n)$ denote the number of positive integer divisors of $n$ (including $1$ and $n$). Find the sum of the six least positive integers $n$ that are solutions to $\tau (n) + \tau (n+1) = 7$.
  architecture: a = coder("off", tools=['number_theory', 'brute_force'], skills=['counting_constraints', 'small_cases'])  # note: Enumerate n starting from 1. Calculate tau(n) and tau(n+1) using prime factoriza; b = solver("off", skills=['case_split', 'number_theory'])  # note: Analyze parity: one of n, n+1 must have an odd number of divisors (perfect squar; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'], only_if="disagree")  # note: Verify the 6 values found by both methods satisfy tau(n)+tau(n+1)=7 exactly. Che; return v; answered 12, correct 540
- [Geometry L5] Given a point $P$ on a triangular piece of paper $ABC,\,$ consider the creases that are formed in the paper when $A, B,\,$ and $C\,$ are folded onto $P.\,$ Let us call $P$ a fold point of $\triangle ABC\,$ if these creases, which number three unless $P$ is one of the vertices, do
  architecture: a = solver("off", skills=['case_split', 'geometry_diagrams'])  # note: The creases are segments of the perpendicular bisectors of AP, BP, and CP. They ; b = coder("off", tools=['python', 'simplify_exact'], skills=['geometry_diagrams'])  # note: Calculate the area of the union of three circular sectors. The sectors are cente; c = verifier("off", a, b, tools=['check_answer', 'simplify_exact'], only_if="disagree")  # note: Verify the area calculation. Check if the radii and angles are correct. Ensure t; return c; answered 36, correct 597
- [Number Theory L5] What is the ones digit of $1^{2009} + 2^{2009} + 3^{2009} + \cdots + 2009^{2009}?$
  architecture: a = coder("off", tools=['brute_force'], skills=['case_split'])  # note: Compute sum mod 10. Pattern of n^2009 mod 10 repeats every 10. Sum one block of ; b = solver("off", skills=['small_cases', 'number_theory'])  # note: Analyze powers mod 10. 1^k=1, 2^k cycles 2,4,8,6, 3^k cycles 3,9,7,1, 4^k cycles; return a; answered 9, correct 5

## Most expensive correct questions (possible waste)
- [Precalculus L5, cost 16957] Let $a$ and $b$ be two 12th roots of unity, not necessarily distinct.  Find the number of different possible values of $(a + b)^{12}.$
  architecture: a = coder("off", tools=['number_theory', 'brute_force'], skills=['case_split', 'roots_power_sums'])  # note: Compute (a+b)^12 for all 144 pairs using brute force; group identical results.; b = solver("off", skills=['case_split', 'exact_algebra'])  # note: Analyze geometrically: a and b are vertices of a regular 12-gon. Sum depends onl; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: List the 11 distinct non-zero sums of roots of unity plus the case a=b. Verify t; return v
- [Number Theory L5, cost 15854] Let $N$ be the number of ways to write $2010$ in the form $2010 = a_3 \cdot 10^3 + a_2 \cdot 10^2 + a_1 \cdot 10 + a_0$, where the $a_i$'s are integers, and $0 \le a_i \le 99$. An 
  architecture: a = coder("off", tools=['brute_force'], skills=['counting_constraints'])  # note: Direct enumeration of valid (a3, a2, a1, a0) tuples where a_i in [0,99] and sum(; b = solver("off", skills=['case_split'])  # note: Analyze constraints on a0 mod 10, a1 mod 10, etc., to derive a closed-form count; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Compare brute force count vs analytical count. If mismatch, re-derive constraint; return v
- [Geometry L4, cost 13912] A line with slope of $-2$ intersects the positive $x$-axis at $A$ and the positive $y$-axis at $B$. A second line intersects the $x$-axis at $C(8,0)$ and the $y$-axis at $D$. The l
  architecture: a = solver("off", skills=['geometry_diagrams'])  # note: Find coords of A, B, C, D, E. Identify polygon OBEC vertices.; b = coder("off", tools=['python', 'simplify_exact'], skills=['exact_algebra'])  # note: Compute area of quadrilateral OBEC using shoelace formula on coordinates.; v = verifier("off", a, b, tools=['check_answer'], only_if="disagree")  # note: Verify coordinates and area calculation. Confirm OBEC is convex and vertices are; return v
- [Precalculus L4, cost 13614] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\
  architecture: a = coder("off", tools=['exact_solve', 'simplify_exact'], skills=['case_split', 'geometry_diagrams'])  # note: Roots are 8th roots of unity excluding 1. Vertices lie on unit circle. Area is s; b = solver("off", skills=['roots_power_sums', 'geometry_diagrams'])  # note: Independent derivation: Sum of areas = (1/2) * sum(|z_i|^2 * sin(theta_{i+1} - t; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'], only_if="disagree")  # note: Compare a and b. If agree, confirm via direct coordinate calculation for 3 conse; return v
- [Intermediate Algebra L4, cost 13370] The equations $x^3 + Ax + 10 = 0$ and $x^3 + Bx^2 + 50 = 0$ have two roots in common.  Then the product of these common roots can be expressed in the form $a \sqrt[b]{c},$ where $a
  architecture: a = solver("off", skills=['case_split', 'exact_algebra'])  # note: Find common roots r1, r2 by subtracting equations to eliminate x^3, solve for li; b = coder("off", tools=['exact_solve', 'simplify_exact'], skills=['exact_algebra'])  # note: Compute exact roots of the quadratic found by 'a' using sympy, simplify the prod; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'], only_if="disagree")  # note: Verify the common roots satisfy both original cubic equations; confirm product m; return v