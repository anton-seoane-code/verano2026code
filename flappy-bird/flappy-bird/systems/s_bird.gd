#=== genieengine ===
# kind: system
# name: BirdSystem
# summary: Handles bird input, gravity, rotation, and collision with pipes and ground.
# uses: c_bird
#=== /genieengine ===
extends Node

signal died()

const GROUND_Y = 536.0
const CEILING_Y = 14.0

func _process(delta: float):
	for bird_node in get_tree().get_nodes_in_group("c_bird"):
		var data = bird_node
		if data.is_dead:
			continue

		var bird = bird_node.get_parent() as Area2D

		if Input.is_action_just_pressed("flap"):
			data.velocity = data.flap_strength

		data.velocity += data.gravity * delta
		data.velocity = minf(data.velocity, data.max_fall_speed)

		bird.position.y += data.velocity * delta

		var target_rot = deg_to_rad(clampf(data.velocity * 0.12, -60, 30))
		bird.rotation = lerpf(bird.rotation, target_rot, data.rotation_speed * delta)

		if bird.position.y >= GROUND_Y:
			bird.position.y = GROUND_Y
			data.is_dead = true
			died.emit()

		if bird.position.y <= CEILING_Y:
			bird.position.y = CEILING_Y
			data.velocity = 0.0

		var bodies = bird.get_overlapping_bodies()
		if bodies.size() > 0:
			data.is_dead = true
			died.emit()
