#=== genieengine ===
# kind: entity
# name: Player
# summary: First-person player character with camera, movement, health, and shooting.
# uses: c_health, c_movement, c_shooter
#=== /genieengine ===
extends CharacterBody3D

func _ready():
	add_to_group("player")
	_build_gun()

func _build_gun():
	var cam = $Camera3D
	if not cam:
		return

	var gun = Node3D.new()
	gun.name = "Gun"
	cam.add_child(gun)

	var mat_barrel = StandardMaterial3D.new()
	mat_barrel.albedo_color = Color(0.15, 0.15, 0.15)
	mat_barrel.metallic = 0.7
	mat_barrel.roughness = 0.4

	var barrel = MeshInstance3D.new()
	barrel.name = "Barrel"
	var bm = BoxMesh.new()
	bm.size = Vector3(0.04, 0.04, 0.5)
	bm.material = mat_barrel
	barrel.mesh = bm
	barrel.position = Vector3(0.25, -0.15, -0.45)
	gun.add_child(barrel)

	var mat_body = StandardMaterial3D.new()
	mat_body.albedo_color = Color(0.2, 0.2, 0.22)
	mat_body.metallic = 0.3
	mat_body.roughness = 0.7

	var body = MeshInstance3D.new()
	body.name = "Body"
	var bm2 = BoxMesh.new()
	bm2.size = Vector3(0.1, 0.08, 0.18)
	bm2.material = mat_body
	body.mesh = bm2
	body.position = Vector3(0.25, -0.15, -0.07)
	gun.add_child(body)

	var mat_grip = StandardMaterial3D.new()
	mat_grip.albedo_color = Color(0.25, 0.15, 0.1)

	var grip = MeshInstance3D.new()
	grip.name = "Grip"
	var bm3 = BoxMesh.new()
	bm3.size = Vector3(0.06, 0.12, 0.06)
	bm3.material = mat_grip
	grip.mesh = bm3
	grip.position = Vector3(0.25, -0.28, 0.02)
	gun.add_child(grip)

	var muzzle = Node3D.new()
	muzzle.name = "Muzzle"
	muzzle.position = Vector3(0.25, -0.15, -0.7)
	gun.add_child(muzzle)
