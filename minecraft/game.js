/* ═══════════════════════════════════════════════════════════════
   Minecraft-style 3D voxel world — Three.js
   Auto-scales quality to fit device capability.
   ═══════════════════════════════════════════════════════════════ */

// ╔══════════════════════════════════════════════════════════════╗
// ║  Quality auto-detection (runs before anything else)         ║
// ╚══════════════════════════════════════════════════════════════╝

var QUALITY = {};

function detectQuality() {
  // URL param override: ?quality=low|medium|high|ultra
  var params = new URLSearchParams(window.location.search);
  var forced = params.get('quality');
  if (forced) {
    var lower = forced.toLowerCase();
    if (['low','medium','high','ultra'].indexOf(lower) !== -1) {
      console.log('[Quality] Manual override: ' + lower);
      return lower;
    }
  }

  var score = 0;

  // Device memory (Chrome / Edge only — undefined elsewhere)
  if (navigator.deviceMemory !== undefined) {
    if (navigator.deviceMemory >= 8) score += 3;
    else if (navigator.deviceMemory >= 4) score += 2;
    else if (navigator.deviceMemory >= 2) score += 1;
  } else {
    // Unknown memory — assume mid-range as a baseline
    score += 1;
  }

  // CPU logical cores
  if (navigator.hardwareConcurrency !== undefined) {
    if (navigator.hardwareConcurrency >= 8) score += 2;
    else if (navigator.hardwareConcurrency >= 4) score += 1;
    // < 4: +0
  } else {
    score += 1; // conservative assumption
  }

  // Pixel ratio — high DPI suggests recent hardware
  var pr = window.devicePixelRatio || 1;
  if (pr > 2) score += 2;
  else if (pr > 1) score += 1;

  // Mobile penalisation — same silicon but thermal + battery constraints
  if (/Android|iPhone|iPad|iPod|mobile|Mobi/i.test(navigator.userAgent)) {
    score -= 2;
  }

  // Small screen — likely an older device or laptop
  if (window.innerWidth < 800) score -= 1;

  // Determine tier
  if (score >= 6) return 'ultra';
  if (score >= 4) return 'high';
  if (score >= 2) return 'medium';
  return 'low';
}

function applyQuality(tier) {
  var presets = {
    low: {
      worldRadius:   10,
      fogFar:        35,
      shadows:       false,
      shadowMapSize: 0,
      pixelRatio:    1,
      antialias:     false,
      treeDensity:   0.003,
      mobCount:      3,
    },
    medium: {
      worldRadius:   16,
      fogFar:        55,
      shadows:       false,
      shadowMapSize: 0,
      pixelRatio:    1,
      antialias:     true,
      treeDensity:   0.005,
      mobCount:      6,
    },
    high: {
      worldRadius:   20,
      fogFar:        80,
      shadows:       true,
      shadowMapSize: 1024,
      pixelRatio:    1.5,
      antialias:     true,
      treeDensity:   0.008,
      mobCount:      10,
    },
    ultra: {
      worldRadius:   28,
      fogFar:        110,
      shadows:       true,
      shadowMapSize: 2048,
      pixelRatio:    Math.min(window.devicePixelRatio || 1, 2),
      antialias:     true,
      treeDensity:   0.012,
      mobCount:      15,
    },
  };

  QUALITY = presets[tier] || presets.medium;
  QUALITY.tier = tier.charAt(0).toUpperCase() + tier.slice(1);
  QUALITY.fogNear = QUALITY.fogFar * 0.6;

  console.log('[Quality] Tier: ' + QUALITY.tier +
    '  |  World: ' + QUALITY.worldRadius + 'r' +
    '  |  Shadows: ' + QUALITY.shadows +
    '  |  Fog: ' + QUALITY.fogFar +
    '  |  PR: ' + QUALITY.pixelRatio +
    '  |  Trees: ' + QUALITY.treeDensity);
}

applyQuality(detectQuality());

// ╔══════════════════════════════════════════════════════════════╗
// ║  Constants                                                  ║
// ╚══════════════════════════════════════════════════════════════╝

var WORLD_RADIUS   = QUALITY.worldRadius;
var GRAVITY        = -28;
var JUMP_SPEED     = 10;
var WALK_SPEED     = 5;
var SNEAK_SPEED    = 2;
var REACH          = 7;
var PLAYER_HEIGHT  = 1.62;
var PLAYER_RADIUS  = 0.3;

var BT = {
  AIR:0, GRASS:1, DIRT:2, STONE:3,
  WOOD:4, LEAVES:5, SAND:6, COBBLE:7,
};

var BLOCK_INFO = {};
BLOCK_INFO[BT.GRASS]  = { name:'Grass',  color:0x7cb342 };
BLOCK_INFO[BT.DIRT]   = { name:'Dirt',   color:0x8d6e63 };
BLOCK_INFO[BT.STONE]  = { name:'Stone',  color:0x9e9e9e };
BLOCK_INFO[BT.WOOD]   = { name:'Wood',   color:0x5d4037 };
BLOCK_INFO[BT.LEAVES] = { name:'Leaves', color:0x2e7d32 };
BLOCK_INFO[BT.SAND]   = { name:'Sand',   color:0xf6e5b3 };
BLOCK_INFO[BT.COBBLE] = { name:'Cobble', color:0x7a7a7a };

var HOTBAR = [BT.GRASS, BT.DIRT, BT.STONE, BT.WOOD, BT.LEAVES, BT.SAND, BT.COBBLE];

// ╔══════════════════════════════════════════════════════════════╗
// ║  State                                                      ║
// ╚══════════════════════════════════════════════════════════════╝

var blocks = new Map();
var meshGroup = new THREE.Group();
var highlightMesh = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01, 1.01, 1.01)),
  new THREE.LineBasicMaterial({ color:0xffffff, transparent:true, opacity:0.4 }),
);
highlightMesh.visible = false;

var player = {
  pos: new THREE.Vector3(0, 0, 0),
  vel: new THREE.Vector3(0, 0, 0),
  yaw: 0, pitch: 0,
  onGround: false,
};

var keys = new Set();
var selectedSlot = 0;
var pointerLocked = false;

// Mouse sensitivity — loaded from localStorage or URL param
var BASE_SENSITIVITY = 0.002;     // default baseline
var mouseSensitivity = BASE_SENSITIVITY;

// Load saved sensitivity
var saved = localStorage.getItem('mc_sensitivity');
if (saved !== null) {
  var parsed = parseFloat(saved);
  if (parsed >= 0.0005 && parsed <= 0.01) mouseSensitivity = parsed;
}
// URL param override: ?sensitivity=0.5  (multiplier relative to baseline)
var sensParam = new URLSearchParams(window.location.search).get('sensitivity');
if (sensParam !== null) {
  var mult = parseFloat(sensParam);
  if (mult >= 0.1 && mult <= 5) mouseSensitivity = BASE_SENSITIVITY * mult;
}

var scene, camera, renderer;
var dummyObj = new THREE.Object3D();
var _v = new THREE.Vector3();

// Mobs
var mobs = [];
var mobsGroup = new THREE.Group();
var MOB_COUNT = QUALITY.mobCount;

// ╔══════════════════════════════════════════════════════════════╗
// ║  Helpers                                                    ║
// ╚══════════════════════════════════════════════════════════════╝

function k(x, y, z) { return Math.floor(x)+','+Math.floor(y)+','+Math.floor(z); }

function getB(x, y, z) { return blocks.get(k(x, y, z)) || 0; }

function setB(x, y, z, type) {
  var key = k(x, y, z);
  if (type === 0) blocks.delete(key);
  else blocks.set(key, type);
}

function isSolid(x, y, z) { return getB(x, y, z) !== 0; }

function blockKey(pos) {
  return { x: Math.floor(pos.x), y: Math.floor(pos.y), z: Math.floor(pos.z) };
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Terrain generation                                         ║
// ╚══════════════════════════════════════════════════════════════╝

function terrainHeight(x, z) {
  return Math.floor(
    Math.sin(x * 0.18 + z * 0.13) * 2.5 +
    Math.sin(x * 0.09 + z * 0.11) * 2.0 +
    Math.cos(x * 0.05 - z * 0.07) * 1.2 +
    3
  );
}

function generateWorld() {
  // Ground layer
  for (var x = -WORLD_RADIUS; x <= WORLD_RADIUS; x++) {
    for (var z = -WORLD_RADIUS; z <= WORLD_RADIUS; z++) {
      var h = terrainHeight(x, z);
      for (var y = 0; y <= h; y++) {
        if (y === h)           setB(x, y, z, BT.GRASS);
        else if (y > h - 3)    setB(x, y, z, BT.DIRT);
        else                   setB(x, y, z, BT.STONE);
      }
    }
  }

  // Trees
  var area = (WORLD_RADIUS * 2 + 1) * (WORLD_RADIUS * 2 + 1);
  var treeCount = Math.floor(area * QUALITY.treeDensity);
  for (var t = 0; t < treeCount; t++) {
    var tx = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    var tz = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    var th = terrainHeight(tx, tz);

    // Trunk 4 blocks
    for (var y = th + 1; y <= th + 4; y++) setB(tx, y, tz, BT.WOOD);

    // Canopy
    for (var dx = -2; dx <= 2; dx++) {
      for (var dz = -2; dz <= 2; dz++) {
        var dist = Math.abs(dx) + Math.abs(dz);
        if (dist > 2 && Math.random() > 0.4) continue;
        for (var dy = 0; dy <= 2; dy++) {
          var ly = th + 4 + dy;
          if (ly > th + 6) continue;
          if (dx === 0 && dz === 0 && dy === 2) continue;
          setB(tx + dx, ly, tz + dz, BT.LEAVES);
        }
      }
    }
    setB(tx, th + 6, tz, BT.LEAVES);
  }

  rebuildMeshes();
  updateDebug();
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Mesh building                                              ║
// ╚══════════════════════════════════════════════════════════════╝

function rebuildMeshes() {
  while (meshGroup.children.length) {
    var child = meshGroup.children[0];
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
    meshGroup.remove(child);
  }

  var counts = {};
  var positions = {};
  for (var i = 0; i < HOTBAR.length; i++) {
    counts[HOTBAR[i]] = 0;
    positions[HOTBAR[i]] = [];
  }

  // First pass: count visible blocks only (skip surrounded)
  var iter = blocks.entries();
  for (var entry = iter.next(); !entry.done; entry = iter.next()) {
    var key = entry.value[0];
    var type = entry.value[1];
    if (!(type in counts)) continue;
    var parts = key.split(',');
    var x = parseInt(parts[0], 10);
    var y = parseInt(parts[1], 10);
    var z = parseInt(parts[2], 10);
    if (isSolid(x-1,y,z) && isSolid(x+1,y,z) && isSolid(x,y-1,z) &&
        isSolid(x,y,z-1) && isSolid(x,y,z+1)) continue;
    counts[type] = (counts[type] || 0) + 1;
    (positions[type] || (positions[type] = [])).push({ x:x, y:y, z:z });
  }

  var geo = new THREE.BoxGeometry(1, 1, 1);
  var dummy = new THREE.Object3D();

  for (var i = 0; i < HOTBAR.length; i++) {
    var type = HOTBAR[i];
    var cnt = counts[type] || 0;
    if (cnt === 0) continue;
    var info = BLOCK_INFO[type];
    var mat = new THREE.MeshLambertMaterial({ color: info.color });
    var im = new THREE.InstancedMesh(geo, mat, cnt);
    var idx = 0;
    var list = positions[type] || [];
    for (var j = 0; j < list.length; j++) {
      var p = list[j];
      dummy.position.set(p.x + 0.5, p.y + 0.5, p.z + 0.5);
      dummy.updateMatrix();
      im.setMatrixAt(idx++, dummy.matrix);
    }
    im.instanceMatrix.needsUpdate = true;
    im.userData.blockType = type;
    meshGroup.add(im);
  }

  scene.add(meshGroup);
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Friendly mobs (NPC villagers)                              ║
// ╚══════════════════════════════════════════════════════════════╝

// Terrain height from block data (accounts for player modifications)
function getGroundHeight(x, z) {
  var bx = Math.floor(x), bz = Math.floor(z);
  for (var y = 25; y >= -1; y--) {
    if (isSolid(bx, y, bz)) return y + 1;
  }
  return 0;
}

// Check if a position is walkable for a mob
function isWalkable(x, z) {
  var bx = Math.floor(x), bz = Math.floor(z);
  if (Math.abs(bx) >= WORLD_RADIUS || Math.abs(bz) >= WORLD_RADIUS) return false;
  var ground = getGroundHeight(x, z);
  if (ground <= 0 || ground > 20) return false;
  // Check body space: need 2 blocks clear above ground
  for (var y = Math.floor(ground); y < Math.floor(ground) + 2; y++) {
    if (isSolid(bx, y, bz)) return false;
  }
  return true;
}

// Find a random valid spawn position
function findMobSpawn() {
  for (var attempt = 0; attempt < 50; attempt++) {
    var x = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    var z = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    if (isWalkable(x, z)) return { x: x, z: z };
  }
  return null;
}

function createMob(x, z) {
  var ground = getGroundHeight(x, z);

  // Materials
  var skinMat  = new THREE.MeshLambertMaterial({ color: 0xe8b88a });
  var shirtMat = new THREE.MeshLambertMaterial({ color: 0x4a86c8 });
  var pantsMat = new THREE.MeshLambertMaterial({ color: 0x3a3a5a });

  var skinColors = [0xe8b88a, 0xd4a574, 0xc4956a, 0xf0caa8, 0xdeb887];
  var shirtColors = [0x4a86c8, 0xe74c3c, 0x2ecc71, 0xf39c12, 0x9b59b6, 0x1abc9c];
  skinMat.color.setHex(skinColors[Math.floor(Math.random() * skinColors.length)]);
  shirtMat.color.setHex(shirtColors[Math.floor(Math.random() * shirtColors.length)]);

  var group = new THREE.Group();

  // Head
  var head = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), skinMat);
  head.position.y = 1.4;
  group.add(head);

  // Eyes (two small dark dots)
  var eyeMat = new THREE.MeshLambertMaterial({ color: 0x222222 });
  var eyeGeo = new THREE.BoxGeometry(0.08, 0.08, 0.05);
  var eyeL = new THREE.Mesh(eyeGeo, eyeMat);
  eyeL.position.set(-0.15, 1.45, -0.3);
  group.add(eyeL);
  var eyeR = new THREE.Mesh(eyeGeo, eyeMat);
  eyeR.position.set(0.15, 1.45, -0.3);
  group.add(eyeR);

  // Body / torso
  var body = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.7, 0.35), shirtMat);
  body.position.y = 0.85;
  group.add(body);

  // Arms
  var armGeo = new THREE.BoxGeometry(0.18, 0.6, 0.18);
  var leftArm = new THREE.Mesh(armGeo, skinMat);
  leftArm.position.set(-0.44, 0.8, 0);
  group.add(leftArm);

  var rightArm = new THREE.Mesh(armGeo, skinMat);
  rightArm.position.set(0.44, 0.8, 0);
  group.add(rightArm);

  // Legs
  var legGeo = new THREE.BoxGeometry(0.22, 0.5, 0.22);
  var leftLeg = new THREE.Mesh(legGeo, pantsMat);
  leftLeg.position.set(-0.15, 0.3, 0);
  group.add(leftLeg);

  var rightLeg = new THREE.Mesh(legGeo, pantsMat);
  rightLeg.position.set(0.15, 0.3, 0);
  group.add(rightLeg);

  group.position.set(x, ground, z);
  group.castShadow = true;

  return {
    group: group,
    head: head, body: body,
    leftArm: leftArm, rightArm: rightArm,
    leftLeg: leftLeg, rightLeg: rightLeg,
    pos: { x: x, y: ground, z: z },
    dir: Math.random() * Math.PI * 2,
    speed: 0.8 + Math.random() * 0.6,
    state: 'idle',
    idleTimer: 1 + Math.random() * 4,
    walkTimer: 0,
    animTimer: Math.random() * 10,
    stuckCheck: { x: x, z: z, age: 0 },
  };
}

function spawnMobs() {
  // Clear any existing mobs from a quality hot-swap
  while (mobsGroup.children.length) {
    var child = mobsGroup.children[0];
    if (child.geometry) child.geometry.dispose();
    if (child.material) child.material.dispose();
    mobsGroup.remove(child);
  }
  mobs = [];

  for (var i = 0; i < MOB_COUNT; i++) {
    var spawn = findMobSpawn();
    if (!spawn) continue;
    var mob = createMob(spawn.x, spawn.z);
    mobs.push(mob);
    mobsGroup.add(mob.group);
  }
}

function updateMobs(dt) {
  dt = Math.min(dt, 0.05);

  for (var i = 0; i < mobs.length; i++) {
    var mob = mobs[i];
    mob.animTimer += dt;

    if (mob.state === 'idle') {
      mob.idleTimer -= dt;
      // Gentle idle sway
      mob.leftArm.rotation.x  = Math.sin(mob.animTimer * 1.5) * 0.06;
      mob.rightArm.rotation.x = Math.sin(mob.animTimer * 1.5 + Math.PI) * 0.06;
      mob.leftLeg.rotation.x  = 0;
      mob.rightLeg.rotation.x = 0;

      if (mob.idleTimer <= 0) {
        // Pick a new random direction
        mob.dir = (Math.random() * 2 - 1) * Math.PI;
        mob.walkTimer = 1.5 + Math.random() * 4;
        mob.state = 'walk';
        mob.stuckCheck.x = mob.pos.x;
        mob.stuckCheck.z = mob.pos.z;
        mob.stuckCheck.age = 0;
      }
    } else if (mob.state === 'walk') {
      // Calculate movement
      var dx = Math.sin(mob.group.rotation.y) * mob.speed * dt;
      var dz = Math.cos(mob.group.rotation.y) * mob.speed * dt;
      var nx = mob.pos.x + dx;
      var nz = mob.pos.z + dz;

      // Check if the new spot is walkable
      if (isWalkable(nx, nz)) {
        var gnd = getGroundHeight(nx, nz);
        mob.pos.x = nx;
        mob.pos.z = nz;
        mob.pos.y = gnd;
      } else {
        // Turn away from obstacle
        mob.dir = mob.dir + Math.PI * (0.6 + Math.random() * 0.8);
      }

      mob.walkTimer -= dt;

      // Stuck detection: haven't moved enough in ~2 seconds
      mob.stuckCheck.age += dt;
      if (mob.stuckCheck.age > 2) {
        var dist = Math.sqrt(
          (mob.pos.x - mob.stuckCheck.x) * (mob.pos.x - mob.stuckCheck.x) +
          (mob.pos.z - mob.stuckCheck.z) * (mob.pos.z - mob.stuckCheck.z)
        );
        if (dist < 0.5) {
          mob.dir += Math.PI * 0.8;
          mob.walkTimer = Math.min(mob.walkTimer, 1);
        }
        mob.stuckCheck.x = mob.pos.x;
        mob.stuckCheck.z = mob.pos.z;
        mob.stuckCheck.age = 0;
      }

      // Walking animation: swing arms and legs
      var swing = Math.sin(mob.animTimer * 7) * 0.6;
      mob.leftArm.rotation.x  = swing;
      mob.rightArm.rotation.x = -swing;
      mob.leftLeg.rotation.x  = -swing * 0.7;
      mob.rightLeg.rotation.x = swing * 0.7;

      if (mob.walkTimer <= 0) {
        mob.idleTimer = 0.8 + Math.random() * 3;
        mob.state = 'idle';
      }
    }

    // Update group position and rotation
    mob.group.position.set(mob.pos.x, mob.pos.y, mob.pos.z);

    // Face direction of travel (instant snap — no lerp to avoid backwards walking)
    if (mob.state === 'walk') {
      mob.group.rotation.y = mob.dir;
    }
  }
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Raycaster                                                  ║
// ╚══════════════════════════════════════════════════════════════╝

function intersectBlocks() {
  var dir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
  var ray = new THREE.Raycaster(camera.position, dir, 0, REACH);
  ray.firstHitOnly = true;

  var hits = ray.intersectObjects(meshGroup.children, false);
  if (hits.length === 0) return null;

  var hit = hits[0];

  if (hit.object.isInstancedMesh && hit.instanceId !== undefined) {
    hit.object.getMatrixAt(hit.instanceId, dummyObj.matrix);
    dummyObj.matrix.decompose(_v, dummyObj.quaternion, dummyObj.scale);
    var bx = Math.floor(_v.x - 0.5);
    var by = Math.floor(_v.y - 0.5);
    var bz = Math.floor(_v.z - 0.5);
    return {
      x: bx, y: by, z: bz,
      type: getB(bx, by, bz),
      normal: hit.face.normal.clone().round(),
    };
  }
  return null;
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Block interaction                                          ║
// ╚══════════════════════════════════════════════════════════════╝

function breakBlock() {
  var t = intersectBlocks();
  if (!t) return;
  setB(t.x, t.y, t.z, 0);
  rebuildMeshes();
}

function placeBlock() {
  var t = intersectBlocks();
  if (!t) return;
  var px = t.x + t.normal.x;
  var py = t.y + t.normal.y;
  var pz = t.z + t.normal.z;

  var pp = blockKey(camera.position);
  if (px === pp.x && py === pp.y && pz === pp.z) return;
  if (px === pp.x && py === pp.y + 1 && pz === pp.z) return;

  if (!isSolid(px, py, pz)) {
    setB(px, py, pz, HOTBAR[selectedSlot]);
    rebuildMeshes();
  }
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Pointer lock                                               ║
// ╚══════════════════════════════════════════════════════════════╝

function initPointerLock() {
  var blocker = document.getElementById('blocker');
  blocker.addEventListener('click', function() {
    renderer.domElement.requestPointerLock();
  });

  document.addEventListener('pointerlockchange', function() {
    pointerLocked = document.pointerLockElement === renderer.domElement;
    blocker.style.display = pointerLocked ? 'none' : 'flex';
    renderer.domElement.style.cursor = pointerLocked ? 'none' : '';
  });

  document.addEventListener('mousemove', function(e) {
    if (!pointerLocked) return;
    player.yaw   -= e.movementX * mouseSensitivity;
    player.pitch -= e.movementY * mouseSensitivity;
    player.pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, player.pitch));
  });
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Keyboard                                                   ║
// ╚══════════════════════════════════════════════════════════════╝

function initKeyboard() {
  document.addEventListener('keydown', function(e) {
    keys.add(e.code);
    if (e.code.startsWith('Digit') && !e.repeat) {
      var n = parseInt(e.code.charAt(5), 10);
      if (n >= 1 && n <= HOTBAR.length) { selectedSlot = n - 1; updateHotbar(); }
    }

    // Quality hot-swap for testing: Ctrl+Q cycles low→medium→high→ultra
    if (e.code === 'KeyQ' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      var tiers = ['low','medium','high','ultra'];
      var idx = tiers.indexOf(QUALITY.tier.toLowerCase());
      var next = tiers[(idx + 1) % tiers.length];
      console.log('[Quality] Hot-swap to ' + next);
      applyQuality(next);
      WORLD_RADIUS = QUALITY.worldRadius;
      MOB_COUNT = QUALITY.mobCount;
      blocks.clear();
      generateWorld();
      spawnMobs();
    }

    // Mouse sensitivity: [ decrease, ] increase
    if (e.code === 'BracketLeft' && !e.repeat) {
      e.preventDefault();
      mouseSensitivity = Math.max(0.0005, mouseSensitivity - 0.00025);
      localStorage.setItem('mc_sensitivity', '' + mouseSensitivity);
      showSensitivityToast();
    }
    if (e.code === 'BracketRight' && !e.repeat) {
      e.preventDefault();
      mouseSensitivity = Math.min(0.01, mouseSensitivity + 0.00025);
      localStorage.setItem('mc_sensitivity', '' + mouseSensitivity);
      showSensitivityToast();
    }
  });
  document.addEventListener('keyup', function(e) { keys.delete(e.code); });
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Player movement                                            ║
// ╚══════════════════════════════════════════════════════════════╝

function updatePlayer(dt) {
  if (!pointerLocked) return;
  dt = Math.min(dt, 0.05);

  var forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
  var right   = new THREE.Vector3( Math.cos(player.yaw), 0, -Math.sin(player.yaw));

  var move = new THREE.Vector3();
  if (keys.has('KeyW') || keys.has('ArrowUp'))    move.add(forward);
  if (keys.has('KeyS') || keys.has('ArrowDown'))   move.sub(forward);
  if (keys.has('KeyA') || keys.has('ArrowLeft'))   move.sub(right);
  if (keys.has('KeyD') || keys.has('ArrowRight'))  move.add(right);
  if (move.lengthSq() > 0) move.normalize();

  var speed = (keys.has('ShiftLeft') || keys.has('ShiftRight')) ? SNEAK_SPEED : WALK_SPEED;
  move.multiplyScalar(speed * dt);

  if (keys.has('Space') && player.onGround) {
    player.vel.y = JUMP_SPEED;
    player.onGround = false;
  }

  player.vel.y += GRAVITY * dt;

  var pos = player.pos;
  var r = PLAYER_RADIUS;
  var h = PLAYER_HEIGHT;

  function collide(px, py, pz) {
    var minX = Math.floor(px - r), maxX = Math.floor(px + r);
    var minY = Math.floor(py),     maxY = Math.floor(py + h);
    var minZ = Math.floor(pz - r), maxZ = Math.floor(pz + r);
    for (var cx = minX; cx <= maxX; cx++) {
      for (var cy = minY; cy <= maxY; cy++) {
        for (var cz = minZ; cz <= maxZ; cz++) {
          if (isSolid(cx, cy, cz)) return true;
        }
      }
    }
    return false;
  }

  var nx = pos.x + move.x;
  if (!collide(nx, pos.y, pos.z)) pos.x = nx;

  var nz = pos.z + move.z;
  if (!collide(pos.x, pos.y, nz)) pos.z = nz;

  var ny = pos.y + player.vel.y * dt;
  if (!collide(pos.x, ny, pos.z)) {
    pos.y = ny;
    player.onGround = false;
  } else {
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  }

  if (pos.y < -10) {
    var sh = terrainHeight(0, 0);
    pos.set(0, sh + 3, 0);
    player.vel.set(0, 0, 0);
  }
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Camera                                                     ║
// ╚══════════════════════════════════════════════════════════════╝

function updateCamera() {
  camera.position.set(player.pos.x, player.pos.y + PLAYER_HEIGHT, player.pos.z);
  var euler = new THREE.Euler(player.pitch, player.yaw, 0, 'YXZ');
  camera.quaternion.setFromEuler(euler);
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Highlight                                                  ║
// ╚══════════════════════════════════════════════════════════════╝

function updateHighlight() {
  var t = intersectBlocks();
  if (t) {
    highlightMesh.position.set(t.x + 0.5, t.y + 0.5, t.z + 0.5);
    highlightMesh.visible = true;
  } else {
    highlightMesh.visible = false;
  }
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  UI                                                         ║
// ╚══════════════════════════════════════════════════════════════╝

function buildHotbar() {
  var el = document.getElementById('hotbar');
  el.innerHTML = '';
  for (var i = 0; i < HOTBAR.length; i++) {
    var type = HOTBAR[i];
    var info = BLOCK_INFO[type];
    var slot = document.createElement('div');
    slot.className = 'slot' + (i === selectedSlot ? ' active' : '');
    slot.dataset.index = i;

    var keyLbl = document.createElement('span');
    keyLbl.className = 'key-label';
    keyLbl.textContent = '' + (i + 1);
    slot.appendChild(keyLbl);

    var preview = document.createElement('div');
    preview.className = 'block-preview';
    var hex = info.color.toString(16);
    while (hex.length < 6) hex = '0' + hex;
    preview.style.background = '#' + hex;
    slot.appendChild(preview);

    var nameLbl = document.createElement('span');
    nameLbl.className = 'slot-name';
    nameLbl.textContent = info.name;
    slot.appendChild(nameLbl);

    slot.addEventListener('click', (function(idx) {
      return function() { selectedSlot = idx; updateHotbar(); };
    })(i));

    el.appendChild(slot);
  }
}

function updateHotbar() {
  var slots = document.querySelectorAll('.slot');
  for (var i = 0; i < slots.length; i++) {
    slots[i].classList.toggle('active', i === selectedSlot);
  }
}

function updateDebug() {
  var el = document.getElementById('debug');
  if (!el) return;
  var p = player.pos;
  var sensMult = (mouseSensitivity / BASE_SENSITIVITY).toFixed(2);
  el.innerHTML =
    'XYZ: ' + p.x.toFixed(1) + ' / ' + p.y.toFixed(1) + ' / ' + p.z.toFixed(1) +
    '  |  Blocks: ' + blocks.size +
    '  |  Mobs: ' + mobs.length +
    '  |  Meshes: ' + meshGroup.children.length +
    '  |  <span style="color:#5cdb5c">' + QUALITY.tier + '</span>' +
    '  |  Sens: <span id="sens-val">' + sensMult + 'x</span>';
}

// Toast notification for sensitivity changes
var sensToastTimeout = null;
function showSensitivityToast() {
  // Remove old toast
  var old = document.getElementById('sens-toast');
  if (old) old.parentNode.removeChild(old);

  var mult = (mouseSensitivity / BASE_SENSITIVITY).toFixed(2);
  var toast = document.createElement('div');
  toast.id = 'sens-toast';
  toast.style.cssText =
    'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);' +
    'background:rgba(0,0,0,0.75);color:#5cdb5c;padding:10px 24px;' +
    'border-radius:6px;font:14px/1 monospace;z-index:20;' +
    'transition:opacity 0.3s;pointer-events:none;';
  toast.textContent = 'Sensitivity: ' + mult + 'x  (' + mouseSensitivity.toFixed(5) + ')';
  document.body.appendChild(toast);

  // Also update the inline sens value if it exists
  var v = document.getElementById('sens-val');
  if (v) v.textContent = mult + 'x';

  // Clear any previous fade timer
  if (sensToastTimeout) clearTimeout(sensToastTimeout);
  sensToastTimeout = setTimeout(function() {
    toast.style.opacity = '0';
    setTimeout(function() { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 400);
  }, 1500);
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Mouse events                                               ║
// ╚══════════════════════════════════════════════════════════════╝

function initMouseActions() {
  renderer.domElement.addEventListener('mousedown', function(e) {
    if (!pointerLocked) return;
    if (e.button === 0) breakBlock();
    if (e.button === 2) placeBlock();
  });
  renderer.domElement.addEventListener('contextmenu', function(e) { e.preventDefault(); });
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Init                                                       ║
// ╚══════════════════════════════════════════════════════════════╝

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb);
  scene.fog = new THREE.Fog(0x87ceeb, QUALITY.fogNear, QUALITY.fogFar);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, QUALITY.fogFar * 2);

  renderer = new THREE.WebGLRenderer({ antialias: QUALITY.antialias });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(QUALITY.pixelRatio);

  if (QUALITY.shadows) {
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  }

  document.body.prepend(renderer.domElement);

  // Lights
  var ambient = new THREE.AmbientLight(0x6688aa, 0.6);
  scene.add(ambient);

  var sun = new THREE.DirectionalLight(0xffeedd, 1.4);
  sun.position.set(50, 80, 30);
  if (QUALITY.shadows) {
    sun.castShadow = true;
    sun.shadow.mapSize.set(QUALITY.shadowMapSize, QUALITY.shadowMapSize);
    sun.shadow.camera.near = 0.5;
    sun.shadow.camera.far = 200;
    var s = QUALITY.worldRadius * 2.5;
    sun.shadow.camera.left = -s;
    sun.shadow.camera.right = s;
    sun.shadow.camera.top = s;
    sun.shadow.camera.bottom = -s;
  }
  scene.add(sun);

  var hemi = new THREE.HemisphereLight(0x87ceeb, 0x3a4a2e, 0.3);
  scene.add(hemi);

  scene.add(highlightMesh);
  scene.add(meshGroup);
  scene.add(mobsGroup);

  // Generate world
  generateWorld();

  // Spawn friendly mobs
  spawnMobs();

  // Place player above terrain centre
  var sh = terrainHeight(0, 0);
  player.pos.set(0, sh + 3, 0);

  // Events
  initPointerLock();
  initKeyboard();
  initMouseActions();
  buildHotbar();

  // Resize
  window.addEventListener('resize', function() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // Show quality tier on the blocker overlay
  var blockQ = document.getElementById('quality-badge');
  if (blockQ) blockQ.textContent = 'Quality: ' + QUALITY.tier;

  var debugEl = document.getElementById('debug');
  if (debugEl) debugEl.innerHTML = 'Ready — click to play  |  <span style="color:#5cdb5c">' + QUALITY.tier + '</span>  |  Sens: <span id="sens-val">' + (mouseSensitivity / BASE_SENSITIVITY).toFixed(2) + 'x</span>';

  // Kick off
  animate(performance.now());
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Game loop                                                  ║
// ╚══════════════════════════════════════════════════════════════╝

var prevTime = performance.now();

function animate(time) {
  requestAnimationFrame(animate);
  var dt = (time - prevTime) / 1000;
  prevTime = time;

  updatePlayer(dt);
  updateMobs(dt);
  updateCamera();
  updateHighlight();
  updateDebug();

  renderer.render(scene, camera);
}

// ╔══════════════════════════════════════════════════════════════╗
// ║  Go                                                         ║
// ╚══════════════════════════════════════════════════════════════╝

init();
