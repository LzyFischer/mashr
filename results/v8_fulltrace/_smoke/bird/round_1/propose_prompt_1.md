You improve a multi-agent system whose task agents answer questions over SQLite databases by writing SQL, by editing its harnesses.
The model (a 9B LLM, no thinking for task agents) is fixed.

# The system
For each question the meta-agent (the 9B model, guided by its meta-harness) writes a team as code:
    a = writer(tools=["run_sql", "find_values"], skills=["value_matching"])
    c = checker(a, tools=["run_sql"], skills=["output_columns"])
    return c
Each line is a task agent with its self harness (its role) and the residual harness the meta-agent
gives it for this question: tools (Python functions on the question's database (no tools = no database access; up to 5 runs)) and skills (how-to texts), chosen from the libraries
below. A node sees the schema, the question, the evidence and the full work of its inputs; with tools it may run Python on the database up to 5 times, then writes its final query. Nodes without inputs run in parallel. `return x`: x's query is the answer. The meta-agent does not do the
question itself. Unusable output -> the first task agent alone with run_sql (fixed).

# Self vs residual
A role is the same on every question, so it can hold only practices that help on every question that agent
works on. Whatever helps only some questions (a method, a check, domain knowledge, a helper function)
belongs to the residual side: a skill or a tool, plus a meta-harness rule that says when to give it.
You learn which parts are general and which vary per question; the meta-agent fills in the varying part
on each question. Before putting a sentence into a role, ask: is it right for every question this agent
sees? If not, make it a skill or a tool and a rule. Conversely, a skill the meta-agent gives to nearly
every node of an agent can move into that agent's role.

# What you edit: three layers
| layer | side | what | effect |
|---|---|---|---|
| task-agent | self | add, remove or edit a task agent (its role) | always on for that agent |
| meta-agent | residual | add, edit or remove a rule of the meta-harness | how the meta-agent staffs, wires and equips teams |
| library | residual | add or edit a skill or a tool (never removed) | what the meta-agent can give; a new item has no effect until the meta-agent gives it |
The model, the answer format and the grader are fixed.

# Principles
- Evidence first: each change targets a failure pattern you see in the traces below (which problems,
  which node, which step went wrong, why), not a general best practice.
- Choose the layer that fits the root cause (see Self vs residual): a practice an agent should always
  follow -> its role; whom to staff, how to wire, which tools and skills -> a meta-harness rule;
  knowledge or a helper that only some questions need -> a skill or tool and a rule.
- Regressions first: if the last accepted change broke problems, find out why before adding more.
- If a failure persists after changes on one layer (verdict INEFFECTIVE, or the problems stay wrong),
  revert them and try another layer.
- Few, decisive changes. Remove rules and agents the evidence does not support. Skills and tools are
  never removed: an unhelpful one is fixed by editing it or by the rules that say when to give it.

# Generality (hard constraints)
- Held-out questions are different questions of the same kind. Write nothing that only fits one question in
  this report: no answers, constants, entity, table or column names, or wording copied from a report
  question. A rule must name a class of questions that can be recognized from the question text alone.
- Target patterns shared by several wrong questions (cite them in evidence), not a single failure.
- No ban lists or name lists ("never give X", "only these tools") unless the cited failures were
  caused by X.
- Prefer removing, merging or shortening rules and roles over adding; if a new rule overlaps an old
  one, edit the old one. Every role, rule and skill costs tokens on each question, and a 9B model follows long
  instructions less reliably.
- A tool is a general helper (compute, check, search, inspect) with a test. It must not contain an
  answer or a special case for one question.
- At most 8 operations in this candidate (all changes together).

# Analysis
1. Read the history: which candidates were accepted or rejected, their held-out results (fixed and
   broken against the incumbent) and, for accepted changes, which of their cited problems were fixed.
   KEEP what works, IMPROVE what is directionally right, ROLLBACK what did not work and re-approach
   that pattern on another layer.
2. Read "Since the last accepted change" in the report: regressions first.
3. Read the traces of the wrong questions: for each, find the node and the step where it went wrong.
   Group them into patterns and find each one's root cause.
4. Check which architectures, tools and skills help and which do not.

Objective: maximize accuracy on held-out problems.
This candidate may edit only the residual side: the meta-agent and library layers.

# Output
A JSON object between <edit> and </edit>:
{"changes": [{"pattern": "<the failure pattern, one sentence>",
               "rationale": "<its root cause in the traces, and why this layer and these ops fix it>",
               "evidence": ["<labels of the wrong dev-A questions that show this pattern, e.g. A12>"],
               "ops": [<edit operations, applied in order>]}]}
One change per failure pattern. If the candidate is accepted, the next round reports which of its
cited questions were fixed.

# Edit operations
task-agent layer:
{"op": "add_agent", "name": "<name>", "role": "<role>"}
{"op": "remove_agent", "name": "<name>"}
{"op": "edit_agent", "name": "<name>", "role": "<new role>"}
meta-agent layer (rule numbers as shown below; new rules are appended):
{"op": "add_rule", "text": "<rule>"}
{"op": "edit_rule", "rule": <number>, "text": "<new rule>"}
{"op": "remove_rule", "rule": <number>}
library layer:
{"op": "add_skill", "name": "<name>", "when": "<when to give it (shown to the meta-agent)>", "text": "<the procedure (shown to the task agent)>"}
{"op": "edit_skill", "name": "<name>", "when": "<optional>", "text": "<optional>"}
{"op": "add_tool", "name": "<name>", "doc": "<signature and what it prints or returns>", "code": "<Python source defining it>", "test": "<Python asserts; must pass>"}
{"op": "edit_tool", "name": "<name>", "doc": "<optional>", "code": "<optional>", "test": "<optional>"}
Tool code runs in a sandbox (Python 3, sqlite3, no network, 30 s) with DB (the path of the question's SQLite file; open it read-only: sqlite3.connect(f"file:{DB}?mode=ro", uri=True)) and DESC (its database_description folder of CSV files) defined; tests run on one dev database. Tools print their results. A new or edited tool is run with its test first; if the test fails, the candidate is sent back.
At most 8 task agents, 20 rules, 40 skills and 24 tools. No rule may
mention a removed agent. Names: a letter, then letters, digits or underscores.

# Tools
- run_sql: run_sql(query, limit=20) -> prints the result rows (at most limit) and the row count of a read-only SQLite query on this database.
```python
import sqlite3
def run_sql(query, limit=20):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        rows = con.execute(query).fetchall()
    except Exception as e:
        print("SQL error:", e); return
    finally:
        con.close()
    print(f"{len(rows)} rows"); [print(r) for r in rows[:limit]]
```
- find_values: find_values(table, column, text, limit=20) -> prints distinct values of table.column that contain text (case-insensitive), to match the exact spelling used in the data.
```python
import sqlite3
def find_values(table, column, text, limit=20):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        rows = con.execute(f'SELECT DISTINCT "{column}" FROM "{table}" WHERE "{column}" LIKE ? LIMIT ?',
                           (f"%{text}%", limit)).fetchall()
    except Exception as e:
        print("error:", e); return
    finally:
        con.close()
    print([r[0] for r in rows] or "no match")
```
- sample_rows: sample_rows(table, n=3) -> prints n rows of the table with column names, to see value formats (dates, codes, units).
```python
import sqlite3
def sample_rows(table, n=3):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        cur = con.execute(f'SELECT * FROM "{table}" LIMIT ?', (n,))
        print([d[0] for d in cur.description]); [print(r) for r in cur.fetchall()]
    except Exception as e:
        print("error:", e)
    finally:
        con.close()
```
- column_info: column_info(table) -> prints the documented meaning and value descriptions of the table's columns (from the database's description files).
```python
import csv, os
def column_info(table):
    path = os.path.join(DESC, f"{table}.csv")
    if not os.path.exists(path):
        print("no description for", table); return
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        for r in csv.DictReader(f):
            line = f"{r.get('original_column_name', '').strip()}: {r.get('column_description', '').strip()}"
            if (r.get("value_description") or "").strip():
                line += f" | values: {r['value_description'].strip()[:300]}"
            print(line)
```

# Skills
- evidence_first (when: the question comes with evidence (formulas, value mappings)): 1. Read the evidence before writing SQL: it defines formulas (rate = A / B), value codes ('F' means female) and which column a phrase refers to. 2. Use the evidence literally: the same columns, the same constants, the same formula. 3. Pitfall: replacing an evidence formula with your own interpretation. 4. Check that every part of the evidence appears in the query.
- value_matching (when: the question names a specific value (a name, a place, a category, a code)): 1. Values in the data may differ from the question in case, spelling or format ('Alameda' vs 'ALAMEDA', 'F' vs 'Female'). 2. Look them up with find_values(table, column, text) or a SELECT DISTINCT before filtering. 3. Use = with the exact stored value; use LIKE only when the question asks for 'contains'. 4. Pitfall: a filter on a misspelled value returns 0 rows; if a query returns nothing, check the values first.
- join_paths (when: the answer needs columns from more than one table): 1. Find the key columns that link the tables (same name or documented as an id). 2. Join along the shortest path; alias tables (T1, T2). 3. Pitfalls: joining on the wrong id column, a join that multiplies rows (then COUNT needs DISTINCT), mixing up columns with the same name in two tables (always prefix with the alias). 4. Run the query and check that the row count is plausible.
- ratio_percentage (when: rates, ratios, percentages, averages computed by division): 1. Integer division truncates in SQLite: write CAST(x AS REAL) / y. 2. Percentage = CAST(part AS REAL) * 100 / total; check whether the question or evidence wants a ratio or a percentage. 3. Conditional counts: SUM(CASE WHEN cond THEN 1 ELSE 0 END) or COUNT(CASE WHEN cond THEN 1 END). 4. Pitfall: dividing counts taken over different row sets. Check the value lies in a sensible range.
- top_k_ties (when: highest, lowest, most, least, top N, the first/last): 1. ORDER BY col DESC LIMIT 1 returns one row; if ties are possible and the question asks for all of them, use WHERE col = (SELECT MAX(col) ...). 2. Exclude NULLs before ordering (ORDER BY puts NULL first in ASC). 3. 'Most frequent': GROUP BY then ORDER BY COUNT(*) DESC LIMIT 1. 4. Return the column the question asks for (the name, not the count), unless both are asked.
- counting (when: how many, number of, count): 1. Decide what is counted: rows, distinct entities (COUNT(DISTINCT id)) or a sum of a count column. 2. After a join, entities can repeat: use COUNT(DISTINCT key). 3. Conditions on related tables go in WHERE after the join, or in EXISTS. 4. Pitfall: COUNT(col) skips NULLs, COUNT(*) does not.
- dates_text (when: dates, years, months, ages, times, or numbers stored as text): 1. Look at the stored format first (sample_rows): 'YYYY-MM-DD', 'YYYY', timestamps, or text. 2. Year: strftime('%Y', col) = '2012' or SUBSTR(col, 1, 4); compare text with text. 3. Ranges: col BETWEEN '2012-01-01' AND '2012-12-31'. 4. Age from birthday: use the year difference the evidence defines. 5. Numbers stored as text: CAST(col AS REAL) before comparing or averaging.
- null_empty (when: missing values, 'not null', 'has a', 'without'): 1. 'Has a value' means col IS NOT NULL (and maybe col != ''). 2. NULLs are skipped by AVG/SUM/COUNT(col) and sort first in ascending order. 3. 'Without X' across tables: NOT EXISTS or LEFT JOIN ... WHERE right.key IS NULL. 4. Check with a quick count of NULLs when the result looks off.
- output_columns (when: before the final query of any question): 1. Select exactly what the question asks, in its order: the asked attribute(s), not extra ids or helper columns. 2. Don't add DISTINCT, LIMIT or ORDER BY unless the question implies them ('list' may need DISTINCT when entities repeat). 3. If several values are asked ('name and age'), return them as separate columns. 4. Run the final query once and look at the rows.
- subquery_vs_join (when: conditions that refer to an aggregate (above average, the one with the max) or to another table): 1. Compare with an aggregate via a scalar subquery: WHERE x > (SELECT AVG(x) FROM t). 2. 'The X of the Y with the most Z': find Y in a subquery (ORDER BY ... LIMIT 1), then select its X. 3. IN (subquery) for membership; EXISTS for 'has at least one'. 4. Pitfall: aggregating in WHERE (use HAVING after GROUP BY).
- explore_then_write (when: unfamiliar schema, ambiguous column choice, or several similar columns): 1. Before writing the query, spend one tool run on exploration: column_info for the tables involved, sample_rows for formats. 2. Pick columns by their documented meaning, not just their names. 3. Write the query, run it, inspect the rows. 4. If the result is empty or implausible, find which filter removes the rows and fix it.
- check_result (when: reviewing another agent's query): 1. Re-read the question and evidence; list each condition and the asked output. 2. Check the query covers each condition with the right column and value, the right joins, and the asked output columns. 3. Run it and judge the rows: count, ranges, NULLs. 4. Keep the query if it is right; otherwise fix the specific error and run the fixed query. Do not rewrite a correct query.

# Current organization
Task agents:
- writer: You write correct SQLite queries that answer questions about a database.
- checker: You check the SQL written by your teammates against the question and the evidence, fix any error, and give the query you believe is correct.
Meta-harness:
1. Simple question: one writer with run_sql.
2. Joins, aggregates, ratios or specific values: a writer with run_sql and find_values, then a checker with run_sql.
3. Give skills that match the question.

# Report
# Report (dev-A)

Organization: acc 50.0% (meta-agent prompt 3183 chars; roles 212 chars). 1 distinct architectures, 2.0 nodes per problem. Fallback (unusable meta-agent output): 0.

## By category
| category | n | acc | architectures |
|---|---|---|---|
| moderate | 3 | 33% | writer[T][S]>checker[T][S] 3 |
| simple | 5 | 60% | writer[T][S]>checker[T][S] 5 |

## Architectures
| architecture | uses | acc |
|---|---|---|
| writer[T][S]>checker[T][S] | 8 | 50% |

## Task agents
answer correct = the node's own answer; cut = its output hit the token limit; for nodes with inputs: changed = its answer differs from its inputs' majority.
| agent | uses | answer correct | cut | changed | to correct | to wrong |
|---|---|---|---|---|---|---|
| writer | 8 | 62% | 0% | - | - | - |
| checker (with inputs) | 8 | 50% | 0% | 1 | - | 1 |

## Residual harness (what the meta-agent gave each node)
| item | nodes given it | node answer correct when given | otherwise |
|---|---|---|---|
| tool:run_sql | 16 | 56% | - |
| skill:output_columns | 9 | 67% | 43% |
| tool:find_values | 8 | 62% | 50% |
| skill:value_matching | 7 | 71% | 44% |
| skill:check_result | 7 | 43% | 67% |
| skill:join_paths | 5 | 80% | 45% |
| tool:sample_rows | 2 | 0% | 64% |
| skill:counting | 2 | 100% | 50% |
| skill:dates_text | 2 | 0% | 64% |
| skill:top_k_ties | 1 | 0% | 60% |
| tool:column_info | 1 | 100% | 53% |
| skill:evidence_first | 1 | 0% | 60% |
| skill:explore_then_write | 1 | 0% | 60% |
Never given: ratio_percentage, null_empty, subquery_vs_join.

## Wrong (4)
- A3 [simple] answered SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5;; correct SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5; team: a = writer(tools=['run_sql', 'find_values', 'sample_rows'], skills=['top_k_ties', 'join_paths', 'output_columns']); c = checker(a, tools=['run_sql'], skills=['check_result']); return c
- A6 [moderate] answered SELECT AVG(
    CAST(SUBSTR(r.fastestLapTime, 1, 2) AS INTEGER) * 60 + 
    CAST(SUBSTR(r.fastestLapTime, 4, 2) AS INTEGER) + 
    CAST(SUBSTR(r.fastestLapTime, 7, 3) AS REAL) / 1000.0
) as average_fa; correct SELECT AVG(CAST(SUBSTR(T2.fastestLapTime, 1, INSTR(T2.fastestLapTime, ':') - 1) AS INTEGER) * 60 + CAST(SUBSTR(T2.fastestLapTime, INSTR(T2.fastestLapTime, ':') + 1) AS REAL)) FROM drivers AS T1 INNER ; team: w = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'evidence_first', 'dates_text']); c = checker(w, tools=['run_sql'], skills=['check_result']); return c
- A7 [simple] answered SELECT COUNT(*) 
FROM results
WHERE raceId > 50 
  AND raceId < 100 
  AND statusId = 2;; correct SELECT SUM(IIF(time IS NOT NULL, 1, 0)) FROM results WHERE statusId = 2 AND raceID < 100 AND raceId > 50; team: w = writer(tools=['run_sql', 'find_values'], skills=['counting', 'value_matching']); c = checker(w, tools=['run_sql'], skills=['output_columns', 'check_result']); return c
- A8 [moderate] answered SELECT 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) AS spent_2019,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS spent_2020,
; correct SELECT SUM(CASE WHEN SUBSTR(T1.event_date, 1, 4) = '2019' THEN T2.spent ELSE 0 END) - SUM(CASE WHEN SUBSTR(T1.event_date, 1, 4) = '2020' THEN T2.spent ELSE 0 END) AS num FROM event AS T1 INNER JOIN bu; team: a = writer(tools=['run_sql', 'find_values', 'sample_rows'], skills=['dates_text', 'value_matching', 'explore_then_write']); c = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return c

## Traces of the wrong problems (4 of 4; node outputs over 6000 chars are cut in the middle)
### A6 [moderate]
Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, results)
Question: What is the average fastest lap time in seconds for Lewis Hamilton in all the Formula_1 races?
Evidence: average fastest lap time = avg(fastestLapTime); The time is recorded on 'MM:SS.mmm'
Correct: SELECT AVG(CAST(SUBSTR(T2.fastestLapTime, 1, INSTR(T2.fastestLapTime, ':') - 1) AS INTEGER) * 60 + CAST(SUBSTR(T2.fastestLapTime, INSTR(T2.fastestLapTime, ':') + 1) AS REAL)) FROM drivers AS T1 INNER JOIN results AS T2 ON T1.driverId = T2.driverId WHERE T1.surname = 'Hamilton' AND T1.forename = 'Lewis'
Team: w = writer(tools=['run_sql', 'find_values'], skills=['value_matching', 'evidence_first', 'dates_text']); c = checker(w, tools=['run_sql'], skills=['check_result']); return c
#### node w = writer(inputs=[], tools=['run_sql', 'find_values'], skills=['value_matching', 'evidence_first', 'dates_text']) -> SELECT AVG(
    CAST(SUBSTR(r.fastestLapTime, 1, 2) AS INTEGER) * 60 + 
    CAST(SUBSTR(r.fastestLapTime, 4, 2) AS INTEGER) + 
    CAST(SUBSTR(r.fastestLapTime, 7, 3) AS REAL) / 1000.0
) as average_fastest_lap_seconds
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE d.driverId = 1; (wrong)
```
To calculate the average fastest lap time in seconds for Lewis Hamilton, I need to:
1.  Identify the `driverId` for Lewis Hamilton from the `drivers` table.
2.  Join the `results` table with the `drivers` table to filter for Lewis Hamilton.
3.  Extract the `fastestLapTime` from the `results` table.
4.  Convert the time format 'MM:SS.mmm' to seconds.
    *   Minutes (`MM`) * 60
    *   Seconds (`SS`) * 1
    *   Milliseconds (`mmm`) / 1000
    *   Formula: `CAST(SUBSTR(time, 1, 2) AS INTEGER) * 60 + CAST(SUBSTR(time, 4, 2) AS INTEGER) + CAST(SUBSTR(time, 7, 3) AS REAL) / 1000.0`
5.  Calculate the average of these converted values.

First, let's verify the exact spelling of Lewis Hamilton's name in the database to ensure we get the correct `driverId`.

```python
run_sql("SELECT driverId, forename, surname FROM drivers WHERE forename = 'Lewis' AND surname = 'Hamilton';")
```

[Python output]
1 rows
(1, 'Lewis', 'Hamilton')

The `driverId` for Lewis Hamilton is 1. The `fastestLapTime` is stored as 'MM:SS.mmm'. To convert this to seconds:
- Extract minutes: `SUBSTR(fastestLapTime, 1, 2)` -> multiply by 60
- Extract seconds: `SUBSTR(fastestLapTime, 4, 2)` -> multiply by 1
- Extract milliseconds: `SUBSTR(fastestLapTime, 7, 3)` -> divide by 1000

The query joins `drivers` and `results` on `driverId`, filters for driverId = 1, converts the time string to a numeric value in seconds, and calculates the average.

```sql
SELECT AVG(
    CAST(SUBSTR(r.fastestLapTime, 1, 2) AS INTEGER) * 60 + 
    CAST(SUBSTR(r.fastestLapTime, 4, 2) AS INTEGER) + 
    CAST(SUBSTR(r.fastestLapTime, 7, 3) AS REAL) / 1000.0
) as average_fastest_lap_seconds
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE d.driverId = 1;
```
```
#### node c = checker(inputs=['w'], tools=['run_sql'], skills=['check_result']) -> SELECT AVG(
    CAST(SUBSTR(r.fastestLapTime, 1, 2) AS INTEGER) * 60 + 
    CAST(SUBSTR(r.fastestLapTime, 4, 2) AS INTEGER) + 
    CAST(SUBSTR(r.fastestLapTime, 7, 3) AS REAL) / 1000.0
) as average_fastest_lap_seconds
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE d.driverId = 1; (wrong)
```
To calculate the average fastest lap time in seconds for Lewis Hamilton, we need to:
1.  Identify Lewis Hamilton's `driverId` in the `drivers` table.
2.  Join the `results` table with the `drivers` table to filter for Lewis Hamilton.
3.  Select the `fastestLapTime` column from the `results` table.
4.  Convert the time format 'MM:SS.mmm' to seconds.
    *   Minutes (`MM`) * 60
    *   Seconds (`SS`) * 1
    *   Milliseconds (`mmm`) / 1000
    *   Formula: `CAST(SUBSTR(time, 1, 2) AS INTEGER) * 60 + CAST(SUBSTR(time, 4, 2) AS INTEGER) + CAST(SUBSTR(time, 7, 3) AS REAL) / 1000.0`
5.  Calculate the average of these converted values.

First, let's verify the exact spelling of Lewis Hamilton's name in the database to ensure we get the correct `driverId`.

```python
run_sql("SELECT driverId, forename, surname FROM drivers WHERE forename = 'Lewis' AND surname = 'Hamilton';")
```

[Python output]
1 rows
(1, 'Lewis', 'Hamilton')

The `driverId` for Lewis Hamilton is 1. The `fastestLapTime` is stored as 'MM:SS.mmm'. To convert this to seconds:
- Extract minutes: `SUBSTR(fastestLapTime, 1, 2)` -> multiply by 60
- Extract seconds: `SUBSTR(fastestLapTime, 4, 2)` -> multiply by 1
- Extract milliseconds: `SUBSTR(fastestLapTime, 7, 3)` -> divide by 1000

The query joins `drivers` and `results` on `driverId`, filters for driverId = 1, converts the time string to a numeric value in seconds, and calculates the average.

```sql
SELECT AVG(
    CAST(SUBSTR(r.fastestLapTime, 1, 2) AS INTEGER) * 60 + 
    CAST(SUBSTR(r.fastestLapTime, 4, 2) AS INTEGER) + 
    CAST(SUBSTR(r.fastestLapTime, 7, 3) AS REAL) / 1000.0
) as average_fastest_lap_seconds
FROM results r
JOIN drivers d ON r.driverId = d.driverId
WHERE d.driverId = 1;
```
```
### A3 [simple]
Database: california_schools (tables: frpm, satscores, schools)
Question: List the top five schools, by descending order, from the highest to the lowest, the most number of Enrollment (Ages 5-17). Please give their NCES school identification number.
Evidence: -
Correct: SELECT T1.NCESSchool FROM schools AS T1 INNER JOIN frpm AS T2 ON T1.CDSCode = T2.CDSCode ORDER BY T2.`Enrollment (Ages 5-17)` DESC LIMIT 5
Team: a = writer(tools=['run_sql', 'find_values', 'sample_rows'], skills=['top_k_ties', 'join_paths', 'output_columns']); c = checker(a, tools=['run_sql'], skills=['check_result']); return c
#### node a = writer(inputs=[], tools=['run_sql', 'find_values', 'sample_rows'], skills=['top_k_ties', 'join_paths', 'output_columns']) -> SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5; (wrong)
```
To answer this question, I need to retrieve the top five schools based on the `Enrollment (Ages 5-17)` column in descending order and return their `NCESDist` (NCES school identification number) from the `schools` table.

First, I will verify the column names and data by sampling the `frpm` and `schools` tables.

```python
run_sql("SELECT * FROM frpm LIMIT 5")
```

```python
run_sql("SELECT * FROM schools LIMIT 5")
```

Based on the schema provided:
- The `frpm` table contains `Enrollment (Ages 5-17)`.
- The `schools` table contains `NCESDist` (NCES school identification number).
- They are linked by `CDSCode`.

The query will join `frpm` and `schools` on `CDSCode`, order by `Enrollment (Ages 5-17)` descending, and limit to 5 rows. I will select `NCESDist` as requested.

```sql
SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5;
```
```
#### node c = checker(inputs=['a'], tools=['run_sql'], skills=['check_result']) -> SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5; (wrong)
```
To answer the question, we need to retrieve the top five schools based on the `Enrollment (Ages 5-17)` column in descending order and return their `NCESDist` (NCES school identification number) from the `schools` table.

The `frpm` table contains the `Enrollment (Ages 5-17)` column, and the `schools` table contains the `NCESDist` column. Both tables can be joined on the `CDSCode` column.

Here is the corrected query:

```sql
SELECT s.NCESDist
FROM frpm f
JOIN schools s ON f.CDSCode = s.CDSCode
ORDER BY f.`Enrollment (Ages 5-17)` DESC
LIMIT 5;
```
```
### A8 [moderate]
Database: student_club (tables: event, major, zip_code, attendance, budget, expense, income, member)
Question: Calculate the difference of the total amount spent in all events by the Student_Club in year 2019 and 2020.
Evidence: The first 4 strings of the event_date values in the event table can represent year; The difference of the total amount spent = SUBTRACT(spent where YEAR(event_date) = 2019, spent where YEAR(event_date) = 2020)
Correct: SELECT SUM(CASE WHEN SUBSTR(T1.event_date, 1, 4) = '2019' THEN T2.spent ELSE 0 END) - SUM(CASE WHEN SUBSTR(T1.event_date, 1, 4) = '2020' THEN T2.spent ELSE 0 END) AS num FROM event AS T1 INNER JOIN budget AS T2 ON T1.event_id = T2.link_to_event
Team: a = writer(tools=['run_sql', 'find_values', 'sample_rows'], skills=['dates_text', 'value_matching', 'explore_then_write']); c = checker(a, tools=['run_sql'], skills=['check_result', 'output_columns']); return c
#### node a = writer(inputs=[], tools=['run_sql', 'find_values', 'sample_rows'], skills=['dates_text', 'value_matching', 'explore_then_write']) -> SELECT 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) AS spent_2019,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS spent_2020,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) - 
    SUM(CASE WHE (wrong)
```
To calculate the difference in total spending between 2019 and 2020, I need to first understand how the `event_date` column is formatted to correctly extract the year. Then I will sum the expenses linked to events in those years.

Let's first explore the `event` table to see the date format.

```python
run_sql("SELECT DISTINCT event_date FROM event LIMIT 10;")
```

[Python output]
10 rows
('2020-03-10T12:00:00',)
('2020-01-14T09:30:00',)
('2019-11-24T09:00:00',)
('2020-03-10T09:30:00',)
('2019-10-05T12:00:00',)
('2020-04-21T12:00:00',)
('2019-10-24T13:00:00',)
('2020-03-24T12:00:00',)
('2019-10-22T12:00:00',)
('2019-09-12T06:00:00',)

The `event_date` column is in the format `'YYYY-MM-DD HH:MM:SS'`. To extract the year, I can use `strftime('%Y', event_date)`.

The question asks for the difference: (Total spent in 2019) - (Total spent in 2020).
The "amount spent" is stored in the `budget` table (column `spent`) linked to events via `link_to_event`.

I will join the `budget` and `event` tables, filter by year, sum the `spent` amounts for 2019 and 2020 separately, and then calculate the difference.

```sql
SELECT 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) AS spent_2019,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS spent_2020,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) - 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS difference
FROM budget b
JOIN event e ON b.link_to_event = e.event_id;
```
```
#### node c = checker(inputs=['a'], tools=['run_sql'], skills=['check_result', 'output_columns']) -> SELECT 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) AS spent_2019,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS spent_2020,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) - 
    SUM(CASE WHE (wrong)
```
To calculate the difference in total spending between 2019 and 2020, we need to:
1. Join the `budget` table with the `event` table to access the `event_date`.
2. Extract the year from `event_date` using `strftime('%Y', event_date)`.
3. Sum the `spent` amounts for events in 2019 and 2020 separately.
4. Calculate the difference: (Total spent in 2019) - (Total spent in 2020).

The teammate's query logic is correct. It uses `CASE` statements to conditionally sum the `spent` column based on the extracted year and then subtracts the two sums. The date format observed (`'YYYY-MM-DD HH:MM:SS'`) is compatible with `strftime('%Y', ...)`.

Here is the final query:

```sql
SELECT 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) AS spent_2019,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS spent_2020,
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2019' THEN b.spent ELSE 0 END) - 
    SUM(CASE WHEN strftime('%Y', e.event_date) = '2020' THEN b.spent ELSE 0 END) AS difference
FROM budget b
JOIN event e ON b.link_to_event = e.event_id;
```
```
### A7 [simple]
Database: formula_1 (tables: circuits, constructors, drivers, seasons, races, constructorResults, constructorStandings, driverStandings, lapTimes, pitStops, qualifying, status, results)
Question: From race no. 50 to 100, how many finishers have been disqualified?
Evidence: disqualified refers to statusID = 2, finisher refers to time! = null; race no. refers to raceId; raceId > 50 and raceId < 100;
Correct: SELECT SUM(IIF(time IS NOT NULL, 1, 0)) FROM results WHERE statusId = 2 AND raceID < 100 AND raceId > 50
Team: w = writer(tools=['run_sql', 'find_values'], skills=['counting', 'value_matching']); c = checker(w, tools=['run_sql'], skills=['output_columns', 'check_result']); return c
#### node w = writer(inputs=[], tools=['run_sql', 'find_values'], skills=['counting', 'value_matching']) -> SELECT COUNT(*) 
FROM results
WHERE raceId > 50 
  AND raceId < 100 
  AND statusId = 2 
  AND time IS NOT NULL; (correct)
```
To answer this question, I need to count the number of drivers who finished a race (indicated by a non-null `time` in the `results` table) but were disqualified. The evidence provided states that disqualification corresponds to `statusId = 2`. The race number constraint is `raceId` between 50 and 100 (exclusive, based on "from... to..." usually implying the range, but the evidence explicitly says `raceId > 50 and raceId < 100`).

Let's verify the `statusId` for "disqualified" first to be absolutely sure, although the evidence states it is 2. Then I will construct the query to count rows in the `results` table where `statusId = 2` and `time IS NOT NULL` for the specified `raceId` range.

```python
# Verify the statusId for 'Disqualified'
run_sql("SELECT statusId, status FROM status WHERE status LIKE '%disquali%';")
```

```sql
SELECT COUNT(*) 
FROM results
WHERE raceId > 50 
  AND raceId < 100 
  AND statusId = 2 
  AND time IS NOT NULL;
```
```
#### node c = checker(inputs=['w'], tools=['run_sql'], skills=['output_columns', 'check_result']) -> SELECT COUNT(*) 
FROM results
WHERE raceId > 50 
  AND raceId < 100 
  AND statusId = 2; (wrong)
```
The teammate's query is almost correct but contains a slight logical redundancy based on the provided evidence. The evidence states: "disqualified refers to statusID = 2, finisher refers to time! = null". In the `results` table, a race result typically has a `time` only if the driver finished. However, the `statusId` itself (e.g., 2 for Disqualified) is the primary indicator of disqualification.

Let's first verify the status codes to ensure `statusId = 2` indeed corresponds to "Disqualified". Then we will construct the final query.

```python
run_sql("SELECT statusId, status FROM status WHERE status LIKE '%disquali%';")
```

```sql
SELECT COUNT(*) 
FROM results
WHERE raceId > 50 
  AND raceId < 100 
  AND statusId = 2;
```
```

# History (held-out dev-B)
round 0 (starting organization): acc 50.0%

Output the JSON object between <edit> and </edit>.