#!/usr/bin/env python3
"""
encounter_demo.py - one simulated encounter through the existing sketches.

Party of three vs a boss and five minions, two full party cycles.
Damage and ongoing numbers are placeholders, not authored values.
`--json PATH` writes the log for the Godot playback in godot_demo/ (display only).
"""

import argparse
import json

from party_cycle_sketch import PartyCycle, step_turn
from propagation_mr_sketch import propagate
from chain_mr_sketch import Chain, Target

BOLT = 30.0  # shortcut: fixed per-jump Lightning damage; the authored random range is still OPEN


def start():
    def foe(hp, carried=None):
        return Target(hp, {}, Chain((carried,)) if carried else Chain())
    return {"boss": Target(2000.0, {"fire": 0.2}), "e1": foe(200), "e3": foe(200, "fire"),
            "e4": foe(200), "e5": foe(200), "mud": foe(200, "earth"), "dark": foe(200, "shadow")}


def spell(i, target, element, amount, ongoing=0.0):
    return [{"id": i, "target": target, "primary": True, "damage": {element: amount}, "ongoing": ongoing}]


def bolt(i, targets, path):
    return propagate(i, targets, path, [BOLT] * len(path))


# (actor, hit id, builder(targets) -> (hits, propagation alerts))
TURNS = [
    ("p1", "c1_water", lambda t: (spell("c1_water", "boss", "water", 100, ongoing=40), [])),
    ("p2", "c1_fire", lambda t: (spell("c1_fire", "boss", "fire", 100, ongoing=50), [])),   # Boil
    ("p3", "c1_bolt", lambda t: bolt("c1_bolt", t, ["e1", "e3", "e4"])),                   # Plasma at e3
    ("p1", "c2_water", lambda t: (spell("c2_water", "boss", "water", 100, ongoing=40), [])), # Steam
    ("p2", "c2_bolt", lambda t: bolt("c2_bolt", t, ["boss", "mud", "e5"])),                # unnamed; Grounding
    ("p3", "c2_bolt2", lambda t: bolt("c2_bolt2", t, ["boss", "dark", "e5"])),             # repeat; Absorption
]


def run_encounter(seed=0):
    targets, cycle, log = start(), PartyCycle(("p1", "p2", "p3")), []
    for actor, tid, build in TURNS:
        hits, prop_alerts = build(targets)
        before, turn_cycle = targets, cycle.number
        targets, cycle, _, alerts = step_turn(targets, cycle, actor, hits, seed)
        log.append({
            "cycle": turn_cycle, "actor": actor, "turn": tid,
            "hits": [(h["target"], next(iter(h["damage"])), h["primary"],
                      round(before[h["target"]].hp - targets[h["target"]].hp, 2)) for h in hits],
            "chains": {h["target"]: targets[h["target"]].chain for h in hits},
            "alerts": prop_alerts + alerts,
        })
    return targets, cycle, log


def chain_json(c):
    return {"elements": list(c.elements), "state": c.state, "closed": c.closed, "ongoing": c.ongoing}


def encounter_json(seed=0):
    _, _, log = run_encounter(seed)
    return {
        "targets": {tid: {"hp": t.hp, "chain": chain_json(t.chain)} for tid, t in start().items()},
        "turns": [{"cycle": e["cycle"], "actor": e["actor"], "turn": e["turn"], "alerts": e["alerts"],
                   "hits": [{"target": t, "form": f, "primary": p, "damage": d} for t, f, p, d in e["hits"]],
                   "chains": {tid: chain_json(c) for tid, c in e["chains"].items()}} for e in log],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--json", metavar="PATH", help="write the encounter log as JSON instead of printing")
    args = ap.parse_args()
    if args.json:
        with open(args.json, "w") as f:
            json.dump(encounter_json(), f, indent=1)
        print("WROTE", args.json)
        return
    targets, cycle, log = run_encounter()
    for e in log:
        print(f"\n[cycle {e['cycle']}] {e['actor']} {e['turn']}")
        for tgt, form, primary, dmg in e["hits"]:
            c = e["chains"][tgt]
            print(f"  {tgt:5} {form:9} {'primary' if primary else 'jump   '} dmg {dmg:7.2f}"
                  f"  chain {'>'.join(c.elements)} state={c.state} closed={c.closed} ongoing={c.ongoing:g}")
        for a in e["alerts"]:
            print(f"  ! {a}")
    print(f"\nend: cycle {cycle.number}")
    for tid, t in targets.items():
        print(f"  {tid:5} hp {t.hp:8.2f}  chain {'>'.join(t.chain.elements)} state={t.chain.state} closed={t.chain.closed}")


if __name__ == "__main__":
    main()
