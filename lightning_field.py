#!/usr/bin/env python3
"""
lightning_field.py - one Lightning strike across a Godot-supplied battlefield.

Godot owns positions: godot_demo/battlefield.json, written by
    godot --headless --path godot_demo -- --export-field
Python owns everything elemental: who carries what, the jump walk, Plasma, stops, damage.
Writes godot_demo/field.json for playback: godot --path godot_demo -- --field

PROVISIONAL (not authored):
  P1. JUMP_RANGE and BOLT damage are placeholders.
  P2. Each jump rolls left/right (seeded): nearest unhit enemy in range on that side,
      else nearest on the other side. The bolt ends when nobody unhit is in range.
  P3. No obstruction: the field has no terrain or collision yet.
  P4. Which enemies carry Fire/Earth/Shadow or Clay/Ash is a seeded placeholder assignment.
"""

import argparse
import json
import math
import random

from chain_mr_sketch import Chain, Target, step_chain
from encounter_demo import chain_json
from propagation_mr_sketch import propagate

JUMP_RANGE = 3.5  # shortcut: placeholder, Lightning's authored reach is OPEN
BOLT = 30.0       # shortcut: placeholder, the authored random damage range is OPEN
CARRIED = {"fire": 5, "earth": 2, "shadow": 1}
CONDITIONS = {"clay": 1, "ash": 1}


def walk(positions, start, seed, jump_range=JUMP_RANGE):
    """Full jump order from `start`, ignoring stops (propagate cuts the path at a stopper)."""
    rng = random.Random(f"{seed}:walk")
    path = [start]
    while True:
        here = positions[path[-1]]
        near = sorted((math.dist(here, p), tid, p[0] < here[0]) for tid, p in positions.items()
                      if tid not in path and math.dist(here, p) <= jump_range)
        if not near:
            return path
        left = rng.random() < 0.5
        path.append(([n for n in near if n[2] == left] or near)[0][1])


def populate(positions, seed):
    """Seeded placeholder cast. Returns (targets, primary target id)."""
    ids = sorted(positions)
    needed = sum(CARRIED.values()) + sum(CONDITIONS.values()) + 1
    if len(ids) < needed:
        raise ValueError(f"field needs at least {needed} enemies, got {len(ids)}")
    random.Random(f"{seed}:cast").shuffle(ids)
    targets, i = {}, 0
    for el, n in CARRIED.items():
        for tid in ids[i:i + n]:
            targets[tid] = Target(200.0, {}, Chain((el,)))
        i += n
    for cond, n in CONDITIONS.items():
        for tid in ids[i:i + n]:
            targets[tid] = Target(200.0, {}, conditions=frozenset({cond}))
        i += n
    for tid in ids[i:]:
        targets[tid] = Target(200.0, {})
    return targets, ids[i]  # strike lands on a plain enemy


def strike(positions, seed=0):
    before, start = populate(positions, seed)
    path = walk(positions, start, seed)
    hits, alerts = propagate("bolt", before, path, [BOLT] * len(path))
    after, _, chain_alerts = step_chain(before, hits, seed)
    return before, after, path, hits, alerts + chain_alerts


def field_json(positions, seed=0):
    before, after, path, hits, alerts = strike(positions, seed)
    return {
        "targets": {tid: {"hp": t.hp, "chain": chain_json(t.chain), "conditions": sorted(t.conditions),
                          "pos": list(positions[tid])} for tid, t in before.items()},
        "walk": path,
        "turns": [{"cycle": 1, "actor": "p1", "turn": "bolt", "alerts": alerts,
                   "hits": [{"target": h["target"], "form": next(iter(h["damage"])), "primary": h["primary"],
                             "damage": round(before[h["target"]].hp - after[h["target"]].hp, 2)} for h in hits],
                   "chains": {h["target"]: chain_json(after[h["target"]].chain) for h in hits}}],
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--positions", default="godot_demo/battlefield.json")
    ap.add_argument("--out", default="godot_demo/field.json")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    with open(args.positions) as f:
        raw = json.load(f)["enemies"]
    positions = {tid: (float(p[0]), float(p[1])) for tid, p in raw.items()}
    data = field_json(positions, args.seed)
    with open(args.out, "w") as f:
        json.dump(data, f, indent=1)
    turn = data["turns"][0]
    print(f"{len(positions)} enemies, seed {args.seed}, full walk {len(data['walk'])} -> {len(turn['hits'])} hits")
    for h in turn["hits"]:
        t = data["targets"][h["target"]]
        carried = (t["chain"]["elements"] or t["conditions"] or ["-"])[0]
        print(f"  {h['target']} carries {carried:7} <- {h['form']:9} {h['damage']:6.2f}")
    for a in turn["alerts"]:
        print("  !", a)
    print("WROTE", args.out)


if __name__ == "__main__":
    main()
