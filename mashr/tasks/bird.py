"""Task: BIRD text-to-SQL (dev set, 11 SQLite databases). A node sees the schema, the question and the
evidence; with tools it may run Python with database helpers preloaded (up to MAX_RUNS times) before
it writes its final query. Grading: execution accuracy (the predicted and gold queries return the
same set of rows), as in the official BIRD evaluation."""
import json
import os
import random
import re
import sqlite3
import threading
import time

from ..sandbox import CODE, run_python

NAME = "bird"
DATA = os.environ.get("MASHR_BIRD", os.path.expanduser("~/project/harness-rsi/data/bird/dev_20240627"))
ANSWER_FMT = "End your response with your final SQLite query in one ```sql``` code block."
MAX_TOKENS = 3072
MAX_RUNS = 5
VOTE_ON_MISSING = True
FALLBACK_TOOLS = ("run_sql",)
TOOLS_ARE_CODE = True    # the evolver may add / edit tools (Python on DB, with a sandbox test)
TOOL_ENV = ("Tool code runs in a sandbox (Python 3, sqlite3, no network, 30 s) with DB (the path of the "
            "question's SQLite file; open it read-only: sqlite3.connect(f\"file:{DB}?mode=ro\", uri=True)) "
            "and DESC (its database_description folder of CSV files) defined; tests run on one dev "
            "database. Tools print their results.")
SPLITS = {"dev_a": 150, "dev_b": 50, "test": 300}
META = {"team": "answer questions over SQLite databases by writing SQL", "item": "question",
        "node": "the agent reads the schema, the question, its skills and the full work of its inputs, "
                "then writes its final SQL query.",
        "final": "`return x`: x's query is the answer.",
        "no_solve": "write no SQL.",
        "tools": f"Python functions on the question's database (no tools = no database access; up to "
                 f"{MAX_RUNS} runs)"}
EXAMPLE = ['a = writer(tools=["run_sql", "find_values"], skills=["value_matching"])',
           'c = checker(a, tools=["run_sql"], skills=["output_columns"])', "return c"]
SYSTEM_NOTE = (f"A node sees the schema, the question, the evidence and the full work of its inputs; "
               f"with tools it may run Python on the database up to {MAX_RUNS} times, then writes its "
               "final query.")

TOOLS = {
    "run_sql": {
        "doc": "run_sql(query, limit=20) -> prints the result rows (at most limit) and the row count of "
               "a read-only SQLite query on this database.",
        "code": '''
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
''',
    },
    "find_values": {
        "doc": "find_values(table, column, text, limit=20) -> prints distinct values of table.column that "
               "contain text (case-insensitive), to match the exact spelling used in the data.",
        "code": '''
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
''',
    },
    "sample_rows": {
        "doc": "sample_rows(table, n=3) -> prints n rows of the table with column names, to see value "
               "formats (dates, codes, units).",
        "code": '''
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
''',
    },
    "column_info": {
        "doc": "column_info(table) -> prints the documented meaning and value descriptions of the "
               "table's columns (from the database's description files).",
        "code": '''
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
''',
    },
}

SKILLS = {
    "evidence_first": {
        "when": "the question comes with evidence (formulas, value mappings)",
        "text": "1. Read the evidence before writing SQL: it defines formulas (rate = A / B), value codes "
                "('F' means female) and which column a phrase refers to. 2. Use the evidence literally: "
                "the same columns, the same constants, the same formula. 3. Pitfall: replacing an "
                "evidence formula with your own interpretation. 4. Check that every part of the "
                "evidence appears in the query.",
    },
    "value_matching": {
        "when": "the question names a specific value (a name, a place, a category, a code)",
        "text": "1. Values in the data may differ from the question in case, spelling or format "
                "('Alameda' vs 'ALAMEDA', 'F' vs 'Female'). 2. Look them up with find_values(table, "
                "column, text) or a SELECT DISTINCT before filtering. 3. Use = with the exact stored "
                "value; use LIKE only when the question asks for 'contains'. 4. Pitfall: a filter on a "
                "misspelled value returns 0 rows; if a query returns nothing, check the values first.",
    },
    "join_paths": {
        "when": "the answer needs columns from more than one table",
        "text": "1. Find the key columns that link the tables (same name or documented as an id). 2. "
                "Join along the shortest path; alias tables (T1, T2). 3. Pitfalls: joining on the wrong "
                "id column, a join that multiplies rows (then COUNT needs DISTINCT), mixing up columns "
                "with the same name in two tables (always prefix with the alias). 4. Run the query and "
                "check that the row count is plausible.",
    },
    "ratio_percentage": {
        "when": "rates, ratios, percentages, averages computed by division",
        "text": "1. Integer division truncates in SQLite: write CAST(x AS REAL) / y. 2. Percentage = "
                "CAST(part AS REAL) * 100 / total; check whether the question or evidence wants a "
                "ratio or a percentage. 3. Conditional counts: SUM(CASE WHEN cond THEN 1 ELSE 0 END) or "
                "COUNT(CASE WHEN cond THEN 1 END). 4. Pitfall: dividing counts taken over different "
                "row sets. Check the value lies in a sensible range.",
    },
    "top_k_ties": {
        "when": "highest, lowest, most, least, top N, the first/last",
        "text": "1. ORDER BY col DESC LIMIT 1 returns one row; if ties are possible and the question "
                "asks for all of them, use WHERE col = (SELECT MAX(col) ...). 2. Exclude NULLs before "
                "ordering (ORDER BY puts NULL first in ASC). 3. 'Most frequent': GROUP BY then ORDER BY "
                "COUNT(*) DESC LIMIT 1. 4. Return the column the question asks for (the name, not the "
                "count), unless both are asked.",
    },
    "counting": {
        "when": "how many, number of, count",
        "text": "1. Decide what is counted: rows, distinct entities (COUNT(DISTINCT id)) or a sum of a "
                "count column. 2. After a join, entities can repeat: use COUNT(DISTINCT key). 3. "
                "Conditions on related tables go in WHERE after the join, or in EXISTS. 4. Pitfall: "
                "COUNT(col) skips NULLs, COUNT(*) does not.",
    },
    "dates_text": {
        "when": "dates, years, months, ages, times, or numbers stored as text",
        "text": "1. Look at the stored format first (sample_rows): 'YYYY-MM-DD', 'YYYY', timestamps, "
                "or text. 2. Year: strftime('%Y', col) = '2012' or SUBSTR(col, 1, 4); compare text with "
                "text. 3. Ranges: col BETWEEN '2012-01-01' AND '2012-12-31'. 4. Age from birthday: "
                "use the year difference the evidence defines. 5. Numbers stored as text: CAST(col AS "
                "REAL) before comparing or averaging.",
    },
    "null_empty": {
        "when": "missing values, 'not null', 'has a', 'without'",
        "text": "1. 'Has a value' means col IS NOT NULL (and maybe col != ''). 2. NULLs are skipped by "
                "AVG/SUM/COUNT(col) and sort first in ascending order. 3. 'Without X' across tables: "
                "NOT EXISTS or LEFT JOIN ... WHERE right.key IS NULL. 4. Check with a quick count of "
                "NULLs when the result looks off.",
    },
    "output_columns": {
        "when": "before the final query of any question",
        "text": "1. Select exactly what the question asks, in its order: the asked attribute(s), not "
                "extra ids or helper columns. 2. Don't add DISTINCT, LIMIT or ORDER BY unless the "
                "question implies them ('list' may need DISTINCT when entities repeat). 3. If several "
                "values are asked ('name and age'), return them as separate columns. 4. Run the final "
                "query once and look at the rows.",
    },
    "subquery_vs_join": {
        "when": "conditions that refer to an aggregate (above average, the one with the max) or to another table",
        "text": "1. Compare with an aggregate via a scalar subquery: WHERE x > (SELECT AVG(x) FROM t). "
                "2. 'The X of the Y with the most Z': find Y in a subquery (ORDER BY ... LIMIT 1), then "
                "select its X. 3. IN (subquery) for membership; EXISTS for 'has at least one'. 4. "
                "Pitfall: aggregating in WHERE (use HAVING after GROUP BY).",
    },
    "explore_then_write": {
        "when": "unfamiliar schema, ambiguous column choice, or several similar columns",
        "text": "1. Before writing the query, spend one tool run on exploration: column_info for the "
                "tables involved, sample_rows for formats. 2. Pick columns by their documented meaning, "
                "not just their names. 3. Write the query, run it, inspect the rows. 4. If the result is "
                "empty or implausible, find which filter removes the rows and fix it.",
    },
    "check_result": {
        "when": "reviewing another agent's query",
        "text": "1. Re-read the question and evidence; list each condition and the asked output. 2. "
                "Check the query covers each condition with the right column and value, the right "
                "joins, and the asked output columns. 3. Run it and judge the rows: count, ranges, "
                "NULLs. 4. Keep the query if it is right; otherwise fix the specific error and run the "
                "fixed query. Do not rewrite a correct query.",
    },
}

SEED = {
    "agents": {
        "writer": {"role": "You write correct SQLite queries that answer questions about a database."},
        "checker": {"role": "You check the SQL written by your teammates against the question and the "
                            "evidence, fix any error, and give the query you believe is correct."},
    },
    "rules": [
        "Simple question: one writer with run_sql.",
        "Joins, aggregates, ratios or specific values: a writer with run_sql and find_values, then a "
        "checker with run_sql.",
        "Give skills that match the question.",
    ],
}

BASELINES = {
    "single": "a = writer()\nreturn a",
    "writer_tools": 'a = writer(tools=["run_sql", "find_values"])\nreturn a',
    "write_check": 'a = writer(tools=["run_sql", "find_values"])\nc = checker(a, tools=["run_sql"])\nreturn c',
}


def _db(db_id):
    return os.path.join(DATA, "dev_databases", db_id, f"{db_id}.sqlite")


_schema = {}


def schema(db_id):
    if db_id not in _schema:
        con = sqlite3.connect(f"file:{_db(db_id)}?mode=ro", uri=True)
        rows = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND sql IS NOT NULL").fetchall()
        con.close()
        _schema[db_id] = "\n\n".join(r[0].strip() for r in rows if "sqlite_sequence" not in r[0])
    return _schema[db_id]


def load(split, n=None):
    rows = json.load(open(os.path.join(DATA, "dev.json")))
    random.Random(0).shuffle(rows)
    a, b = SPLITS["dev_a"], SPLITS["dev_b"]
    lo, hi = {"dev_a": (0, a), "dev_b": (a, a + b), "test": (a + b, a + b + SPLITS["test"])}[split]
    out = [{"id": f"bird/{r['question_id']}", "db": r["db_id"], "question": r["question"],
            "evidence": r["evidence"], "gold": r["SQL"], "bucket": r["difficulty"],
            "hard": r["difficulty"] != "simple"} for r in rows[lo:hi]]
    return out[:n] if n else out


def _prelude(db_id):
    return (f"DB = {_db(db_id)!r}\nDESC = "
            f"{os.path.join(DATA, 'dev_databases', db_id, 'database_description')!r}\n")


def tool_prelude():
    """Prepended to a tool's code and test when the evolver adds or edits a tool: the database of the
    first dev-A question (DB, DESC)."""
    return _prelude(load("dev_a", 1)[0]["db"])


def meta_view(item):
    con = sqlite3.connect(f"file:{_db(item['db'])}?mode=ro", uri=True)
    tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'") if t != "sqlite_sequence"]
    con.close()
    return (f"Database: {item['db']} (tables: {', '.join(tables)})\nQuestion: {item['question']}\n"
            f"Evidence: {item['evidence'] or '-'}")


def _execute(db_id, sql, timeout=30.0):
    """Rows of a query (as a set), or None on error / timeout."""
    con = sqlite3.connect(f"file:{_db(db_id)}?mode=ro", uri=True)
    deadline = time.time() + timeout
    con.set_progress_handler(lambda: 1 if time.time() > deadline else 0, 10000)
    try:
        return set(con.execute(sql).fetchall())
    except Exception:
        return None
    finally:
        con.close()


_gold, _lock = {}, threading.Lock()


def grade(pred, item):
    if not pred:
        return False
    with _lock:
        if item["id"] not in _gold:
            _gold[item["id"]] = None
    if _gold[item["id"]] is None:
        _gold[item["id"]] = _execute(item["db"], item["gold"])
    got = _execute(item["db"], pred)
    return got is not None and got == _gold[item["id"]]


def extract(text):
    m = re.findall(r"```sql\s*\n(.*?)```", text, re.S | re.I)
    if m:
        return m[-1].strip()
    m = re.findall(r"(SELECT\b.*?)(?:;|\Z)", text, re.S | re.I)
    return m[-1].strip() if m else None


def run_node(eng, pool, node, item, work, is_output):
    user = (f"Database: {item['db']}\nSchema:\n{schema(item['db'])}\n\nQuestion: {item['question']}\n"
            f"Evidence: {item['evidence'] or '-'}")
    if work:
        user += f"\n\nWork from your teammates:\n{work}\n\nGive your own final query."
    user += f"\n\n{ANSWER_FMT}"
    S, T = pool.get("skills", SKILLS), pool.get("tools", TOOLS)
    system = pool["agents"][node["agent"]]["role"]
    if node["skills"]:
        system += "\n\nSkills to apply:\n" + "\n".join(f"- {k}: {S[k]['text']}" for k in node["skills"])
    if node["tools"]:
        system += (f"\n\nYou can run Python on this database up to {MAX_RUNS} times: write one ```python``` "
                   "code block that calls these functions and prints what you need, then stop and wait "
                   "for its output:\n" + "\n".join(f"- {T[t]['doc']}" for t in node["tools"]))
    msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    pre = _prelude(item["db"]) + "\n".join(T[t].get("code", "") for t in node["tools"])
    calls, shown = [], []
    for k in range(MAX_RUNS + 1):
        r = eng.chat(msgs, MAX_TOKENS)
        calls.append({"agent": node["agent"], "node": node["id"], "prompt_tokens": r.prompt_tokens,
                      "gen_tokens": r.gen_tokens})
        shown.append(r.text)
        code = CODE.findall(r.text)
        final = re.search(r"```sql", r.text.split("```python")[-1], re.I)
        if not node["tools"] or not code or final or k == MAX_RUNS:
            break
        out, _ = run_python(pre + "\n" + code[-1], timeout=30)
        shown.append(f"[Python output]\n{out}")
        more = (f"You may run code again ({MAX_RUNS - k - 1} runs left) or give the final query."
                if k + 1 < MAX_RUNS else "No more runs. Give the final query now.")
        msgs += [{"role": "assistant", "content": r.text},
                 {"role": "user", "content": f"Output:\n{out}\n\n{more} {ANSWER_FMT}"}]
    return {"text": "\n\n".join(shown), "answer": extract(r.text), "calls": calls,
            "cut": any(c["gen_tokens"] >= MAX_TOKENS for c in calls)}
