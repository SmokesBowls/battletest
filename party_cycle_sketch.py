#!/usr/bin/env python3
"""
party_cycle_sketch.py - Party Cycle Tracking (SKETCH, not canon)

Wraps chain_mr_sketch.step_chain with an explicit full-party cycle counter.
Chains live on targets, so they persist across cycles untouched; the cycle only
records who has acted. Damage never reads the cycle.

AUTHOR-APPROVED (canon):
  A1. Chains may span multiple full-party cycles (no fixed hit limit).

PROVISIONAL:
  P1. A cycle completes when every party member has taken one turn; then it advances.
  P2. A member acting twice in one cycle, or a non-member acting, is rejected.
  P3. A turn with no hits (heal, utility) still counts as that member's turn.
  P4. Ongoing damage doesn't tick on cycle advance yet.
"""

from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, List, Mapping, Tuple

from chain_mr_sketch import Target, step_chain


@dataclass(frozen=True)
class PartyCycle:
    party: Tuple[str, ...]
    number: int = 1
    acted: FrozenSet[str] = frozenset()


def record_turn(cycle: PartyCycle, actor: str) -> PartyCycle:
    if actor not in cycle.party:
        raise ValueError(f"{actor} is not in the party")
    if actor in cycle.acted:
        raise ValueError(f"{actor} already acted in cycle {cycle.number}")
    acted = cycle.acted | {actor}
    if acted >= set(cycle.party):
        return replace(cycle, number=cycle.number + 1, acted=frozenset())
    return replace(cycle, acted=acted)


def step_turn(
    targets: Mapping[str, Target],
    cycle: PartyCycle,
    actor: str,
    hits: List[Dict],
    seed: int = 0,
) -> Tuple[Dict[str, Target], PartyCycle, List[str], List[str]]:
    """One party member's turn. Returns (targets_out, cycle_out, accepted_hit_ids, alerts)."""
    next_cycle = record_turn(cycle, actor)  # validate before resolving any damage
    out, accepted, alerts = step_chain(targets, hits, seed)
    return out, next_cycle, accepted, alerts
