import unittest

from chain_mr_sketch import Chain, Target, step_chain
from party_cycle_sketch import PartyCycle, record_turn, step_turn
from propagation_mr_sketch import propagate


def hit(i, damage, ongoing=0.0, primary=True, target="foe"):
    # standard 0 zeroes the rolled chain bonus, so damage totals are exact.
    return {"id": i, "target": target, "primary": primary, "damage": damage, "ongoing": ongoing, "standard": 0}


def foe(resist=None):
    return {"foe": Target(hp=1000.0, resist=resist or {})}


class FinalInfliction(unittest.TestCase):
    def test_fire_replaced_by_water(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 10}, ongoing=50), hit("b", {"water": 10}, ongoing=20)])
        self.assertAlmostEqual(s["foe"].hp, 1000 - 10 - 10 - 50 * 1.02)
        self.assertEqual((s["foe"].chain.state, s["foe"].chain.ongoing), ("Steam", 20.0))

    def test_water_replaced_by_fire(self):
        s, _, _ = step_chain(foe(), [hit("a", {"water": 10}, ongoing=40), hit("b", {"fire": 10}, ongoing=30)])
        self.assertAlmostEqual(s["foe"].hp, 1000 - 10 - 10 - 40 * 1.01)
        self.assertEqual((s["foe"].chain.state, s["foe"].chain.ongoing), ("Boil", 30.0))

    def test_resistance_applies_once(self):
        # Fire resist 50%: 10 -> 5 hit, 50 ongoing stored as 25, final 25 * 1.02 (not resisted again).
        s, _, _ = step_chain(foe({"fire": 0.5}), [hit("a", {"fire": 10}, ongoing=50), hit("b", {"water": 10})])
        self.assertAlmostEqual(s["foe"].hp, 1000 - 5 - 10 - 25 * 1.02)
        # Incoming Water's ongoing is resisted on entry.
        s, _, _ = step_chain(foe({"water": 0.25}), [hit("a", {"fire": 10}), hit("b", {"water": 8}, ongoing=40)])
        self.assertEqual(s["foe"].chain.ongoing, 30.0)

    def test_replacement_chain_of_three(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 10}, ongoing=50), hit("b", {"water": 10}, ongoing=20),
                                     hit("c", {"fire": 10}, ongoing=5)])
        self.assertAlmostEqual(s["foe"].hp, 1000 - 30 - 50 * 1.02 - 20 * 1.01)
        self.assertEqual(s["foe"].chain.ongoing, 5.0)

    def test_no_ongoing_no_infliction(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 10}), hit("b", {"water": 10})])
        self.assertAlmostEqual(s["foe"].hp, 980)

    def test_secondary_hit_does_not_replace(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 10}, ongoing=50), hit("b", {"water": 10}, primary=False)])
        self.assertAlmostEqual(s["foe"].hp, 980)
        self.assertEqual(s["foe"].chain, Chain(("fire",), ongoing=50.0))


class Repeat(unittest.TestCase):
    def test_repeat_ends_chain_normal_damage(self):
        hits = [hit("a", {"water": 10}, ongoing=40), hit("b", {"fire": 10}, ongoing=30), hit("c", {"fire": 10}, ongoing=99)]
        s, _, al = step_chain(foe(), hits)
        c = s["foe"].chain
        self.assertEqual((c.elements, c.state, c.closed, c.ongoing), (("water", "fire"), "Boil", True, 30.0))
        self.assertAlmostEqual(s["foe"].hp, 1000 - 30 - 40 * 1.01)  # repeat: plain 10, no final infliction
        self.assertIn("repeated fire", al[-1])

    def test_repeat_without_bonus(self):
        # Real standard: the repeat must not roll a chain bonus.
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 10}), dict(hit("b", {"fire": 10}), standard=10)])
        self.assertEqual(s["foe"].hp, 980.0)

    def test_after_repeat_fresh_chain(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 1}), hit("b", {"fire": 1}), hit("c", {"water": 1})])
        self.assertEqual(s["foe"].chain.elements, ("water",))

    def test_no_limit_and_cap(self):
        hits = [hit(str(i), {e: 1}) for i, e in enumerate(["fire", "water", "fire", "water", "fire"])]
        s, _, _ = step_chain(foe(), hits)
        self.assertEqual((len(s["foe"].chain.elements), s["foe"].chain.closed), (5, False))
        s, _, _ = step_chain(foe(), hits[:2], max_hits=2)
        self.assertTrue(s["foe"].chain.closed)


class Propagation(unittest.TestCase):
    def setUp(self):
        mk = lambda el: Target(100.0, {}, Chain((el,)) if el else Chain())
        self.t = {"e1": mk(None), "e2": mk(None), "e3": mk(None), "e4": mk("fire"), "e5": mk(None),
                  "mud": mk("earth"), "dark": mk("shadow")}

    def test_plasma_continues(self):
        hits, _ = propagate("bolt", self.t, ["e1", "e2", "e3", "e4", "e5"], [5] * 5)
        self.assertEqual([next(iter(h["damage"])) for h in hits], ["lightning"] * 3 + ["plasma"] * 2)
        self.assertEqual([h["primary"] for h in hits], [True] + [False] * 4)

    def test_grounding_and_shadow_stop_but_receive(self):
        for stopper in ("mud", "dark"):
            hits, al = propagate("bolt", self.t, ["e1", "e2", stopper, "e3"], [5] * 4)
            self.assertEqual([h["target"] for h in hits], ["e1", "e2", stopper])
            self.assertIn("bolt stops", al[-1])

    def test_primary_on_fire_carrier_lands_as_lightning(self):
        # Chain gets Fire -> Lightning = Plasma; the bolt carries on as Plasma; no "plasma" chain element.
        hits, _ = propagate("bolt", self.t, ["e4", "e1"], [5, 5])
        self.assertEqual([next(iter(h["damage"])) for h in hits], ["lightning", "plasma"])
        s, _, _ = step_chain(self.t, hits)
        self.assertEqual((s["e4"].chain.elements, s["e4"].chain.state), (("fire", "lightning"), "Plasma"))

    def test_jumps_never_advance_chains(self):
        hits, _ = propagate("bolt", self.t, ["e1", "e4"], [5, 5])
        s, _, _ = step_chain(self.t, hits)
        self.assertEqual(s["e1"].chain.elements, ("lightning",))
        self.assertEqual(s["e4"].chain.elements, ("fire",))
        self.assertEqual(s["e4"].hp, 95.0)

    def test_clay_and_ash_inherit_the_stop(self):
        t = dict(self.t, clay=Target(100.0, {}, conditions=frozenset({"clay"})),
                 ash=Target(100.0, {}, conditions=frozenset({"ash"})))
        for stopper, name in (("clay", "Grounding"), ("ash", "Absorption")):
            hits, al = propagate("bolt", t, ["e1", stopper, "e2"], [5] * 3)
            self.assertEqual([h["target"] for h in hits], ["e1", stopper])
            self.assertIn(f"{name} at {stopper}", al[-1])

    def test_clay_is_not_an_element(self):
        # Inherits Grounding only: Clay doesn't enter or alter the chain as Earth would.
        t = {"foe": Target(1000.0, {}, Chain(("water",)), conditions=frozenset({"clay"}))}
        s, _, al = step_chain(t, [hit("a", {"lightning": 10})])
        self.assertEqual((s["foe"].chain.elements, s["foe"].chain.state), (("water", "lightning"), None))


class PartyCycles(unittest.TestCase):
    PARTY = ("p1", "p2", "p3")

    def test_cycle_advances_after_full_party(self):
        c = PartyCycle(self.PARTY)
        c = record_turn(record_turn(c, "p1"), "p2")
        self.assertEqual((c.number, c.acted), (1, frozenset({"p1", "p2"})))
        c = record_turn(c, "p3")
        self.assertEqual((c.number, c.acted), (2, frozenset()))

    def test_rejects_double_turn_and_outsider(self):
        c = record_turn(PartyCycle(self.PARTY), "p1")
        with self.assertRaises(ValueError):
            record_turn(c, "p1")
        with self.assertRaises(ValueError):
            record_turn(c, "boss")

    def test_boss_chain_across_two_cycles(self):
        boss = {"boss": Target(5000.0, {"fire": 0.2})}
        # (actor, element, base damage, ongoing) over two full party cycles, no consecutive repeats.
        turns = [("p1", "water", 100, 40), ("p2", "fire", 100, 50), ("p3", "lightning", 100, 0),
                 ("p1", "earth", 100, 30), ("p2", "water", 100, 20), ("p3", "fire", 100, 50)]
        # Expected per-turn damage from the rules alone, ignoring cycles:
        # own damage after resistance + previous element's remaining ongoing x (1 + its final %).
        expected = [100, 80 + 40 * 1.01, 100 + 40 * 1.02, 100, 100 + 30, 80 + 20 * 1.01]
        cycle, state, deltas, cycles_seen = PartyCycle(self.PARTY), boss, [], []
        for i, (actor, el, dmg, ong) in enumerate(turns):
            cycles_seen.append(cycle.number)
            before = state["boss"].hp
            state, cycle, accepted, _ = step_turn(state, cycle, actor, [hit(f"t{i}", {el: dmg}, ongoing=ong, target="boss")])
            self.assertEqual(accepted, [f"t{i}"])
            deltas.append(before - state["boss"].hp)

        self.assertEqual(cycles_seen, [1, 1, 1, 2, 2, 2])
        self.assertEqual((cycle.number, cycle.acted), (3, frozenset()))
        chain = state["boss"].chain
        self.assertEqual(chain.elements, ("water", "fire", "lightning", "earth", "water", "fire"))
        self.assertFalse(chain.closed)  # persisted through both cycle boundaries
        self.assertEqual((chain.state, chain.ongoing), ("Boil", 40.0))  # fire 50 at 20% resist
        for got, want in zip(deltas, expected):
            self.assertAlmostEqual(got, want)

        # Independence: the cycle-2 turns produce the same damage as the same hits with no cycle wrapper.
        s, _, _ = step_chain(boss, [hit(f"t{i}", {el: d}, ongoing=o, target="boss") for i, (_, el, d, o) in enumerate(turns)])
        self.assertAlmostEqual(s["boss"].hp, state["boss"].hp)



class StartThreshold(unittest.TestCase):
    def test_weak_hit_damages_but_starts_nothing(self):
        s, _, al = step_chain(foe(), [dict(hit("a", {"fire": 25}, ongoing=50), strength=0.25)])
        self.assertEqual((s["foe"].hp, s["foe"].chain), (975.0, Chain()))
        self.assertIn("no chain started", al[0])

    def test_bands(self):
        for strength, started in ((0.39, False), (0.40, True), (0.60, True), (0.90, True)):
            s, _, _ = step_chain(foe(), [dict(hit("a", {"fire": 10}), strength=strength)])
            self.assertEqual(s["foe"].chain.elements == ("fire",), started, strength)

    def test_measured_before_resistance(self):
        # Full strength into 90% Fire resist: 1 damage, still starts the chain.
        s, _, _ = step_chain(foe({"fire": 0.9}), [dict(hit("a", {"fire": 10}), strength=1.0)])
        self.assertEqual((s["foe"].chain.elements, round(s["foe"].hp, 6)), (("fire",), 999.0))

    def test_weak_hit_continues_started_chain(self):
        s, _, _ = step_chain(foe(), [hit("a", {"water": 10}, ongoing=40), dict(hit("b", {"fire": 10}), strength=0.2)])
        self.assertEqual(s["foe"].chain.state, "Boil")

    def test_weak_hit_cannot_restart_closed_chain(self):
        s, _, _ = step_chain(foe(), [hit("a", {"fire": 1}), hit("b", {"fire": 1}), dict(hit("c", {"water": 1}), strength=0.1)])
        self.assertEqual((s["foe"].chain.elements, s["foe"].chain.closed), (("fire",), True))


class EncounterDemo(unittest.TestCase):
    def test_six_behaviors(self):
        from encounter_demo import run_encounter
        targets, cycle, log = run_encounter()
        turn = {e["turn"]: e for e in log}
        self.assertEqual(turn["c1_fire"]["chains"]["boss"].state, "Boil")                        # 1
        self.assertEqual(turn["c2_water"]["chains"]["boss"].state, "Steam")                      # 2
        self.assertEqual([h[1] for h in turn["c1_bolt"]["hits"]], ["lightning", "plasma", "plasma"])  # 3
        for t, stopper in (("c2_bolt", "mud"), ("c2_bolt2", "dark")):                            # 4
            self.assertEqual([h[0] for h in turn[t]["hits"]][-1], stopper)
            self.assertEqual(targets["e5"].hp, 200.0)
        unnamed = turn["c2_bolt"]["chains"]["boss"]                                              # 5
        self.assertEqual((unnamed.elements[-1], unnamed.state, unnamed.closed), ("lightning", None, False))
        self.assertGreater(turn["c2_bolt"]["hits"][0][3], 0)
        final = targets["boss"].chain                                                            # 6
        self.assertTrue(final.closed and final.elements.count("lightning") == 1)
        self.assertEqual(turn["c2_bolt2"]["hits"][0][3], 30.0)  # repeat: plain damage
        self.assertEqual(cycle.number, 3)

    def test_json_export_matches_run(self):
        import json
        from encounter_demo import encounter_json
        data = json.loads(json.dumps(encounter_json()))
        from encounter_demo import run_encounter
        targets, _, _ = run_encounter()
        for tid, t in targets.items():
            dealt = sum(h["damage"] for turn in data["turns"] for h in turn["hits"] if h["target"] == tid)
            self.assertAlmostEqual(data["targets"][tid]["hp"] - dealt, t.hp, places=1)


class LightningField(unittest.TestCase):
    # 6x5 grid, 2.6 apart: same shape as the Godot export, without depending on it.
    POS = {f"f{r * 6 + c:02d}": (c * 2.6, r * 2.6) for r in range(5) for c in range(6)}

    def test_walk_stays_in_range_and_never_revisits(self):
        import math
        from lightning_field import JUMP_RANGE, walk
        for seed in range(20):
            path = walk(self.POS, "f14", seed)
            self.assertEqual(len(path), len(set(path)))
            for a, b in zip(path, path[1:]):
                self.assertLessEqual(math.dist(self.POS[a], self.POS[b]), JUMP_RANGE)
            self.assertEqual(path, walk(self.POS, "f14", seed))  # seeded: repeatable

    def test_field_too_small_is_a_clear_error(self):
        from lightning_field import populate
        with self.assertRaises(ValueError):
            populate({"a": (0, 0), "b": (1, 0)}, 0)

    def test_walk_ends_when_nobody_in_range(self):
        from lightning_field import walk
        self.assertEqual(walk({"a": (0, 0), "b": (2, 0), "far": (50, 0)}, "a", 0), ["a", "b"])

    def test_strike_obeys_propagation_rules(self):
        from lightning_field import strike
        from propagation_mr_sketch import stop_family
        for seed in range(20):
            before, after, path, hits, _ = strike(self.POS, seed)
            hit_ids = [h["target"] for h in hits]
            self.assertEqual(hit_ids, path[:len(hits)])                     # follows the walk
            self.assertTrue(all(stop_family(before[t]) is None for t in hit_ids[:-1]))
            if len(hits) < len(path):                                      # cut short only by a stopper
                self.assertIsNotNone(stop_family(before[hit_ids[-1]]))
            forms = [next(iter(h["damage"])) for h in hits]
            fire_at = next((i for i, t in enumerate(hit_ids) if before[t].chain.elements[-1:] == ("fire",)), None)
            self.assertEqual(forms, ["lightning"] * (fire_at if fire_at is not None else len(forms))
                             + ["plasma"] * (len(forms) - fire_at if fire_at is not None else 0))
            for t in hit_ids[1:]:                                          # jumps never touch chains
                self.assertEqual(after[t].chain, before[t].chain)

if __name__ == "__main__":
    unittest.main(verbosity=1)
