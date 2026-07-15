#=== genieengine ===
# kind: component
# name: Bird
# summary: Bird physics data — gravity, flap strength, velocity and alive state.
# uses: none
#=== /genieengine ===
extends Node

@export var gravity: float = 980.0
@export var flap_strength: float = -330.0
@export var max_fall_speed: float = 600.0
@export var rotation_speed: float = 3.0

var velocity: float = 0.0
var is_dead: bool = false

func _ready():
	add_to_group("c_bird")
