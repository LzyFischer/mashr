# Report (dev-A)

Organization: acc 60.7% (meta-agent prompt 3958 chars). 4 distinct architectures, 1.9 nodes per problem. Fallback (unusable meta-agent output): 5.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| challenging | 18 | 44% | writer[T][S]>checker[T][S] 17, writer[T][S] 1 |
| moderate | 53 | 47% | writer[T][S]>checker[T][S] 45, writer[T] 4, writer[T][S] 3 |
| simple | 79 | 73% | writer[T][S]>checker[T][S] 67, writer[T][S] 11, writer[T] 1 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| writer[T][S]>checker[T][S] | 129 | 61% |
| writer[T][S] | 15 | 53% |
| writer[T] | 5 | 80% |
| checker[T][S],writer[T][S] | 1 | 0% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| writer | 150 | 60% | 4% | - | - | - |
| checker (with inputs) | 129 | 61% | 3% | 39 | 22 | 21 |
| checker | 1 | 0% | 0% | - | - | - |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_sql | 280 | 60% | - |
| skill:output_columns | 160 | 60% | 61% |
| tool:find_values | 114 | 59% | 61% |
| skill:join_paths | 113 | 59% | 61% |
| skill:value_matching | 88 | 65% | 58% |
| skill:check_result | 75 | 55% | 62% |
| skill:evidence_first | 52 | 56% | 61% |
| skill:top_k_ties | 33 | 42% | 63% |
| skill:counting | 28 | 71% | 59% |
| skill:ratio_percentage | 15 | 40% | 62% |
| skill:dates_text | 12 | 50% | 61% |
| tool:column_info | 4 | 0% | 61% |
| skill:null_empty | 2 | 100% | 60% |
| tool:sample_rows | 1 | 0% | 61% |
Never given: subquery_vs_join, explore_then_write.

Meta-agent output problems: syntax error: invalid syntax (line 2) (3); line 1: unknown agent 'agent' (2); line 2: unknown agent 'agent' (2); return must name a node defined above (2); no node (2)

## Wrong (59)
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.
Evidence: -
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'top_k_ties']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5;, correct SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5
- [moderate] Database: california_schools (tables: frpm, satscores, schools)
Question: What is the complete address of the school with the lowest excellence rate? Indicate the Street, City, Zip and State.
Evidence: Execellence Rate = NumGE1500 / NumTstTakr; complete address has Street, City, 
  architecture: a = writer(tools=['run_sql'], skills=['join_paths', 'top_k_ties']); c = checker(a, tools=['run_sql'], skills=['output_columns']); return c; answered SELECT 
    s.Street, 
    s.City, 
    s.Zip, 
    s.State
FROM schools s
JOIN satscores sc ON s.CDSCode = sc.cds
WHERE sc.NumTstTakr IS NOT NULL AND sc.NumTstTakr > 0
ORDER BY 
    CAST(sc.NumGE1500 AS REAL) / sc.NumTstTakr ASC
LIMIT 1;, correct SELECT T2.Street, T2.City, T2.State, T2.Zip FROM satscores AS T1 INNER JOIN schools AS T2 ON T1.cds = T2.CDSCode ORDER BY CAST(T1.NumGE1500 AS REAL) / T1.NumTstTakr ASC LIMIT 1
- [moderate] Database: toxicology (tables: atom, bond, connected, molecule)
Question: Calculate the percentage of carcinogenic molecules which contain the Chlorine element.
Evidence: label = '+' mean molecules are carcinogenic; percentage = DIVIDE(SUM(label = '+' and element = 'cl'), COUNT(mo
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'ratio_percentage', 'value_matching']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT 
    CAST(COUNT(DISTINCT CASE WHEN a.element = 'cl' THEN m.molecule_id END) AS REAL) * 100.0 / 
    (SELECT COUNT(*) FROM molecule WHERE label = '+') AS percentage
FROM molecule m
JOIN atom a ON m.molecule_id = a.molecule_id
WHERE m.label = '+';, correct SELECT COUNT(CASE WHEN T2.label = '+' AND T1.element = 'cl' THEN T2.molecule_id ELSE NULL END) * 100 / COUNT(T2.molecule_id) FROM atom AS T1 INNER JOIN molecule AS T2 ON T1.molecule_id = T2.molecule_id
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: Among the patients with a normal Ig G level, how many of them have symptoms?
Evidence: normal Ig G level refers to IGG > 900 and IGG < 2000; have symptoms refers to Symptoms IS NOT NULL;
  architecture: w = writer(tools=['run_sql'], skills=['evidence_first', 'counting', 'null_empty']); c = checker(w, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT COUNT(DISTINCT e.ID)
FROM Examination e
JOIN Laboratory l ON e.ID = l.ID
WHERE l.IGG > 900 AND l.IGG < 2000 AND e.Symptoms IS NOT NULL;, correct SELECT COUNT(T1.ID) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID INNER JOIN Examination AS T3 ON T3.ID = T2.ID WHERE T2.IGG BETWEEN 900 AND 2000 AND T3.Symptoms IS NOT NULL
- [moderate] Database: thrombosis_prediction (tables: Examination, Patient, Laboratory)
Question: For all patients with normal uric acid (UA), what is the average UA index based on their latest laboratory examination result?
Evidence: uric acid (UA) with normal range refers to UA < 8.0 and SE
  architecture: writer = writer(tools=['run_sql', 'find_values'], skills=['evidence_first', 'value_matching', 'join_paths']); checker = checker(writer, tools=['run_sql'], skills=['output_columns', 'check_result']); return checker; answered WITH NormalPatientIDs AS (
        SELECT DISTINCT lab.ID
        FROM Laboratory lab
        JOIN Patient pat ON lab.ID = pat.ID
        WHERE (lab.UA < 8.0 AND pat.SEX = 'M') OR (lab.UA < 6.5 AND pat.SEX = 'F')
    ),
    LatestDates AS (
        SELECT ID, MAX(Date) as MaxDate
        FROM Laboratory
        WHERE ID IN (SELECT ID FROM NormalPatientIDs)
        GROUP BY ID
    )
    SELECT AVG(l.UA)
    FROM Laboratory l
    JOIN LatestDates ld ON l.ID = ld.ID AND l.Date = ld.MaxDate;, correct SELECT AVG(T2.UA) FROM Patient AS T1 INNER JOIN Laboratory AS T2 ON T1.ID = T2.ID WHERE (T2.UA < 6.5 AND T1.SEX = 'F') OR (T2.UA < 8.0 AND T1.SEX = 'M') AND T2.Date = ( SELECT MAX(Date) FROM Laboratory )
- [moderate] Database: codebase_community (tables: badges, comments, postHistory, postLinks, posts, tags, users, votes)
Question: User No.23853 gave a comment to a post at 9:08:18 on 2013/7/12, was that post well-finished?
Evidence: user no. 23853 refers to UserId = '23853'; at 9:08:18 on 201
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching', 'evidence_first']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT CASE 
    WHEN p.ClosedDate IS NOT NULL THEN 'Well-finished'
    ELSE 'Not well-finished'
END AS Status
FROM comments c
JOIN posts p ON c.PostId = p.Id
WHERE c.UserId = 23853 
  AND c.CreationDate = '2013-07-12 09:08:18.0';, correct SELECT IIF(T2.ClosedDate IS NULL, 'NOT well-finished', 'well-finished') AS resylt FROM comments AS T1 INNER JOIN posts AS T2 ON T1.PostId = T2.Id WHERE T1.UserId = 23853 AND T1.CreationDate = '2013-07-12 09:08:18.0'
- [simple] Database: card_games (tables: cards, foreign_data, legalities, sets, set_translations, rulings)
Question: What is the type of the card "Ancestor's Chosen" as originally printed?
Evidence: Ancestor's Chosen' is the name of card; type of the card as originally printed refers to ori
  architecture: a = writer(tools=['run_sql'], skills=['value_matching']); return a; answered SELECT originalType
FROM cards
WHERE name = 'Ancestor''s Chosen';, correct SELECT originalType FROM cards WHERE name = 'Ancestor''s Chosen' AND originalType IS NOT NULL
- [simple] Database: california_schools (tables: frpm, satscores, schools)
Question: Which active district has the highest average score in Reading?
Evidence: -
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'top_k_ties', 'ratio_percentage']); b = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return b; answered SELECT T2.District
FROM schools AS T2
JOIN satscores AS T1 ON T1.cds = T2.CDSCode
WHERE T2.StatusType = 'Active'
GROUP BY T2.District
ORDER BY AVG(T1.AvgScrRead) DESC
LIMIT 1;, correct SELECT T1.District FROM schools AS T1 INNER JOIN satscores AS T2 ON T1.CDSCode = T2.cds WHERE T1.StatusType = 'Active' ORDER BY T2.AvgScrRead DESC LIMIT 1
- [challenging] Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, results)
Question: Among all the lap records set on various circuits, what is the time for the fastest 
  architecture: a = writer(tools=['run_sql'], skills=['top_k_ties']); return a; answered SELECT time
FROM lapTimes
ORDER BY milliseconds
LIMIT 1;, correct SELECT time FROM lapTimes ORDER BY (CASE WHEN INSTR(time, ':') <> INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':') THEN CAST(SUBSTR(time, 1, INSTR(time, ':') - 1) AS REAL) * 3600 ELSE 0 END) + (CAST(SUBSTR(time, INSTR(time, ':') - 2 * (INSTR(time, ':') = INSTR(SUBSTR(time, INSTR(time, ':') + 1), ':') + INSTR(time, ':')), INSTR(time, ':') - 1) AS REAL) * 60) + (CAST(SUBSTR(time, INSTR(time, ':') + 1, INSTR(time, '.') - INSTR(time, ':') - 1) AS REAL)) + (CAST(SUBSTR(time, INSTR(time, '.') + 1) AS REAL) / 1000) ASC LIMIT 1
- [simple] Database: student_club (tables: event, major, zip_code, attendance, budget, expense, income, member)
Question: Please list the full names of the students in the Student_Club that come from the Art and Design Department.
Evidence: full name refers to first_name, last_name;
  architecture: a = writer(tools=['run_sql', 'find_values'], skills=['join_paths', 'value_matching', 'output_columns']); c = checker(a, tools=['run_sql'], skills=['output_columns', 'check_result']); return c; answered SELECT m.first_name, m.last_name
FROM member m
JOIN major maj ON m.link_to_major = maj.major_id
WHERE maj.department = 'Art and Design';, correct SELECT T1.first_name, T1.last_name FROM member AS T1 INNER JOIN major AS T2 ON T1.link_to_major = T2.major_id WHERE T2.department = 'Art and Design Department'