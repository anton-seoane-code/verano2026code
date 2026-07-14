#=== genieengine ===
# kind: entity
# name: Ground
# summary: Scrolling ground with tiled sprites and the c_ground component.
# uses: c_ground
#=== /genieengine ===
extends Node2D

const GROUND_WIDTH = 1152.0

func _ready():
	var texture = preload("res://assets/entities/e_ground/ground.svg")

	for i in range(3):
		var sprite = Sprite2D.new()
		sprite.texture = texture
		sprite.position.x = i * GROUND_WIDTH
		add_child(sprite)

	add_child(preload("res://components/c_ground.gd").new())
