# Report (dev-A)

Organization: acc 88.0%, cost 4966/problem, of which the meta-agent 2933 (its prompt 4422 chars). Answered by the meta-agent itself: 69 (acc 100%). 9 distinct architectures, 0.9 nodes per problem. Fallback (unusable meta-agent output): 20.

## By category
| category | n | acc | cost | architectures |
|---|---|---|---|---|
| Algebra L4 | 17 | 100% | 3121 | answer 12, solver[T][S] 2, solver[T][S]>verifier[T] 2 |
| Algebra L5 | 18 | 100% | 3150 | answer 14, solver[T][S]>verifier[T] 3, solver[T][S]>verifier[T][S] 1 |
| Counting & Probability L4 | 8 | 100% | 3958 | answer 3, solver[T][S]>verifier[T] 3, solver[T][S]>verifier[T][S] 1 |
| Counting & Probability L5 | 9 | 89% | 6012 | answer 3, solver[T][S]>verifier[T] 3, coder[T][S]>verifier[T][S] 1 |
| Geometry L4 | 5 | 80% | 4180 | answer 2, solver[T] 2, solver[T][S]>verifier[T][S] 1 |
| Geometry L5 | 7 | 43% | 7486 | solver[T] 5, answer 1, solver[T][S]>verifier[T] 1 |
| Intermediate Algebra L4 | 14 | 100% | 4990 | answer 5, solver[T][S]>verifier[T] 4, solver[T] 3 |
| Intermediate Algebra L5 | 17 | 65% | 7077 | solver[T][S]>verifier[T] 5, solver[T] 5, answer 4 |
| Number Theory L4 | 9 | 100% | 4347 | answer 5, solver[T][S]>verifier[T] 2, solver[T][S]>verifier[T][S] 2 |
| Number Theory L5 | 16 | 88% | 5444 | answer 6, solver[T][S]>verifier[T] 4, coder[T][S]>verifier[T][S] 2 |
| Prealgebra L4 | 12 | 100% | 3077 | answer 9, solver[T][S]>verifier[T] 2, coder[T][S]>verifier[T] 1 |
| Prealgebra L5 | 9 | 100% | 5314 | answer 5, solver[S]>verifier[T] 1, coder[T][S]>verifier[T] 1 |
| Precalculus L4 | 3 | 67% | 6294 | solver[T] 2, solver[T][S]>verifier[T][S] 1 |
| Precalculus L5 | 6 | 50% | 9339 | solver[T][S]>verifier[T][S] 2, solver[T][S]>verifier[T] 2, coder[T][S]>verifier[T] 1 |

## Architectures
| architecture | uses | acc | mean cost |
|---|---|---|---|
| answer | 69 | 100% | 2944 |
| solver[T][S]>verifier[T] | 32 | 88% | 5914 |
| solver[T] | 20 | 40% | 7367 |
| solver[T][S]>verifier[T][S] | 15 | 93% | 7101 |
| coder[T][S]>verifier[T] | 6 | 100% | 7764 |
| solver[T][S] | 3 | 100% | 4351 |
| coder[T][S]>verifier[T][S] | 3 | 100% | 5877 |
| solver[S]>verifier[T] | 1 | 100% | 9342 |
| solver[T]>verifier[T][S] | 1 | 0% | 12012 |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| solver | 72 | 72% | 28% | 2486 | - | - | - |
| verifier (with inputs) | 58 | 90% | 9% | 1836 | 7 | 2 | - |
| coder | 9 | 100% | 0% | 2159 | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:python | 86 | 78% | 87% |
| tool:check_answer | 45 | 91% | 77% |
| skill:algebra_manipulation | 25 | 88% | 80% |
| skill:check_answer_form | 18 | 83% | 81% |
| skill:integer_equations | 10 | 80% | 81% |
| skill:counting_setup | 9 | 100% | 80% |
| tool:number_theory | 8 | 62% | 82% |
| tool:polynomial | 6 | 83% | 81% |
| skill:geometry_coordinates | 6 | 83% | 81% |
| skill:divisors_primes | 6 | 100% | 80% |
| tool:exact_solve | 4 | 75% | 81% |
| tool:counting | 4 | 100% | 81% |
| tool:coord_geometry | 3 | 67% | 82% |
| tool:brute_force | 3 | 100% | 81% |
| skill:modular | 3 | 67% | 82% |
| skill:trig_complex | 2 | 100% | 81% |
| skill:complement_and_pie | 2 | 100% | 81% |
| skill:geometry_synthetic | 1 | 100% | 81% |
| no tools (no Python) | 1 | 100% | 81% |
| skill:polynomials_vieta | 1 | 100% | 81% |
| skill:inequalities_extrema | 1 | 100% | 81% |
Never given: simplify_exact, sequence, probability, functions_sequences.

Meta-agent output problems: syntax error: invalid syntax (line 1) (4); line 1: expected `x = agent(inputs..., tools=[...], skills=[...])` (4); line 2: expected `x = agent(inputs..., tools=[...], skills=[...])` (4); line 3: expected `x = agent(inputs..., tools=[...], skills=[...])` (4); line 4: expected `x = agent(inputs..., tools=[...], skills=[...])` (3); syntax error: expected an indented block after 'for' statement on line 8 (line 8) (2)

## Wrong (18)
- [Intermediate Algebra L5] There is a unique polynomial $P(x)$ of degree $8$ with rational coefficients and leading coefficient $1,$ which has the number \[\sqrt{2} + \sqrt{3} + \sqrt{5}\]as a root. Compute $P(1).$
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python']); return v; answered 4, correct -71
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['check_answer']); return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver(tools=['number_theory'], skills=['modular']); v = verifier(a, tools=['check_answer']); return v; answered 32, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver(tools=['python']); return a; answered 2, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = solver(tools=['python']); return a; answered -2, correct 660
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = solver(tools=['python']); return a; answered 6, correct 810
- [Precalculus L4] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\frac{a + b \sqrt{c}}{d},$ where $a,$ $b,$ $c,$ $d$ are positive integers, in simplest form.  Find $a
  architecture: a = solver(tools=['python']); return a; answered 4, correct 8
- [Geometry L4] A line with slope of $-2$ intersects the positive $x$-axis at $A$ and the positive $y$-axis at $B$. A second line intersects the $x$-axis at $C(8,0)$ and the $y$-axis at $D$. The lines intersect at $E(4,4)$. What is the area of the shaded quadrilateral $OBEC$? [asy]
draw((0,-1)--
  architecture: a = solver(tools=['python']); return a; answered 36, correct 40
- [Number Theory L5] Let $\tau (n)$ denote the number of positive integer divisors of $n$ (including $1$ and $n$). Find the sum of the six least positive integers $n$ that are solutions to $\tau (n) + \tau (n+1) = 7$.
  architecture: a = solver(tools=['python']); v = verifier(a, tools=['python'], skills=['check_answer_form']); return v; answered 3721, correct 540
- [Geometry L5] Given a point $P$ on a triangular piece of paper $ABC,\,$ consider the creases that are formed in the paper when $A, B,\,$ and $C\,$ are folded onto $P.\,$ Let us call $P$ a fold point of $\triangle ABC\,$ if these creases, which number three unless $P$ is one of the vertices, do
  architecture: a = solver(tools=['python']); return a; answered 0, correct 597

## Most expensive correct problems (possible waste)
- [Precalculus L5, cost 11406] Three unit circles are drawn so they are mutually tangent, as shown below.  A blue circle that is externally tangent to all three unit circles is drawn.  Finally, three red circles
  architecture: a = coder(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['check_answer']); return v
- [Intermediate Algebra L5, cost 10865] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver(tools=['number_theory'], skills=['integer_equations']); v = verifier(a, tools=['check_answer']); return v
- [Precalculus L5, cost 10688] Let $a$ and $b$ be two 12th roots of unity, not necessarily distinct.  Find the number of different possible values of $(a + b)^{12}.$
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python', 'check_answer'], skills=['check_answer_form']); return v
- [Intermediate Algebra L5, cost 10404] During the car ride home, Michael looks back at his recent math exams. A problem on Michael's calculus mid-term gets him starting thinking about a particular quadratic,\[x^2-sx+p,\
  architecture: a = solver(tools=['polynomial'], skills=['algebra_manipulation']); v = verifier(a, tools=['check_answer']); return v
- [Prealgebra L5, cost 9935] In the diagram, $AB,$ $BC,$ $CD,$ $DE,$ $EF,$ $FG,$ $GH,$ and $HK$ all have length $4,$ and all angles are right angles, with the exception of the angles at $D$ and $F.$

[asy]
dra
  architecture: a = coder(tools=['python'], skills=['geometry_coordinates']); v = verifier(a, tools=['check_answer']); return v