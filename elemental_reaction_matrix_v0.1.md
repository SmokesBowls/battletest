# Elemental Reaction Matrix v0.1 — Two-Hit Cells

**Status:** working matrix. Only cells marked AUTHOR-CONFIRMED are canon. No damage values, durations or battlefield geometry; those live in the spec.

## Notation

Every cell is written **First → Second** in time order. "Water → Fire" means Water landed first, then Fire hit the wet target. No "X on Y" arrows.

## Classification

| Class | Meaning |
|---|---|
| AUTHOR-CONFIRMED | Author established this reaction for this order |
| SOURCE-RECOVERED | An original magic document defines it; not necessarily ratified |
| PHYSICS-PROPOSED | Follows the reasoned physics model (Drafts 1/2); unapproved |
| CONFLICT | Proposal contradicts an author rule, a source, or another draft |

**Terminal** is tracked separately from the reaction:
`confirmed` = author confirmed this cell ends the chain · `candidate` = the result is one of the seven ratified terminal states (Char, Ash, Grounding, Shatter, Stasis, Banish, Cleansing) but this pairing is unconfirmed · `open` = not decided.

~~Author rule for all chains: the third hit always ends the chain.~~ **Superseded 2026-10-22:** no fixed hit limit (a configurable cap stays disabled); repeating the same element consecutively ends the chain. A resulting field (e.g. Lava Field) may persist; any later interaction with it is a new chain, if authorized.

**Moon cells** carry *Moon pending*: Moon = "local shadow of self", expression governed by Keen's Queen/Maiden state, character attributes and planetary conditions. Gravity/tide readings come from older sources and are not settled.

## Evidence keys

- **[A]** author decision, this design session (2026-10-20)
- **[S03] / [S04]** `ENGAIN_COMBAT_MAGIC_SPEC_v0.1/03_…` / `04_…`
- **[fire] [water] [earth] [lightning] [shadow]** element files, "vs X" sections. **Order unspecified** (see finding 1)
- **[gpt#n]** `gptelements.txt` combination n, which **states order explicitly**
- **[D1] / [D2]** physics drafts 1 and 2 (proposals)

## Source-order finding

1. **The element files are not directional.** If "Fire vs Water" meant "Fire hits a wet target", `fire.txt` would say Water → Fire = Steam and Lightning → Fire = Plasma, contradicting both author rules. `water.txt` and `lightning.txt` would fit. Treat every "vs" entry as an unordered pair.
2. **`gptelements.txt` #1 contradicts the author:** "Water first, followed by Fire: Steam". Author rule: Water → Fire = Boil. Author wins; the source entry is recorded as superseded, not deleted.
3. **No Ice, Moon or Spirit element file exists in this export.** `shadow.txt` ends "continue with Spirit next?". Those rows rely on other elements' "vs" entries only.
4. **Draft 1 places Grounding in the wrong order.** [S03] author rule: Lightning arriving on Earth-primed contact grounds, so Earth → Lightning = Grounding. Draft 1 gave Earth → Lightning = Fulgurite and Lightning → Earth = Grounding.

---

## Earth first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Earth → Earth | Quake | PHYSICS-PROPOSED | open | [D1]. Whether a same-element repeat is a reaction at all is OPEN |
| Earth → Water | Mudstorm | AUTHOR-CONFIRMED | open | [S04 §4] recovered + author resolution rule. Drafts call it "Mud" |
| Earth → Fire | Magma *vs* Baked | CONFLICT | open | [fire] [earth]: Magma. [D2]: Baked/Hardened |
| Earth → Ice | Crystal Explosion *vs* Permafrost | CONFLICT | open | [gpt#3] ordered: Earth then Ice = Crystal Explosion. [earth]: crystal, brittle. [D1/D2]: Permafrost |
| Earth → Lightning | Grounding | AUTHOR-CONFIRMED | candidate | [S03] "Earth grounds/stops" Lightning path. Stopping the path ≠ ending the chain; confirm. [D1] Fulgurite conflicts |
| Earth → Moon | Landslide / Gravity crush | PHYSICS-PROPOSED | open | [earth]: Gravity crush. [D1]. *Moon pending* |
| Earth → Shadow | Burial / Grave Soil | CONFLICT | open | [earth] [shadow]: hide/concealment. [D1/D2]: shackle or blind+slow |
| Earth → Spirit | Grave *vs* Consecrated | CONFLICT | open | [earth]: Spirit stone, block field. [D1] Grave, [D2] Consecrated; drafts disagree |

## Water first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Water → Earth | Mud | SOURCE-RECOVERED | open | [water] [earth] unordered. May equal Earth → Water if author agrees; evaluate independently |
| Water → Water | Flood | PHYSICS-PROPOSED | open | [D1] |
| Water → Fire | Boil / Scald | AUTHOR-CONFIRMED | open | [A] fire cannot put the water out. Supersedes [gpt#1] Steam. Recovered name "Steamforged Tempest" [S04 §10] |
| Water → Ice | Freeze / Ice Lock | SOURCE-RECOVERED | open | [water]: freeze chance, slick surface. Name Ice Lock is [D1] |
| Water → Lightning | Aqua Lightning (conductive) | SOURCE-RECOVERED | open | [S04 §7], [S03]: Water lets Lightning continue (author rule on propagation) |
| Water → Moon | High Tide / Tidal boost | SOURCE-RECOVERED | open | [water]: tidal boost, low gravity. *Moon pending* |
| Water → Shadow | Murk | CONFLICT | open | [water]: reveal hidden. [shadow]: dark tide, blind. Sources disagree |
| Water → Spirit | Cleansing (Purify) | SOURCE-RECOVERED | candidate | [water]: purify + heal. See Cleansing rule below |

## Fire first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Fire → Earth | Ash *vs* Magma | CONFLICT | candidate | [fire] [earth]: Magma. [D1/D2]: Ash (ratified terminal name, pairing unconfirmed) |
| Fire → Water | Steam | AUTHOR-CONFIRMED | open | [A] water puts the fire out; burn DoT negated, steam remains. Agrees with [water] |
| Fire → Fire | Conflagration | PHYSICS-PROPOSED | open | [D1] |
| Fire → Ice | Quench → Steam | PHYSICS-PROPOSED | open | [fire]: Melt / Thermal shock (unordered) |
| Fire → Lightning | Plasma (Blazing Plasma) | AUTHOR-CONFIRMED | open | [A], [S03], [gpt#2] ordered. Onward propagation OPEN [S03] |
| Fire → Moon | Solar flare / Solar Eclipse *vs* Pale Flame | CONFLICT | open | [fire]: Solar empowerment/flare/eclipse; Thang's Solar Eclipse is Fire + Moon. [D1]: Pale Flame. Solar isn't an element yet [A]. *Moon pending* |
| Fire → Shadow | Smoke | CONFLICT | open | [shadow]: smoke screen. [fire]: reveal. Sources disagree |
| Fire → Spirit | Soul fire | SOURCE-RECOVERED | open | [fire]: Spirit flame / Soul fire / Phoenix flame |

## Lightning first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Lightning → Earth | Grounding | PHYSICS-PROPOSED | candidate | [D1]. [S03] covers only Earth → Lightning |
| Lightning → Water | Shock | PHYSICS-PROPOSED | open | [S04 §7]: reverse order "not separately authored"; Aqua Lightning used as fallback for one instance only |
| Lightning → Fire | Char | AUTHOR-CONFIRMED | confirmed | [A]. [fire] Plasma superseded; [S04 §8] "Lightning + Fire" label superseded |
| Lightning → Ice | Superconduct *vs* Shatter | CONFLICT | open | [lightning]: shatter chance. [D1/D2]: Superconduct |
| Lightning → Lightning | Overload | PHYSICS-PROPOSED | open | [D1] |
| Lightning → Moon | Storm call *vs* Static Tide | CONFLICT | open | [lightning]: Storm call / Lightning eclipse. [D1]: Static Tide. *Moon pending* |
| Lightning → Shadow | Umbral Arc | CONFLICT | open | [lightning]: reveal. [shadow]: Storm shadow, phase shift |
| Lightning → Spirit | Energy Overload | CONFLICT | open | Name belongs to recovered triple Lightning + Earth + Spirit [S04 §9]. [lightning]: Spirit shock, paralyze |

## Ice first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Ice → Earth | Shatter | SOURCE-RECOVERED | candidate | [earth]: brittle, shatter field |
| Ice → Water | Ice Lock | SOURCE-RECOVERED | open | [water]: freeze chance, slick |
| Ice → Fire | Melt → Steam | SOURCE-RECOVERED | open | [fire]: Melt, removes ice effects |
| Ice → Lightning | Superconduct *vs* Shatter | CONFLICT | open | [lightning]: shatter chance. [D1/D2]: Superconduct |
| Ice → Ice | Deep Freeze | PHYSICS-PROPOSED | open | [D1] |
| Ice → Moon | Frost Moon | PHYSICS-PROPOSED | open | [D1]. *Moon pending* |
| Ice → Shadow | Black Ice | CONFLICT | open | [shadow]: Frozen shadow, caster movement buff. [D1]: blind + slip |
| Ice → Spirit | Stasis | PHYSICS-PROPOSED | candidate | [D1]. No source |

## Moon first (all *Moon pending*)

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Moon → Earth | Landslide / Gravity crush | PHYSICS-PROPOSED | open | [earth] gravity crush (unordered). [D1] |
| Moon → Water | High Tide | SOURCE-RECOVERED | open | [water]: tidal boost, low gravity |
| Moon → Fire | Moonburn *vs* Solar | CONFLICT | open | [fire]: Solar names. [D1]: Moonburn |
| Moon → Lightning | Static Moon *vs* Storm call | CONFLICT | open | [lightning]: Storm call. [D1]: Static Moon |
| Moon → Ice | Frost Moon | PHYSICS-PROPOSED | open | [D1] |
| Moon → Moon | Full Moon | PHYSICS-PROPOSED | open | [D1] |
| Moon → Shadow | Eclipse | SOURCE-RECOVERED | open | [shadow]: Eclipse strike. Name recovered; effect OPEN. [A]: Moon and Shadow don't inherently cancel. [D2]'s "light and dark cancel" rationale conflicts |
| Moon → Spirit | Lucid Dream | PHYSICS-PROPOSED | open | [D1]. Reverse order has a source (see Spirit → Moon) |

## Shadow first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Shadow → Earth | Burial | CONFLICT | open | [shadow] [earth]: hide/concealment. [D1]: shackle |
| Shadow → Water | Murk | CONFLICT | open | [shadow]: blind. [water]: reveal |
| Shadow → Fire | Shadowflame *vs* Reveal | CONFLICT | open | [fire]: light burst reveals. [shadow]: smoke screen. Fire dispelling darkness fits this order physically; author call |
| Shadow → Lightning | Shadow Storm | SOURCE-RECOVERED | open | [gpt#5] ordered: Shadow then Lightning. [D1] name Umbral Arc superseded. [lightning]: reveal conflicts |
| Shadow → Ice | Black Ice | CONFLICT | open | [shadow]: Frozen shadow, movement buff |
| Shadow → Moon | Eclipse | SOURCE-RECOVERED | open | [shadow]: Eclipse strike. Effect OPEN [A] |
| Shadow → Shadow | Deep Gloom / Mute | PHYSICS-PROPOSED | open | [D1] |
| Shadow → Spirit | Banish *vs* Haunt | CONFLICT | candidate | [D1] matrix Banish; [D1] chain H and [D2] chain 6 Haunt. [shadow]: Spirit drain, dark heal |

## Spirit first

| First → Second | Reaction | Class | Terminal | Evidence / note |
|---|---|---|---|---|
| Spirit → Earth | Grave *vs* Consecrated | CONFLICT | open | [earth]: Spirit stone, block field. Drafts disagree |
| Spirit → Water | Cleansing | SOURCE-RECOVERED | candidate | [water]: purify + heal (unordered) |
| Spirit → Fire | Soulfire | SOURCE-RECOVERED | open | [fire]: Soul fire |
| Spirit → Lightning | Energy Overload | CONFLICT | open | Triple name collision [S04 §9]. [lightning]: Spirit shock / Spirit charge |
| Spirit → Ice | Stasis | PHYSICS-PROPOSED | candidate | [D1]. No source |
| Spirit → Moon | Ethereal Form | SOURCE-RECOVERED | open | [gpt#4] ordered: Spirit then Moon. [D1] Lucid Dream superseded. *Moon pending* |
| Spirit → Shadow | Possession *vs* Spirit drain | CONFLICT | open | [shadow]: Spirit drain, dark heal. [D1]: Possession |
| Spirit → Spirit | Spirit Amp | PHYSICS-PROPOSED | open | [D1] |

---

## Cleansing rule (author, Option A)

Cleansing is allegiance-neutral physics: it removes applicable conditions from whoever receives it, so cleansing an enemy can remove their Burning. **Healing is a separate operation.** It goes only to the recipients the spell's own rules make eligible. Recovered Cleansing Flood [S04 §9] says "heal **allies** 25%". `water.txt`'s Purify + Heal names no recipient: OPEN.

## Tally

| Class | Cells |
|---|---|
| AUTHOR-CONFIRMED | 6 |
| SOURCE-RECOVERED | 16 |
| PHYSICS-PROPOSED | 18 |
| CONFLICT | 24 |
