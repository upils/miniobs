import re
import sqlite3
from datetime import datetime

relation_re = re.compile(r"opid:\s*(\d+)\s+dpid:\s*(\d+)\s+id:\s*(\d+)\s+id:\s*(\d+)")

attribute_re = re.compile(
    r"(\d{4}-\d{2}-\d{2}T[0-9:.]+)\s+rpc-attr\s+pid:\s*(\d+)\s+sm_id:\s*(\d+)\s+([A-Za-z0-9_-]+)\s+key:\s*([A-Za-z0-9_-]+)\s+value:\s*(\d+)"
)

event_re = re.compile(
    r"(\d{4}-\d{2}-\d{2}T[0-9:.]+)\s+\w+\s+pid:\s*(\d+)\s+sm_id:\s*(\d+)\s+([A-Za-z0-9_-]+)"
)


def parse_log(logfile, dbfile="logs.db"):
    # Setup SQLite
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS relations (
            opid INTEGER,
            dpid INTEGER,
            o_id INTEGER,
            d_id INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            time TEXT,
            pid INTEGER,
            id INTEGER,
            event TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attributes (
            time TEXT,
            pid INTEGER,
            id INTEGER,
            event TEXT,
            key TEXT,
            value TEXT
        )
    """)

    with open(logfile, "r") as f:
        for line in f:
            if "-to-" in line:
                m = relation_re.search(line)
                if m:
                    cur.execute(
                        "INSERT INTO relations (opid, dpid, o_id, d_id) VALUES (?, ?, ?, ?)",
                        tuple(map(int, m.groups())),
                    )
            elif "rpc-attr" in line:
                m = attribute_re.search(line)
                if m:
                    t, pid, sm_id, event, key, value = m.groups()
                    cur.execute(
                        "INSERT INTO attributes (time, pid, id, event, key, value) VALUES (?, ?, ?, ?, ?, ?)",
                        (t, int(pid), int(sm_id), event, key, value),
                    )
            else:
                m = event_re.search(line)
                if m:
                    t, pid, sm_id, event = m.groups()
                    cur.execute(
                        "INSERT INTO events (time, pid, id, event) VALUES (?, ?, ?, ?)",
                        (t, int(pid), int(sm_id), event),
                    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    parse_log("trace.txt")
    print("Parsing complete. Data written to logs.db")
