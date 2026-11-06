# Report (dev-A)

Organization: acc 100.0% (meta-agent prompt 3061 chars; roles 421 chars). 2 distinct architectures, 1.5 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| mbpp_plus | 8 | 100% | coder[T][S]>tester[T][S] 4, coder[T][S] 4 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| coder[T][S]>tester[T][S] | 4 | 100% |
| coder[T][S] | 4 | 100% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| coder | 8 | 100% | 0% | - | - | - |
| tester (with inputs) | 4 | 100% | 0% | 2 | 2 | 2 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_examples | 11 | 100% | 100% |
| tool:python | 8 | 100% | 100% |
| skill:examples_check | 6 | 100% | 100% |
| skill:read_spec | 5 | 100% | 100% |
| skill:edge_cases | 5 | 100% | 100% |
| skill:assert_signature | 4 | 100% | 100% |
| skill:string_rules | 3 | 100% | 100% |
| skill:numeric_rules | 2 | 100% | 100% |
| tool:compare | 1 | 100% | 100% |
Never given: timed, efficiency.

## Wrong (0)

## Traces of the wrong problems (0 of 0; node outputs over 6000 chars are cut in the middle)