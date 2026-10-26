# battletest

Magic and combat design work for *Burdens of a Forgotten Past*: the authored elemental chain rules, the spec, research sources, and disposable test sims.

Start with `SESSION_HANDOFF_2026-10-20.md`. It separates **author decisions (canon)** from recovered sources and open questions.

## Interactive battle test

Choose an element, a delivery pattern and a first enemy, then press SPACE to watch the hits land and each enemy's elemental stack update.

```
python3 battletest/delivery_viz.py
```

Run it from this folder (it imports `chain_mr_sketch.py` from here). It needs Python 3 with tkinter.

- **Element:** E W F L, or the buttons
- **Pattern:** S D T Q M (Single, Double, Triple, Quad, Mortar)
- **Click** an enemy for the first target, or a ground point for Mortar
- **SPACE** attacks; **R** resets the stacks; the Layout menu switches the test positions

### Rules it uses

- **Author-approved:** one hit per enemy per attack; Double, Triple and Quad hit 2, 3 and 4 different enemies, with no jump range; directional follow-ups with a fallback to the other side; every hit is a full hit; nothing carries between enemies; one stack per enemy. The stack logic is the unchanged `chain_mr_sketch.advance`.
- **Simulation assumptions, not canon:** the side is a left/right roll from the first target and the attack hops to the nearest unhit enemy on that side; the Mortar radius is a 2 m placeholder; the layouts are test positions.

### Numbers without the window

```
python3 battletest/delivery_sim.py            # pattern comparison -> battletest/results_delivery.md
python3 battletest/delivery_sim.py --openers  # shared vs independent first targets -> results_openers.md
```

Both scripts run a self-check first.

## Other checks

```
python3 test_chain_mr_sketch.py
python3 test_chain_zw_bridge.py
```
