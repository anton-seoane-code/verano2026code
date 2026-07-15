#=== genieengine ===
# kind: system
# name: GroundSystem
# summary: Scrolls ground sprites left continuously to create an endless running effect.
# uses: c_ground
#=== /genieengine ===
extends Node

const GROUND_WIDTH = 1152.0
const SCROLL_SPEED = 100.0

func _process(delta: float):
	var birds = get_tree().get_nodes_in_group("c_bird")
	if not birds.is_empty() and birds[0].is_dead:
		return

	for ground_node in get_tree().get_nodes_in_group("c_ground"):
		var ground = ground_node.get_parent()
		for child in ground.get_children():
			if child is Sprite2D:
				child.position.x -= SCROLL_SPEED * delta
				if child.position.x <= -GROUND_WIDTH:
					child.position.x += GROUND_WIDTH * 3
