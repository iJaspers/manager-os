"""Durable, append-safe opportunity record store. Offline, stdlib only."""
import json
import os
import sqlite3
from pathlib import Path
from opportunity import evaluate

SCHEMA = """
CREATE TABLE IF NOT EXISTS opportunities (
 id TEXT PRIMARY KEY, url TEXT NOT NULL, payload TEXT NOT NULL,
 first_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 last_seen TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS events (
 seq INTEGER PRIMARY KEY AUTOINCREMENT, opportunity_id TEXT NOT NULL,
 kind TEXT NOT NULL, detail TEXT NOT NULL,
 at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), timeout=10)
        self.db.execute("PRAGMA busy_timeout=10000")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(SCHEMA)

    def close(self):
        self.db.close()

    def ingest(self, items):
        if not isinstance(items, list):
            raise ValueError("Expected list")
        output = []
        for item in items:
            record = evaluate(item, set())
            with self.db:
                row = self.db.execute("SELECT payload FROM opportunities WHERE id=?", (record["id"],)).fetchone()
                if row:
                    prior = json.loads(row[0])
                    # Repeated observations never erase feedback, review state or history.
                    self.db.execute("UPDATE opportunities SET last_seen=CURRENT_TIMESTAMP WHERE id=?", (record["id"],))
                    output.append(dict(prior, duplicate_observation=True))
                else:
                    self.db.execute("INSERT INTO opportunities(id,url,payload) VALUES (?,?,?)",
                                    (record["id"],record["url"],json.dumps(record,sort_keys=True)))
                    self.db.execute("INSERT INTO events(opportunity_id,kind,detail) VALUES (?,?,?)",
                                    (record["id"],"INGEST",json.dumps({"gate":record["gate"]})))
                    output.append(record)
        return output

    def feedback(self, ident, verdict, note=""):
        if verdict not in ("GOOD","BAD","UNSURE"):
            raise ValueError("Invalid feedback")
        with self.db:
            row = self.db.execute("SELECT payload FROM opportunities WHERE id=?", (ident,)).fetchone()
            if not row:
                raise KeyError(ident)
            record = json.loads(row[0])
            record["feedback"] = {"verdict":verdict,"reason":str(note)[:1000]}
            self.db.execute("UPDATE opportunities SET payload=?,last_seen=CURRENT_TIMESTAMP WHERE id=?",
                            (json.dumps(record,sort_keys=True),ident))
            self.db.execute("INSERT INTO events(opportunity_id,kind,detail) VALUES (?,?,?)",
                            (ident,"FEEDBACK",json.dumps(record["feedback"])))

    def list_records(self):
        return [json.loads(row[0]) for row in self.db.execute("SELECT payload FROM opportunities ORDER BY first_seen,id")]

    def event_count(self):
        return self.db.execute("SELECT count(*) FROM events").fetchone()[0]
