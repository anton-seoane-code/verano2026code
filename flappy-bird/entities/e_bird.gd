#=== genieengine ===
# kind: entity
# name: Bird
# summary: Player-controlled bird with sprite, circular collision, and c_bird component.
# uses: c_bird
#=== /genieengine ===
extends Area2D

func _ready():
	var sprite = Sprite2D.new()
	sprite.texture = preload("res://assets/entities/e_bird/bird.svg")
	add_child(sprite)

	var shape = CollisionShape2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 14
	shape.shape = circle
	add_child(shape)

	add_child(preload("res://components/c_bird.gd").new())
