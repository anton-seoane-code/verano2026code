#=== genieengine ===
# kind: other
# name: Main
# summary: Entry scene script — instantiates entities and hosts the systems.
# uses: none
#=== /genieengine ===
extends Node3D

var game_over: bool = false

func _ready():
	_setup_input_actions()
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	print("Doom FPS is running")

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
