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
def delta(after, before):
    return (after - before + 180) % 360 - 180

look_rows = [(a,b) for a,b in zip(look["lens"], look["lens"][1:]) if b["testLook"]]
sprint_rows = [(a,b) for a,b in zip(sprint["lens"], sprint["lens"][1:]) if b["sprintIntent"]]
assert len(look_rows) == 6 and len(sprint_rows) == 15
directions = []
for a,b in look_rows:
    requested = b["lookX"] * 180 / 3.141592653589793
    shown = delta(b["shown"], a["shown"])
    directions.append(requested > 0)
    assert abs(b["turn"] - a["turn"]) <= .25 * abs(requested) + 1e-8
    assert shown * requested > 0
    assert abs(shown) >= .65 * abs(requested)
    print(f"look {b['since']:2d}: request {requested:+.2f}°, screen {shown:+.2f}°, immediate clear {b['immediateClearDelta']:+.2f}°")
assert set(directions) == {True, False}
for a,b in look_rows+sprint_rows:
    assert b["override"]
    assert abs(b["turn"]) <= abs(a["turn"]) + 1e-8
    assert abs(b["turn"]-a["turn"]) <= 48 * b["dt"] + 1e-8
    assert 0 <= a["widen"] - b["widen"] <= 36 * b["dt"] + 1e-8
assert not sprint_rows[-1][1]["turn"] and not sprint_rows[-1][1]["widen"]
print(f"Clipped samples, stock/live: {stock_bad}/{live_bad}. Contact out-of-frame counts: {clipped(contact)}.")
print(f"Look handoff frames: {len(look_rows)}; sprint-intent handoff frames: {len(sprint_rows)}.")
