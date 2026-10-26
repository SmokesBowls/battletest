#!/usr/bin/env python3
"""
chain_mr_sketch.py - Elemental Chain Kernel (SKETCH, not canon)

Pure functional kernel: snapshot-in -> snapshot-out.
Resolves elemental reaction chains per target using only the author-confirmed
cells from elemental_reaction_matrix_v0.1.md. Every other cell is "no reaction yet".

AUTHOR-APPROVED (canon):
  A1. Only primary hits advance a chain; secondary hits (jumps, splash) deal damage only.
  A2. Dual-element hits: each element deals its own damage; only the dominant
      element (most damage after resistance) enters the chain.
  A3. Reactions are order-dependent pairs, REACTIONS[(first, second)]; Char is terminal.
  A4. Repeating the previous element ends the chain; that hit deals normal damage only.
  A5. No fixed hit limit: chains may span party cycles. MAX_CHAIN_HITS exists, disabled (None).
  A6. Unauthored pairs still replace: the hit counts, no reaction is named.
  A7. Chain bonus: 2nd hit +2-4%, 3rd +3-5% of the spell's standard damage, rolled.
  A8. Replacement: the outgoing element's remaining ongoing damage lands once as a final
      infliction, Water +1%, Fire +2%; then the incoming element's ongoing replaces it.
  A9. Starting a chain needs strength >= 40% of standard, measured before resistance.
      Weaker hits still deal damage. Continuing an already-started chain has no threshold.
      (80-100% also affects terrain: not modeled, no terrain yet.)

PROVISIONAL (implementation choices, not authored):
  P1. Hits 4+ use the 3rd-hit bonus band.
  P2. Hits 3+ look up FOLLOW_UP[(state, element)] first, then REACTIONS[(previous, element)].
  P3. Other elements' final infliction is +0% (FINAL_INFLICTION has only Water and Fire).
  P4. The repeat hit gets no bonus and no final infliction, and leaves the stored ongoing as is.
  P5. Hit bonus and stored ongoing are reduced by the target's resistance to that element;
      the final infliction is not resisted a second time.
  P6. Bonus roll seeded by (seed, hit id). Tie-break: declared affinity, else no advance.
  P7. Exactly 40% starts a chain (40-80% band is inclusive at 40%). Strength defaults to 1.0.
Out of scope: ongoing ticks (no turns yet), fields, Vale. Propagation: propagation_mr_sketch.py.
"""

import random
from dataclasses import dataclass, replace
from typing import Dict, FrozenSet, List, Mapping, Optional, Tuple

Element = str  # "earth" "water" "fire" "lightning" "ice" "moon" "shadow" "spirit"


@dataclass(frozen=True)
class Reaction:
    name: str
    terminal: bool = False


# Author-confirmed two-hit cells, time order (first, second).
REACTIONS: Mapping[Tuple[Element, Element], Reaction] = {
    ("water", "fire"): Reaction("Boil"),
    ("fire", "water"): Reaction("Steam"),
    ("fire", "lightning"): Reaction("Plasma"),
    ("lightning", "fire"): Reaction("Char", terminal=True),
    ("earth", "water"): Reaction("Mudstorm"),
    ("earth", "lightning"): Reaction("Grounding"),  # whether it ends the chain is OPEN
}

# (reaction state, next element) -> Reaction, for hits 3+. Empty until ratified
# (e.g. Mudstorm + fire -> Volcanic Eruption is source-recovered, not confirmed).
FOLLOW_UP: Mapping[Tuple[str, Element], Reaction] = {}

# Optional cap on chain length. Author: configurable, disabled for now.
MAX_CHAIN_HITS: Optional[int] = None

# Chain hit number -> bonus range, fraction of the spell's standard damage. Hits 4+ use 3 (P1).
HIT_BONUS: Mapping[int, Tuple[float, float]] = {2: (0.02, 0.04), 3: (0.03, 0.05)}

# Outgoing element -> bonus on its remaining ongoing damage. Only Water and Fire are authored;
# shortcut: other elements give their remaining ongoing at +0%, fill in when authored.
FINAL_INFLICTION: Mapping[Element, float] = {"water": 0.01, "fire": 0.02}

# Minimum strength (fraction of standard, before resistance) to start a chain.
START_THRESHOLD = 0.40


@dataclass(frozen=True)
class Chain:
    elements: Tuple[Element, ...] = ()
    state: Optional[str] = None  # current reaction name
    closed: bool = False
    ongoing: float = 0.0  # remaining ongoing damage of elements[-1], after resistance


@dataclass(frozen=True)
class Target:
    hp: float
    resist: Mapping[Element, float]  # 0.5 = 50% resist
    chain: Chain = Chain()
    conditions: FrozenSet[str] = frozenset()  # symbolic forms like "clay", "ash"; not elements


# ============================================================
# PURE HELPERS
# ============================================================

def after_resist(damage: Mapping[Element, float], resist: Mapping[Element, float]) -> Dict[Element, float]:
    # Immunity or absorption never counts as damage for dominance.
    return {e: max(0.0, d * (1.0 - resist.get(e, 0.0))) for e, d in damage.items()}


def dominant(dealt: Mapping[Element, float], affinity: Optional[Element]) -> Optional[Element]:
    """Element that enters the chain, or None (no damage, or unbroken tie)."""
    top = max(dealt.values(), default=0.0)
    if top <= 0.0:
        return None
    tied = [e for e, d in dealt.items() if d == top]
    if len(tied) == 1:
        return tied[0]
    # shortcut: tie-break is OPEN; declared affinity wins, else no advancement.
    return affinity if affinity in tied else None


def advance(chain: Chain, element: Element, max_hits: Optional[int] = MAX_CHAIN_HITS) -> Tuple[Chain, Optional[str]]:
    """Apply one primary element to a chain. Returns (new chain, alert or None)."""
    if chain.closed or not chain.elements:
        return Chain(elements=(element,), closed=max_hits == 1), None
    prev = chain.elements[-1]
    if element == prev:
        return replace(chain, closed=True), f"repeated {element} ends the chain"

    elements = chain.elements + (element,)
    reaction = (len(elements) > 2 and FOLLOW_UP.get((chain.state or "", element))) or REACTIONS.get((prev, element))
    alert = None if reaction else f"unauthored cell {prev}->{element}"
    closed = bool(reaction and reaction.terminal) or (max_hits is not None and len(elements) >= max_hits)
    return Chain(elements, reaction.name if reaction else None, closed), alert


# ============================================================
# CORE KERNEL
# ============================================================

def step_chain(
    targets: Mapping[str, Target],
    hits: List[Dict],
    seed: int = 0,
    max_hits: Optional[int] = MAX_CHAIN_HITS,
) -> Tuple[Dict[str, Target], List[str], List[str]]:
    """
    hits: [{"id", "target", "primary": bool, "damage": {element: amount}, "affinity"?: element,
            "standard"?: spell standard damage (default: sum of damage),
            "ongoing"?: ongoing damage the dominant element applies, before resistance,
            "strength"?: fraction of standard strength before resistance (default 1.0)}]
    The bonus roll is seeded by (seed, hit id), so results don't depend on batch order.
    Returns (targets_out, accepted_hit_ids, alerts). Inputs are never mutated.
    """
    out = dict(targets)
    accepted: List[str] = []
    alerts: List[str] = []

    for hit in hits:
        t = out.get(hit["target"])
        if t is None:
            alerts.append(f"{hit['id']}: unknown target")
            continue

        dealt = after_resist(hit["damage"], t.resist)
        total = sum(dealt.values())
        chain = t.chain
        if hit["primary"]:
            element = dominant(dealt, hit.get("affinity"))
            starting = chain.closed or not chain.elements
            if element is not None and starting and hit.get("strength", 1.0) < START_THRESHOLD:
                alerts.append(f"{hit['id']}: strength below {START_THRESHOLD:.0%}, no chain started")
            elif element is not None:
                prev = chain.elements[-1] if chain.elements else None
                repeat = element == prev and not chain.closed
                if prev is not None and element != prev:
                    total += chain.ongoing * (1.0 + FINAL_INFLICTION.get(prev, 0.0))
                chain, alert = advance(chain, element, max_hits)
                if alert:
                    alerts.append(f"{hit['id']}: {alert}")
                band = None if repeat else HIT_BONUS.get(min(len(chain.elements), 3))
                if band:
                    pct = random.Random(f"{seed}:{hit['id']}").uniform(*band)
                    standard = hit.get("standard", sum(hit["damage"].values()))
                    total += pct * standard * (1.0 - t.resist.get(element, 0.0))
                if not repeat:
                    ongoing = hit.get("ongoing", 0.0) * (1.0 - t.resist.get(element, 0.0))
                    chain = replace(chain, ongoing=max(0.0, ongoing))
            elif total > 0:
                alerts.append(f"{hit['id']}: element tie, chain not advanced")

        out[hit["target"]] = replace(t, hp=t.hp - total, chain=chain)
        accepted.append(hit["id"])

    return out, accepted, alerts


# ============================================================
# SELF-CHECK
# ============================================================

if __name__ == "__main__":
    def hit(i, element_damage, primary=True, affinity=None, target="foe", ongoing=0.0):
        return {"id": i, "target": target, "primary": primary, "damage": element_damage,
                "affinity": affinity, "ongoing": ongoing}

    foe = {"foe": Target(hp=1000.0, resist={})}

    # Water -> Fire = Boil, chain still open for a third hit.
    s, _, _ = step_chain(foe, [hit("a", {"water": 10}), hit("b", {"fire": 10})])
    assert s["foe"].chain == Chain(("water", "fire"), "Boil", closed=False)

    # Order matters: Lightning -> Fire = Char (terminal); Fire -> Lightning = Plasma.
    s, _, _ = step_chain(foe, [hit("a", {"lightning": 10}), hit("b", {"fire": 10})])
    assert s["foe"].chain.state == "Char" and s["foe"].chain.closed
    s, _, _ = step_chain(foe, [hit("a", {"fire": 10}), hit("b", {"lightning": 10})])
    assert s["foe"].chain.state == "Plasma" and not s["foe"].chain.closed

    # Water -> Fire: Fire gets the 2nd-hit bonus, 2-4% of standard 10 -> 0.2..0.4 extra.
    s, _, _ = step_chain(foe, [hit("a", {"water": 10}), hit("b", {"fire": 10})])
    assert 1000 - 20 - 0.4 <= s["foe"].hp <= 1000 - 20 - 0.2
    # Same seed + hit id -> same roll; different seed -> different roll.
    s2, _, _ = step_chain(foe, [hit("a", {"water": 10}), hit("b", {"fire": 10})])
    s3, _, _ = step_chain(foe, [hit("a", {"water": 10}), hit("b", {"fire": 10})], seed=1)
    assert s2["foe"].hp == s["foe"].hp != s3["foe"].hp

    # Replacement: Fire leaves 50 ongoing; Water replaces it -> 50 * 1.02 final infliction.
    s, _, _ = step_chain(foe, [hit("a", {"fire": 10}, ongoing=50), hit("b", {"water": 10}, ongoing=20)])
    assert 1000 - 20 - 51 - 0.4 <= s["foe"].hp <= 1000 - 20 - 51 - 0.2
    assert s["foe"].chain.state == "Steam" and s["foe"].chain.ongoing == 20
    # 3rd hit: Water's 20 ongoing at +1%, plus 3-5% of standard 10.
    s, _, _ = step_chain(s, [hit("c", {"earth": 10})])
    hp = 1000 - 30 - 51 - 20.2
    assert hp - 0.4 - 0.5 <= s["foe"].hp <= hp - 0.2 - 0.3
    # Ongoing is stored after resistance.
    s, _, _ = step_chain({"foe": Target(hp=1000.0, resist={"fire": 0.5})}, [hit("a", {"fire": 10}, ongoing=50)])
    assert s["foe"].chain.ongoing == 25

    # Secondary hits deal damage but never advance the chain.
    s, _, _ = step_chain(foe, [hit("a", {"water": 10}), hit("b", {"fire": 10}, primary=False)])
    assert s["foe"].chain == Chain(("water",)) and s["foe"].hp == 980.0

    # No hit limit by default: the chain stays open past three hits.
    four = [hit("a", {"fire": 1}), hit("b", {"water": 1}), hit("c", {"lightning": 1}), hit("d", {"earth": 1})]
    s, _, _ = step_chain(foe, four)
    assert not s["foe"].chain.closed and len(s["foe"].chain.elements) == 4
    # Configured cap closes it; the next primary starts a fresh chain.
    s, _, _ = step_chain(foe, four[:3], max_hits=3)
    assert s["foe"].chain.closed
    s, _, _ = step_chain(s, [four[3]], max_hits=3)
    assert s["foe"].chain.elements == ("earth",)

    # Dual element: Fire 100 @50% resist vs Spirit 100 @10% -> Spirit enters chain, total 140.
    resistant = {"foe": Target(hp=1000.0, resist={"fire": 0.5, "spirit": 0.1})}
    s, _, _ = step_chain(resistant, [hit("a", {"fire": 100, "spirit": 100})])
    assert s["foe"].chain.elements == ("spirit",) and s["foe"].hp == 860.0

    # Same spell, no resistances: tie. No affinity -> no advance; affinity breaks it.
    s, _, al = step_chain(foe, [hit("a", {"fire": 100, "spirit": 100})])
    assert s["foe"].chain == Chain() and "tie" in al[0]
    s, _, _ = step_chain(foe, [hit("a", {"fire": 100, "spirit": 100}, affinity="fire")])
    assert s["foe"].chain.elements == ("fire",)

    # Full immunity never counts as dominant.
    immune = {"foe": Target(hp=1000.0, resist={"fire": 1.0})}
    s, _, _ = step_chain(immune, [hit("a", {"fire": 100, "spirit": 5})])
    assert s["foe"].chain.elements == ("spirit",)

    # Unauthored cell: alert, the hit still counts, no reaction named.
    s, _, al = step_chain(foe, [hit("a", {"moon": 1}), hit("b", {"shadow": 1})])
    assert s["foe"].chain == Chain(("moon", "shadow")) and "unauthored" in al[0]

    # Inputs untouched.
    assert foe["foe"].chain == Chain() and foe["foe"].hp == 1000.0
    print("chain_mr_sketch: all checks passed")
