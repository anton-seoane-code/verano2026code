#=== genieengine ===
# kind: component
# name: Health
# summary: Hit points with a died signal emitted when hp reaches 0.
# uses: none
#=== /genieengine ===
extends Node

@export var max_hp: float = 100.0
var hp: float

signal died

func _ready():
	add_to_group("c_health")
	hp = max_hp

func take_damage(amount: float):
	hp -= amount
	if hp <= 0:
		hp = 0
		died.emit()
