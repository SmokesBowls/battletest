Technical Implementation Analysis of EngAIn Combat & Magic Specification v0.1
Platform Geometry and Hierarchical Spatial Topology
Architectural Triad and Composite Addressing Schema
The spatial execution environment within the EngAIn platform decouples combat positioning into three discrete structural layers: static environmental base-form grid cells, dynamic enemy entity footprints, and configuration-local landing pad templates. Base-form grid cells represent static, uniformly scaled partitions anchored to absolute world coordinates (X_w, Y_w, Z_w). These cells maintain persistent physical and elemental surface states such as mud, lava, and electrical conductivity entirely independent of entity occupancy.
Dynamic enemy entity footprints define the continuous spatial volume or oriented bounding area occupied by an enemy's physical presence, potentially spanning multiple underlying base-form cells and translating continuously across the global field. Configuration-local landing pad templates comprise discrete tactical anchor sites defined relative to the enemy's local origin. These pads serve as physical landing positions for player combatants following melee actions, contact vectors for targeted magic, and topological vertices for platform combination locks and directed Lightning routing.
Landing pad identifiers are configuration-local labels reused across distinct enemy instances sharing an authored layout archetype. Because platform labels are not globally unique primary keys, referring to a landing pad solely by an integer introduces spatial ambiguity whenever multiple enemies of identical configuration coexist. The authoritative runtime snapshot enforces absolute entity disambiguation through a composite address tuple:
\text{PadAddress} = \langle \text{BattleInstanceID}, \text{EnemyInstanceID}, \text{PlatformLabel} \rangle
Through this addressing contract, a label such as platform six on a Type 3 enemy resolves to a unique, fully qualified memory record, completely isolating it from platform six on an adjacent entity.
struct WorldCoordinate { float64 x; float64 y; float64 z; };
struct CellIndex { int32 x; int32 y; };
struct PadAddress { uint64 battle_instance_id; uint64 enemy_instance_id; uint8 platform_label; };
struct PlatformInstance { PadAddress address; WorldCoordinate local_offset; WorldCoordinate cached_world_pos; uint64 current_occupants[2]; uint8 occupant_count; };
Local-to-World Coordinate Translation and Post-Attack Guard Modifiers
Local platform offsets are transformed into authoritative world coordinates via affine matrix transformations synchronized with the enemy entity's world transform. Given an enemy position vector \mathbf{T}_{enemy} and yaw rotation angle \theta_{yaw}, the absolute world position \mathbf{P}_{world} of platform label L possessing authored local coordinate vector \mathbf{P}_{local}(L) is derived via standard planar rotation and translation:
\mathbf{P}_{world} = \mathbf{T}_{enemy} + \mathbf{R}_z(\theta_{yaw}) \mathbf{P}_{local}(L) \begin{bmatrix} X_w \\ Y_w \\ Z_w \end{bmatrix} = \begin{bmatrix} X_{enemy} \\ Y_{enemy} \\ Z_{enemy} \end{bmatrix} + \begin{bmatrix} \cos\theta_{yaw} & -\sin\theta_{yaw} & 0 \\ \sin\theta_{yaw} & \cos\theta_{yaw} & 0 \\ 0 & 0 & 1 \end{bmatrix} \begin{bmatrix} X_{local} \\ Y_{local} \\ Z_{local} \end{bmatrix}
Following the execution of an offensive action, a combatant must commit to one of two tactical postures: STAY or RETURN. Each posture executes distinct state machine transitions that govern the character's incoming guard coefficient G \in [0.0, 1.0]:
Under the STAY posture, the character remains stationed upon the enemy's landing pad. This posture grants an entity-specific guard bonus against attacks originating from the occupied enemy (\delta_{stay\_bonus}). However, attacks originating from external combatants striking the character's rear arc incur an exposure penalty (\delta_{rear\_penalty}). Frontal and lateral incoming strikes from external entities incur no directional guard modifier (\delta_{front} = 0):
G_{eff} = \begin{cases} G_{base} \cdot (1.0 + \delta_{stay\_bonus}) & \text{if attacker} = \text{OccupiedEnemy} \\ G_{base} \cdot (1.0 - \delta_{rear\_penalty}) & \text{if attacker} \neq \text{OccupiedEnemy} \land \vert{}\Delta\theta\vert{} > \frac{3\pi}{4} \\ G_{base} & \text{otherwise} \end{cases}
Under the RETURN posture, the combatant retreats to the party formation line. During active transit, the combatant turns their back to the engagement front, triggering a universal guard vulnerability window (\delta_{return\_vulnerability}) that persists until the character is fully restationed in formation:
G_{eff} = G_{base} \cdot (1.0 - \delta_{return\_vulnerability})
enum CombatantPosture { FORMATION, TRANSIT_TO_PAD, STAY, TRANSIT_TO_FORMATION };
struct GuardResolutionContext { CombatantPosture posture; uint64 occupied_enemy_id; float64 character_facing_yaw; float64 attack_vector_yaw; float64 base_guard; };
float64 ResolveEffectiveGuard(GuardResolutionContext ctx, uint64 attacker_id) { if (ctx.posture == STAY) { if (attacker_id == ctx.occupied_enemy_id) { return ctx.base_guard * (1.0 + STAY_BONUS_MODIFIER); } float64 angle_diff = NormalizeAngle(ctx.attack_vector_yaw - ctx.character_facing_yaw); if (Abs(angle_diff) > THREE_QUARTER_PI) { return ctx.base_guard * (1.0 - REAR_EXPOSURE_PENALTY); } return ctx.base_guard; } else if (ctx.posture == TRANSIT_TO_FORMATION) { return ctx.base_guard * (1.0 - RETURN_TRANSIT_PENALTY); } return ctx.base_guard; }
Canonical Boundary: Approved Rules Versus Unresolved Topology
The spatial implementation is bounded by strict canonical demarcations between ratified design rules and unresolved architectural decisions.
Feature Component
Specification Status
Author-Approved Rule
Unresolved Implementation Decision
Platform Allocation & Labels
Author-Approved
Exactly six enemy archetypes allocate thirty-one configuration-local labels (Type 1: 1; Type 2: 2–3; Type 3: 4–7; Type 4: 8–13; Type 5: 14–21; Type 6: 22–31).
Layout assignment per enemy tier is fixed; dynamic runtime resizing of platform counts is prohibited.
Platform Identifiers
Author-Approved
Labels are configuration-local; identical integer labels coexist across distinct enemy instances.
Addressing must strictly use composite keys; global primary-key integer indexing is rejected.
Layout Coordinates & Facing
Open / Unresolved
Author diagrams govern relative connectivity sequences.
Authoritative 3D Cartesian coordinates (X, Y, Z), local facing norms, and true anatomical front/rear vectors remain unassigned.
Type 6 Topologies
Open / Unresolved
Ten circumferential pads with lateral flank nodes designated as 24 and 29.
Exact geometric placement vectors relative to enemy directional forward remain unratified.
Penetration Scaling
Open / Unresolved
Values 100%, 60%, 20%, and 5% along with 90% for side pads are experimental baselines.
Mathematical coupling between entry vectors, armor mitigation, and penetration falloff is not locked.

Combo Qualification Engine, Platform Locks, and Obstruction
Dual and Triple Lock Topologies
Combo qualification is governed by platform locks, which evaluate whether combatants occupy authorized sets of relative landing pads on a shared enemy instance. Spatial proximity alone cannot satisfy combo criteria; explicit lock tags authored in Zero-World (ZW) definitions must match active runtime pad occupancy.
On Type 4 configurations, containing six pads labeled 8 through 13, authored dual locks are restricted to opposite and diagonal pairings \{8, 13\} and \{10, 11\}. On Type 5 configurations, containing eight pads labeled 14 through 21, dual locks expand to include perimeter and flank pairings \{14, 21\}, \{15, 16\}, \{17, 18\}, and \{19, 20\}. On Type 6 configurations, containing ten pads labeled 22 through 31, triple locks are authored as contiguous triplets along the lateral flanks. Candidate triples are \{23, 24, 25\} on the left flank and \{28, 29, 30\} on the right flank. Proposed dual pairings on Type 6, such as \{22, 31\}, \{26, 27\}, \{23, 24\}, \{24, 25\}, \{28, 29\}, and \{29, 30\}, remain unratified proposals.
struct ComboLockDefinition { uint32 lock_id; uint8 enemy_type; uint8 required_pad_count; uint8 platform_labels[3]; bool is_triple_lock; };
const ComboLockDefinition TYPE_4_LOCKS[2] = { { 401, 4, 2, {8, 13, 0}, false }, { 402, 4, 2, {10, 11, 0}, false } };
const ComboLockDefinition TYPE_5_LOCKS[4] = { { 501, 5, 2, {14, 21, 0}, false }, { 502, 5, 2, {15, 16, 0}, false }, { 503, 5, 2, {17, 18, 0}, false }, { 504, 5, 2, {19, 20, 0}, false } };
Mastered Triple Extension Graph Expansion
At baseline proficiency, triple combinations are restricted to dedicated authored three-pad configurations. Upon unlocking triple combo mastery, the qualification engine executes dynamic graph expansion, allowing an authorized dual lock to bind an eligible third platform on smaller topologies. The runtime engine validates that two characters satisfy a base dual lock \{p_a, p_b\} \in \mathcal{L}_{dual}. It then evaluates the candidate third combatant's occupied pad p_c against the topological extension matrix \mathcal{E}(E_{type}, \{p_a, p_b\}). For Type 4 enemies, authorized master extensions expand as follows:
\{8, 13\} \cup \{9\} \implies \{8, 13, 9\} \{8, 13\} \cup \{12\} \implies \{8, 13, 12\} \{10, 11\} \cup \{9\} \implies \{10, 11, 9\} \{10, 11\} \cup \{12\} \implies \{10, 11, 12\}
If p_c \in \mathcal{E}(E_{type}, \{p_a, p_b\}) and character mastery tags satisfy skill validation, the action is promoted to an active triple combination.
bool QualifiesMasteredTriple( uint8 enemy_type, uint8 p1, uint8 p2, uint8 p3, bool has_triple_mastery ) { if (!has_triple_mastery) return false;
if (enemy_type == 4) { bool is_8_13 = (p1 == 8 && p2 == 13) |
| (p1 == 13 && p2 == 8); bool is_10_11 = (p1 == 10 && p2 == 11) |
| (p1 == 11 && p2 == 10);
if (is_8_13 |
| is_10_11) { return (p3 == 9 |
| p3 == 12); } } return false; }
Overcrowding and Obstruction Resolution
The simulation permits multiple friendly combatants to occupy a single landing pad simultaneously, up to an authoritative ceiling of two combatants per pad. Physical co-occupancy does not disqualify a combo attempt outright; instead, executing an action from an overcrowded platform incurs an obstruction failure check.
Let \mathcal{O}(p) represent the occupant count on platform p. The obstruction check evaluates across all platforms involved in the combo attempt:
P_{obstruction} = 1.0 - \prod_{p \in \mathcal{P}_{combo}} (1.0 - \psi(\mathcal{O}(p)))
Where the single-pad overcrowding penalty function is defined as:
\psi(n) = \begin{cases} 0.0 & \text{if } n \le 1 \\ \lambda_{fail\_rate} & \text{if } n > 1 \end{cases}
The failure coefficient \lambda_{fail\_rate} \in [0.75, 0.90] represents severe operational interference. When an obstruction check evaluates to true, the combo action fails, forfeiting allocated Action Points (AP), triggering an execution fumble state, and terminating resolution prior to damage calculation.
enum ComboExecutionResult { SUCCESS, DISQUALIFIED_TOPOLOGY, FAILED_OBSTRUCTION, FAILED_MASTERY_GATE };
ComboExecutionResult ResolveComboAttempt( PadAddress pads[], uint8 participant_count, float64 obstruction_seed_roll, float64 lambda_fail_rate ) { for (uint8 i = 0; i < participant_count; ++i) { if (GetPlatformOccupantCount(pads[i]) > 1) { if (obstruction_seed_roll < lambda_fail_rate) { return FAILED_OBSTRUCTION; } } } return SUCCESS; }
Decoupled Progression Architecture
The combo qualification engine enforces complete structural decoupling between physical combo proficiencies and elemental magic chain masteries. Physical combo progression tracks formation utilization, pair coordination frequency, and platform lock executions. This progression is partitioned into four distinct capability gates: base dual capability, duo coordination proficiency, dedicated triple unlock capability, and mastered triple extension capability.
Elemental chain progression is governed strictly by spellcasting volume, elemental tier proficiency, and reaction catalysis. A party may attain master-tier elemental chaining while remaining restricted to basic dual locks on physical platforms. The mathematical models governing experience acquisition curves, failure compensation points, and individual versus shared party progression vectors remain open decisions.
Directional Lightning Propagation and Traversal Graph
Directed Local-Pad Graphs and Spatial Jump Vectors
Lightning propagation does not evaluate radial proximity queries or traverse sequential numeric indices. Propagation resolves across an authored directed graph consisting of intra-entity pad-to-pad edges and inter-entity spatial jump vectors.
struct DirectedGraphEdge { uint8 target_pad_label; bool is_inter_entity_jump; float64 jump_distance_max; };
struct PlatformAdjacencyList { uint8 pad_label; uint8 exit_count; DirectedGraphEdge exits[3]; };
const PlatformAdjacencyList TYPE_3_GRAPH[4] = { { 4, 2, { {5, false, 0.0}, {7, false, 0.0} } }, { 5, 2, { {6, false, 0.0}, {0, true, 8.0} } }, { 7, 2, { {6, false, 0.0}, {0, true, 8.0} } }, { 6, 1, { {0, true, 8.0} } } };
Propagation obeys four topological rules: Path reversal is strictly prohibited; the traversal engine maintains a history of visited pads within the current chain, rejecting any edge targeting the immediate predecessor or bypassing intermediate topological nodes. When multiple non-reversing exits are valid, such as branching to pad 5 versus pad 7 from pad 4, the path is selected via deterministic pseudo-random roll. When an exit edge is flagged as an inter-entity vector, the simulation queries for enemy instances within maximum jump distance D_{max}.
Spatial alignment supersedes label ordering: destination pad labels can be numerically lower and non-consecutive, such as transitions 6 \to 2, 17 \to 31, or 18 \to 22 across distinct entity instances. If an edge cannot resolve a valid local continuation and no foreign enemy satisfies the spatial jump constraints, the bolt fizzles and propagation terminates. Pad 1 on a Type 1 enemy is topologically terminal upon initial impact.
uint8 SelectNextLightningHop( uint64 current_battle_id, uint64 current_enemy_id, uint8 current_pad_label, uint8 previous_pad_label, float64 prng_sample, bool *out_is_jump ) { PlatformAdjacencyList node = GetAdjacency(current_enemy_id, current_pad_label); uint8 valid_exits[3]; bool is_jump_exit[3]; uint8 valid_count = 0;
for (uint8 i = 0; i < node.exit_count; ++i) { DirectedGraphEdge edge = node.exits[i]; if (!edge.is_inter_entity_jump && edge.target_pad_label == previous_pad_label) { continue; } valid_exits[valid_count] = edge.target_pad_label; is_jump_exit[valid_count] = edge.is_inter_entity_jump; valid_count++; }
if (valid_count == 0) return 0;
uint8 selected_idx = (uint8)(prng_sample * valid_count) % valid_count; *out_is_jump = is_jump_exit[selected_idx]; return valid_exits[selected_idx]; }
Reconciling Local Pad Contacts with Distinct Entity Damage Budgets
A structural conflict exists between the historical spell description of Thunder's Wrath and the topological pad routing model. Thunder's Wrath explicitly states that baseline Lightning chains to exactly one additional nearby target for 50\% base damage. Conversely, topological routing dictates that a single cast striking a Type 4 or Type 5 enemy traverses multiple local pads (e.g., 14 \to 15 \to 16 \to 17) on the same entity to reach elemental primes or exit vectors.
The simulation resolves this conflict by separating traversal into distinct operational budgets:
\text{TraversalState} = \langle \text{PadContactBudget}, \text{EntityDamageBudget}, \text{VisitedEntitiesSet} \rangle
The \text{PadContactBudget} decrements on every intra-entity directed edge traversal, governing visual continuity, elemental prime interaction, and pad occupancy checks. The \text{EntityDamageBudget} decrements strictly when a distinct enemy instance receives an initial damage packet. For baseline Thunder's Wrath, \text{EntityDamageBudget} = 2 (one primary target plus one secondary target). Intra-entity pad hops on the primary entity consume \text{PadContactBudget} but do not deplete \text{EntityDamageBudget}, nor do they reapply base damage to the primary entity unless an authored multi-strike reaction explicitly authorizes restriking.
Elemental Reaction State Machine and Interception Pipeline
Reaction Matrix and Interaction Taxonomy
The simulation executes a pre-damage lifecycle hook whenever an elemental spell impacts a pad or world cell. If an elemental prime exists at the contact site, the incoming spell is intercepted, suppressing or modifying its base effects to execute a compound reaction.
Incoming Element
Contact Prime State
Resultant Reaction
Primary Outcome & Terrain Modification
Propagation Trajectory
Water
Earth
Mudstorm
Direct DoT (10\% Earth base for 3 turns); enemy move -30\%; spawns Mudfields on world base forms (+15\% Earth damage, -10\% evasion).
Replaces Tidal Surge base damage; terminates standard Water splash.
Fire
Earth + Water (Mudstorm)
Volcanic Eruption
High AoE (150\% Earth base); Burning DoT (10\% for 3 turns); spawns Lava Field on base forms (+15\% Fire/Earth damage for 3 turns).
Terminating triple resolution; suppresses standard Fire base packet.
Lightning
Water
Aqua Lightning
High AoE (125\% Lightning base); chains to 2 additional targets; spawns Conductive Zone (+25\% Lightning damage for 2 turns).
Continues propagation; author-approved non-termination rule.
Lightning
Earth
Grounding
Spell grounding interaction; dissipates electrical potential into earth terrain.
Terminates propagation immediately; path fizzles.
Lightning
Fire
Blazing Plasma
High AoE (150\% Lightning base); Burning DoT (10\% Fire for 2 turns); spawns Plasma Field (-15\% enemy armor for 3 turns).
Reaction executes; onward routing remains an open decision.
Lightning
Valid Double Chain
Triple Reaction
High-tier compound damage and status payload.
Terminates incoming Lightning traversal while resolving triple effect.

Elemental reactions govern graph execution flow across five behaviors: Grounding completely dissipates remaining path budgets, forcing graph termination. Amplification modifies damage coefficients without altering graph trajectories, such as Lightning traversing a Conductive Zone. Branching expands the traversal topology, as seen in Aqua Lightning generating secondary targets upon water contact. Transformation alters gameplay tags, elemental typings, and visual archetypes, such as Fire and Lightning compounding into Blazing Plasma. Triple Termination stops incoming Lightning paths upon striking a prepared double chain, transferring execution authority to the autonomous triple AoE spell.
Pre-Damage Execution Interception Pipeline
To prevent double-spending anomalies—wherein a cast inflicts full standalone spell damage and subsequently triggers full combo damage—the engine executes an atomic pre-damage interception pipeline:
struct ContactSiteState { uint8 active_element_primes; uint8 chain_tier; uint32 terrain_effect_id; };
struct DamageResolutionPacket { float64 direct_hp_delta; uint32 status_effect_id; float64 status_duration; uint32 spawn_terrain_id; bool suppress_base_damage; bool terminate_propagation; };
DamageResolutionPacket InterceptSpellContact( SpellDefinition incoming_spell, ContactSiteState *site_state ) { DamageResolutionPacket packet = {0};
if (incoming_spell.element == ELEMENT_WATER && (site_state->active_element_primes & ELEMENT_EARTH_BIT)) { packet.direct_hp_delta = 0.0; packet.status_effect_id = STATUS_MUDSTORM_DOT; packet.status_duration = 3.0; packet.spawn_terrain_id = TERRAIN_MUDFIELD; packet.suppress_base_damage = true; packet.terminate_propagation = true;
site_state->active_element_primes |= ELEMENT_WATER_BIT; site_state->chain_tier = 2; return packet; }
if (incoming_spell.element == ELEMENT_FIRE && site_state->chain_tier == 2 && (site_state->active_element_primes & (ELEMENT_EARTH_BIT | ELEMENT_WATER_BIT))) { packet.direct_hp_delta = incoming_spell.base_potency * 1.50; packet.status_effect_id = STATUS_BURNING_DOT; packet.status_duration = 3.0; packet.spawn_terrain_id = TERRAIN_LAVA_FIELD; packet.suppress_base_damage = true; packet.terminate_propagation = true;
site_state->active_element_primes = 0; site_state->chain_tier = 0; return packet; }
if (incoming_spell.element == ELEMENT_LIGHTNING && (site_state->active_element_primes & ELEMENT_WATER_BIT)) { packet.direct_hp_delta = incoming_spell.base_potency * 1.25; packet.spawn_terrain_id = TERRAIN_CONDUCTIVE_ZONE; packet.suppress_base_damage = true; packet.terminate_propagation = false; return packet; }
packet.direct_hp_delta = incoming_spell.base_potency; packet.suppress_base_damage = false; packet.terminate_propagation = false; return packet; }
Open Semantic Decisions: Stacking, Decay, and Commutativity
Three elemental execution policies remain open decisions: Status debuff collision resolution requires explicit authorial specification. Ground Tremor inflicts movement -20\%, whereas Mudstorm inflicts movement -30\%. The author established that direct enemy debuffs must not duplicate base-form terrain penalties, but interaction between the two independent movement debuffs remains unspecified (candidate policies include max-suppression \max(20\%, 30\%), additive stacking to -50\%, or priority replacement).
The lifecycle of an elemental prime following reaction resolution is similarly open. It must be established whether triggering Mudstorm completely consumes the underlying Earth prime or leaves an Earth+Water composite prime capable of immediate promotion to Volcanic Eruption within the same turn cycle.
Finally, universal element commutativity is explicitly rejected: historical documents distinguish Fire + Water (Steamforged Blast) from Water + Fire (Steamforged Tempest). Order of application defines identity, requiring explicit authoring for every permutation.
Persistent Terrain Mechanics and World-Grid Decoupling
Base-Form Environmental Grid Data Contract
Persistent terrain effects exist exclusively within the static base-form world grid, fully decoupled from mobile enemy footprints and landing pads.
struct BaseFormCell { CellIndex grid_index; WorldCoordinate world_bounds_min; WorldCoordinate world_bounds_max; uint32 active_terrain_type; uint8 remaining_turns; uint64 source_entity_id; };
struct WorldGridState { int32 grid_width; int32 grid_height; float64 cell_size; BaseFormCell cells[MAX_CELLS]; };
Dynamic Spatial Overlap Queries
When an enemy translates across the battlefield, its configuration-local landing pads update their world coordinates. Persistent environmental modifiers, such as Mudfields granting +15\% Earth damage and -10\% evasion, do not follow the translating enemy. When an attack targets an enemy landing pad \text{PadAddress} = \langle B, E, L \rangle, the runtime executes a point-in-cell query to resolve the underlying base-form cell C:
X_{cell} = \left\lfloor \frac{X_w(\text{PadAddress})}{\text{CellSize}} \right\rfloor, \quad Y_{cell} = \left\lfloor \frac{Y_w(\text{PadAddress})}{\text{CellSize}} \right\rfloor
BaseFormCell* ResolvePadTerrainOverlap(WorldGridState *grid, PadAddress pad) { WorldCoordinate world_pos = GetPadWorldPosition(pad); int32 cell_x = (int32)floor(world_pos.x / grid->cell_size); int32 cell_y = (int32)floor(world_pos.y / grid->cell_size);
if (cell_x < 0 |
| cell_x >= grid->grid_width | | cell_y < 0 | | cell_y >= grid->grid_height) { return NULL; }
return &grid->cells[cell_y * grid->grid_width + cell_x]; }
If an enemy vacates a Mudfield-covered cell, subsequent attacks landing on its relocated pads receive no environmental Earth damage bonus. Conversely, any secondary combatant entering the vacated cell immediately inherits the evasion penalty.
Lifecycle Management: Decay and Non-Portability
Base-form cell lifetimes are governed by turn-cycle counters decremented during encounter phase maintenance. When remaining_turns reaches zero, the terrain state reverts to default. Higher-tier elemental reactions targeting an active cell can overwrite or consume the active terrain state.
The debuff non-portability contract guarantees that direct entity statuses follow combatants across the field, whereas spatial debuffs remain bound to world cells. Moving an entity never migrates base-form cell state pointers into entity state components.
Area-of-Effect Targeting and Collision Resolution
Mathematical Footprint Generators
Area-of-effect spells target world-grid coordinates within caster range, completely independent of the enemy landing pad network. Spells evaluate footprints on the horizontal plane (X_w, Y_w) across four geometric families.
enum AoEGeometryFamily { AOE_RADIAL, AOE_LINE, AOE_FORK_3, AOE_CROSS_4 };
struct AoEParameters { AoEGeometryFamily family; WorldCoordinate target_origin; float64 orientation_yaw; float64 radius; float64 length; float64 width; };
The Radial footprint evaluates all cells whose center points fall within Euclidean radius R of the target coordinate \mathbf{C}_{target} = (X_0, Y_0):
\text{Contains}_{radial}(\mathbf{P}) \iff (X - X_0)^2 + (Y - Y_0)^2 \le R^2
The Line footprint projects a directed bounding box of length L and width W along yaw orientation \theta:
\begin{bmatrix} X' \\ Y' \end{bmatrix} = \begin{bmatrix} \cos\theta & \sin\theta \\ -\sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} X - X_0 \\ Y - Y_0 \end{bmatrix} \text{Contains}_{line}(\mathbf{P}) \iff 0 \le X' \le L \land \vert{}Y'\vert{} \le \frac{W}{2}
The Fork footprint projects a central line along angle \theta flanked by two divergent rays oriented at \theta \pm \Delta\theta_{fork}:
\text{Contains}_{fork}(\mathbf{P}) \iff \text{Contains}_{line}(\mathbf{P}, \theta) \lor \text{Contains}_{line}(\mathbf{P}, \theta + \Delta\theta) \lor \text{Contains}_{line}(\mathbf{P}, \theta - \Delta\theta)
The Cross-4 footprint evaluates center cell (X_c, Y_c) and its cardinal orthogonal neighbors within cell distance K:
\text{Contains}_{cross}(\mathbf{P}) \iff \vert{}X_{cell} - X_c\vert{} + \vert{}Y_{cell} - Y_c\vert{} \le K \land (X_{cell} = X_c \lor Y_{cell} = Y_c)
Multi-Cell Footprint Intersection and Friendly Fire Resolution
Entity physical volumes are modeled as 2D oriented bounding boxes (OBB) overlapping the world grid. An entity is intercepted by an AoE spell if the intersection between the spell footprint \mathcal{F}_{AoE} and the entity footprint \mathcal{B}_{entity} is non-empty:
\text{IsHit}(Entity) \iff \mathcal{F}_{AoE} \cap \mathcal{B}_{entity} \neq \emptyset
bool EvaluateAoEIntersection(AoEParameters aoe, BoundingBox2D entity_bb) { if (!BroadphaseOverlap(aoe, entity_bb)) return false;
WorldCoordinate corners[4]; GetBoxCorners(entity_bb, corners); for (int i = 0; i < 4; ++i) { if (PointInAoE(aoe, corners[i])) return true; }
WorldCoordinate center = GetBoxCenter(entity_bb); return PointInAoE(aoe, center); }
Line and Fork projections evaluate grid cells sequentially along their vectors. If an intermediate cell contains an obstacle flagged with BLOCKS_MAGIC_LINE, subsequent cells along that trajectory are occluded. Spells encode explicit friendly-fire policies: HOSTILE_ONLY, ALL_COMBATANTS, or ALLIES_EXCLUDED. Under ALL_COMBATANTS spells, such as Volcanic Eruption, party members occupying landing pads within the computed base-form footprint are subject to damage resolution.
Simulation Loop, AP Authorization Boundaries, and Deterministic Replay
Architectural Authority Boundaries and Transaction Pipeline
The EngAIn architecture enforces absolute separation between semantic definitions, authorization boundaries, authoritative simulation state, and presentation clients.
Architectural Layer
Core Responsibility
Ingress Interface
Egress Interface
Authority Guarantee
Presentation Client (Godot / Dragon)
Renders visuals, animations, audio, and UI.
Authoritative Snapshot & Read-Only Event Log.
Combat Action Requests.
Zero authority; cannot calculate damage or alter simulation state.
AP Authorization Gateway
Validates turn tokens, action point budgets, and range.
Combat Action Requests from Client.
Validated Action Intent to Simulation Kernel.
Authority gatekeeper; rejects unauthorized client intents.
Zero-World (ZW) Semantics
Stores static spell schemas, topologies, and lock rules.
Static System Initialization.
Read-only schema queries from Kernel.
Canonical rule authority; agnostic of narrative lore.
Combat3D Simulation Kernel
Executes spatial math, graph routing, and damage pipelines.
Validated Action Intents.
Atomic Snapshot Mutations & Event Stream.
Sole mutable simulation authority.
Authoritative Runtime Snapshot
Single authoritative memory store for battle state.
Atomic mutations from Kernel.
State serialization and event emission.
Single source of truth for all combatant and terrain data.

The transaction pipeline follows a strict execution sequence:
The presentation client submits an unauthenticated action request.
The AP gateway validates actor turn tokens, action point reserves, and geometric range.
The Combat3D kernel queries ZW definitions to resolve targeting, contact sites, and reaction rules.
The kernel evaluates pre-damage interception, suppresses or applies base damage, and resolves graph traversal.
The authoritative runtime snapshot is mutated atomically.
A read-only event stream is emitted to presentation clients for rendering.
struct CombatantState { uint64 entity_id; uint32 current_hp; uint32 max_hp; uint16 current_ap; uint8 posture; PadAddress current_pad; float64 facing_yaw; uint32 active_statuses[8]; };
struct SnapshotHeader { uint64 battle_id; uint32 frame_tick; uint32 turn_index; uint64 prng_state; uint32 combatant_count; uint32 active_terrain_count; };
struct AuthoritativeCombatSnapshot { SnapshotHeader header; CombatantState combatants[MAX_COMBATANTS]; BaseFormCell active_terrains[MAX_CELLS]; };
Deterministic Replay and PRNG Tracking Contract
Bit-identical execution replay requires complete PRNG isolation. The kernel utilizes a 64-bit generator embedded within the snapshot header. No simulation system may query unseeded host system time or non-deterministic math libraries. Every stochastic event—landing pad randomization, Lightning branch selection, and obstruction checks—logs its state to an authoritative roll log:
struct PRNGRollRecord { uint32 step_index; uint64 seed_prior; float64 generated_value; uint8 subsystem_tag; };
float64 StepDeterministicRoll(AuthoritativeCombatSnapshot *snapshot, uint8 subsystem_tag) { uint64 z = (snapshot->header.prng_state += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; uint64 result = z ^ (z >> 31);
float64 normalized = (double)(result >> 11) * (1.0 / 9007199254740992.0);
LogRollRecord(snapshot->header.frame_tick, snapshot->header.prng_state, normalized, subsystem_tag); return normalized; }
Combat Calibration Harness and Verification Test Suite
Dual-Mode Calibration Architecture
To establish empirical enemy health metrics without artificially suppressing authored spell potencies, the calibration harness establishes two operational modes utilizing nonlethal target dampeners. Enemies track cumulative virtual damage without triggering death transitions, providing unclipped damage datasets across multi-turn windows.
Harness Dimension
Offensive Ceiling Mode (OCM)
Realistic Combat Mode (RCM)
Enemy AI State
Inert; counterattacks and movement disabled.
Active; executes counterattacks, displacement, and staggers.
Player Action Budget
100\% allocated to offensive throughput.
Diluted by healing, guarding, and repositioning.
Elemental Chains
Perfect uninterrupted execution sequences.
Windows disrupted by enemy staggers and turn shifts.
Obstruction Checks
Isolated mathematical failure frequencies.
Compounded by tactical positioning pressure.
Measurement Focus
Maximum theoretical output (D_{ceil}) over N rounds.
Realized damage distribution (D_{real}) and party survival.

Empirical HP Derivation Formulation
Target enemy health pools (HP_{target}) are derived from cumulative damage distributions generated via Monte Carlo sweeps across random seeds under Realistic Combat Mode. Let D_{cum}(R, \mathbf{S}) represent the cumulative damage inflicted across R rounds under seed \mathbf{S}. The empirical cumulative distribution function (ECDF) is formulated as:
\hat{F}_{D}(x) = \frac{1}{M} \sum_{i=1}^M \mathbb{I}(D_{cum}(R, \mathbf{S}_i) \le x)
To calibrate an enemy tier to survive R combat rounds with survival confidence 1 - \alpha against premature defeat:
HP_{target} = \hat{F}_{D}^{-1}(1 - \alpha) = \inf \{x \in \mathbb{R} : \hat{F}_{D}(x) \ge 1 - \alpha\}
If Offensive Ceiling Mode establishes that an uninterrupted party deals a median 3-round cumulative total of 210 damage, but Realistic Combat Mode demonstrates that action dilution reduces the 95\text{th-percentile} damage to 165, setting HP_{target} = 170 guarantees the enemy survives through round three in 95\% of realistic encounters.
Formal Verification Test Suite
The following verification test suite defines formal assertions for each mechanical subsystem.
Test 1: Composite Pad Address Disambiguation
Initial State: Two Type 3 enemies (E_1, E_2) instantiate in battle B_1.
Input Action: Ally A_1 attacks pad label 6 on E_1; Ally A_2 attacks pad label 6 on E_2.
Assertions:
\text{Assert}(A_1.\text{PadAddress} == \langle B_1, E_1, 6 \rangle)
\text{Assert}(A_2.\text{PadAddress} == \langle B_1, E_2, 6 \rangle)
\text{Assert}(A_1.\text{WorldPosition} \neq A_2.\text{WorldPosition})
\text{Assert}(E_1.\text{Pad}[6].\text{Occupants} == \{A_1\})
\text{Assert}(E_2.\text{Pad}[6].\text{Occupants} == \{A_2\})
Test 2: Decoupled Terrain Persistency on Footprint Translation
Initial State: Enemy E_1 occupies cell (10, 10). Cast Ground Tremor to spawn a Mudfield at (10, 10).
Input Action: Enemy E_1 moves to cell (15, 10).
Assertions:
\text{Assert}(\text{WorldGrid}[10, 10].\text{terrain\_type} == \text{TERRAIN\_MUDFIELD})
\text{Assert}(\text{WorldGrid}[15, 10].\text{terrain\_type} == \text{TERRAIN\_NORMAL})
\text{Assert}(E_1.\text{ActiveStatuses}.\text{Contains}(\text{MUDFIELD\_MODIFIER}) == \text{FALSE})
Test 3: Lightning Graph Routing and Intermediate Node Invariance
Initial State: Enemy E_1 of Type 3 (labels 4–7). Thunder's Wrath lands on entry pad 4.
Input Action: Advance simulation tick through path traversal.
Assertions:
\text{Assert}(\text{PathHistory}[0] == 4)
\text{Assert}(\text{PathHistory}[1] == 5 \lor \text{PathHistory}[1] == 7)
\text{Assert}(\text{PathHistory}[1] \neq 6) (Direct hop from 4 to 6 is rejected).
\text{Assert}(\text{PathHistory}[2] == 6)
Test 4: Pre-Damage Interception and Double-Spend Suppression
Initial State: Enemy E_1 pad 8 holds active ELEMENT_EARTH_BIT prime.
Input Action: Cast Tidal Surge (Water, base potency 100) targeting pad 8.
Assertions:
\text{Assert}(\text{CombatEventLog}.\text{Contains}(\text{EVENT\_MUDSTORM\_TRIGGERED}) == \text{TRUE})
\text{Assert}(E_1.\text{DirectDamageReceived} == 0.0) (Base Tidal Surge direct damage suppressed).
\text{Assert}(E_1.\text{ActiveStatuses}.\text{Contains}(\text{STATUS\_MUDSTORM\_DOT}) == \text{TRUE})
\text{Assert}(\text{WorldGrid}.\text{GetCellAtPad}(E_1, 8).\text{terrain\_type} == \text{TERRAIN\_MUDFIELD})
Test 5: Mastered Triple Extension on Type 4 Topology
Initial State: Enemy E_1 of Type 4 (labels 8–13). Combatants C_1, C_2 occupy pads 8 and 13. Combatant C_3 occupies pad 9.
Input Action: Evaluate combo qualification under Profile A (triple_mastery = FALSE) and Profile B (triple_mastery = TRUE).
Assertions:
\text{Assert}(\text{EvaluateCombo}(\text{Profile A}) == \text{DISQUALIFIED\_TOPOLOGY})
\text{Assert}(\text{EvaluateCombo}(\text{Profile B}) == \text{SUCCESS})
Test 6: Stochastic Overcrowding Obstruction Failure
Initial State: Combatants C_1 and C_2 occupy pad 8 on Type 4 enemy E_1; C_3 occupies pad 13. Party attempts combo \{8, 13\} with failure parameter \lambda = 0.85.
Input Action: Execute 1,000 deterministic simulation trials across distinct seeds.
Assertions:
\text{Assert}(\text{DisqualifiedTopologyCount} == 0)
\text{Assert}(\text{FailedObstructionCount} \in [820, 880])
Test 7: Unoccupied World-Grid AoE Terrain Modification
Initial State: Coordinate (20, 20) contains no entity footprints or combatants.
Input Action: Cast Volcanic Eruption centered at world cell (20, 20).
Assertions:
\text{Assert}(\text{DamageEventsEmitted}.\text{Count} == 0)
\text{Assert}(\text{WorldGrid}[20, 20].\text{terrain\_type} == \text{TERRAIN\_LAVA\_FIELD})
\text{Assert}(\text{WorldGrid}[20, 20].\text{remaining\_turns} == 3)
Architectural Synthesis and Implementation Roadmap
The mechanics specified in EngAIn Combat & Magic Specification v0.1 operate as a cohesive spatial simulation engine rather than isolated damage formulas. Correct engine-independent execution demands strict compliance with spatial decoupling: Landing Pads provide the targeting and transit interface, Footprints define continuous physical volumes, and Base Forms maintain persistent world state.
The runtime pipeline integrates these layers through strict authorization boundaries. Zero-World supplies immutable semantic data definitions for spells, platform locks, and reaction rules. The AP authorization gateway validates action budgets and cryptographic turn tokens, admitting only authorized intents to the Combat3D kernel.
Within the kernel, spatial coordinate transformations project local pads onto world coordinates and evaluate base-form cell overlaps. Incoming spells pass through pre-damage interception to resolve compound reactions such as Mudstorm, Aqua Lightning, or Blazing Plasma before any base damage executes. Graph traversal algorithms resolve non-reversing Lightning paths and mastered triple extensions, mutating the Authoritative Combat Snapshot atomically and emitting a deterministic, read-only event stream to presentation clients.
Implementation Phase
Milestone Focus
Core Technical Deliverables
Verification Gate
Phase 1: Spatial Topology
Spatial Decoupling & Coordinate Mapping
Implement composite addressing schema (battle_id, enemy_id, pad_label), local-to-world affine translation matrices, and point-in-cell base-form overlap queries.
Validate Test 1 (Address Disambiguation) and Test 2 (Decoupled Terrain Persistency).
Phase 2: Reaction Lifecycle
Pre-Damage Interception & Overlap Pipeline
Implement pre-damage lifecycle hooks within Combat3D, suppressing base spell damage on elemental prime match and instantiating Mudfield/Lava Field terrain.
Validate Test 4 (Pre-Damage Interception) and Test 7 (Unoccupied AoE Terrain).
Phase 3: Graph Traversal
Directed Routing & Combo Qualification
Build directed non-reversing adjacency graph for Lightning propagation, inter-entity jump vectors, combo lock engine, mastered triple extensions, and obstruction rolls.
Validate Test 3 (Lightning Invariance), Test 5 (Mastered Triples), and Test 6 (Obstruction).
Phase 4: Calibration & Replay
Empirical Durability & Deterministic Auditing
Deploy dual-mode calibration harness (OCM and RCM), execute Monte Carlo sweeps to derive empirical enemy HP pools, and lock PRNG replay logging.
Achieve bit-identical replay logs across 10,000 multi-turn simulated battle runs.


