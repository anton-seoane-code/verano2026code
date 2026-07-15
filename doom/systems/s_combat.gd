#=== genieengine ===
# kind: system
# name: CombatSystem
# summary: Handles shooting raycasts and damage application, also cleans up dead enemies.
# uses: c_shooter, c_health
#=== /genieengine ===
extends Node

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

	var space_state = player.get_world_3d().direct_space_state
	var from = camera.global_position
	var to = from - camera.global_transform.basis.z * shooter.range

	var query = PhysicsRayQueryParameters3D.create(from, to)
	query.set_exclude([player])
	query.collision_mask = 1
	var result = space_state.intersect_ray(query)

	if result:
		var hit_entity = result.collider
		var health = hit_entity.get_node("c_health")
		if health:
			health.take_damage(shooter.damage)

	await get_tree().create_timer(shooter.fire_rate).timeout
	if is_instance_valid(shooter):
		shooter.can_shoot = true
