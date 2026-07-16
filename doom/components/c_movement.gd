#=== genieengine ===
# kind: component
# name: Movement
# summary: Movement speed data for entities.
# uses: none
#=== /genieengine ===
extends Node

@export var speed: float = 5.0

func _ready():
	add_to_group("c_movement")
