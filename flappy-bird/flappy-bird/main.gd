#=== genieengine ===
# kind: other
# name: Main
# summary: Entry scene — instantiates entities, hosts systems, manages UI, score, and game state.
# uses: c_bird, c_pipe, c_ground
#=== /genieengine ===
extends Node2D

var score: int = 0
var is_game_over: bool = false

var score_label: Label
var game_over_ui: CanvasLayer

func _ready():
	_setup_input()
	_setup_background()
	_create_ui()
	_create_entities()
	_create_systems()

func _setup_input():
	var flap_key = InputEventKey.new()
	flap_key.keycode = KEY_SPACE
	InputMap.add_action("flap")
	InputMap.action_add_event("flap", flap_key)

	var flap_click = InputEventMouseButton.new()
	flap_click.button_index = MOUSE_BUTTON_LEFT
	InputMap.action_add_event("flap", flap_click)

func _setup_background():
	RenderingServer.set_default_clear_color(Color(0.4, 0.7, 1.0))

	var ground_entity = preload("res://entities/e_ground.tscn").instantiate()
	ground_entity.position = Vector2(0, 536)
	add_child(ground_entity)

func _create_ui():
	var layer = CanvasLayer.new()
	add_child(layer)

	score_label = Label.new()
	score_label.text = "0"
	score_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	score_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	score_label.position = Vector2(476, 60)
	score_label.size = Vector2(200, 60)
	score_label.add_theme_font_size_override("font_size", 56)
	score_label.add_theme_color_override("font_color", Color.WHITE)
	layer.add_child(score_label)

	game_over_ui = CanvasLayer.new()
	game_over_ui.visible = false
	add_child(game_over_ui)

	var bg = ColorRect.new()
	bg.color = Color(0, 0, 0, 0.5)
	bg.anchors_preset = Control.PRESET_FULL_RECT
	game_over_ui.add_child(bg)

	var go_label = Label.new()
	go_label.text = "Game Over"
	go_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	go_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	go_label.position = Vector2(426, 224)
	go_label.size = Vector2(300, 60)
	go_label.add_theme_font_size_override("font_size", 56)
	go_label.add_theme_color_override("font_color", Color.WHITE)
	game_over_ui.add_child(go_label)

	var fs_label = Label.new()
	fs_label.name = "FinalScore"
	fs_label.text = "Score: 0"
	fs_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	fs_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	fs_label.position = Vector2(426, 304)
	fs_label.size = Vector2(300, 40)
	fs_label.add_theme_font_size_override("font_size", 32)
	fs_label.add_theme_color_override("font_color", Color.WHITE)
	game_over_ui.add_child(fs_label)

	var rt_label = Label.new()
	rt_label.text = "Tap to Restart"
	rt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rt_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	rt_label.position = Vector2(426, 364)
	rt_label.size = Vector2(300, 40)
	rt_label.add_theme_font_size_override("font_size", 24)
	rt_label.add_theme_color_override("font_color", Color(1, 1, 1, 0.7))
	game_over_ui.add_child(rt_label)

func _create_entities():
	var bird = preload("res://entities/e_bird.tscn").instantiate()
	bird.position = Vector2(200, 300)
	add_child(bird)

func _create_systems():
	var bird_sys = preload("res://systems/s_bird.gd").new()
	bird_sys.died.connect(_on_bird_died)
	add_child(bird_sys)

	var pipe_sys = preload("res://systems/s_pipe_spawner.gd").new()
	pipe_sys.scored.connect(_on_scored)
	add_child(pipe_sys)

	var ground_sys = preload("res://systems/s_ground.gd").new()
	add_child(ground_sys)

func _on_bird_died():
	is_game_over = true
	score_label.visible = false
	game_over_ui.visible = true
	game_over_ui.get_node("FinalScore").text = "Score: " + str(score)

func _on_scored():
	score += 1
	score_label.text = str(score)

func _process(delta: float):
	if is_game_over and Input.is_action_just_pressed("flap"):
		get_tree().reload_current_scene()
