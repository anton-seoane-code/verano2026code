#=== genieengine ===
# kind: entity
# name: Enemy
# summary: Enemy character that moves toward the player and deals contact damage.
# uses: c_health, c_enemy
#=== /genieengine ===
extends CharacterBody3D

func _ready():
	add_to_group("enemy")
	_build_mesh()

func _build_mesh():
	var vis = Node3D.new()
	vis.name = "Visual"
	add_child(vis)

	var skin = StandardMaterial3D.new()
	skin.albedo_color = Color(0.7, 0.5, 0.4)

	var cloth = StandardMaterial3D.new()
	cloth.albedo_color = Color(0.5, 0.18, 0.12)

	var dark = StandardMaterial3D.new()
	dark.albedo_color = Color(0.15, 0.1, 0.08)

	var head_mat = StandardMaterial3D.new()
	head_mat.albedo_color = Color(0.75, 0.55, 0.45)

	var eye_mat = StandardMaterial3D.new()
	eye_mat.albedo_color = Color(1, 0.9, 0.1)
	eye_mat.emission_enabled = true
	eye_mat.emission = Color(1, 0.8, 0)

	var s = SphereMesh.new()
	s.radius = 0.15
	s.height = 0.3
	s.material = skin

	var t = BoxMesh.new()
	t.size = Vector3(0.55, 0.7, 0.35)
	t.material = cloth

	var a = BoxMesh.new()
	a.size = Vector3(0.1, 0.45, 0.1)
	a.material = cloth

	var l = BoxMesh.new()
	l.size = Vector3(0.14, 0.35, 0.14)
	l.material = dark

	var head = MeshInstance3D.new()
	head.mesh = s
	head.position = Vector3(0, 1.15, 0)
	vis.add_child(head)

	var torso = MeshInstance3D.new()
	torso.mesh = t
	torso.position = Vector3(0, 0.6, 0)
	vis.add_child(torso)

	var left_arm = MeshInstance3D.new()
	left_arm.mesh = a
	left_arm.position = Vector3(-0.33, 0.75, 0)
	vis.add_child(left_arm)

	var right_arm = MeshInstance3D.new()
	right_arm.mesh = a
	right_arm.position = Vector3(0.33, 0.75, 0)
	vis.add_child(right_arm)

	var left_leg = MeshInstance3D.new()
	left_leg.mesh = l
	left_leg.position = Vector3(-0.14, 0.2, 0)
	vis.add_child(left_leg)

	var right_leg = MeshInstance3D.new()
	right_leg.mesh = l
	right_leg.position = Vector3(0.14, 0.2, 0)
	vis.add_child(right_leg)

	var eye_l = MeshInstance3D.new()
	eye_l.mesh = SphereMesh.new()
	eye_l.mesh.radius = 0.04
	eye_l.mesh.height = 0.08
	eye_l.material_override = eye_mat
	eye_l.position = Vector3(-0.06, 1.22, -0.14)
	vis.add_child(eye_l)

	var eye_r = MeshInstance3D.new()
	eye_r.mesh = SphereMesh.new()
	eye_r.mesh.radius = 0.04
	eye_r.mesh.height = 0.08
	eye_r.material_override = eye_mat
	eye_r.position = Vector3(0.06, 1.22, -0.14)
	vis.add_child(eye_r)
