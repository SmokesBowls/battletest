extends Node3D
## Plays back a combat log written by the Python sketches. Display only: every number shown
## comes from Python; nothing elemental is computed here. Godot owns positions (--export-field).
## User args (after `--`):
##   --field         play res://field.json (lightning_field.py) instead of res://encounter.json
##   --export-field  write res://battlefield.json (30 enemy positions) and quit
##   --check         apply all turns instantly, print state, quit
##   --shot          play through, save res://shot.png, quit

const STEP := 1.6  # seconds between turns
const HOP := 0.4   # seconds between hits in one turn, so a bolt's path reads in order
const BASE := Color(0.45, 0.45, 0.5)
const COLORS := {
	"water": Color(0.2, 0.45, 1.0), "fire": Color(1.0, 0.4, 0.1), "lightning": Color(1.0, 0.95, 0.2),
	"plasma": Color(1.0, 0.2, 0.9), "earth": Color(0.55, 0.38, 0.2), "shadow": Color(0.35, 0.1, 0.5),
	"ice": Color(0.6, 0.9, 1.0), "moon": Color(0.8, 0.8, 0.9), "spirit": Color(1.0, 1.0, 1.0),
	"clay": Color(0.7, 0.45, 0.3), "ash": Color(0.6, 0.6, 0.6),
}
const FIELD_COLS := 6
const FIELD_ROWS := 5
const FIELD_SPACING := 2.6

var data: Dictionary
var nodes := {}  # target id -> {"mat", "label", "body", "hp", "chain", "conditions"}
var hud: Label
var field_mode := false
var shot_mode := false


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if "--export-field" in args:
		_export_field()
		get_tree().quit(0)
		return
	field_mode = "--field" in args
	shot_mode = "--shot" in args
	var path := "res://field.json" if field_mode else "res://encounter.json"
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("%s missing: see the run commands in SESSION_HANDOFF" % path)
		get_tree().quit(1)
		return
	var parsed = JSON.parse_string(f.get_as_text())
	if typeof(parsed) != TYPE_DICTIONARY or not parsed.has("targets") or not parsed.has("turns"):
		push_error("%s is not a valid combat log" % path)
		get_tree().quit(1)
		return
	data = parsed
	_build_scene()

	if "--check" in args:
		for turn in data.turns:
			_apply_turn(turn)
		for tid in nodes:
			print("%s hp=%.2f chain=%s" % [tid, nodes[tid].hp, _chain_text(nodes[tid].chain)])
		get_tree().quit(0)
		return
	await _play()
	if "--shot" in args:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://shot.png")
		get_tree().quit(0)


func _export_field() -> void:
	# Jittered grid; seeded so the battlefield is the same every export.
	var rng := RandomNumberGenerator.new()
	rng.seed = 7
	var enemies := {}
	for r in FIELD_ROWS:
		for c in FIELD_COLS:
			var x := (c - (FIELD_COLS - 1) / 2.0) * FIELD_SPACING + rng.randf_range(-0.7, 0.7)
			var z := (r - (FIELD_ROWS - 1) / 2.0) * FIELD_SPACING + rng.randf_range(-0.7, 0.7)
			enemies["f%02d" % (r * FIELD_COLS + c)] = [snappedf(x, 0.01), snappedf(z, 0.01)]
	var out := FileAccess.open("res://battlefield.json", FileAccess.WRITE)
	out.store_string(JSON.stringify({"enemies": enemies}, " "))
	print("WROTE res://battlefield.json (%d enemies)" % enemies.size())


func _build_scene() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.08, 0.08, 0.1)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color.WHITE
	env.ambient_light_energy = 0.5
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-50, 30, 0)
	add_child(light)

	var cam := Camera3D.new()
	add_child(cam)
	if field_mode:
		cam.look_at_from_position(Vector3(0, 11, 8.5), Vector3(0, 0, 0.8))
	else:
		cam.look_at_from_position(Vector3(0, 5.5, 9), Vector3(0, 1, 0))

	var minions: Array = data.targets.keys().filter(func(id): return id != "boss")
	for tid in data.targets:
		var t: Dictionary = data.targets[tid]
		var size := 2.0 if tid == "boss" else 1.0
		var pos: Vector3
		if t.has("pos"):
			pos = Vector3(t.pos[0], 0.5, t.pos[1])
		elif tid == "boss":
			pos = Vector3(0, 1, 2.5)
		else:
			pos = Vector3(-6.25 + minions.find(tid) * 2.5, 0.5, -2.5)
		var mat := StandardMaterial3D.new()
		var box := BoxMesh.new()
		box.size = Vector3.ONE * size
		var body := MeshInstance3D.new()
		body.mesh = box
		body.material_override = mat
		body.position = pos
		add_child(body)

		var label := Label3D.new()
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.font_size = 40
		label.pixel_size = 0.009
		label.outline_size = 8
		# Boss label sits in front of it so it doesn't cover the minion row behind.
		label.position = pos + (Vector3(0, -0.6, 1.4) if tid == "boss" else Vector3(0, size * 0.5 + 0.9, 0))
		add_child(label)

		nodes[tid] = {"mat": mat, "label": label, "body": body, "hp": float(t.hp), "chain": t.chain,
				"conditions": t.get("conditions", [])}
		_refresh(tid)

	var layer := CanvasLayer.new()
	add_child(layer)
	hud = Label.new()
	hud.position = Vector2(16, 12)
	hud.add_theme_font_size_override("font_size", 20)
	layer.add_child(hud)


func _chain_text(chain: Dictionary) -> String:
	var text := ">".join(chain.elements) if chain.elements.size() > 0 else "-"
	if chain.state != null:
		text += " [%s]" % chain.state
	if chain.closed:
		text += " (ended)"
	return text


func _rest_color(tid: String) -> Color:
	var els: Array = nodes[tid].chain.elements
	if els.size() > 0:
		return COLORS.get(els[-1], BASE).darkened(0.35)
	var conds: Array = nodes[tid].conditions
	return COLORS.get(conds[0], BASE).darkened(0.35) if conds.size() > 0 else BASE


func _refresh(tid: String) -> void:
	var n: Dictionary = nodes[tid]
	var shown := _chain_text(n.chain)
	if n.conditions.size() > 0:
		shown += " {%s}" % ",".join(n.conditions)
	n.label.text = "%s\nHP %.1f\n%s" % [tid, n.hp, shown]
	n.mat.albedo_color = _rest_color(tid)


func _apply_hit(turn: Dictionary, hit: Dictionary) -> void:
	var tid: String = hit.target
	nodes[tid].hp -= float(hit.damage)
	if turn.chains.has(tid):
		nodes[tid].chain = turn.chains[tid]
	_refresh(tid)


func _apply_turn(turn: Dictionary) -> void:
	for hit in turn.hits:
		_apply_hit(turn, hit)


func _play() -> void:
	await get_tree().create_timer(1.0).timeout
	for turn in data.turns:
		hud.text = "Cycle %d   %s   %s\n%s" % [turn.cycle, turn.actor, turn.turn, "\n".join(turn.alerts)]
		var hits: Array = turn.hits
		for i in hits.size():
			if not hits[i].primary and i > 0:
				_beam(hits[i - 1].target, hits[i])
			_apply_hit(turn, hits[i])
			_flash(hits[i], i)
			await get_tree().create_timer(HOP).timeout
		if not (shot_mode and turn == data.turns[-1]):  # screenshot while the last beams are visible
			await get_tree().create_timer(STEP).timeout


func _beam(from_id: String, hit: Dictionary) -> void:
	# One hop of a bolt, coloured by the form that arrives (Lightning or Plasma).
	var a: Vector3 = nodes[from_id].body.position + Vector3(0, 0.3, 0)
	var b: Vector3 = nodes[hit.target].body.position + Vector3(0, 0.3, 0)
	var color: Color = COLORS.get(hit.form, Color.WHITE)
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.albedo_color = color
	var box := BoxMesh.new()
	box.size = Vector3(0.12, 0.12, a.distance_to(b))
	var beam := MeshInstance3D.new()
	beam.mesh = box
	beam.material_override = mat
	add_child(beam)
	beam.look_at_from_position((a + b) / 2.0, b)
	var tw := create_tween()
	tw.tween_interval(1.2 if field_mode else 0.8)
	tw.tween_property(mat, "albedo_color:a", 0.0, 0.6)
	tw.tween_callback(beam.queue_free)


func _flash(hit: Dictionary, index: int) -> void:
	var n: Dictionary = nodes[hit.target]
	var color: Color = COLORS.get(hit.form, Color.WHITE)
	n.mat.albedo_color = color
	create_tween().tween_property(n.mat, "albedo_color", _rest_color(hit.target), 0.8)

	var pop := Label3D.new()
	pop.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	pop.font_size = 56 if hit.primary else 44
	pop.pixel_size = 0.009
	pop.outline_size = 10
	pop.modulate = color
	pop.text = "-%.1f %s" % [hit.damage, hit.form]
	# In front of the box (not over its label), staggered so consecutive hops don't stack.
	pop.position = n.body.position + Vector3(0, 0.2 + (index % 3) * 0.45, 0.9)
	add_child(pop)
	var tw := create_tween().set_parallel()
	tw.tween_property(pop, "position:y", pop.position.y + 1.0, 1.1)
	tw.tween_property(pop, "modulate:a", 0.0, 1.1)
	tw.chain().tween_callback(pop.queue_free)
