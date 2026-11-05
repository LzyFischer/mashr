# Report (dev-A)

Organization: acc 90.0%, cost 6800/problem, of which the meta-agent 3259 (its prompt 6785 chars). 9 distinct architectures, 1.8 nodes per problem. Fallback (unusable meta-agent output): 1.

## By category
| category | n | acc | cost | architectures |
|---|---|---|---|---|
| Algebra L4 | 17 | 100% | 4409 | solver[T][S] 9, solver[T][S]>verifier[T][S] 7, solver[S] 1 |
| Algebra L5 | 18 | 100% | 5336 | solver[T][S]>verifier[T][S] 12, solver[T][S] 4, solver[S]>verifier[T] 1 |
| Counting & Probability L4 | 8 | 88% | 5042 | solver[T][S]>verifier[T][S] 5, solver[T][S] 3 |
| Counting & Probability L5 | 9 | 89% | 7770 | solver[T][S]>verifier[T][S] 4, solver[T][S]>verifier[T] 2, solver[S]>verifier[T][S] 1 |
| Geometry L4 | 5 | 100% | 5736 | solver[T][S]>verifier[T][S] 3, solver[T][S] 2 |
| Geometry L5 | 7 | 57% | 9438 | solver[T][S]>verifier[T][S] 6, solver[T] 1 |
| Intermediate Algebra L4 | 14 | 100% | 7021 | solver[T][S]>verifier[T][S] 10, solver[S]>verifier[T][S] 2, solver[S] 1 |
| Intermediate Algebra L5 | 17 | 65% | 10016 | solver[T][S]>verifier[T][S] 13, solver[T][S]>verifier[T] 3, solver[S]>verifier[T][S] 1 |
| Number Theory L4 | 9 | 100% | 6549 | solver[T][S]>verifier[T][S] 7, solver[T][S]>verifier[T] 1, solver[T]>verifier[T] 1 |
| Number Theory L5 | 16 | 94% | 7474 | solver[T][S]>verifier[T][S] 11, solver[T][S] 3, solver[T][S]>verifier[T] 2 |
| Prealgebra L4 | 12 | 100% | 3895 | solver[T][S] 9, solver[T][S]>verifier[T][S] 2, solver[S] 1 |
| Prealgebra L5 | 9 | 100% | 6582 | solver[T][S]>verifier[T][S] 5, solver[T][S] 3, solver[T][S]>verifier[T] 1 |
| Precalculus L4 | 3 | 67% | 8541 | solver[T][S]>verifier[T][S] 2, solver[T][S]>verifier[T] 1 |
| Precalculus L5 | 6 | 67% | 10880 | solver[T][S]>verifier[T][S] 4, solver[T][S]>verifier[T] 2 |

## Architectures
| architecture | uses | acc | mean cost |
|---|---|---|---|
| solver[T][S]>verifier[T][S] | 91 | 89% | 7560 |
| solver[T][S] | 33 | 100% | 4052 |
| solver[T][S]>verifier[T] | 14 | 79% | 8361 |
| solver[S]>verifier[T][S] | 4 | 75% | 9392 |
| solver[S] | 3 | 100% | 3439 |
| solver[T]>verifier[T] | 2 | 100% | 5261 |
| solver[S]>verifier[T] | 1 | 100% | 4975 |
| solver[T][S],verifier[T][S] | 1 | 100% | 9433 |
| solver[T] | 1 | 0% | 8381 |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| solver | 150 | 83% | 19% | 2001 | - | - | - |
| verifier (with inputs) | 112 | 88% | 12% | 2046 | 24 | 11 | 1 |
| verifier | 1 | 100% | 0% | 1982 | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:python | 247 | 86% | 75% |
| skill:algebra_manipulation | 106 | 89% | 83% |
| skill:counting_setup | 36 | 89% | 85% |
| skill:divisors_primes | 28 | 89% | 85% |
| skill:geometry_coordinates | 26 | 77% | 86% |
| tool:check_answer | 21 | 71% | 86% |
| skill:integer_equations | 20 | 75% | 86% |
| skill:modular | 14 | 71% | 86% |
| skill:check_answer_form | 13 | 62% | 86% |
| tool:number_theory | 12 | 83% | 85% |
| no tools (no Python) | 8 | 75% | 85% |
| skill:inequalities_extrema | 8 | 88% | 85% |
| skill:polynomials_vieta | 7 | 71% | 86% |
| skill:geometry_synthetic | 6 | 67% | 86% |
| tool:counting | 6 | 100% | 85% |
| skill:functions_sequences | 6 | 100% | 85% |
| skill:trig_complex | 4 | 100% | 85% |
| tool:exact_solve | 4 | 100% | 85% |
| tool:coord_geometry | 2 | 100% | 85% |
| tool:polynomial | 2 | 50% | 85% |
| tool:brute_force | 1 | 0% | 85% |
| skill:complement_and_pie | 1 | 100% | 85% |
| skill:probability | 1 | 100% | 85% |
| tool:simplify_exact | 1 | 100% | 85% |
Never given: sequence.

Meta-agent output problems: minor: line 1: unknown tools/skills ['geometry_coordinates'] dropped (2); minor: line 2: unknown tools/skills ['check_answer'] dropped (2); minor: line 1: unknown tools/skills ['polynomials_vieta', 'algebra_manipulation'] dropped (2); minor: line 1: unknown tools/skills ['algebra_manipulation'] dropped (1); minor: line 1: unknown tools/skills ['combinatorics'] dropped (1); minor: line 1: unknown tools/skills ['number_theory'] dropped (1)

## Wrong (15)
- [Intermediate Algebra L5] The real function $f$ has the property that, whenever $a,$ $b,$ $n$ are positive integers such that $a + b = 2^n,$ the equation
\[f(a) + f(b) = n^2\]holds.  What is $f(2002)$?
  architecture: a = solver(tools=['python'], skills=['integer_equations']); v = verifier(a, tools=['python', 'check_answer'], skills=['integer_equations', 'check_answer_form']); return v; answered 1, correct 96
- [Precalculus L5] A sphere, lying in the octant where all the coordinates are nonnegative, is tangent to the $xy$-, $xz$-, and $yz$-plane.  A point on the sphere has distances of 50, 29, and 41 from the $xy$-, $xz$-, and $yz$-planes, respectively.  Enter all possible values for the radius of the s
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python'], skills=['check_answer_form']); return v; answered 27, correct 2793
- [Counting & Probability L5] A bored student walks down a hall that contains a row of closed lockers, numbered $1$ to $1024$. He opens the locker numbered 1, and then alternates between skipping and opening each locker thereafter. When he reaches the end of the hall, the student turns around and starts back.
  architecture: a = solver(tools=['python'], skills=['modular']); v = verifier(a, tools=['python'], skills=['modular']); return v; answered 2, correct 342
- [Intermediate Algebra L5] Real numbers $r$ and $s$ are roots of $p(x)=x^3+ax+b$, and $r+4$ and $s-3$ are roots of $q(x)=x^3+ax+b+240$. Enter all possible values of $b,$ separated by commas.
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python'], skills=['algebra_manipulation']); return v; answered 42, correct -33090
- [Geometry L5] The graphs of the equations
$y=k, \qquad y=\sqrt{3}x+2k, \qquad y=-\sqrt{3}x+2k,$
are drawn in the coordinate plane for $k=-10,-9,-8,\ldots,9,10.\,$ These 63 lines cut part of the plane into equilateral triangles of side $2/\sqrt{3}.\,$ How many such triangles are formed?
  architecture: a = solver(tools=['python'], skills=['counting_setup']); v = verifier(a, tools=['python'], skills=['counting_setup']); return v; answered 2, correct 660
- [Intermediate Algebra L5] Consider the set of 30 parabolas defined as follows: all parabolas have as focus the point $(0,0)$ and the directrix lines have the form $y=ax+b$ with $a$ and $b$ integers such that $a\in \{-2,-1,0,1,2\}$ and $b\in \{-3,-2,-1,1,2,3\}$. No three of these parabolas have a common po
  architecture: a = solver(tools=['python', 'check_answer'], skills=['modular', 'geometry_coordinates']); v = verifier(a, tools=['python', 'check_answer'], skills=['modular', 'geometry_coordinates']); return v; answered -6, correct 810
- [Precalculus L4] Let $P$ be the convex polygon in the complex plane whose vertices are the roots of
\[z^7 + z^6 + z^5 + z^4 + z^3 + z^2 + z + 1 = 0.\]The area of $P$ can be expressed in the form $\frac{a + b \sqrt{c}}{d},$ where $a,$ $b,$ $c,$ $d$ are positive integers, in simplest form.  Find $a
  architecture: a = solver(tools=['python'], skills=['polynomials_vieta', 'geometry_coordinates']); v = verifier(a, tools=['python']); return v; answered 90, correct 8
- [Number Theory L5] Let $\tau (n)$ denote the number of positive integer divisors of $n$ (including $1$ and $n$). Find the sum of the six least positive integers $n$ that are solutions to $\tau (n) + \tau (n+1) = 7$.
  architecture: a = solver(tools=['number_theory', 'check_answer', 'python'], skills=['divisors_primes', 'integer_equations']); v = verifier(a, tools=['python', 'check_answer'], skills=['divisors_primes', 'integer_equations']); return v; answered 6, correct 540
- [Geometry L5] Given a point $P$ on a triangular piece of paper $ABC,\,$ consider the creases that are formed in the paper when $A, B,\,$ and $C\,$ are folded onto $P.\,$ Let us call $P$ a fold point of $\triangle ABC\,$ if these creases, which number three unless $P$ is one of the vertices, do
  architecture: a = solver(tools=['python'], skills=['geometry_synthetic', 'check_answer_form']); v = verifier(a, tools=['python'], skills=['geometry_synthetic', 'check_answer_form']); return v; answered 90, correct 597
- [Precalculus L5] A prism is constructed so that its vertical edges are parallel to the $z$-axis.  Its cross-section is a square of side length 10.

[asy]
import three;

size(180);
currentprojection = perspective(6,3,2);

triple A, B, C, D, E, F, G, H;

A = (1,1,0);
B = (1,-1,0);
C = (-1,-1,0);
D 
  architecture: a = solver(tools=['python'], skills=['geometry_coordinates']); v = verifier(a, tools=['python']); return v; answered -7, correct 225

## Most expensive correct problems (possible waste)
- [Number Theory L5, cost 15080] Let $N$ be the number of ways to write $2010$ in the form $2010 = a_3 \cdot 10^3 + a_2 \cdot 10^2 + a_1 \cdot 10 + a_0$, where the $a_i$'s are integers, and $0 \le a_i \le 99$. An 
  architecture: a = solver(tools=['python'], skills=['counting_setup']); v = verifier(a, tools=['python'], skills=['counting_setup']); return v
- [Precalculus L5, cost 13818] Find the number of ordered quadruples $(a,b,c,d)$ of real numbers such that
\[\begin{pmatrix} a & b \\ c & d \end{pmatrix}^2 = \begin{pmatrix} c & a \\ d & b \end{pmatrix}.\]
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python'], skills=['algebra_manipulation']); return v
- [Precalculus L5, cost 11138] Three unit circles are drawn so they are mutually tangent, as shown below.  A blue circle that is externally tangent to all three unit circles is drawn.  Finally, three red circles
  architecture: a = solver(tools=['python'], skills=['algebra_manipulation']); v = verifier(a, tools=['python']); return v
- [Geometry L5, cost 11128] Square $ABCD$ has center $O,\ AB=900,\ E$ and $F$ are on $AB$ with $AE<BF$ and $E$ between $A$ and $F, m\angle EOF =45^\circ,$ and $EF=400.$ Given that $BF=p+q\sqrt{r},$ where $p,q
  architecture: a = solver(tools=['python'], skills=['geometry_coordinates', 'algebra_manipulation']); v = verifier(a, tools=['python'], skills=['geometry_coordinates', 'algebra_manipulation']); return v
- [Precalculus L5, cost 11090] Let $a$ and $b$ be two 12th roots of unity, not necessarily distinct.  Find the number of different possible values of $(a + b)^{12}.$
  architecture: a = solver(tools=['python', 'number_theory'], skills=['modular', 'check_answer_form']); v = verifier(a, tools=['python'], skills=['modular']); return v