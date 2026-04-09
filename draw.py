import sqlite3
from datetime import datetime

import matplotlib.pyplot as plt

conn = sqlite3.connect("logs.db")
cur = conn.cursor()
cur.execute("""
WITH related AS (
    SELECT dpid AS pid, d_id AS id FROM relations WHERE opid = 101
    UNION
    SELECT pid, id FROM events WHERE pid = 101
)
SELECT e.time, e.pid, e.id, e.event,
    GROUP_CONCAT(a.key || '=' || a.value) AS attrs
FROM events e
JOIN related r ON e.pid = r.pid AND e.id = r.id
LEFT JOIN attributes a ON a.pid = e.pid AND a.id = e.id AND a.event = e.event
GROUP BY e.time, e.pid, e.id, e.event
ORDER BY e.pid, e.id, e.time
""")
rows = cur.fetchall()
conn.close()

# Group by (pid, id)
groups = {}
for time, pid, id_, event, attrs in rows:
    attrs_dict = dict(pair.split("=") for pair in attrs.split(",")) if attrs else {}
    groups.setdefault((pid, id_), []).append((time, event, attrs_dict))

plt.figure(figsize=(14, 3))

all_events = {e for _, events in groups.items() for _, e, _ in events}
event_colors = {e: plt.cm.tab20(i % 20) for i, e in enumerate(sorted(all_events))}

for i, ((pid, id_), events) in enumerate(groups.items()):
    times = [datetime.fromisoformat(t) for t, _, _ in events]
    evnames = [e for _, e, _ in events]

    color = [event_colors[e] for e in evnames]

    y = [-i] * len(times)
    # Draw segments between consecutive points, colored by the starting event
    for j in range(len(times) - 1):
        plt.plot(
            [times[j], times[j + 1]],
            [y[j], y[j + 1]],
            color=event_colors[evnames[j]],
            linewidth=2,
        )
    plt.scatter(times, y, marker="|", c=[event_colors[e] for e in evnames], zorder=3)

    for t, ev in zip(times, evnames):
        plt.text(
            t,
            -i,
            ev,
            rotation=90,
            ha="center",
            va="bottom",
            fontsize=8,
        )


plt.yticks(
    [-i for i in range(len(groups))],
    [
        "pid={} id={} {}".format(
            pid, id_,
            " ".join(f"{k}={v}" for k, v in {k: v for _, _, a in events for k, v in a.items()}.items())
        )
        for (pid, id_), events in groups.items()
    ],
)
plt.xlabel("Time")
plt.title("Event Timeline")
plt.grid(axis="both", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
