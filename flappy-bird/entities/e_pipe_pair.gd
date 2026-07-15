#=== genieengine ===
# kind: entity
# name: PipePair
# summary: A pair of top/bottom pipes with a gap, collision, and c_pipe component.
# uses: c_pipe
#=== /genieengine ===
extends Node2D

var top_pipe: StaticBody2D
var bottom_pipe: StaticBody2D

const PIPE_BODY_HEIGHT = 800.0
const PIPE_WIDTH = 52.0
const CAP_WIDTH = 64.0
const CAP_HEIGHT = 24.0
const GAP_HEIGHT = 150.0

func _ready():
	var body_tex = preload("res://assets/entities/e_pipe/pipe_body.svg")
	var cap_tex = preload("res://assets/entities/e_pipe/pipe_cap.svg")

	top_pipe = StaticBody2D.new()
	_add_pipe_children(top_pipe, body_tex, cap_tex, -1)
	add_child(top_pipe)

	bottom_pipe = StaticBody2D.new()
	_add_pipe_children(bottom_pipe, body_tex, cap_tex, 1)
	add_child(bottom_pipe)

	add_child(preload("res://components/c_pipe.gd").new())

func _add_pipe_children(parent: StaticBody2D, body_tex: Texture2D, cap_tex: Texture2D, sign_mult: int):
	var cap = Sprite2D.new()
	cap.texture = cap_tex
	parent.add_child(cap)

	var body = Sprite2D.new()
	body.texture = body_tex
	body.position.y = sign_mult * (CAP_HEIGHT / 2.0 + PIPE_BODY_HEIGHT / 2.0)
	parent.add_child(body)

	var col = CollisionShape2D.new()
	var shape = RectangleShape2D.new()
	shape.size = Vector2(CAP_WIDTH, PIPE_BODY_HEIGHT + CAP_HEIGHT)
	col.shape = shape
	col.position.y = sign_mult * PIPE_BODY_HEIGHT / 2.0
	parent.add_child(col)

func setup(gap_y: float):
	top_pipe.position.y = gap_y - GAP_HEIGHT / 2.0
	bottom_pipe.position.y = gap_y + GAP_HEIGHT / 2.0
