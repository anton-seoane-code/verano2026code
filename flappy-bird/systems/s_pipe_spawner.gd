#=== genieengine ===
# kind: system
# name: PipeSpawner
# summary: Spawns pipe pairs, scrolls them left, scores when the bird passes, and removes off-screen pipes.
# uses: c_pipe
#=== /genieengine ===
extends Node

signal scored()

const BIRD_X = 200.0
const PIPE_SPEED = 200.0
const SPAWN_INTERVAL = 1.6
const MIN_GAP_Y = 150.0
const MAX_GAP_Y = 420.0
const REMOVE_X = -120.0
const SPAWN_X = 1252.0

var timer: float = 0.0

func _process(delta: float):
	var birds = get_tree().get_nodes_in_group("c_bird")
	if birds.is_empty() or birds[0].is_dead:
		return

	timer += delta
	if timer >= SPAWN_INTERVAL:
		timer = 0.0
		_spawn_pipe()

	for pipe_node in get_tree().get_nodes_in_group("c_pipe"):
		var pair = pipe_node.get_parent()
		pair.position.x -= PIPE_SPEED * delta

		if not pipe_node.scored and pair.position.x < BIRD_X:
			pipe_node.scored = true
			scored.emit()

		if pair.position.x < REMOVE_X:
			pair.queue_free()

func _spawn_pipe():
	var pipe = preload("res://entities/e_pipe_pair.tscn").instantiate()
	pipe.position = Vector2(SPAWN_X, 0.0)
	get_parent().add_child(pipe)

	var gap_y = randf_range(MIN_GAP_Y, MAX_GAP_Y)
	pipe.setup(gap_y)
