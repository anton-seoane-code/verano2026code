#=== genieengine ===
# kind: system
# name: InputSystem
# summary: Handles WASD movement and mouse look for the player.
# uses: c_movement
#=== /genieengine ===
extends Node

@export var mouse_sensitivity: float = 0.002

func _input(event):
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		var player = get_tree().get_first_node_in_group("player")
		if not player:
			return
		player.rotate_y(-event.relative.x * mouse_sensitivity)
		var camera = player.get_node("Camera3D")
		if camera:
			camera.rotation.x -= event.relative.y * mouse_sensitivity
			camera.rotation.x = clamp(camera.rotation.x, -1.5, 1.5)

func _physics_process(delta):
	var player = get_tree().get_first_node_in_group("player")
	if not player:
		return

	var input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var move_dir = Vector3(input_dir.x, 0, input_dir.y).rotated(Vector3.UP, player.rotation.y)
	move_dir = move_dir.normalized()

	var movement_component = player.get_node("c_movement")
	var speed = movement_component.speed if movement_component else 5.0

	var vel = player.velocity
	vel.x = move_dir.x * speed
	vel.z = move_dir.z * speed
	vel.y -= 9.8 * delta
	player.velocity = vel
	player.move_and_slide()
