# Report (dev-A)

Organization: acc 56.7% (meta-agent prompt 2970 chars). 5 distinct architectures, 2.0 nodes per problem. Fallback (unusable meta-agent output): 2.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| challenging | 18 | 33% | writer[T][S]>checker[T][S] 17, writer[T][S] 1 |
| moderate | 53 | 47% | writer[T][S]>checker[T][S] 50, writer[T][S]>writer[T][S]>checker[T][S] 1, writer[T] 1 |
| simple | 79 | 68% | writer[T][S]>checker[T][S] 70, writer[T][S] 6, writer[T][S],writer[T][S]>checker[T][S] 2 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| writer[T][S]>checker[T][S] | 137 | 57% |
| writer[T][S] | 7 | 57% |
| writer[T][S],writer[T][S]>checker[T][S] | 3 | 100% |
| writer[T] | 2 | 0% |
| writer[T][S]>writer[T][S]>checker[T][S] | 1 | 0% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| writer | 153 | 55% | 2% | - | - | - |
| checker (with inputs) | 141 | 57% | 4% | 42 | 13 | 9 |
| writer (with inputs) | 1 | 0% | 0% | 1 | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_sql | 291 | 56% | 50% |
| skill:output_columns | 148 | 56% | 56% |
| tool:find_values | 123 | 54% | 58% |
| skill:value_matching | 123 | 59% | 54% |
| skill:check_result | 110 | 55% | 56% |
| skill:join_paths | 92 | 50% | 59% |
| skill:evidence_first | 33 | 58% | 56% |
| skill:counting | 27 | 59% | 56% |
| skill:ratio_percentage | 26 | 42% | 57% |
| tool:column_info | 22 | 41% | 57% |
| skill:top_k_ties | 22 | 36% | 58% |
| tool:sample_rows | 15 | 40% | 57% |
| skill:explore_then_write | 14 | 57% | 56% |
| skill:dates_text | 9 | 44% | 56% |
| skill:null_empty | 2 | 100% | 56% |
| skill:subquery_vs_join | 2 | 100% | 56% |

Meta-agent output problems: syntax error: closing parenthesis ')' does not match opening parenthesis '[' (line 1) (1); line 1: unknown agent 'agent' (1); line 2: unknown agent 'agent' (1); return must name a node defined above (1); no node (1)

## Wrong (65)
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.
Evidence: -
  architecture: a = writer(tools=['run_sql', 'find_values', 'sample_rows'], skills=['explore_then_write', 'counting']); c = checker(a, tools=['run_sql'], skills=['top_k_ties', 'output_columns']); return c; answered SELECT CDSCode
FROM frpm
ORDER BY `Enrollment (Ages 5-17)` DESC
LIMIT 5;, correct SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5
- [moderate] Database: financial (tables: account, card, client, disp, district, loan, order, trans)
Question: What is the average number of crimes committed in 1995 in regions where the number exceeds 4000 and the region has accounts that are opened starting from the year 1997?
Evidence: A3 
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'explore_then_write', 'ratio_percentage']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT AVG(A15)
FROM district
WHERE A15 > 4000
  AND district_id IN (
    SELECT DISTINCT district_id
    FROM account
    WHERE date LIKE '1997%'
  );, correct SELECT AVG(T1.A15) FROM district AS T1 INNER JOIN account AS T2 ON T1.district_id = T2.district_id WHERE STRFTIME('%Y', T2.date) >= '1997' AND T1.A15 > 4000
- [moderate] Database: california_schools (tables: frpm, satscores, schools)
Question: What is the complete address of the school with the lowest excellence rate? Indicate the Street, City, Zip and State.
Evidence: Execellence Rate = NumGE1500 / NumTstTakr; complete address has Street, City, 
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'ratio_percentage', 'join_paths']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT s.Street, s.City, s.Zip, s.State
FROM schools s
JOIN satscores sc ON s.CDSCode = sc.cds
WHERE sc.NumTstTakr > 0
ORDER BY CAST(sc.NumGE1500 AS REAL) / sc.NumTstTakr ASC
LIMIT 1;, correct SELECT T2.Street, T2.City, T2.State, T2.Zip FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode ORDER BY CAST(T1.NumGE1500 AS REAL) / T1.NumTstTakr ASC LIMIT 1
- [moderate] Database: toxicology (tables: atom, bond, connected, molecule)
Question: Calculate the percentage of carcinogenic molecules which contain the Chlorine element.
Evidence: label = '+' mean molecules are carcinogenic; percentage = DIVIDE(SUM(label = '+' and element = 'cl'), COUNT(mo
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'join_paths', 'ratio_percentage']); c = checker(a, tools=['run_sql'], skills=['ratio_percentage', 'output_columns', 'check_result']); return c; answered SELECT 
    CAST(COUNT(DISTINCT CASE WHEN a.element = 'cl' THEN m.molecule_id END) AS REAL) * 100.0 / COUNT(DISTINCT m.molecule_id) AS percentage
FROM molecule m
JOIN atom a ON m.molecule_id = a.molecule_id
WHERE m.label = '+';, correct SELECT COUNT(CASE WHEN T2.label = '+' AND T1.element = 'cl' THEN T2.molecule_id ELSE NULL END) * 100 / COUNT(T2.molecule_id) FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: Among the patients with a normal Ig G level, how many of them have symptoms?
Evidence: normal Ig G level refers to IGG > 900 and IGG < 2000; have symptoms refers to Symptoms IS NOT NULL;
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['evidence_first', 'counting']); c = checker(w, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT COUNT(DISTINCT p.ID)
FROM Patient p
JOIN Laboratory l ON p.ID = l.ID
JOIN Examination e ON p.ID = e.ID
WHERE l.IGG > 900 
  AND l.IGG < 2000 
  AND e.Symptoms IS NOT NULL;, correct SELECT COUNT(T1.ID) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID INNER JOIN Examination AS T3 ON T3.ID = T2.ID WHERE T2.IGG BETWEEN 900 AND 2000 AND T3.Symptoms IS NOT NULL
- [simple] Database: card_games (tables: cards, foreign_data, legalities, sets, set_translations, rulings)
Question: Please list the name of the cards in the set Coldsnap with the highest converted mana cost.
Evidence: card set Coldsnap refers to name = 'Coldsnap'
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'top_k_ties', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['check_result']); return c; answered SELECT c.name
FROM cards c
JOIN sets s ON c.setCode = s.code
WHERE s.name = 'Coldsnap'
AND c.convertedManaCost = (
    SELECT MAX(c2.convertedManaCost)
    FROM cards c2
    JOIN sets s2 ON c2.setCode = s2.code
    WHERE s2.name = 'Coldsnap'
)
ORDER BY c.convertedManaCost DESC;, correct SELECT T1.name FROM cards AS T1 INNER JOIN sets AS T2 ON T2.code = T1.setCode WHERE T2.name = 'Coldsnap' ORDER BY T1.convertedManaCost DESC LIMIT 1
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: For all patients with normal uric acid (UA), what is the average UA index based on their latest laboratory examination result?
Evidence: uric acid (UA) with normal range refers to UA < 8.0 and SE
  architecture: w1 = writer(tools=['column_info', 'run_sql'], skills=['explore_then_write', 'join_paths']); w2 = writer(w1, tools=['run_sql'], skills=['value_matching', 'dates_text', 'output_columns']); c = checker(w2, tools=['run_sql'], skills=['check_result', 'output_columns']); return c; answered SELECT AVG(L.UA) AS average_UA_index
FROM (
    SELECT L.*,
           ROW_NUMBER() OVER (PARTITION BY L.ID ORDER BY L.Date DESC) AS rn
    FROM Laboratory L
    JOIN Patient P ON L.ID = P.ID
) L
WHERE L.rn = 1
  AND ((P.SEX = 'M' AND L.UA < 8.0) OR (P.SEX = 'F' AND L.UA < 6.5));, correct SELECT AVG(T2.UA) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE (T2.UA < 6.5 AND T1.SEX = 'F') OR (T2.UA < 8.0 AND T1.SEX = 'M') AND T2.Date = ( SELECT MAX(Date) FROM Laboratory )
- [moderate] Database: codebase_community (tables: badges, comments, postHistory, postLinks, posts, tags, users, votes)
Question: User No.23853 gave a comment to a post at 9:08:18 on 2013/7/12, was that post well-finished?
Evidence: user no. 23853 refers to UserId = '23853'; at 9:08:18 on 201
  architecture: a = writer(tools=['run_sql'], skills=['value_matching', 'join_paths', 'output_columns']); c = checker(a, tools=['run_sql'], skills=['check_result']); return c; answered SELECT p.Title, p.ClosedDate
FROM comments c
JOIN posts p ON c.PostId = p.Id
WHERE c.UserId = 23853
  AND c.CreationDate = '2013-07-12 09:08:18.0';, correct SELECT IIF(T2.ClosedDate IS NULL, 'NOT well-finished', 'well-finished') AS resylt FROM comments AS T1 INNER JOIN posts AS T2 ON T1.PostId = T2.Id WHERE T1.UserId = 23853 AND T1.CreationDate = '2013-07-12 09:08:18.0'
- [simple] Database: card_games (tables: cards, foreign_data, legalities, sets, set_translations, rulings)
Question: What is the type of the card "Ancestor's Chosen" as originally printed?
Evidence: Ancestor's Chosen' is the name of card; type of the card as originally printed refers to ori
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'output_columns']); c = checker(w, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT originalType
FROM cards
WHERE name = 'Ancestor''s Chosen';, correct SELECT originalType FROM cards WHERE name = 'Ancestor''s Chosen' AND originalType IS NOT NULL
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: Which active district has the highest average score in Reading?
Evidence: -
  architecture: w = writer(tools=['run_sql', 'find_values', 'column_info'], skills=['explore_then_write', 'join_paths', 'top_k_ties']); c = checker(w, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT s.District
FROM satscores t
JOIN schools s ON t.cds = s.CDSCode
WHERE s.StatusType = 'Active'
GROUP BY s.District
ORDER BY AVG(t.AvgScrRead) DESC
LIMIT 1;, correct SELECT T1.District FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Active' ORDER BY T2.AvgScrRead DESC LIMIT 1