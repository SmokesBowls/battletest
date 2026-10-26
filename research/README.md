
The Gemini file has the most EngAIn-specific material. I'll check its "author-approved" labels against spec file 02 before reporting.

  Ran 1 shell command

There's real gold in here, mostly in the Gemini file. I read all three: all of the Gemini file, all of "Deterministic Combat," and about two-thirds of "Narrative-Free Combat" plus a skim of the rest.

Gold nuggets worth keeping

From technical implementation magic Gemini.md (the only one written specifically for EngAIn):
1. Two separate budgets for Lightning. Hopping between pads on one enemy uses a pad-contact budget; damaging a new enemy uses a separate entity-damage budget. That resolves the Thunder's Wrath conflict listed in spec 03 ("chains to 1 target" vs many pad hops), and it matches your primary/secondary rule.
2. Reactions replace the base spell's damage instead of adding to it. When a spell lands on an already-primed target, the reaction resolves in place of the spell's normal damage. That's how spec 03's "don't apply full base spell and full combo twice" would actually work in code. My sketch currently applies both, so this is the first thing to fix in it.
3. A friendly-fire setting on every spell: HOSTILE_ONLY / ALL_COMBATANTS / ALLIES_EXCLUDED. That's the missing piece for Cleansing (it removes statuses from anyone, but healing goes only to eligible targets) and for Vale's Weight of Presence (it affects friends too).
4. Terrain lives on the world grid, not on enemies. Mudfields stay put when an enemy moves. That matches the author clarification in spec 04.
5. A good format for the calibration harness and its tests. The calibration plan (spec 06) already exists; this file shows how to write its tests.

From "Deterministic Combat":
6. Each subsystem gets its own random-number stream. Drawing a random value for a Lightning branch must not shift the random state used for reactions. The Gemini file uses one shared generator, so this beats it.
7. Four replay tests:
- Same seed plus same commands must produce the same result.
- Save and reload mid-fight must change nothing.
- The AI must make the same choices from the same state.
- Adding a new random subsystem must not disturb existing ones.
8. Whole-number ("fixed-point") math instead of floating-point for anything the simulation relies on, so every machine gets identical results. Both the Gemini file and my sketch use floats, so that needs changing before porting.
9. Names for spec 03's open "does each pad contact damage again?" question: IGNORE_REPEATED / AMPLIFY_REPEATED / APPLY_DAMAGE_REPEATED.

From "Narrative-Free Combat":
10. Nested tags like Status.Burning and Element.Fire. That's the clean way to implement the personal-magic rule: "if a personal spell produces a condition the elemental physics recognizes, it can join a chain" becomes a simple tag match. The rest of this PDF is general advice on how to structure the engine, nothing EngAIn-specific.

Places they put words in your mouth

- The Gemini file invents numbers. It uses an obstruction failure rate of 0.75–0.90 (0.85 in its tests), a cap of two characters per pad, and "forfeits AP plus a fumble state." Spec 01 says no failure probability has been chosen.
- The Gemini code has two bugs:
  - Volcanic Eruption scales off the incoming Fire spell's power, but spec 04 says 150% of Earth's base damage.
  - Its Earth+Water check uses OR, so a target primed with Water alone would erupt.
- It predates your order rules. It has no Boil or Steam, and its Lightning-meets-Water check ignores which element came first.
- "Deterministic Combat" confuses the 3-hit elemental chain limit with Lightning's hop limit (max_chain_length: 3 = "triple-chain termination"). Those are different mechanics.

What to leave out

- Genshin's elemental gauge system (aura units, Pyro/Hydro, Melt coefficients). It's a different model from another game: reactions consume an aura, instead of your ordered physics chain.
- Fighting-game frame-advantage math. EngAIn is turn-based.
- Granblue-style damage caps.
- Mudstorm as pre-placed map geometry that Lightning "prefers" to follow. That contradicts the spec, where Mudfields are created by reactions during combat.
- Many of the PDFs' citations are Reddit, Instagram and wiki pages, so treat their claims as unverified.

Suggested next step: nuggets 2, 3 and 6 each slot into the chain sketch cleanly (the reaction replacing base damage, a recipient policy on each hit, a seed per subsystem). Nugget 1 belongs in the Lightning kernel once you build it. I haven't changed anything yet. Want me to add those three to the sketch?
