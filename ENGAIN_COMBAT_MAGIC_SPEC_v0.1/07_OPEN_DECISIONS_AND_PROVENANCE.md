# Open Decisions, Clarifications and Preservation Notes

This list is intentionally explicit: these decisions must not be filled in by assistant guesswork.

## Critical design choices still OPEN

1. **Numbered diagrams / facing:** confirm top-down coordinates, exact IDs on each edge, true front/back and type 6 pad placement against original drawings.
2. **Type 6 combo locks:** ratify which dual pairs and left/right side triple groups are approved (earlier assistant suggested several).
3. **Environment-to-pad chain lookup:** if a moving enemy shifts launch pads over fixed base-form cells, what spatial overlap qualifies a pad as water/earth-primed? What happens to a preexisting double-chain when its enemy moves?
4. **Status stacking:** Ground Tremor slow −20% versus Mudstorm slow −30%; replace, additive, max-only, independent durations? Terrain modifiers apply only while in affected cells.
5. **Chain lifetime:** priming duration, consumption on trigger, clearing/transformation of base-form effects and whether unconsumed old effects persist.
6. **Reactions by element:** continuing/transforming/terminating Lightning; Earth stops; Water continues; Fire→Plasma; triple stops original travel currently. Need other elements and elemental sequence order.
7. **Basic Lightning allowance:** hop path over multiple pads vs one additional *distinct target* at level 1. How are repeated hits to same enemy prevented or scaled?
8. **Aqua Lightning additional targets:** use authored directional pad topology or other target-selection logic? Relationship to incoming Lightning's remaining allowance and conductivity.
9. **Randomizer:** aim accuracy, landing rules, range, roll distribution, difficulty/mastery scaling and seed model.
10. **AoE geometry:** spell-specific grids (radial, straight, trident), collision/cover, friendly fire, occupant footprint intersection and whether triple explosion extends to adjacent pad-base intersections.
11. **Penetration/facing:** author floated 100/60/20/5 and 90% for pad 24/29; no fixed formula. Determine impact on armor/surface layers; no silent stacking.
12. **Character combo learning:** discover vs learned vs successfully demonstrated, qualification gates, duo/trio-specific mastery and failure learning.
13. **Physical combat:** audit existing surface-layer/weapon rules, don't reduce to plain HP.
14. **Spell document discrepancies:** Fire+Water vs Water+Fire names/effects; potential alternate copies; DoT percentages' bases.
15. **Additional powers:** Vril, Graviton, Void, named first/second magics and Spirit Walking compatibility. Never silently merge with original eight elements.
16. **NPC chain library:** verify exact spell source files, skill tiers and progression for generic NPC/basic magic.
17. **Encounter timing:** initiative, interrupts, turns, effects ticking relative to player action and enemy response.
18. **Authority:** trusted AP issuer, existing rule registry and 8090/8080/8765 path integration; no fail-open, no untrusted client authority claims.

## Source classification reminders

- Numbered pad scheme **1, 2–3, 4–7, 8–13, 14–21, 22–31**: author-approved from final sketch.
- Character duo locks Type 4 + Type 5: author-specified.
- Advanced triple `8+13+9`, `8+13+12`, `10+11+9`, `10+11+12`: author-specified examples.
- Local Lightning route and branching/jump logic: author described across several turns, assistant diagrams illustrative only.
- 'Three chain effects': author mentioned three, but their exact original formal category names **have not been recovered**. Do not equate with single/double/triple by assumption.
- Standard AoE aim within character range independent from launch pads: author preference; pad snapping fallback allowed if needed.
- Physical attack damage values, nonlethal test mode, Combat3D snapshot integration: design only.
- The magic docs are historical source text; original exact copies and variants have not been exported/deduplicated into this ZIP.

## Safe source-recovery plan

1. Preserve originals of all local and Drive magic documents without renaming/moving.
2. Obtain alternate variants and compare byte hashes and meaning before consolidating.
3. Review `vale magic.txt` as **completeness reference** for named-character first/second magic; verify every named character separately.
4. Compare `Single chains`, `triple chains.txt`, and per-element files against new platform and area rules, without retroactively rewriting historical originals.
5. Author explicitly approves any final ZW definition and AP authority changes after read-only code audit.

## Original discussions vs this document

This is an authored **summary/specification draft derived from conversation**, not a verbatim chat transcript. If full history is needed, export the chat separately and keep alongside this archive as provenance. Screenshots and diagrams are conversation attachments, not necessarily included here; collect originals as controlled references before geometry encoding.
