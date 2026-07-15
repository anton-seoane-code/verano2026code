#=== genieengine ===
# kind: entity
# name: Enemy
# summary: Enemy character that moves toward the player and deals contact damage.
# uses: c_health, c_enemy
#=== /genieengine ===
extends CharacterBody3D

func _ready():
	add_to_group("enemy")
