# Report (dev-A)

Organization: acc 62.0%, cost 2608/problem, of which the meta-agent 804 (its prompt 3069 chars). 3 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | cost | architectures |
|---|---|---|---|---|
| challenging | 18 | 33% | 3074 | writer[T][S]>checker[T][S] 15, writer[T][S] 2, writer[T][S],writer[T][S]>checker[T][S] 1 |
| moderate | 53 | 51% | 3055 | writer[T][S]>checker[T][S] 48, writer[T][S] 5 |
| simple | 79 | 76% | 2202 | writer[T][S]>checker[T][S] 67, writer[T][S] 12 |

## Architectures
| architecture | uses | acc | mean cost |
|---|---|---|---|
| writer[T][S]>checker[T][S] | 130 | 63% | 2752 |
| writer[T][S] | 19 | 58% | 1456 |
| writer[T][S],writer[T][S]>checker[T][S] | 1 | 0% | 5836 |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | mean cost | changed | to correct | to wrong |
|---|---|---|---|---|---|---|---|
| writer | 151 | 56% | 3% | 1031 | - | - | - |
| checker (with inputs) | 131 | 63% | 2% | 877 | 40 | 22 | 13 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_sql | 282 | 59% | - |
| skill:output_columns | 143 | 61% | 57% |
| skill:value_matching | 107 | 54% | 62% |
| tool:find_values | 106 | 54% | 62% |
| skill:check_result | 93 | 57% | 60% |
| skill:join_paths | 89 | 52% | 62% |
| skill:evidence_first | 42 | 55% | 60% |
| skill:top_k_ties | 21 | 67% | 58% |
| skill:ratio_percentage | 21 | 52% | 59% |
| skill:counting | 19 | 47% | 60% |
| skill:explore_then_write | 7 | 71% | 59% |
| tool:column_info | 6 | 50% | 59% |
| skill:dates_text | 5 | 60% | 59% |
| tool:sample_rows | 3 | 33% | 59% |
| skill:subquery_vs_join | 1 | 0% | 59% |
Never given: null_empty.

Meta-agent output problems: return must name a node defined above (1); no return; using the last node (1)

## Wrong (57)
- [moderate] Database: financial (tables: account, card, client, disp, district, loan, order, trans)
Question: What is the average number of crimes committed in 1995 in regions where the number exceeds 4000 and the region has accounts that are opened starting from the year 1997?
Evidence: A3 
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['evidence_first', 'value_matching', 'output_columns']); c = checker(w, tools=['run_sql'], skills=['check_result', 'output_columns']); return c; answered SELECT DISTINCT d.A15
FROM district d
JOIN account a ON d.district_id = a.district_id
WHERE d.A15 > 4000
  AND a.date >= '1997-01-01', correct SELECT AVG(T1.A15) FROM district AS T1 INNER JOIN account AS T2 ON T1.district_id = T2.district_id WHERE STRFTIME('%Y', T2.date) >= '1997' AND T1.A15 > 4000
- [moderate] Database: california_schools (tables: frpm, satscores, schools)
Question: What is the complete address of the school with the lowest excellence rate? Indicate the Street, City, Zip and State.
Evidence: Execellence Rate = NumGE1500 / NumTstTakr; complete address has Street, City, 
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'ratio_percentage', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return c; answered SELECT 
    s.Street,
    s.City,
    s.Zip,
    s.State
FROM schools s
JOIN satscores sc ON s.CDSCode = sc.cds
WHERE sc.NumTstTakr > 0
ORDER BY CAST(sc.NumGE1500 AS REAL) / sc.NumTstTakr ASC
LIMIT 1;, correct SELECT T2.Street, T2.City, T2.State, T2.Zip FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode ORDER BY CAST(T1.NumGE1500 AS REAL) / T1.NumTstTakr ASC LIMIT 1
- [moderate] Database: toxicology (tables: atom, bond, connected, molecule)
Question: Calculate the percentage of carcinogenic molecules which contain the Chlorine element.
Evidence: label = '+' mean molecules are carcinogenic; percentage = DIVIDE(SUM(label = '+' and element = 'cl'), COUNT(mo
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'ratio_percentage', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT 
    CAST(
        COUNT(DISTINCT CASE WHEN a.element = 'cl' THEN m.molecule_id END) 
    AS REAL) * 100.0 / 
    COUNT(DISTINCT m.molecule_id)
FROM molecule m
JOIN atom a ON m.molecule_id = a.molecule_id
WHERE m.label = '+', correct SELECT COUNT(CASE WHEN T2.label = '+' AND T1.element = 'cl' THEN T2.molecule_id ELSE NULL END) * 100 / COUNT(T2.molecule_id) FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: Among the patients with a normal Ig G level, how many of them have symptoms?
Evidence: normal Ig G level refers to IGG > 900 and IGG < 2000; have symptoms refers to Symptoms IS NOT NULL;
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['evidence_first', 'value_matching', 'join_paths']); c = checker(a, tools=['run_sql'], skills=['check_result']); return c; answered SELECT COUNT(DISTINCT P.ID)
FROM Patient P
JOIN Laboratory L ON P.ID = L.ID
JOIN Examination E ON P.ID = E.ID
WHERE L.IGG > 900 
  AND L.IGG < 2000 
  AND E.Symptoms IS NOT NULL;, correct SELECT COUNT(T1.ID) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID INNER JOIN Examination AS T3 ON T3.ID = T2.ID WHERE T2.IGG BETWEEN 900 AND 2000 AND T3.Symptoms IS NOT NULL
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: For all patients with normal uric acid (UA), what is the average UA index based on their latest laboratory examination result?
Evidence: uric acid (UA) with normal range refers to UA < 8.0 and SE
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching', 'output_columns']); c = checker(w, tools=['run_sql'], skills=['check_result', 'output_columns']); return c; answered WITH LatestResults AS (
    SELECT 
        ID,
        Date,
        UA,
        ROW_NUMBER() OVER (PARTITION BY ID ORDER BY Date DESC) as rn
    FROM Laboratory
)
SELECT 
    AVG(lr.UA) as avg_ua_index
FROM LatestResults lr
JOIN Patient p ON lr.ID = p.ID
WHERE lr.rn = 1
  AND ((lr.UA < 8.0 AND p.SEX = 'M') OR (lr.UA < 6.5 AND p.SEX = 'F'));, correct SELECT AVG(T2.UA) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE (T2.UA < 6.5 AND T1.SEX = 'F') OR (T2.UA < 8.0 AND T1.SEX = 'M') AND T2.Date = ( SELECT MAX(Date) FROM Laboratory )
- [moderate] Database: codebase_community (tables: badges, comments, postHistory, postLinks, posts, tags, users, votes)
Question: User No.23853 gave a comment to a post at 9:08:18 on 2013/7/12, was that post well-finished?
Evidence: user no. 23853 refers to UserId = '23853'; at 9:08:18 on 201
  architecture: w = writer(tools=['run_sql', 'find_values', 'column_info'], skills=['join_paths', 'value_matching', 'output_columns']); c = checker(w, tools=['run_sql'], skills=['check_result']); return c; answered SELECT c.PostId, p.ClosedDate
FROM comments c
JOIN users u ON c.UserId = u.Id
JOIN posts p ON c.PostId = p.Id
WHERE u.Id = 23853
  AND c.CreationDate = '2013-07-12 09:08:18.0';, correct SELECT IIF(T2.ClosedDate IS NULL, 'NOT well-finished', 'well-finished') AS resylt FROM comments AS T1 INNER JOIN posts AS T2 ON T1.PostId = T2.Id WHERE T1.UserId = 23853 AND T1.CreationDate = '2013-07-12 09:08:18.0'
- [simple] Database: card_games (tables: cards, foreign_data, legalities, sets, set_translations, rulings)
Question: What is the type of the card "Ancestor's Chosen" as originally printed?
Evidence: Ancestor's Chosen' is the name of card; type of the card as originally printed refers to ori
  architecture: a = writer(tools=['run_sql'], skills=['value_matching']); return a; answered SELECT originalType FROM cards WHERE name = 'Ancestor''s Chosen';, correct SELECT originalType FROM cards WHERE name = 'Ancestor''s Chosen' AND originalType IS NOT NULL
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: Which active district has the highest average score in Reading?
Evidence: -
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'top_k_ties']); c = checker(w, tools=['run_sql'], skills=['check_result']); return c; answered SELECT 
    T1.District,
    AVG(T2.AvgScrRead) as AvgReadingScore
FROM 
    schools T1
JOIN 
    satscores T2 ON T1.CDSCode = T2.cds
WHERE 
    T1.StatusType = 'Active'
GROUP BY 
    T1.District
ORDER BY 
    AvgReadingScore DESC
LIMIT 1;, correct SELECT T1.District FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Active' ORDER BY T2.AvgScrRead DESC LIMIT 1
- [challenging] Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, results)
Question: Among all the lap records set on various circuits, what is the time for the fastest 
  architecture: a = writer(tools=['run_sql'], skills=['top_k_ties', 'value_matching']); return a; answered SELECT time, milliseconds
FROM lapTimes
WHERE milliseconds IS NOT NULL
ORDER BY milliseconds ASC
LIMIT 1;, correct SELECT time FROM lapTimes ORDER BY (CASE WHEN INSTR(time, ':') <> INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':') THEN CAST(SUBSTR(time, 1, INSTR(time, ':') - 1) AS REAL) * 3600 ELSE 0 END) + (CAST(SUBSTR(time, INSTR(time, ':') - 2 * (INSTR(time, ':') = INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':')), INSTR(time, ':') - 1) AS REAL) * 60) + (CAST(SUBSTR(time, INSTR(time, ':') + 1, INSTR(time, '.') - INSTR(time, ':') - 1) AS REAL)) + (CAST(SUBSTR(time, INSTR(time, '.') + 1) AS REAL) / 1000) ASC LIMIT 1
- [challenging] Database: superhero (tables: alignment, attribute, colour, gender, publisher, race, superhero, hero_attribute, superpower, hero_power)
Question: In superheroes with missing weight data, calculate the difference between the number of superheroes with blue eyes and no eye color.
Ev
  architecture: a = writer(tools=['run_sql'], skills=['join_paths', 'counting']); c = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return c; answered SELECT 
    SUM(CASE WHEN c.id = 7 THEN 1 ELSE 0 END) - SUM(CASE WHEN c.id = 1 THEN 1 ELSE 0 END) AS difference
FROM superhero s
JOIN colour c ON s.eye_colour_id = c.id
WHERE s.weight_kg IS NULL;, correct SELECT SUM(CASE WHEN T2.id = 7 THEN 1 ELSE 0 END) - SUM(CASE WHEN T2.id = 1 THEN 1 ELSE 0 END) FROM superhero AS T1 INNER JOIN colour AS T2 ON T1.eye_colour_id = T2.id WHERE T1.weight_kg = 0 OR T1.weight_kg is NULL

## Most expensive correct problems (possible waste)
- [simple, cost 6263] Database: california_schools (tables: frpm, satscores, schools)
Question: In chartered schools with charter number 00D2, what are the names of all the administrators? Include the n
  architecture: a = writer(tools=['run_sql', 'find_values', 'column_info'], skills=['explore_then_write', 'join_paths', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c
- [moderate, cost 5980] Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, res
  architecture: w = writer(tools=['run_sql', 'find_values', 'column_info'], skills=['evidence_first', 'ratio_percentage', 'join_paths']); c = checker(w, tools=['run_sql'], skills=['check_result', 'output_columns']); return c
- [moderate, cost 5878] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: What is the ratio of outpatient to inpatient followed up treatment among all the 'SLE' diagnose
  architecture: a = writer(tools=['run_sql'], skills=['ratio_percentage', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return c
- [moderate, cost 5715] Database: financial (tables: account, card, client, disp, district, loan, order, trans)
Question: Which district has highest active loan?
Evidence: A3 refers to district names; Act
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'top_k_ties']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c
- [challenging, cost 4928] Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, res
  architecture: w = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching', 'top_k_ties']); c = checker(w, tools=['run_sql'], skills=['check_result']); return c