# EngAIn — Combat & Magic Design Archive

**Version:** 0.1 — conversation-derived design capture, 2026-10-19  
**Status:** DRAFT / PROVISIONAL, not an implemented or approved authority contract.  
**Purpose:** Preserve the author's decisions from the design discussion, recover original magic ideas, and make future implementation/auditing possible without redefining ZW, AP, or Combat3D.

## Contents

| File | Focus |
|---|---|
| `01_BATTLEFIELD_SPATIAL.md` | Four-character arena, platforms, base forms, entity footprints, facing and movement |
| `02_COMBO_LOCKS_PROGRESS.md` | Platform combo locks, dual/triple qualifications, mastery |
| `03_MAGIC_TARGETING_PROPAGATION.md` | Single, chain, AoE, Lightning routing, collision and spell state |
| `04_ELEMENTAL_RULES_AND_EXAMPLES.md` | Original recovered spell examples and provisional integration |
| `05_COMBAT_RUNTIME_CONTRACT.md` | Simulation ownership, effects, AP/ZW boundaries, event design and pseudocode |
| `06_TEST_CALIBRATION_PLAN.md` | Phased implementation and nonlethal combat measurement |
| `07_OPEN_DECISIONS_AND_PROVENANCE.md` | Unresolved ambiguities, preservation/source notes, decisions checklist |

## Evidence hierarchy

- **AUTHOR RULE** — explicitly established or corrected by the author in this conversation.
- **RECOVERED DOCUMENT** — content read from the author's Google Drive magic documents; *historical source*, not necessarily current canon.
- **DESIGN PROPOSAL** — suggested during discussion, useful but not author-approved.
- **OPEN** — conflicting, incomplete or still to be determined.

Don't promote proposals to canonical rules without author review. Do not mistake implementation suggestions for existing code.

## Scope and non-goals

- EngAIn remains **manuscript-agnostic** and **rendering-engine-agnostic**.
- ZW supplies semantic definitions, AP remains the authority boundary, Combat3D resolves actions, runtime snapshot owns authoritative simulation state, Godot or other clients present results.
- No hardcoded Burdens-specific names in universal runtime rules.
- This archive contains **design**, not an assertion that Combat3D currently implements magic, platforms, status effects, or combo progression.
- Preserve original lore documents; no destructive moves, canon rewrites or code changes were made.

## Prior art and source references

Author's Google Drive documents examined in conversation:
- [Single chains](https://docs.google.com/document/d/1J75TY9TbLd-G1AMM33inEnTAhofJD-t8_bCOWpgDy5c/edit)
- [Triple chains.txt](https://drive.google.com/file/d/1DpZvKPowTtZGFn7OjRvmqVTr3FXl2nrc/view)
- [Earth chain.txt](https://drive.google.com/file/d/1T7zFnJeQxa08cDbw0mrU3QOSvI228lYR/view)
- [Water chain.txt](https://drive.google.com/file/d/1JoBoE1Ok38j9uscvuKjjbijRG1iqSPep/view)
- [Fire chain.txt](https://drive.google.com/file/d/1rCdJa07KvQGgeYgfMxpkL1U8WA5k_bJe/view)

Also author-described local files under `building_the_world/`: `vale magic.txt`, `magic tree.txt`, `magic tree 2.txt`, character-specific magic files, `character effects.txt`. Their contents were **not comprehensively audited** in this session.

Original drawings and screenshots were supplied in conversation. The labels in text below are a working transcription; use the original images to confirm the exact orientation and routing before encoding geometry.
