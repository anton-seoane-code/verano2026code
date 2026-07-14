#=== genieengine ===
# kind: component
# name: Shooter
# summary: Shooting data: damage, fire rate, range.
# uses: none
#=== /genieengine ===
extends Node

@export var damage: float = 25.0
@export var fire_rate: float = 0.3
@export var range: float = 100.0

var can_shoot: bool = true

func _ready():
	add_to_group("c_shooter")
