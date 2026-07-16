#=== genieengine ===
# kind: other
# name: Main
# summary: Entry scene script — instantiates entities and hosts the systems.
# uses: none
#=== /genieengine ===
extends Node3D

var game_over: bool = false

const ENEMY_SCENE = preload("res://entities/e_enemy.tscn")

var spawn_positions = [
	Vector3(-10, 0, -10),
	Vector3(0, 0, -10),
	Vector3(10, 0, -10),
	Vector3(-10, 0, 0),
	Vector3(10, 0, 0),
	Vector3(-10, 0, 10),
	Vector3(0, 0, 10),
	Vector3(10, 0, 10),
]

var _bgm_player: AudioStreamPlayer

func _ready():
	_setup_input_actions()
	_build_level()
	_add_room_lights()
	_start_enemy_spawning()
	_start_bgm()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	print("Doom FPS is running")

func _start_bgm():
	_bgm_player = AudioStreamPlayer.new()
	_bgm_player.stream = _gen_bgm()
	_bgm_player.volume_db = -12
	add_child(_bgm_player)
	_bgm_player.play()

func _gen_bgm() -> AudioStreamWAV:
	var rate = 22050
	var dur = 8.0
	var samples = int(rate * dur)
	var data = PackedByteArray()
	data.resize(samples * 2)
	for i in range(samples):
		var t = float(i) / rate
		var s = sin(t * 55 * TAU) * 0.08 + sin(t * 110 * TAU) * 0.04 + sin(t * 82.5 * TAU) * 0.03 + sin(t * 220 * TAU) * 0.015
		s += sin(t * 165 * TAU) * 0.02 if int(t * 2) % 2 == 0 else 0.0
		var val = clampi(int(s * 32767), -32768, 32767)
		data.encode_s16(i * 2, val)
	var wav = AudioStreamWAV.new()
	wav.data = data
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = rate
	wav.stereo = false
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.loop_begin = 0
	wav.loop_end = samples
	return wav

func _process(_delta):
	_update_health_bar()
	if game_over and Input.is_action_just_pressed("shoot"):
		get_tree().reload_current_scene()

func _input(event):
	if event.is_action_pressed("escape"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _setup_input_actions():
	var actions = {
		"move_forward": [KEY_W, KEY_UP],
		"move_back": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"shoot": [MOUSE_BUTTON_LEFT],
		"escape": [KEY_ESCAPE]
	}

	for action_name in actions:
		if not InputMap.has_action(action_name):
			InputMap.add_action(action_name)
			for key in actions[action_name]:
				var event
				if key == MOUSE_BUTTON_LEFT:
					event = InputEventMouseButton.new()
					event.button_index = MOUSE_BUTTON_LEFT
				else:
					event = InputEventKey.new()
					event.keycode = key
				InputMap.action_add_event(action_name, event)

func _build_level():
	var wall_mat = StandardMaterial3D.new()
	wall_mat.albedo_color = Color(0.35, 0.3, 0.3)
	wall_mat.emission_enabled = true
	wall_mat.emission = Color(0.08, 0.06, 0.06)
	var floor_mat = StandardMaterial3D.new()
	floor_mat.albedo_color = Color(0.2, 0.2, 0.22)

	$Floor/MeshInstance3D.material_override = floor_mat

	var walls = [
		# Outer boundary
		[Vector3(0, 1.5, -15), Vector3(30, 3, 0.2)],
		[Vector3(0, 1.5, 15), Vector3(30, 3, 0.2)],
		[Vector3(-15, 1.5, 0), Vector3(0.2, 3, 30)],
		[Vector3(15, 1.5, 0), Vector3(0.2, 3, 30)],
		# Inner vertical walls (x=±5) — gap at center for passage
		[Vector3(-5, 1.5, -8), Vector3(0.2, 3, 14)],
		[Vector3(-5, 1.5, 8), Vector3(0.2, 3, 14)],
		[Vector3(5, 1.5, -8), Vector3(0.2, 3, 14)],
		[Vector3(5, 1.5, 8), Vector3(0.2, 3, 14)],
		# Inner horizontal walls (z=±5) — gap at center for passage
		[Vector3(-8, 1.5, -5), Vector3(14, 3, 0.2)],
		[Vector3(8, 1.5, -5), Vector3(14, 3, 0.2)],
		[Vector3(-8, 1.5, 5), Vector3(14, 3, 0.2)],
		[Vector3(8, 1.5, 5), Vector3(14, 3, 0.2)],
	]

	for w in walls:
		var body = StaticBody3D.new()
		body.position = w[0]

		var col = CollisionShape3D.new()
		var box = BoxShape3D.new()
		box.size = w[1]
		col.shape = box
		body.add_child(col)

		var mi = MeshInstance3D.new()
		var bm = BoxMesh.new()
		bm.size = w[1]
		bm.material = wall_mat
		mi.mesh = bm
		body.add_child(mi)

		$Walls.add_child(body)

func _add_room_lights():
	var room_centers = [
		Vector3(-10, 2.8, -10),
		Vector3(0, 2.8, -10),
		Vector3(10, 2.8, -10),
		Vector3(-10, 2.8, 0),
		Vector3(0, 2.8, 0),
		Vector3(10, 2.8, 0),
		Vector3(-10, 2.8, 10),
		Vector3(0, 2.8, 10),
		Vector3(10, 2.8, 10),
	]
	for pos in room_centers:
		var light = OmniLight3D.new()
		light.position = pos
		light.light_color = Color(1, 0.95, 0.85)
		light.light_energy = 1.5
		light.omni_range = 8
		$Lights.add_child(light)

var _spawn_timer: Timer
var _spawn_count: int = 0

func _start_enemy_spawning():
	_spawn_timer = Timer.new()
	_spawn_timer.wait_time = 15.0
	_spawn_timer.autostart = true
	_spawn_timer.timeout.connect(_spawn_enemy)
	add_child(_spawn_timer)

func _spawn_enemy():
	_spawn_count += 1
	if _spawn_count >= 2:
		_spawn_timer.wait_time = 5.0
	var pos = spawn_positions[randi() % spawn_positions.size()]
	var enemy = ENEMY_SCENE.instantiate()
	enemy.position = pos
	$Entities.add_child(enemy)

func _update_health_bar():
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		return
	var health = player.get_node("c_health")
	if not health:
		return

	var fill = $UI/HealthBarFill
	if fill:
		var ratio = max(0.0, health.hp / health.max_hp)
		fill.offset_right = fill.offset_left + 196.0 * ratio
		if ratio < 0.5:
			fill.color = Color(1.0 - ratio * 2.0, ratio * 2.0, 0.0, 0.9)
		else:
			fill.color = Color(0.2, 0.8, 0.2, 0.9)

	if health.hp <= 0 and not game_over:
		game_over = true
		$UI/GameOverLabel.visible = true
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
