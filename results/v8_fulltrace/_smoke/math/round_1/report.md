# Report (dev-A)

Organization: acc 87.5% (meta-agent prompt 4534 chars; roles 276 chars). 3 distinct architectures, 1.8 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| Algebra L4 | 3 | 100% | solver[T][S]>verifier[T][S] 2, solver[T][S] 1 |
| Algebra L5 | 1 | 100% | solver[T][S] 1 |
| Counting & Probability L5 | 1 | 100% | solver[T][S]>verifier[T][S] 1 |
| Intermediate Algebra L4 | 1 | 100% | solver[T][S],verifier[T][S] 1 |
| Intermediate Algebra L5 | 2 | 50% | solver[T][S]>verifier[T][S] 2 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| solver[T][S]>verifier[T][S] | 5 | 80% |
| solver[T][S] | 2 | 100% |
| solver[T][S],verifier[T][S] | 1 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| solver | 8 | 88% | 12% | - | - | - |
| verifier (with inputs) | 5 | 80% | 20% | 1 | - | - |
| verifier | 1 | 100% | 0% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:python | 10 | 80% | 100% |
| skill:algebra_manipulation | 8 | 88% | 83% |
| tool:check_answer | 6 | 83% | 88% |
| tool:simplify_exact | 5 | 80% | 89% |
| skill:check_answer_form | 5 | 80% | 89% |
| tool:exact_solve | 2 | 100% | 83% |
| tool:polynomial | 2 | 50% | 92% |
| skill:polynomials_vieta | 2 | 50% | 92% |
| skill:geometry_coordinates | 2 | 100% | 83% |
| tool:number_theory | 1 | 100% | 85% |
| skill:integer_equations | 1 | 100% | 85% |
| tool:counting | 1 | 100% | 85% |
| skill:counting_setup | 1 | 100% | 85% |
| tool:coord_geometry | 1 | 100% | 85% |
Never given: brute_force, sequence, complement_and_pie, probability, modular, divisors_primes, functions_sequences, inequalities_extrema, geometry_synthetic, trig_complex.

Meta-agent output problems: line 1: input 'problem' is not a node defined above (1); minor: line 1: unknown tools/skills ['algebra_manipulation'] dropped (1)

## Wrong (1)
- A6 [Intermediate Algebra L5] answered 2; correct -71; team: s = solver(tools=['python', 'polynomial', 'simplify_exact'], skills=['algebra_manipulation', 'polynomials_vieta']); v = verifier(s, tools=['python', 'check_answer'], skills=['check_answer_form']); return v

## Traces of the wrong problems (1 of 1; node outputs over 6000 chars are cut in the middle)
### A6 [Intermediate Algebra L5]
Problem: There is a unique polynomial $P(x)$ of degree $8$ with rational coefficients and leading coefficient $1,$ which has the number \[\sqrt{2} + \sqrt{3} + \sqrt{5}\]as a root. Compute $P(1).$
Correct: -71
Team: s = solver(tools=['python', 'polynomial', 'simplify_exact'], skills=['algebra_manipulation', 'polynomials_vieta']); v = verifier(s, tools=['python', 'check_answer'], skills=['check_answer_form']); return v
#### node s = solver(inputs=[], tools=['python', 'polynomial', 'simplify_exact'], skills=['algebra_manipulation', 'polynomials_vieta']) -> 1369 (wrong, cut at the token limit)
```
To find the value of $P(1)$, we first need to determine the unique monic polynomial $P(x)$ with rational coefficients that has $\alpha = \sqrt{2} + \sqrt{3} + \sqrt{5}$ as a root.

Let $\alpha = \sqrt{2} + \sqrt{3} + \sqrt{5}$.
We want to eliminate the radicals to find a polynomial equation with rational coefficients satisfied by $\alpha$.

**Step 1: Isolate one radical**
Let's group terms to isolate one square root.
$\alpha - (\sqrt{2} + \sqrt{3}) = \sqrt{5}$
Square both sides:
$(\alpha - (\sqrt{2} + \sqrt{3}))^2 = 5$
$\alpha^2 - 2\alpha(\sqrt{2} + \sqrt{3}) + (\sqrt{2} + \sqrt{3})^2 = 5$
$\alpha^2 - 2\alpha(\sqrt{2} + \sqrt{3}) + (2 + 3 + 2\sqrt{6}) = 5$
$\alpha^2 + 5 + 2\sqrt{6} - 2\alpha(\sqrt{2} + \sqrt{3}) = 5$
$\alpha^2 + 2\sqrt{6} = 2\alpha(\sqrt{2} + \sqrt{3})$

**Step 2: Eliminate the remaining radicals**
Square both sides again.
$(\alpha^2 + 2\sqrt{6})^2 = (2\alpha(\sqrt{2} + \sqrt{3}))^2$
$\alpha^4 + 4\alpha^2\sqrt{6} + 4(6) = 4\alpha^2 (2 + 3 + 2\sqrt{6})$
$\alpha^4 + 4\alpha^2\sqrt{6} + 24 = 4\alpha^2 (5 + 2\sqrt{6})$
$\alpha^4 + 4\alpha^2\sqrt{6} + 24 = 20\alpha^2 + 8\alpha^2\sqrt{6}$

Move terms with $\sqrt{6}$ to one side and rational terms to the other:
$24 - 20\alpha^2 = 8\alpha^2\sqrt{6} - 4\alpha^2\sqrt{6}$
$24 - 20\alpha^2 = 4\alpha^2\sqrt{6}$

Divide by 4:
$6 - 5\alpha^2 = \alpha^2\sqrt{6}$

**Step 3: Final squaring**
Square both sides one last time to eliminate $\sqrt{6}$:
$(6 - 5\alpha^2)^2 = (\alpha^2\sqrt{6})^2$
$36 - 60\alpha^2 + 25\alpha^4 = 6\alp
[... 11178 chars omitted ...]
t{2} + \epsilon_2\sqrt{3} + \epsilon_3\sqrt{5})$.
This product is known to be 576? Or something else?
Let's calculate the product of all 8 conjugates.
Consider the norm $N(\alpha) = \prod \sigma(\alpha)$.
In $\mathbb{Q}(\sqrt{2}, \sqrt{3}, \sqrt{5})$, the norm of $\sqrt{2}+\sqrt{3}+\sqrt{5}$.
Let's use the property that $P(x) = \prod (x - r_i)$.
Constant term $P(0) = \prod (-r_i) = \prod r_i$.
Let's compute the product of $(\epsilon_1\sqrt{2} + \epsilon_2\sqrt{3} + \epsilon_3\sqrt{5})$.
Group terms: $(\sqrt{2}+\sqrt{3}+\sqrt{5})(\sqrt{2}+\sqrt{3}-\sqrt{5}) = (5+2\sqrt{6}) - 5 = 2\sqrt{6}$.
$(\sqrt{2}-\sqrt{3}+\sqrt{5})(\sqrt{2}-\sqrt{3}-\sqrt{5}) = (2+3-2\sqrt{6}) - 5 = 5-2\sqrt{6} - 5 = -2\sqrt{6}$.
$(\sqrt{2}-\sqrt{3}-\sqrt{5})(-\sqrt{2}+\sqrt{3}+\sqrt{5}) = -(\sqrt{2}-\sqrt{3}-\sqrt{5})(\sqrt{2}-\sqrt{3}-\sqrt{5})$? No.
Let's pair them properly.
Pairs:
1. $(\sqrt{2}+\sqrt{3}+\sqrt{5})(\sqrt{2}+\sqrt{3}-\sqrt{5}) = 2\sqrt{6}$.
2. $(\sqrt{2}-\sqrt{3}+\sqrt{5})(\sqrt{2}-\sqrt{3}-\sqrt{5}) = -2\sqrt{6}$.
3. $(-\sqrt{2}+\sqrt{3}+\sqrt{5})(-\sqrt{2}+\sqrt{3}-\sqrt{5}) = -2\sqrt{6}$.
4. $(-\sqrt{2}-\sqrt{3}+\sqrt{5})(-\sqrt{2}-\sqrt{3}-\sqrt{5}) = 2\sqrt{6}$.
Product of these 4 pairs: $(2\sqrt{6})(-2\sqrt{6})(-2\sqrt{6})(2\sqrt{6}) = 16 \cdot 36 = 576$.
So the constant term is indeed $+576$.
My derived polynomial $x^8 - 40x^6 + 352x^4 - 960x^2 + 576$ has constant term 576. This matches.

Now check the coefficient of $x^2$.
$P(x) = x^8 + c_6 x^6 + c_4 x^4 + c_2 x^2 + 576$.
Sum of roots squared? No, $c_6 = - \sum r_i^2$.
$r_i^2 = (\epsilon_1\sqrt{2} + \epsilon_2\sqrt{3} + \epsilon_3\sqrt{5})^2 = 2+3+5 + 2(\epsilon_1\epsilon_2\sqrt{6} + \epsilon_1\epsilon_3\sqrt{10} + \epsilon_2\epsilon_3\sqrt{15}) = 10 + 2(\dots)$.
Sum of $r_i^2$ over all 8 combinations:
The cross terms $\sqrt{6}$ etc. sum to 0 because $\sum \epsilon_i \epsilon_j = 0$.
So $\sum r_i^2 = 8 \times 10 = 80$.
$c_6 = -80$.
Wait, my derived polynomial had $-40$. Why?
Ah, the polynomial is $x^8 - (\sum r_i) x^7 + \dots$.
But the polynomial is even, so odd coefficients are 0.
The coefficient $c_6$ corresponds to the term $x^6$.
$P(x) = \prod (x^2 - r_i^2)$.
Let $y = x^2$. Then $Q(y) = \prod_{i=1}^4 (y - r_i^2)$? No, there are 8 roots, so 4 distinct values for $x^2$?
No, $r_i^2$ takes values based on the signs.
$r_{\epsilon}^2 = 10 + 2(\epsilon_1\epsilon_2\sqrt{6} + \epsilon_1\epsilon_3\sqrt{10} + \epsilon_2\epsilon_3\sqrt{15})$.
There are 8 such values. They are not just 4.
Let's list $r^2$:
Signs of $(\epsilon_1, \epsilon_2, \epsilon_3)$:
1. (+,+,+): $10 + 2(\sqrt{6}+\sqrt{10}+\sqrt{15})$
2. (+,+,-): $10 + 2(\sqrt{6}-\sqrt{10}-\sqrt{15})$
3. (+,-,+): $10 + 2(-\sqrt{6}+\sqrt{10}-\sqrt{15})$
4. (+,-,-): $10 + 2(-\sqrt{6}-\sqrt{10}+\sqrt{15})$
5. (-,+,+): $10 + 2(-\sqrt{6}-\sqrt{10}-\sqrt{15})$
6. (-,+,-): $10 + 2(-\sqrt{6}+\sqrt{10}-\sqrt{15})$ -- Wait, $\epsilon_1\epsilon_2 = -\sqrt{6}/2$? No.
$\epsilon_1\epsilon_2$ for (-,+,+) is $-1$. So $-\sqrt{6}$.
Let's re-evaluate the sum of $r_i^6$? No.
The polynomial in $x$ is $P(x) = \prod_{\epsilon} (x - r_\epsilon)$.
Since $P(x)$ is even, $P(x) = Q(x^2)$.
$Q(y) = \prod_{\epsilon} (x - r_\epsilon)$ evaluated at $x=\sqrt{y}$? No.
$P(x) = \prod_{\epsilon} (x - r_\epsilon)$.
Since $r_{-\epsilon} = -r_\epsilon$, roots come in pairs $\pm \beta_k$.
So $P(x) = \prod_{k=1}^4 (x^2 - \beta_k^2)$.
Here $\beta_k$ are the 4 positive values? No, there are 8 roots $\pm \beta_1, \pm \beta_2, \pm \beta_3, \pm \beta_4$.
So $Q(y) = (y - \beta_1^2)(y - \beta_2^2)(y - \beta_3^2)(y - \beta_4^2)$.
The roots $\beta_k^2$ are the values of $r^2$ for the 4 combinations with $\epsilon_1=1$ (say).
Values of $r^2$ for $\epsilon_1=1$:
1. (+,+,+): $10 + 2\sqrt{6} + 2\sqrt{10} + 2\sqrt{15}$
2. (+,+,-): $10 + 2\sqrt{6} - 2\sqrt{10} - 2\sqrt{15}$
3. (+,-,+): $10 - 2\sqrt{6} + 2\sqrt{10} - 2\sqrt{15}$
4. (+,-,-): $10 - 2\sqrt{6} - 2\sqrt{10} + 2\sqrt{15}$
Let $S = 10 + 2\sqrt{6} + 2\sqrt{10} + 2\sqrt{15}$.
The four values are $S$, $S - 4\sqrt{10} - 4\sqrt{15}$, etc.
Actually, let's just sum the roots of $Q(y)$.
Sum of roots of $Q(y)$ is $\sum r_i^2$ (for half the roots? No).
The roots of $P(x)$ are $\pm \sqrt{y_1}, \pm \sqrt{y_2}, \pm \sqrt{y_3}, \pm \sqrt{y_4}$.
So $P(x) = x^8 - e_1 x^6 + e_2 x^4 - e_3 x^2 + e_4$.
Where $e_1 = \sum (\pm \sqrt{y_i})^2 = \sum y_i$.
Wait, coefficient of $x^6$ is $-\sum_{roots} r^2$?
No. $P(x) = x^8 - (\sum r) x^7 + (\sum r_i r_j) x^6 \dots$
Since roots are symmetric, $\sum r = 0$.
$\sum_{i<j} r_i r_j = \frac{1}{2} [ (\sum r)^
```
#### node v = verifier(inputs=['s'], tools=['python', 'check_answer'], skills=['check_answer_form']) -> 2 (wrong, cut at the token limit)
```
To find the polynomial $P(x)$, we start with the given root $\alpha = \sqrt{2} + \sqrt{3} + \sqrt{5}$.
Since $P(x)$ has rational coefficients, all conjugates of $\alpha$ must also be roots. The conjugates are formed by changing the signs of $\sqrt{2}, \sqrt{3}, \sqrt{5}$ independently.
The set of roots is $R = \{ \pm\sqrt{2} \pm\sqrt{3} \pm\sqrt{5} \}$. There are $2^3 = 8$ such roots.
Let the roots be $r_{\epsilon_1, \epsilon_2, \epsilon_3} = \epsilon_1\sqrt{2} + \epsilon_2\sqrt{3} + \epsilon_3\sqrt{5}$ where $\epsilon_i \in \{1, -1\}$.

The polynomial is monic of degree 8:
$P(x) = \prod_{\epsilon_1, \epsilon_2, \epsilon_3} (x - (\epsilon_1\sqrt{2} + \epsilon_2\sqrt{3} + \epsilon_3\sqrt{5}))$.

Notice that for every root $r$, $-r$ is also a root (by flipping all signs). Thus, $P(x)$ is an even function, i.e., $P(x) = Q(x^2)$.
Let $y = x^2$. Then $Q(y) = \prod_{\epsilon_1, \epsilon_2, \epsilon_3} (x - r)$? No.
We can group the factors in pairs: $(x-r)(x+r) = x^2 - r^2$.
So $P(x) = \prod_{\text{distinct positive } r} (x^2 - r^2)$.
The distinct values of $r^2$ correspond to the squares of the 4 combinations where $\epsilon_1=1$ (since $r_{-\epsilon}^2 = r_{\epsilon}^2$).
Let the four values be $y_1, y_2, y_3, y_4$. These are the squares of:
1. $r_1 = \sqrt{2} + \sqrt{3} + \sqrt{5}$
2. $r_2 = \sqrt{2} + \sqrt{3} - \sqrt{5}$
3. $r_3 = \sqrt{2} - \sqrt{3} + \sqrt{5}$
4. $r_4 = \sqrt{2} - \sqrt{3} - \sqrt{5}$

Then $P(x) = (x^2-y_1)(x^2-y_2)(x^2-y_3)(x^2-y_4) = x^8 - (\sum y_i)x^6 +
[... 1137 chars omitted ...]


**Step 2: Calculate the product $S_4 = \prod y_i$.**
This is the constant term of $P(x)$.
$P(0) = \prod_{\epsilon} (-r_\epsilon) = (-1)^8 \prod r_\epsilon = \prod r_\epsilon$.
Wait, $P(x) = \prod (x-r)$. So $P(0) = \prod (-r) = (-1)^8 \prod r = \prod r$.
Let's compute the product of the 8 roots directly or via the pairs.
Product of pairs:
$(r_1)(-r_1) = -r_1^2 = -y_1$.
Actually, the roots are $\pm r_1, \pm r_2, \pm r_3, \pm r_4$.
Product = $(r_1)(-r_1) (r_2)(-r_2) (r_3)(-r_3) (r_4)(-r_4) = (-1)^4 (r_1 r_2 r_3 r_4)^2 = (r_1 r_2 r_3 r_4)^2$.
Let's compute $K = r_1 r_2 r_3 r_4$.
$r_1 r_2 = (\sqrt{2}+\sqrt{3}+\sqrt{5})(\sqrt{2}+\sqrt{3}-\sqrt{5}) = (\sqrt{2}+\sqrt{3})^2 - 5 = (2+3+2\sqrt{6}) - 5 = 2\sqrt{6}$.
$r_3 r_4 = (\sqrt{2}-\sqrt{3}+\sqrt{5})(\sqrt{2}-\sqrt{3}-\sqrt{5}) = (\sqrt{2}-\sqrt{3})^2 - 5 = (2+3-2\sqrt{6}) - 5 = -2\sqrt{6}$.
So $K = (2\sqrt{6})(-2\sqrt{6}) = -4 \times 6 = -24$.
Then the product of all 8 roots is $K^2 = (-24)^2 = 576$.
So the constant term of $P(x)$ is $576$.
Alternatively, using $y_i$: $\prod y_i = (r_1 r_2 r_3 r_4)^2 = (-24)^2 = 576$.

**Step 3: Calculate $S_2 = \sum_{i<j} y_i y_j$.**
We know $(\sum y_i)^2 = \sum y_i^2 + 2 \sum_{i<j} y_i y_j$.
So $S_2 = \frac{1}{2} (S_1^2 - \sum y_i^2)$.
We need $\sum y_i^2$.
$y_i = 10 + 2\delta_{i1}\sqrt{6} + 2\delta_{i2}\sqrt{10} + 2\delta_{i3}\sqrt{15}$?
Let's list them again clearly:
$y_1 = 10 + 2\sqrt{6} + 2\sqrt{10} + 2\sqrt{15}$
$y_2 = 10 + 2\sqrt{6} - 2\sqrt{10} - 2\sqrt{15}$
$y_3 = 10 - 2\sqrt{6} + 2\sqrt{10} - 2\sqrt{15}$
$y_4 = 10 - 2\sqrt{6} - 2\sqrt{10} + 2\sqrt{15}$
Let $u = 2\sqrt{6}, v = 2\sqrt{10}, w = 2\sqrt{15}$.
$y_1 = 10 + u + v + w$
$y_2 = 10 + u - v - w$
$y_3 = 10 - u + v - w$
$y_4 = 10 - u - v + w$
Note that $y_1+y_2 = 20+2u$, $y_3+y_4 = 20-2u$.
$y_1+y_3 = 20+2v$, $y_2+y_4 = 20-2v$.
$y_1+y_4 = 20+2w$, $y_2+y_3 = 20-2w$.
Sum of $y_i = 40$.
Sum of squares:
$y_1^2 + y_2^2 + y_3^2 + y_4^2$.
Expand $y_1^2 = (10+u+v+w)^2 = 100 + u^2+v^2+w^2 + 2(uv+uw+vw) + 20(u+v+w)$.
$y_2^2 = (10+u-v-w)^2 = 100 + u^2+v^2+w^2 + 2(-uv+u(-w)+v(-w)? No. (u-(v+w))^2 = u^2 + (v+w)^2 - 2u(v+w) = u^2+v^2+w^2+2vw - 2uv - 2uw$.
So $y_2^2 = 100 + u^2+v^2+w^2 + 2vw - 2uv - 2uw$.
$y_3^2 = (10-u+v-w)^2 = 100 + u^2+v^2+w^2 + 2(-uv+(-u)(-w)+vw) + 20(-u+v-w) = 100 + u^2+v^2+w^2 - 2uv + 2uw + 2vw - 20u + 20v - 20w$.
$y_4^2 = (10-u-v+w)^2 = 100 + u^2+v^2+w^2 + 2(-uv-u(-w)+(-v)w) + 20(-u-v+w) = 100 + u^2+v^2+w^2 - 2uv + 2uw - 2vw - 20u - 20v + 20w$.

Summing coefficients:
Constant: $400$.
$u^2, v^2, w^2$: $4$ each.
$uv$: $2 - 2 - 2 - 2 = -4$.
$uw$: $2 - 2 + 2 + 2 = 4$.
$vw$: $2 + 2 + 2 - 2 = 4$.
Linear terms ($20 \times \dots$):
$u$: $20 - 20 - 20 - 20 = -40$.
$v$: $20 + 20 + 20 - 20 = 40$.
$w$: $20 - 20 - 20 + 20 = 0$.

So $\sum y_i^2 = 400 + 4(u^2+v^2+w^2) - 4uv + 4uw + 4vw - 40u + 40v$.
Substitute values:
$u = 2\sqrt{6} \implies u^2 = 24$.
$v = 2\sqrt{10} \implies v^2 = 40$.
$w = 2\sqrt{15} \implies w^2 = 60$.
$uv = 4\sqrt{60} = 8\sqrt{15} = 4w$.
$uw = 4\sqrt{90} = 12\sqrt{10} = 6v$.
$vw = 4\sqrt{150} = 10\sqrt{6} = 5u$.
$u = 2\sqrt{6}$.
$v = 2\sqrt{10}$.
$w = 2\sqrt{15}$.

Calculate terms:
$4(u^2+v^2+w^2) = 4(24+40+60) = 4(124) = 496$.
$-4uv = -4(8\sqrt{15}) = -32\sqrt{15} = -16w$.
$4uw = 4(12\sqrt{10}) = 48\sqrt{10} = 24v$.
$4vw = 4(10\sqrt{6}) = 40\sqrt{6} = 20u$.
$-40u = -80\sqrt{6} = -40u$.
$40v = 80\sqrt{10} = 40v$.
Linear sum: $(-16w + 24v + 20u) + (-40u + 40v) = -16w + 64v - 20u$.
Values:
$-16(2\sqrt{15}) = -32\sqrt{15}$.
$64(2\sqrt{10}) = 128\sqrt{10}$.
$-20(2\sqrt{6}) = -40\sqrt{6}$.
Wait, did I mess up the expansion?
Let's use a simpler method.
$y_i$ are roots of a quadratic in terms of $z = u, v, w$? No.
Consider the polynomial whose roots are $y_i$.
$y_1, y_2, y_3, y_4$.
$y_1+y_2 = 20+2u$, $y_3+y_4 = 20-2u$.
$y_1+y_3 = 20+2v$, $y_2+y_4 = 20-2v$.
$y_1+y_4 = 20+2w$, $y_2+y_3 = 20-2w$.
Also $y_1-y_2 = 2(v+w)$.
$y_3-y_4 = -2(v+w)$.
$y_1-y_3 = 2(u-w)$.
$y_2-y_4 = 2(u-w)$.
$y_1-y_4 = 2(u+v)$.
$y_2-y_3 = 2(u+v)$.

Let's compute $S_2 = \sum_{i<j} y_i y_j$.
$S_2 = y_1y_2 + y_3y_4 + y_1y_3 + y_2y_4 + y_1y_4 + y_2y_3$.
Group by pairs that sum to something simple?
$y_1y_2 = (10+u)^2 - (v+w)^2 = 100 + 20u + u^2 - (v^2+w^2+2vw)$.
$y_3y_4 = (10-u)^2 - (v-w)^2 = 100 - 20u + u^2 - (v^2+w^2-2vw)$.
Sum $y_1y_2 + y_3y_4 = 200 + 2u^2 - 2v^2 - 2w^2$.
$y_1y_3 = (10+v)^2 - (u-w)^2 = 100 + 20v + v^2 - (u^2+w^2-2uw)$.
$y_2y_4 = (10-v)^2 - (u+w)^2 = 100 - 20v + v^2 - (u^2+w^2+2uw)$.
Sum $y_1y_3 + y_2y_4 = 200 + 2v^2 - 2u^2 - 2w^2$.
$y_1y_4 = (10+w)^2 - (u-v)^2 = 100 + 20w + w^2 - (
```