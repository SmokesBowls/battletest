# Shared Combat Runtime — Proposed Integration Contract

**Status: DESIGN PROPOSAL.** This document is NOT a claim about live API signatures or present kernel coverage.

## Authority and agnosticism

- **ZW** expresses authored character spells, elemental chains, conditional rules, topology and geometry/relationships without hardcoding one game's narrative.
- **AP** authorizes state-changing actions, including trusted actor identity and context. Runtime must not bypass AP or allow client-supplied authority to stand in for a trusted issuer.
- **EngAInRuntime snapshot / runtime owner** is the authoritative simulation state for entities and battlefield conditions.
- **Combat3D** resolves attacks and produces effects/events; **spatial/topology subsystem** resolves footprint and addresses. Avoid duplicate owners of mutable combat state.
- **Godot/Dragon** animates and renders; no independent combat HP, elemental-chain or spatial truth.
- Do not conflate 8080 gateway rules, 8090 authority gate, or 8765 independent AP runtime—previous audits found they were not a unified magic execution path.
- Existing Combat3D implements some health/damage/death behavior according to Dragon's read-only audit. **Magic/surface layers/formation coverage must be audited in code**, not assumed.

## Semantic entities and states [PROPOSED]

```text
BattleState
  combatants: entity_id -> {hp, status, facing, position, ...}
  enemy_footprints: entity_id -> occupied_world_cells
  pad_instances: (enemy_id, pad_label) -> {world_anchor, occupants, ...}
  base_forms: world_cell_id -> {terrain, active_effects, expiry, provenance}
  encounter: {turn, initiative, rng_seed, sequence_id, ...}
  combo_proficiency: (participants, combo_id) -> qualification/progress

SpellDefinition
  id, element(s), caster_requirements
  targeting_policy, range
  impact_policy, propagation_policy
  direct_entity_effects, environment_effects
  elemental_reaction_conditions and overrides

CombatAction
  source_entity, action_id, selection
  target_entity? target_pad_instance? target_world_cell?
  trusted_authority_context [server issued, not client asserted]
```

This is pseudostructure, not a ZW schema. Actual ZW envelope and vocabulary must be derived from existing contracts.

## Event pipeline [PROPOSED]

1. Receive authenticated, AP-governed action request.
2. Resolve current world position, valid range, target cell or `(enemy,pad)`; preserve seed/roll log.
3. Resolve impact landing (may be randomized), check actual base-form environmental and contact chain states.
4. Select correct spell/reaction *before* applying normal triggering-spell effects; avoid double resolution.
5. Resolve action-specific graph traversal or AoE cells, and any elemental transform/fallback/stop behavior.
6. Determine affected entities by cell occupancy/footprint intersection, including permitted allies/objects, and apply surface/defense/status rules.
7. Update authoritative entity and base-form state atomically and persist expiry/chain provenance.
8. Emit event trail describing every hit, contact, chosen path, reaction, terrain conversion, interruption, fizzle and guard/obstruction resolution.
9. Presentation consumes events/snapshot and renders; it does not recalculate outcomes.

## Key invariants [PROPOSED]

- Pad label only unique within a platform **type**; use enemy instance identity.
- Environmental effects live at **world cells** and never automatically follow moving entities.
- Attack pads may follow enemy position; contact resolution re-evaluates overlapped world cells.
- Combo lock graph != Lightning local path graph != world-grid AoE geometry.
- Pad hops != distinct damaged entity hits.
- Randomizer chooses only valid outgoing routes; no backwards hop along a forbidden Lightning path.
- Existing attack effects are not repeated merely because a reaction was triggered at another pad.
- Damage direct/DoT/terrain/penetration tracked separately for balancing.
- A spell can affect unoccupied terrain; target needn't be an enemy.
- Replayable seed/roll log required for diagnosing nondeterministic chains.

## Counterexample test cases

- Three enemies each have pad `6`: no shared chain state or occupancy due to duplicate label.
- Earth primes one world base form; enemy moves; mud remains behind, no phantom movement of field.
- Lightning at `4` cannot jump locally straight to `6`; route through `5` or `7` if valid.
- Lightning at `7` with no outward enemy continues toward `6`, then fizzles if no onward eligible exit.
- Fire encounters Lightning and resolves Plasma without incorrectly applying full base Fire and full Plasma damage twice.
- Type 4 combo pair `8+13` plus `9` only meets *mastered* triple when learned.
- Two party characters on same pad remain able to try qualifying action but roll severe obstruction risk.
- AoE aimed at empty world cell changes terrain even if no enemy is struck.
