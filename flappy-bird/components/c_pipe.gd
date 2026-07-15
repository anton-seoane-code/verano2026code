#=== genieengine ===
# kind: component
# name: Pipe
# summary: Pipe scoring state — tracks whether this pipe pair has already been scored.
# uses: none
#=== /genieengine ===
extends Node

var scored: bool = false

func _ready():
	add_to_group("c_pipe")
