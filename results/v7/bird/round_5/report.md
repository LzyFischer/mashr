# Report (dev-A)

Organization: acc 56.7% (meta-agent prompt 4282 chars). 2 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| challenging | 18 | 33% | writer[T][S]>checker[T][S] 17, writer[T][S] 1 |
| moderate | 53 | 40% | writer[T][S]>checker[T][S] 52, writer[T][S] 1 |
| simple | 79 | 73% | writer[T][S]>checker[T][S] 66, writer[T][S] 13 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| writer[T][S]>checker[T][S] | 135 | 56% |
| writer[T][S] | 15 | 67% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| writer | 150 | 57% | 5% | - | - | - |
| checker (with inputs) | 135 | 56% | 2% | 46 | 17 | 17 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_sql | 285 | 56% | - |
| skill:output_columns | 137 | 55% | 57% |
| tool:find_values | 108 | 56% | 56% |
| skill:join_paths | 107 | 53% | 58% |
| skill:value_matching | 103 | 60% | 54% |
| skill:counting | 35 | 71% | 54% |
| skill:evidence_first | 29 | 52% | 57% |
| skill:top_k_ties | 26 | 42% | 58% |
| skill:check_result | 12 | 50% | 56% |
| skill:dates_text | 10 | 50% | 56% |
| skill:ratio_percentage | 8 | 38% | 57% |
| tool:column_info | 4 | 75% | 56% |
Never given: sample_rows, null_empty, subquery_vs_join, explore_then_write.

## Wrong (65)
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.
Evidence: -
  architecture: a = writer(tools=['run_sql'], skills=['counting']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT s.NCESSchool, f.`Enrollment (Ages 5-17)`
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
WHERE f.`Enrollment (Ages 5-17)` IS NOT NULL
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5;, correct SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5
- [moderate] Database: california_schools (tables: frpm, satscores, schools)
Question: What is the complete address of the school with the lowest excellence rate? Indicate the Street, City, Zip and State.
Evidence: Execellence Rate = NumGE1500 / NumTstTakr; complete address has Street, City, 
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'join_paths', 'ratio_percentage']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT s.Street, s.City, s.Zip, s.State
FROM schools s
JOIN satscores sc ON s.CDSCode = sc.cds
WHERE sc.NumTstTakr > 0
ORDER BY CAST(sc.NumGE1500 AS REAL) / sc.NumTstTakr ASC
LIMIT 1;, correct SELECT T2.Street, T2.City, T2.State, T2.Zip FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode ORDER BY CAST(T1.NumGE1500 AS REAL) / T1.NumTstTakr ASC LIMIT 1
- [moderate] Database: toxicology (tables: atom, bond, connected, molecule)
Question: Calculate the percentage of carcinogenic molecules which contain the Chlorine element.
Evidence: label = '+' mean molecules are carcinogenic; percentage = DIVIDE(SUM(label = '+' and element = 'cl'), COUNT(mo
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT 
    CAST(SUM(CASE WHEN a.element = 'cl' THEN 1 ELSE 0 END) AS REAL) * 100.0 / COUNT(*) AS percentage
FROM 
    molecule m
JOIN 
    atom a ON m.molecule_id = a.molecule_id
WHERE 
    m.label = '+';, correct SELECT COUNT(CASE WHEN T2.label = '+' AND T1.element = 'cl' THEN T2.molecule_id ELSE NULL END) * 100 / COUNT(T2.molecule_id) FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: Among the patients with a normal Ig G level, how many of them have symptoms?
Evidence: normal Ig G level refers to IGG > 900 and IGG < 2000; have symptoms refers to Symptoms IS NOT NULL;
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['counting', 'join_paths', 'evidence_first']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT COUNT(DISTINCT P.ID)
FROM Patient P
JOIN Laboratory L ON P.ID = L.ID
JOIN Examination E ON P.ID = E.ID
WHERE L.IGG > 900 AND L.IGG < 2000 AND E.Symptoms IS NOT NULL;, correct SELECT COUNT(T1.ID) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID INNER JOIN Examination AS T3 ON T3.ID = T2.ID WHERE T2.IGG BETWEEN 900 AND 2000 AND T3.Symptoms IS NOT NULL
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: For all patients with normal uric acid (UA), what is the average UA index based on their latest laboratory examination result?
Evidence: uric acid (UA) with normal range refers to UA < 8.0 and SE
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'evidence_first']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT AVG(latest.UA)
FROM (
    SELECT l.ID, l.UA
    FROM Laboratory l
    JOIN Patient p ON l.ID = p.ID
    WHERE (l.UA < 8.0 AND p.SEX = 'M') OR (l.UA < 6.5 AND p.SEX = 'F')
      AND l.Date = (
          SELECT MAX(l2.Date)
          FROM Laboratory l2
          JOIN Patient p2 ON l2.ID = p2.ID
          WHERE l2.ID = l.ID
      )
) latest, correct SELECT AVG(T2.UA) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE (T2.UA < 6.5 AND T1.SEX = 'F') OR (T2.UA < 8.0 AND T1.SEX = 'M') AND T2.Date = ( SELECT MAX(Date) FROM Laboratory )
- [moderate] Database: codebase_community (tables: badges, comments, postHistory, postLinks, posts, tags, users, votes)
Question: User No.23853 gave a comment to a post at 9:08:18 on 2013/7/12, was that post well-finished?
Evidence: user no. 23853 refers to UserId = '23853'; at 9:08:18 on 201
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT CASE WHEN p.ClosedDate IS NULL THEN 'Yes' ELSE 'No' END as status
FROM comments c
JOIN posts p ON c.PostId = p.Id
WHERE c.UserId = 23853
  AND c.CreationDate = '2013-07-12 09:08:18.0';, correct SELECT IIF(T2.ClosedDate IS NULL, 'NOT well-finished', 'well-finished') AS resylt FROM comments AS T1 INNER JOIN posts AS T2 ON T1.PostId = T2.Id WHERE T1.UserId = 23853 AND T1.CreationDate = '2013-07-12 09:08:18.0'
- [simple] Database: card_games (tables: cards, foreign_data, legalities, sets, set_translations, rulings)
Question: What is the type of the card "Ancestor's Chosen" as originally printed?
Evidence: Ancestor's Chosen' is the name of card; type of the card as originally printed refers to ori
  architecture: a = writer(tools=['run_sql'], skills=['value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT originalType
FROM cards
WHERE name = 'Ancestor''s Chosen';, correct SELECT originalType FROM cards WHERE name = 'Ancestor''s Chosen' AND originalType IS NOT NULL
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: Which active district has the highest average score in Reading?
Evidence: -
  architecture: a = writer(tools=['run_sql'], skills=['join_paths', 'top_k_ties']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT T1.`District Name`
FROM frpm T1
JOIN schools T2 ON T1.CDSCode = T2.CDSCode
JOIN satscores T3 ON T1.`School Code` = T3.cds
WHERE T2.StatusType = 'Active'
GROUP BY T1.`District Name`
ORDER BY AVG(T3.AvgScrRead) DESC
LIMIT 1;, correct SELECT T1.District FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Active' ORDER BY T2.AvgScrRead DESC LIMIT 1
- [challenging] Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, results)
Question: Among all the lap records set on various circuits, what is the time for the fastest 
  architecture: a = writer(tools=['run_sql'], skills=['top_k_ties']); return a; answered SELECT time
FROM lapTimes
ORDER BY milliseconds
LIMIT 1;, correct SELECT time FROM lapTimes ORDER BY (CASE WHEN INSTR(time, ':') <> INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':') THEN CAST(SUBSTR(time, 1, INSTR(time, ':') - 1) AS REAL) * 3600 ELSE 0 END) + (CAST(SUBSTR(time, INSTR(time, ':') - 2 * (INSTR(time, ':') = INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':')), INSTR(time, ':') - 1) AS REAL) * 60) + (CAST(SUBSTR(time, INSTR(time, ':') + 1, INSTR(time, '.') - INSTR(time, ':') - 1) AS REAL)) + (CAST(SUBSTR(time, INSTR(time, '.') + 1) AS REAL) / 1000) ASC LIMIT 1
- [moderate] Database: toxicology (tables: atom, bond, connected, molecule)
Question: Among the molecules with element Calcium, are they mostly carcinogenic or non carcinogenic?
Evidence: calcium refers to element = 'ca'; label = '+' mean molecules are carcinogenic; label = '-' means molecule
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'join_paths']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT CASE WHEN MAX(m.label) = '+' THEN 'carcinogenic' ELSE 'non-carcinogenic' END as status
FROM atom a
JOIN molecule m ON a.molecule_id = m.molecule_id
WHERE a.element = 'ca';, correct SELECT T2.label FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id WHERE T1.element = 'ca' GROUP BY T2.label ORDER BY COUNT(T2.label) DESC LIMIT 1