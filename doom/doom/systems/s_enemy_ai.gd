#=== genieengine ===
# kind: system
# name: EnemyAISystem
# summary: Moves enemies toward the player when detected and applies contact damage.
# uses: c_enemy, c_health
#=== /genieengine ===
extends Node

func _physics_process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		return

	var enemies = get_tree().get_nodes_in_group("enemy")
	for enemy in enemies:
		var enemy_comp = enemy.get_node("c_enemy")
		if not enemy_comp:
			continue

		var health = enemy.get_node("c_health")
		if health and health.hp <= 0:
			continue

		var dir_to_player = player.global_position - enemy.global_position
		var dist = dir_to_player.length()

		if dist <= enemy_comp.detection_range:
			var target_pos = Vector3(player.global_position.x, enemy.global_position.y, player.global_position.z)
			enemy.look_at(target_pos, Vector3.UP)

			if dist > 1.5:
				var move_dir = dir_to_player.normalized()
				var vel = enemy.velocity
				vel.x = move_dir.x * enemy_comp.move_speed
				vel.z = move_dir.z * enemy_comp.move_speed
				vel.y -= 9.8 * delta
				enemy.velocity = vel
			else:
				var vel = enemy.velocity
				vel.x = 0
				vel.z = 0
				vel.y -= 9.8 * delta
				enemy.velocity = vel

			enemy.move_and_slide()

			if dist < 1.5:
				var player_health = player.get_node("c_health")
				if player_health:
					player_health.take_damage(enemy_comp.contact_damage * delta)
