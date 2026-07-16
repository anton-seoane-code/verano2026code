#=== genieengine ===
# kind: system
# name: CombatSystem
# summary: Handles shooting raycasts and damage application, also cleans up dead enemies.
# uses: c_shooter, c_health
#=== /genieengine ===
extends Node

var _bullet_mat: StandardMaterial3D
var _shoot_audio: AudioStreamWAV

func _ready():
	_bullet_mat = StandardMaterial3D.new()
	_bullet_mat.albedo_color = Color(1, 1, 0.6)
	_bullet_mat.emission_enabled = true
	_bullet_mat.emission = Color(1, 0.8, 0.2)

	_shoot_audio = _gen_audio("shoot")

func _process(_delta):
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		return

	var shooter = player.get_node("c_shooter")
	if not shooter:
		return

	if Input.is_action_just_pressed("shoot") and shooter.can_shoot:
		_shoot(player, shooter)

	var enemies = get_tree().get_nodes_in_group("enemy")
	for enemy in enemies:
		var health = enemy.get_node("c_health")
		if health and health.hp <= 0:
			enemy.queue_free()

func _shoot(player, shooter):
	shooter.can_shoot = false

	var camera = player.get_node("Camera3D")
	if not camera:
		shooter.can_shoot = true
		return

	var muzzle = camera.get_node("Gun/Muzzle")
	var from = camera.global_position
	if muzzle:
		from = muzzle.global_position

	var space_state = player.get_world_3d().direct_space_state
	var to = camera.global_position - camera.global_transform.basis.z * shooter.range

	var query = PhysicsRayQueryParameters3D.create(from, to)
	query.set_exclude([player])
	query.collision_mask = 1
	var result = space_state.intersect_ray(query)

	var hit_pos = to
	if result:
		hit_pos = result.position
		var hit_entity = result.collider
		var health = hit_entity.get_node("c_health")
		if health:
			health.take_damage(shooter.damage)

	_spawn_bullet(from, hit_pos)
	_play_sound(_shoot_audio, from)

	if muzzle:
		_spawn_muzzle_flash(muzzle.global_position)

	await get_tree().create_timer(shooter.fire_rate).timeout
	if is_instance_valid(shooter):
		shooter.can_shoot = true

func _spawn_bullet(from: Vector3, to: Vector3):
	var bullet = MeshInstance3D.new()
	var sm = SphereMesh.new()
	sm.radius = 0.04
	sm.height = 0.08
	sm.material = _bullet_mat
	bullet.mesh = sm
	bullet.position = from
	get_tree().current_scene.add_child(bullet)

	var dist = from.distance_to(to)
	var speed = max(50.0, dist / 0.08)
	var duration = dist / speed
	var tween = create_tween()
	tween.tween_method(func(p): bullet.position = from.lerp(to, p), 0.0, 1.0, duration)
	tween.tween_callback(bullet.queue_free)

func _spawn_muzzle_flash(pos: Vector3):
	var light = OmniLight3D.new()
	light.position = pos
	light.light_color = Color(1, 0.9, 0.5)
	light.light_energy = 3
	light.omni_range = 2
	get_tree().current_scene.add_child(light)
	var tween = create_tween()
	tween.tween_property(light, "light_energy", 0.0, 0.06)
	tween.tween_callback(light.queue_free)

func _play_sound(stream: AudioStreamWAV, pos: Vector3):
	var player = AudioStreamPlayer3D.new()
	player.stream = stream
	player.position = pos
	player.max_distance = 20
	player.volume_db = -6
	get_tree().current_scene.add_child(player)
	player.play()
	await get_tree().create_timer(0.3).timeout
	if is_instance_valid(player):
		player.queue_free()

func _gen_audio(type: String) -> AudioStreamWAV:
	var rate = 22050
	var dur = 0.0
	match type:
		"shoot": dur = 0.12
		"hit": dur = 0.2
		"bgm": dur = 4.0
	var samples = int(rate * dur)
	var data = PackedByteArray()
	data.resize(samples * 2)
	for i in range(samples):
		var t = float(i) / rate
		var s = 0.0
		match type:
			"shoot":
				s = randf_range(-0.4, 0.4) * exp(-t * 35)
			"hit":
				s = sin(t * 150 * TAU) * exp(-t * 8) * 0.4
			"bgm":
				s = sin(t * 55 * TAU) * 0.08 + sin(t * 110 * TAU) * 0.04 + sin(t * 165 * TAU) * 0.02
		var val = clampi(int(s * 32767), -32768, 32767)
		data.encode_s16(i * 2, val)
	var wav = AudioStreamWAV.new()
	wav.data = data
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = rate
	wav.stereo = false
	return wav
