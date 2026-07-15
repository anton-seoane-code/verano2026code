#=== genieengine ===
# kind: component
# name: Ground
# summary: Ground scroll speed data.
# uses: none
#=== /genieengine ===
extends Node

@export var speed: float = 100.0

func _ready():
	add_to_group("c_ground")
