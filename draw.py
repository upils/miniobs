import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

conn = sqlite3.connect("logs.db")
cur = conn.cursor()
qrows = ["SELECT time, event FROM events WHERE pid=101 AND id=1 ORDER BY time",
         "SELECT time, event FROM events WHERE pid=101 AND id=2 ORDER BY time",
         "SELECT time, event FROM events WHERE pid=101 AND id=3 ORDER BY time",
         "SELECT time, event FROM events WHERE pid=101 AND id=4 ORDER BY time"]

plt.figure(figsize=(14, 3))
for i, q in enumerate(qrows):
    cur.execute(q)
    rows = cur.fetchall()
    times = [datetime.fromisoformat(t) for t, _ in rows]
    events = [e for _, e in rows]

    y = [-i] * len(times)
    plt.plot(times, y, color="lightgray", linewidth=1)
    plt.scatter(times, y, marker="|", color="steelblue")

    for t, ev in zip(times, events):
        plt.text(t, -i, ev, rotation=90, ha="center", va="bottom", fontsize=8)

conn.close()
plt.yticks([])
plt.xlabel("Time")
plt.title("Event Timeline")
plt.grid(axis="x", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
