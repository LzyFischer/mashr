# Diagnostic report (dev-A)

Organization: acc 84.7%, cost 5410/question, of which the HR 430 (HR prompt 6100 chars). 9 distinct architectures, 2.3 nodes per question. HR outputs: repaired 0, written again 0, fallback 0.

## By category
| category | n | acc | full acc | cost | full cost | architectures |
|---|---|---|---|---|---|---|
| Algebra L4 | 17 | 100% | - | 2247 | 0 | solver.off[S]>verifier.off[T] 15, coder.off[T][S],solver.off[S]>verifier.off[T] 1, coder.off[T][S]>verifier.off[T] 1 |
| Algebra L5 | 18 | 89% | - | 3724 | 0 | solver.off[S]>verifier.off[T] 10, coder.off[T][S],solver.off[S]>verifier.off[T] 4, coder.off[T],solver.off[S]>verifier.off[T] 2 |
| Counting & Probability L4 | 8 | 100% | - | 4148 | 0 | solver.off[S]>verifier.off[T] 5, solver.off>verifier.off[T] 1, solver.off[S]>coder.off[T][S]>verifier.off[T] 1 |
| Counting & Probability L5 | 9 | 67% | - | 7778 | 0 | solver.off[S]>verifier.off[T] 5, coder.off[T][S],solver.off[S]>verifier.off[T] 4 |
| Geometry L4 | 5 | 100% | - | 3481 | 0 | solver.off[S]>verifier.off[T] 3, solver.off>verifier.off[T] 1, solver.off[S]>coder.off[T][S]>verifier.off[T] 1 |
| Geometry L5 | 7 | 43% | - | 10494 | 0 | coder.off[T][S],solver.off[S]>verifier.off[T] 3, solver.off[S]>coder.off[T][S]>verifier.off[T] 2, solver.off[S]>verifier.off[T] 1 |
| Intermediate Algebra L4 | 14 | 100% | - | 6144 | 0 | solver.off[S]>verifier.off[T] 7, coder.off[T][S],solver.off[S]>verifier.off[T] 7 |
| Intermediate Algebra L5 | 17 | 59% | - | 9583 | 0 | solver.off[S]>verifier.off[T] 6, coder.off[T][S],solver.off[S]>verifier.off[T] 5, solver.off[S]>coder.off[T][S]>verifier.off[T] 3 |
| Number Theory L4 | 9 | 100% | - | 3797 | 0 | solver.off[S]>verifier.off[T] 8, coder.off[T][S],solver.off[S]>verifier.off[T] 1 |
| Number Theory L5 | 16 | 81% | - | 4233 | 0 | solver.off[S]>verifier.off[T] 13, coder.off[T][S],solver.off[S]>verifier.off[T] 1, solver.off[S] 1 |
| Prealgebra L4 | 12 | 92% | - | 1988 | 0 | solver.off[S]>verifier.off[T] 9, solver.off>verifier.off[T] 1, solver.off[S]>coder.off[T][S]>verifier.off[T] 1 |
| Prealgebra L5 | 9 | 89% | - | 5147 | 0 | solver.off[S]>verifier.off[T] 6, coder.off[T][S],solver.off[S]>verifier.off[T] 2, solver.off[S] 1 |
| Precalculus L4 | 3 | 100% | - | 7461 | 0 | solver.off[S]>verifier.off[T] 1, coder.off[T][S],solver.off[S]>verifier.off[T] 1, solver.off[S]>coder.off[T][S]>verifier.off[T] 1 |
| Precalculus L5 | 6 | 67% | - | 11483 | 0 | solver.off[S]>coder.off[T][S]>verifier.off[T] 4, coder.off[T][S],solver.off[S]>verifier.off[T] 2 |

## Architectures the HR wrote
| architecture | uses | acc | mean cost |
|---|---|---|---|
| solver.off[S]>verifier.off[T] | 89 | 93% | 3418 |
| coder.off[T][S],solver.off[S]>verifier.off[T] | 32 | 72% | 9011 |
| solver.off[S]>coder.off[T][S]>verifier.off[T] | 13 | 85% | 9977 |
| coder.off[T],solver.off[S]>verifier.off[T] | 4 | 50% | 10041 |
| coder.off[T][S]>verifier.off[T] | 4 | 25% | 6307 |
| solver.off>verifier.off[T] | 3 | 100% | 2653 |
| solver.off[S] | 2 | 100% | 1026 |
| solver.off[S]>coder.off[T]>verifier.off[T] | 2 | 100% | 5579 |
| solver.off | 1 | 0% | 2725 |

## Nodes (employee.thinking)
answer correct = the node's own answer; hit budget = the reasoning was cut at the thinking budget; for nodes with inputs: changed = its answer differs from its inputs' majority.
| node | uses | answer correct | hit budget | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| verifier.off (with inputs) | 147 | 85% | 0% | 1993 | 29 | 13 | 4 |
| solver.off | 146 | 80% | 0% | 1924 | - | - | - |
| coder.off | 40 | 65% | 0% | 3162 | - | - | - |
| coder.off (with inputs) | 15 | 80% | 0% | 3114 | 6 | 4 | - |

## Leave-one-out on 60 questions with 2+ nodes
Remove the node (its consumers lose that input; a removed output hands over to its first input) and re-run: 'needed' = right becomes wrong; 'harmful' = wrong becomes right.
| removed | uses | needed | harmful | no effect | mean cost saved |
|---|---|---|---|---|---|
| solver.off (input) | 60 | 3 | 4 | 53 | 1987 |
| verifier.off (output) | 60 | 5 | 4 | 51 | 2148 |
| coder.off (input) | 17 | 2 | 3 | 12 | 4028 |

## Residual harness (what the HR gave each node)
| item | nodes given it | node answer correct when given | node answer correct otherwise |
|---|---|---|---|
| note | 345 | 81% | 67% |
| tool:check_answer | 147 | 85% | 77% |
| no tools (no Python) | 146 | 80% | 81% |
| skill:number_theory_counts | 101 | 76% | 82% |
| skill:quadratic_methods | 77 | 78% | 81% |
| tool:python | 55 | 69% | 83% |
| tool:simplify_exact | 15 | 80% | 80% |
| skill:inverse_functions | 9 | 89% | 80% |
| skill:state_simulation | 4 | 50% | 81% |
| tool:number_theory | 2 | 50% | 81% |
Notes: 345 nodes got one, mean 91 chars. Example: Isolate Q by cubing both sides appropriately or converting radicals to fractional exponents; handle Q >= 0 constraint.

## Organization wrong (23)
- [Intermediate Algebra L5] During the car ride home, Michael looks back at his recent math exams. A problem on Michael's calculus mid-term gets him starting thinking about a particular quadratic,\[x^2-sx+p,\]with roots $r_1$ and $r_2$. He notices that\[r_1+r_2=r_1^2+r_2^2=r_1^3+r_2^3=\cdots=r_1^{2007}+r_2^
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Determine that roots must be roots of unity (specifically 1 or -1) based on the ; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Enumerate all valid pairs of roots (r1, r2) that satisfy the condition and compu; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'])  # note: Verify the sum conditions for the selected pairs and confirm the arithmetic of t; return v; answered 0, correct 2
- [Prealgebra L5] The area of the shaded region is 78 square inches. All angles are right angles and all measurements are given in inches. What is the perimeter of the non-shaded region?

[asy]size(101);
filldraw(((0,0)--(0,8)--(10,8)--(10,-2)--(6,-2)--(6,0)--cycle^^(2.5,3)--(2.5,5)--(7.5,5)--(7.5
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Determine outer dimensions and hole dimensions from the diagram; set up equation; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute perimeter of non-shaded region using found side lengths and Python for a; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify area calculation and perimeter summation against original constraints.; return v; answered 18, correct 14
- [Intermediate Algebra L5] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver("off", skills=['inverse_functions'])  # note: Derive f(2^k) = 0 by setting a=b=2^(k-1). Use induction with a=2^k, b=2^k-2^j to; v = verifier("off", a, tools=['check_answer'])  # note: Verify f(2002) using derived recurrence and base cases.; return v; answered 2, correct 96
- [Counting & Probability L5] The number of increasing sequences of positive integers $a_1 \le a_2 \le a_3 \le \cdots \le a_{10} \le 2007$ such that $a_i-i$ is even for $1\le i \le 10$ can be expressed as ${m \choose n}$ for some positive integers $m > n$. Compute the remainder when $m$ is divided by 1000.
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Reduce to counting non-decreasing sequences of length 10 from {1,3,5,...,2007} v; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute N = 1004, k = 10, answer = C(N, k). Reduce m = N + k, check m mod 1000.; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify N = 1004, k = 10, m = 1014. Check 1014 mod 1000 = 14.; return v; answered 19, correct 8
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Solve d1*d2*d3 = r^3 * sqrt(2)*sqrt(3)*sqrt(4) ... wait, derive formula d1*d2*d3; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Implement exact solver for cubic/radical equation derived from distance constrai; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify each candidate radius satisfies the distance conditions exactly.; return v; answered 27, correct 2793
- [Intermediate Algebra L5] A nonzero polynomial with rational coefficients has all of the numbers \[1+\sqrt{2}, \; 2+\sqrt{3}, \;3+\sqrt{4},\; \dots, \;1000+\sqrt{1001}\]as roots. What is the smallest possible degree of such a polynomial?
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Count distinct minimal polynomials for each term 1000+sqrt(1001) by analyzing th; v = verifier("off", a, tools=['check_answer'])  # note: Verify that the count of distinct minimal polynomials equals the sum of degrees ; return v; answered 1, correct 1970
- [Number Theory L5] When the decimal $0.1\overline{23}$ is written as a fraction $\frac{a}{b}$ with $a$ and $b$ being positive integers with a greatest common divisor of 1, what is $a+b$?
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Convert 0.12323... to fraction using geometric series or algebraic manipulation;; v = verifier("off", a, tools=['check_answer'])  # note: Verify a, b are coprime and sum matches the derived fraction.; return v; answered 10, correct 556
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver("off", skills=['state_simulation'])  # note: Simulate the walk manually to find the pattern for the last opened locker.; b = coder("off", tools=['python'], skills=['state_simulation'])  # note: Implement a simulation in Python to verify the manual result for N=1024.; v = verifier("off", a, b, tools=['check_answer'])  # note: Check that the candidate answer satisfies the process for N=1024.; return v; answered 10, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Identify that shifting roots implies a relation between the polynomials; set up ; b = coder("off", a, tools=['python'], skills=['number_theory_counts'])  # note: Solve the resulting cubic equation for 'a' using Python to find exact integer so; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify that for each candidate pair (a, b), the roots of p(x) and q(x) satisfy t; return v; answered -16, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Count k from -10 to 10. Identify regions where lines form triangles. Sum valid c; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Verify arithmetic for total count using Python loop.; v = verifier("off", a, b, tools=['check_answer'])  # note: Confirm final sum matches constraints.; return v; answered 2, correct 660

## Most expensive correct questions (possible waste)
- [Precalculus L5, cost 16349] Let $a$ and $b$ be two 12th roots of unity, not necessarily distinct.  Find the number of different possible values of $(a + b)^{12}.$
  architecture: a = solver("off", skills=['number_theory_counts'])  # note: Count pairs (a,b) of 12th roots yielding distinct (a+b)^12; handle symmetry a <-; b = coder("off", a, tools=['python'], skills=['number_theory_counts'])  # note: Enumerate all 144 pairs, compute (a+b)^12, collect unique exact values using Pyt; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify count matches symmetry argument and check boundary cases a=b.; return v
- [Intermediate Algebra L4, cost 13974] Find the largest constant $m,$ so that for any positive real numbers $a,$ $b,$ $c,$ and $d,$
\[\sqrt{\frac{a}{b + c + d}} + \sqrt{\frac{b}{a + c + d}} + \sqrt{\frac{c}{a + b + d}} 
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Apply Cauchy-Schwarz to bound the sum from below; identify the infimum as variab; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Use numerical simulation with extreme values (e.g., one variable approaching 0, ; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'])  # note: Substitute the candidate limit value into the original inequality conditions to ; return v
- [Counting & Probability L4, cost 13948] Define a $\it{good\ word}$ as a sequence of letters that consists only of the letters $A$, $B$, and $C$ --- some of these letters may not appear in the sequence --- and in which $A
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Model as adjacency matrix power; compute (M^7)[0,0]+(M^7)[1,1]+(M^7)[2,2] where ; b = coder("off", a, tools=['python'], skills=['number_theory_counts'])  # note: Implement matrix exponentiation with integers to compute M^7 and sum diagonal en; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'])  # note: Verify matrix definition, exponentiation logic, and final sum against manual sma; return v
- [Intermediate Algebra L4, cost 11523] The equations $x^3 + Ax + 10 = 0$ and $x^3 + Bx^2 + 50 = 0$ have two roots in common.  Then the product of these common roots can be expressed in the form $a \sqrt[b]{c},$ where $a
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Use resultants or substitution to find product of common roots; express as simpl; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute exact radical form using sympy and sum a+b+c.; v = verifier("off", a, b, tools=['check_answer', 'simplify_exact'])  # note: Verify common roots satisfy both equations and check final sum.; return v
- [Precalculus L4, cost 11036] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\
  architecture: a = solver("off", skills=['quadratic_methods'])  # note: Identify roots as 8th roots of unity excluding 1; use symmetry to split polygon ; b = coder("off", tools=['python'], skills=['number_theory_counts'])  # note: Compute exact coordinates of vertices and use shoelace formula via Python to get; v = verifier("off", a, b, tools=['check_answer'])  # note: Verify symmetry arguments and check that the computed area matches the form (a +; return v