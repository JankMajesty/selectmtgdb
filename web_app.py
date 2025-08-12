# web_app.py
import os
import sqlite3
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mtg_database.db")

MAX_ROWS = 1000

def get_ro_connection():
    # Connect read-only using SQLite URI
    uri = f"file:{DB_PATH}?mode=ro"
    return sqlite3.connect(uri, uri=True, check_same_thread=False)

DISALLOWED_TOKENS = {
    "ATTACH", "DETACH", "PRAGMA", "ALTER", "INSERT", "UPDATE", "DELETE",
    "DROP", "CREATE", "REPLACE", "VACUUM", "ANALYZE", "TRIGGER", "INDEX",
    "BEGIN", "COMMIT", "ROLLBACK"
}

def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "Query is empty."
    q = sql.strip().strip(";")
    upper = q.lstrip().upper()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False, "Only SELECT or WITH queries are allowed."
    # Very basic single-statement check
    if ";" in q:
        return False, "Multiple statements are not allowed."
    for bad in DISALLOWED_TOKENS:
        if f" {bad} " in f" {upper} ":
            return False, f"Disallowed token detected: {bad}"
    return True, q

def run_query(q: str):
    con = get_ro_connection()
    cur = con.cursor()
    try:
        cur.execute(q)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        truncated = False
        if len(rows) > MAX_ROWS:
            rows = rows[:MAX_ROWS]
            truncated = True
        return {"columns": cols, "rows": rows, "truncated": truncated, "error": None}
    except Exception as e:
        return {"columns": [], "rows": [], "truncated": False, "error": str(e)}
    finally:
        con.close()

def get_schema():
    con = get_ro_connection()
    cur = con.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [r[0] for r in cur.fetchall()]
        schema = {}
        for t in tables:
            try:
                cur.execute(f"PRAGMA table_info('{t}')")
                cols = cur.fetchall()
                schema[t] = [{"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "dflt_value": c[4], "pk": c[5]} for c in cols]
            except Exception:
                schema[t] = []
        return schema
    finally:
        con.close()

SAMPLE_QUERIES = [
    {
        "name": "First 50 cards",
        "sql": "SELECT CardID, CardName, ManaCost, ConvertedManaCost FROM Card ORDER BY CardID LIMIT 50"
    },
    {
        "name": "Cards with set code and rarity",
        "sql": """SELECT c.CardName, s.SetCode, r.RarityName
FROM Card c
JOIN CardSet s ON c.SetID = s.SetID
JOIN Rarity r ON c.RarityID = r.RarityID
ORDER BY c.CardName
LIMIT 50"""
    },
    {
        "name": "Blue creature cards",
        "sql": """SELECT DISTINCT c.CardName
FROM Card c
JOIN Card_CardType cct ON c.CardID = cct.CardID
JOIN CardType ct ON cct.CardTypeID = ct.CardTypeID
JOIN Card_Color cc ON c.CardID = cc.CardID
JOIN Color col ON cc.ColorID = col.ColorID
WHERE ct.TypeName = 'Creature' AND col.Color = 'U'
ORDER BY c.CardName
LIMIT 50"""
    },
    {
        "name": "Legendary cards by set",
        "sql": """SELECT s.SetCode, COUNT(*) AS legendary_count
FROM Card c
JOIN CardSet s ON c.SetID = s.SetID
WHERE c.SuperType = 'Legendary'
GROUP BY s.SetCode
ORDER BY legendary_count DESC"""
    },
]

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        schema=get_schema(),
        sample_queries=SAMPLE_QUERIES,
        query_text="",
        result=None
    )

@app.route("/query", methods=["POST"])
def query():
    sql = request.form.get("sql", "")
    ok, cleaned = validate_sql(sql)
    if not ok:
        return render_template(
            "index.html",
            schema=get_schema(),
            sample_queries=SAMPLE_QUERIES,
            query_text=sql,
            result={"error": cleaned, "columns": [], "rows": [], "truncated": False}
        )
    result = run_query(cleaned)
    return render_template(
        "index.html",
        schema=get_schema(),
        sample_queries=SAMPLE_QUERIES,
        query_text=cleaned,
        result=result
    )

@app.route("/schema.json", methods=["GET"])
def schema_json():
    return jsonify(get_schema())

@app.route("/query.json", methods=["POST"])
def query_json():
    data = request.get_json(silent=True) or {}
    sql = data.get("sql", "")
    ok, cleaned = validate_sql(sql)
    if not ok:
        return jsonify({"error": cleaned, "columns": [], "rows": [], "truncated": False}), 400
    return jsonify(run_query(cleaned))

if __name__ == "__main__":
    # Run: python web_app.py
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
