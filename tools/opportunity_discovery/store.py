"""Durable, append-safe opportunity record store. Offline, stdlib only."""
import hashlib
import json
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
            # Bind source text and evaluated controls without storing another raw copy.
            # Age in fractional days changes on every read. Its policy effect is in "stale".
            observation = {
                "evaluation": record,
                "source": {key: item.get(key) for key in
                           ("source_text", "source_created_at", "source_author")},
            }
            encoded = json.dumps(observation, sort_keys=True, separators=(",", ":")).encode()
            fingerprint = hashlib.sha256(encoded).hexdigest()
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                row = self.db.execute(
                    "SELECT payload FROM opportunities WHERE id=?", (record["id"],)
                ).fetchone()
                prior = json.loads(row[0]) if row else None
                if prior is not None and prior.get("observation_sha256") == fingerprint:
                    self.db.execute(
                        "UPDATE opportunities SET last_seen=CURRENT_TIMESTAMP WHERE id=?",
                        (record["id"],),
                    )
                    output.append(dict(prior, duplicate_observation=True))
                    continue

                record["observation_sha256"] = fingerprint
                if prior is None:
                    kind = "INGEST"
                    self.db.execute(
                        "INSERT INTO opportunities(id,url,payload) VALUES (?,?,?)",
                        (record["id"], record["url"], json.dumps(record, sort_keys=True)),
                    )
                else:
                    # A changed or previously unbound observation needs a new review.
                    # Keep earlier feedback only in the historical event it describes.
                    kind = "OBSERVATION_CHANGED"
                    record["gate"] = "NEEDS_REVIEW"
                    record["decision"] = "BLOCKED"
                    record["gate_reasons"].append("changed observation requires review")
                    self.db.execute(
                        "UPDATE opportunities SET payload=?,last_seen=CURRENT_TIMESTAMP WHERE id=?",
                        (json.dumps(record, sort_keys=True), record["id"]),
                    )
                detail = {"current": record, "prior": prior, "gate": record["gate"]}
                self.db.execute(
                    "INSERT INTO events(opportunity_id,kind,detail) VALUES (?,?,?)",
                    (record["id"], kind, json.dumps(detail, sort_keys=True)),
                )
                output.append(record)
        return output

    def feedback(self, ident, verdict, note=""):
        if verdict not in ("GOOD","BAD","UNSURE"):
            raise ValueError("Invalid feedback")
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
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
