# Report (dev-A)

Organization: acc 90.0%, cost 6631/problem, of which the meta-agent 3304 (its prompt 6071 chars). 6 distinct architectures, 1.7 nodes per problem. Fallback (unusable meta-agent output): 2.

## By category
| category | n | acc | cost | architectures |
|---|---|---|---|---|
| Algebra L4 | 17 | 100% | 4398 | solver[T][S] 9, solver[T][S]>verifier[T][S] 3, solver[T][S]>verifier[T] 3 |
| Algebra L5 | 18 | 94% | 5226 | solver[T][S]>verifier[T][S] 8, solver[T][S] 6, solver[T][S]>verifier[T] 3 |
| Counting & Probability L4 | 8 | 100% | 5205 | solver[T][S]>verifier[T] 4, solver[T][S] 2, solver[T][S]>verifier[T][S] 1 |
| Counting & Probability L5 | 9 | 89% | 7460 | solver[T][S]>verifier[T][S] 7, solver[T][S]>verifier[T] 2 |
| Geometry L4 | 5 | 100% | 5668 | solver[T][S] 2, solver[T][S]>verifier[T][S] 2, solver[S] 1 |
| Geometry L5 | 7 | 57% | 9588 | solver[T][S]>verifier[T] 4, solver[T][S]>verifier[T][S] 2, solver[T] 1 |
| Intermediate Algebra L4 | 14 | 100% | 7366 | solver[T][S]>verifier[T][S] 9, solver[T][S]>verifier[T] 4, solver[S] 1 |
| Intermediate Algebra L5 | 17 | 65% | 9133 | solver[T][S]>verifier[T] 12, solver[T][S]>verifier[T][S] 4, solver[T][S] 1 |
| Number Theory L4 | 9 | 100% | 6134 | solver[T][S]>verifier[T] 4, solver[T][S]>verifier[T][S] 3, solver[T][S] 2 |
| Number Theory L5 | 16 | 88% | 7114 | solver[T][S]>verifier[T][S] 10, solver[T][S]>verifier[T] 4, solver[T] 1 |
| Prealgebra L4 | 12 | 100% | 3985 | solver[T][S] 8, solver[S] 3, solver[T][S]>verifier[T] 1 |
| Prealgebra L5 | 9 | 100% | 6497 | solver[T][S]>verifier[T][S] 4, solver[T][S]>verifier[T] 2, solver[T][S] 2 |
| Precalculus L4 | 3 | 67% | 8823 | solver[S]>verifier[T][S] 1, solver[T][S]>verifier[T] 1, solver[T][S]>verifier[T][S] 1 |
| Precalculus L5 | 6 | 83% | 10243 | solver[T][S]>verifier[T] 4, solver[T][S]>verifier[T][S] 2 |

## Architectures
| architecture | uses | acc | mean cost |
|---|---|---|---|
| solver[T][S]>verifier[T][S] | 56 | 98% | 6942 |
| solver[T][S]>verifier[T] | 48 | 77% | 8457 |
| solver[T][S] | 33 | 94% | 4255 |
| solver[S] | 10 | 100% | 3826 |
| solver[T] | 2 | 50% | 7998 |
| solver[S]>verifier[T][S] | 1 | 100% | 5355 |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| solver | 150 | 85% | 17% | 1959 | - | - | - |
| verifier (with inputs) | 105 | 89% | 11% | 1954 | 19 | 9 | 1 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:python | 182 | 88% | 82% |
| skill:algebra_manipulation | 97 | 90% | 84% |
| tool:check_answer | 75 | 85% | 87% |
| skill:counting_setup | 26 | 85% | 86% |
| skill:integer_equations | 24 | 83% | 87% |
| skill:divisors_primes | 23 | 96% | 85% |
| skill:check_answer_form | 21 | 90% | 86% |
| skill:geometry_coordinates | 19 | 68% | 88% |
| tool:exact_solve | 14 | 93% | 86% |
| tool:number_theory | 13 | 92% | 86% |
| skill:polynomials_vieta | 12 | 75% | 87% |
| no tools (no Python) | 11 | 100% | 86% |
| tool:polynomial | 6 | 67% | 87% |
| tool:counting | 6 | 67% | 87% |
| skill:trig_complex | 5 | 60% | 87% |
| skill:modular | 5 | 100% | 86% |
| tool:simplify_exact | 5 | 60% | 87% |
| tool:coord_geometry | 4 | 50% | 87% |
| skill:inequalities_extrema | 4 | 100% | 86% |
| tool:brute_force | 3 | 67% | 87% |
| skill:complement_and_pie | 3 | 67% | 87% |
| skill:geometry_synthetic | 2 | 100% | 86% |
| skill:functions_sequences | 2 | 100% | 86% |
| skill:probability | 2 | 100% | 86% |
Never given: sequence.

Meta-agent output problems: minor: line 1: unknown tools/skills ['number_theory'] dropped (2); syntax error: expected an indented block after function definition on line 3 (line 3) (1); no return; using the last node (1); minor: line 1: unknown tools/skills ['geometry_coordinates'] dropped (1); minor: line 2: unknown tools/skills ['number_theory'] dropped (1); minor: line 1: unknown tools/skills ['algebra_manipulation'] dropped (1)

## Wrong (15)
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['check_answer']); return v; answered 27, correct 2793
- [Intermediate Algebra L5] Let $(a_1, b_1),$ $(a_2, b_2),$ $\dots,$ $(a_n, b_n)$ be the real solutions to
\begin{align*}
a + \frac{17a + 6b}{a^2 + b^2} &= 6, \\
b + \frac{6a - 17b}{a^2 + b^2} &= 0.
\end{align*}Find $a_1 + b_1 + a_2 + b_2 + \dots + a_n + b_n.$

Hint: Use complex numbers.
  architecture: a = solver(tools=['polynomial', 'python'], skills=['trig_complex', 'polynomials_vieta', 'algebra_manipulation']); v = verifier(a, tools=['python', 'check_answer'], skills=['trig_complex', 'algebra_manipulation', 'check_answer_form']); return v; answered 2, correct 6
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver(tools=['python'], skills=['counting_setup']); v = verifier(a, tools=['check_answer']); return v; answered 40, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver(tools=['python', 'polynomial'], skills=['algebra_manipulation']); return a; answered 90, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = solver(tools=['counting'], skills=['complement_and_pie']); v = verifier(a, tools=['counting']); return v; answered 441, correct 660
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = solver(tools=['python'], skills=['counting_setup']); v = verifier(a, tools=['check_answer']); return v; answered -1, correct 810
- [Precalculus L4] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\frac{a + b \sqrt{c}}{d},$ where $a,$ $b,$ $c,$ $d$ are positive integers, in simplest form.  Find $a
  architecture: a = solver(tools=['python', 'simplify_exact'], skills=['geometry_coordinates', 'algebra_manipulation']); v = verifier(a, tools=['check_answer', 'simplify_exact']); return v; answered 10, correct 8
- [Number Theory L5] Let $\tau (n)$ denote the number of positive integer divisors of $n$ (including $1$ and $n$). Find the sum of the six least positive integers $n$ that are solutions to $\tau (n) + \tau (n+1) = 7$.
  architecture: a = solver(tools=['number_theory', 'python'], skills=['divisors_primes', 'integer_equations']); v = verifier(a, tools=['check_answer']); return v; answered 37, correct 540
- [Geometry L5] Given a point $P$ on a triangular piece of paper $ABC,\,$ consider the creases that are formed in the paper when $A, B,\,$ and $C\,$ are folded onto $P.\,$ Let us call $P$ a fold point of $\triangle ABC\,$ if these creases, which number three unless $P$ is one of the vertices, do
  architecture: a = solver(tools=['python'], skills=['geometry_coordinates', 'check_answer_form']); v = verifier(a, tools=['check_answer']); return v; answered 3, correct 597
- [Algebra L5] How many zeros are in the expansion of $999,\!999,\!999,\!998^2$?
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); return a; answered 12, correct 11

## Most expensive correct problems (possible waste)
- [Precalculus L5, cost 14245] Let $a$ and $b$ be two 12th roots of unity, not necessarily distinct.  Find the number of different possible values of $(a + b)^{12}.$
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation', 'polynomials_vieta']); v = verifier(a, tools=['check_answer'], skills=['modular']); return v
- [Intermediate Algebra L4, cost 13799] The equations $x^3 + Ax + 10 = 0$ and $x^3 + Bx^2 + 50 = 0$ have two roots in common.  Then the product of these common roots can be expressed in the form $a \sqrt[b]{c},$ where $a
  architecture: a = solver(tools=['python'], skills=['polynomials_vieta', 'algebra_manipulation']); v = verifier(a, tools=['python']); return v
- [Intermediate Algebra L5, cost 12319] Find the sum of all complex numbers $z$ that satisfy
\[z^3 + z^2 - |z|^2 + 2z = 0.\]
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['check_answer']); return v
- [Intermediate Algebra L5, cost 12073] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver(tools=['python'], skills=['integer_equations']); v = verifier(a, tools=['check_answer']); return v
- [Geometry L5, cost 11085] Square $ABCD$ has center $O,\ AB=900,\ E$ and $F$ are on $AB$ with $AE<BF$ and $E$ between $A$ and $F, m\angle EOF =45^\circ,$ and $EF=400.$ Given that $BF=p+q\sqrt{r},$ where $p,q
  architecture: a = solver(tools=['python'], skills=['geometry_coordinates']); v = verifier(a, tools=['check_answer']); return v