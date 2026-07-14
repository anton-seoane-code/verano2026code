#=== genieengine ===
# kind: entity
# name: Player
# summary: First-person player character with camera, movement, health, and shooting.
# uses: c_health, c_movement, c_shooter
#=== /genieengine ===
extends CharacterBody3D

func _ready():
	add_to_group("player")
