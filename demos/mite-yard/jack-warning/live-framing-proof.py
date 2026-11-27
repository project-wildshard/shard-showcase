"""Cross-check locally generated native probe receipts. Never store screenshots here."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
for name in ("none", "look", "sprint"):
    parser.add_argument(name, type=Path, help=f"native probe result directory for {name}")
args = parser.parse_args()
get = lambda p: json.loads((p / "live-framing.json").read_text())
normal, look, sprint = map(get, (args.none, args.look, args.sprint))
assert [r["control"] for r in (normal, look, sprint)] == ["none", "look", "sprint"]

def clipped(row):
    return [sum(a["outside"] + a["behind"] for a in r["actors"].values()) for r in row["results"]]

contact = normal["contact"]
assert contact and contact["hp"][1] < 132 and contact["hp"][0] == 204
assert clipped(contact)[0] > 0 and clipped(contact)[1] == 0
stock_bad = sum(clipped(s)[0] > 0 for s in normal["samples"])
live_bad = sum(clipped(s)[1] > 0 for s in normal["samples"])
assert (stock_bad, live_bad) == (5, 0)
assert any(s["since"] < contact["since"] and s["turn"] > 0 for s in normal["lens"])
for before, after in zip(normal["lens"], normal["lens"][1:]):
    assert abs(after["turn"] - before["turn"]) <= 105 * after["dt"] + 1e-8
    assert abs(after["widen"] - before["widen"]) <= 80 * after["dt"] + 1e-8
look_rows = [s for s in look["lens"] if s["testLook"]]
sprint_rows = [s for s in sprint["lens"] if s["sprintIntent"]]
for rows in (look_rows, sprint_rows):
    assert rows and all(s["override"] and not s["turn"] and not s["widen"] for s in rows)
assert all(s["lookX"] > 0 for s in look_rows)
print(f"Clipped samples, stock/live: {stock_bad}/{live_bad}. Contact out-of-frame counts: {clipped(contact)}.")
print(f"Look override frames: {len(look_rows)}; sprint-intent override frames: {len(sprint_rows)}.")
