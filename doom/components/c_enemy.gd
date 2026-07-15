#=== genieengine ===
# kind: component
# name: Enemy
# summary: Enemy AI data: detection range, contact damage, move speed.
# uses: none
#=== /genieengine ===
extends Node

@export var detection_range: float = 30.0
@export var contact_damage: float = 10.0
@export var move_speed: float = 3.0

func _ready():
	add_to_group("c_enemy")
