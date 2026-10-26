#!/usr/bin/env python3
"""
propagation_mr_sketch.py - Lightning Propagation (SKETCH, not canon)

Separate from elemental chaining: it only decides who a bolt reaches and with what
element, and emits hits for chain_mr_sketch.step_chain. It never touches a chain itself.

AUTHOR-APPROVED (canon):
  A1. Jumps are secondary hits: they deal damage and never advance a chain.
  A2. Lightning reaching an enemy carrying Fire becomes Plasma and continues as Plasma.
  A3. Grounding (Earth) and Shadow absorption stop the bolt: the stopping enemy
      still receives the infliction, nobody after it does.
  A4. Clay and Ash are symbolic forms, not elements: Clay inherits Earth's Grounding,
      Ash inherits Shadow's Lightning stop. They inherit only that behavior (STOP_INHERITED),
      never every Earth or Shadow interaction.

PROVISIONAL:
  P1. An enemy's carried element = the last element of its chain, if any.
  P2. Clay/Ash are read from Target.conditions; what creates them is not modeled yet.
  P3. Plasma damage is keyed "plasma"; whether it can enter a chain is OPEN (handoff Q4/Q5).
  P4. The per-jump random damage and left/right choice come from the caller as `path` and `amounts`.
"""

from typing import Dict, List, Mapping, Optional, Sequence, Tuple

from chain_mr_sketch import Target

STOPS: Mapping[str, str] = {"earth": "Grounding", "shadow": "Absorption"}
# Symbolic form -> element whose Lightning stop it inherits (that behavior only).
STOP_INHERITED: Mapping[str, str] = {"clay": "earth", "ash": "shadow"}


def stop_family(t: Target) -> Optional[str]:
    """Element family whose stop applies to this enemy, or None."""
    carried = t.chain.elements[-1:] if t.chain.elements else ()
    for marker in (*carried, *sorted(t.conditions)):
        family = marker if marker in STOPS else STOP_INHERITED.get(marker)
        if family:
            return family
    return None


def propagate(
    bolt_id: str,
    targets: Mapping[str, Target],
    path: Sequence[str],
    amounts: Sequence[float],
) -> Tuple[List[Dict], List[str]]:
    """path[0] is the primary target. Returns (hits for step_chain, alerts). Pure."""
    hits: List[Dict] = []
    alerts: List[str] = []
    element = "lightning"
    for i, (tid, amount) in enumerate(zip(path, amounts)):
        t = targets.get(tid)
        if t is None:
            alerts.append(f"{bolt_id}: unknown target {tid}, bolt stops")
            break
        carried = t.chain.elements[-1] if t.chain.elements else None
        if carried == "fire" and element == "lightning":
            element = "plasma"
            alerts.append(f"{bolt_id}: becomes Plasma at {tid}")
        # The primary hit always lands as the base element: on a Fire carrier the chain's own
        # Fire -> Lightning cell yields Plasma. Plasma is a derived form, never a chain element.
        delivered = "lightning" if i == 0 else element
        hits.append({"id": f"{bolt_id}:{i}", "target": tid, "primary": i == 0, "damage": {delivered: amount}})
        family = stop_family(t)
        if family:
            alerts.append(f"{bolt_id}: {STOPS[family]} at {tid}, bolt stops")
            break
    return hits, alerts
