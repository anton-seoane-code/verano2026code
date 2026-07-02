// ═══════════════════════════════════════════════════════════════
// Minecraft-style 3D voxel world — Three.js
// ═══════════════════════════════════════════════════════════════
import * as THREE from 'three';

// ─── Constants ────────────────────────────────────────────────
const WORLD_RADIUS   = 20;         // world is -R .. +R on X and Z
const GRAVITY        = -28;
const JUMP_SPEED     = 10;
const WALK_SPEED     = 5;
const SNEAK_SPEED    = 2;
const REACH          = 7;
const PLAYER_HEIGHT  = 1.62;
const PLAYER_RADIUS  = 0.3;

const BT = {                // block-type constants
  AIR:0, GRASS:1, DIRT:2, STONE:3,
  WOOD:4, LEAVES:5, SAND:6, COBBLE:7,
};

const BLOCK_INFO = {
  [BT.GRASS]:  { name:'Grass',  color:0x7cb342, top:0x7cb342, side:0x8d6e63 },
  [BT.DIRT]:   { name:'Dirt',   color:0x8d6e63 },
  [BT.STONE]:  { name:'Stone',  color:0x9e9e9e },
  [BT.WOOD]:   { name:'Wood',   color:0x5d4037 },
  [BT.LEAVES]: { name:'Leaves', color:0x2e7d32 },
  [BT.SAND]:   { name:'Sand',   color:0xf6e5b3 },
  [BT.COBBLE]: { name:'Cobble', color:0x7a7a7a },
};

const HOTBAR = [BT.GRASS, BT.DIRT, BT.STONE, BT.WOOD, BT.LEAVES, BT.SAND, BT.COBBLE];

// ─── State ────────────────────────────────────────────────────
const blocks = new Map();            // "x,y,z" → block-type
const meshGroup = new THREE.Group(); // all visible block meshes
const highlightMesh = new THREE.LineSegments(
  new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01, 1.01, 1.01)),
  new THREE.LineBasicMaterial({ color:0xffffff, transparent:true, opacity:0.4 }),
);
highlightMesh.visible = false;

const player = {
  pos: new THREE.Vector3(0, 0, 0),
  vel: new THREE.Vector3(0, 0, 0),
  yaw: 0, pitch: 0,
  onGround: false,
};

const keys = new Set();              // currently-pressed key set
let selectedSlot = 0;
let pointerLocked = false;

// Three.js objects (set up in init)
let scene, camera, renderer;

// ─── Helpers ──────────────────────────────────────────────────
const _v = new THREE.Vector3();

function k(x, y, z) { return `${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`; }

function getB(x, y, z) { return blocks.get(k(x, y, z)) || 0; }

function setB(x, y, z, type) {
  const key = k(x, y, z);
  if (type === 0) blocks.delete(key);
  else blocks.set(key, type);
}

function isSolid(x, y, z) { return getB(x, y, z) !== 0; }

function blockKey(pos) {
  return { x: Math.floor(pos.x), y: Math.floor(pos.y), z: Math.floor(pos.z) };
}

// ─── Terrain generation ──────────────────────────────────────
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
  for (let x = -WORLD_RADIUS; x <= WORLD_RADIUS; x++) {
    for (let z = -WORLD_RADIUS; z <= WORLD_RADIUS; z++) {
      const h = terrainHeight(x, z);
      for (let y = 0; y <= h; y++) {
        if (y === h)           setB(x, y, z, BT.GRASS);
        else if (y > h - 3)    setB(x, y, z, BT.DIRT);
        else                   setB(x, y, z, BT.STONE);
      }
    }
  }

  // Trees (scattered)
  const treeCount = Math.floor((WORLD_RADIUS * 2) ** 2 * 0.008);
  for (let t = 0; t < treeCount; t++) {
    const tx = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    const tz = Math.floor(Math.random() * (WORLD_RADIUS * 2 - 8)) - WORLD_RADIUS + 4;
    const th = terrainHeight(tx, tz);

    // Trunk 4 blocks tall
    for (let y = th + 1; y <= th + 4; y++) setB(tx, y, tz, BT.WOOD);

    // Canopy
    for (let dx = -2; dx <= 2; dx++) {
      for (let dz = -2; dz <= 2; dz++) {
        const dist = Math.abs(dx) + Math.abs(dz);
        if (dist > 2 && Math.random() > 0.4) continue;
        for (let dy = 0; dy <= 2; dy++) {
          const ly = th + 4 + dy;
          if (ly > th + 6) continue;
          if (dx === 0 && dz === 0 && dy === 2) continue; // leave top centre clear-ish
          setB(tx + dx, ly, tz + dz, BT.LEAVES);
        }
      }
    }
    // Cap
    setB(tx, th + 6, tz, BT.LEAVES);
  }

  rebuildMeshes();
  updateDebug();
}

// ─── Mesh building ───────────────────────────────────────────
function rebuildMeshes() {
  // Remove old children
  while (meshGroup.children.length) {
    const child = meshGroup.children[0];
    child.geometry?.dispose();
    child.material?.dispose();
    meshGroup.remove(child);
  }

  // Pre-count visible blocks per type for InstancedMesh
  const counts = {};
  const positions = {};
  for (const type of HOTBAR) { counts[type] = 0; positions[type] = []; }

  // First pass: count visible blocks
  for (const [key, type] of blocks) {
    if (!HOTBAR.includes(type)) continue;
    const [x, y, z] = key.split(',').map(Number);
    if (isSolid(x-1,y,z) && isSolid(x+1,y,z) && isSolid(x,y-1,z) &&
        isSolid(x,y,z-1) && isSolid(x,y,z+1)) continue; // fully buried
    counts[type] = (counts[type] || 0) + 1;
    (positions[type] = positions[type] || []).push({ x, y, z });
  }

  // Second pass: create InstancedMesh for each type
  const geo = new THREE.BoxGeometry(1, 1, 1);
  const dummy = new THREE.Object3D();

  for (const type of HOTBAR) {
    const cnt = counts[type] || 0;
    if (cnt === 0) continue;
    const info = BLOCK_INFO[type];
    const mat = new THREE.MeshLambertMaterial({ color: info.color });
    const im = new THREE.InstancedMesh(geo, mat, cnt);
    let idx = 0;
    for (const p of (positions[type] || [])) {
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

// ─── Raycaster helpers ────────────────────────────────────────
const _ray = new THREE.Raycaster();

function intersectBlocks() {
  const dir = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
  _ray.set(camera.position, dir);
  _ray.far = REACH;
  _ray.firstHitOnly = true;

  const hits = _ray.intersectObjects(meshGroup.children, false);
  if (hits.length === 0) return null;

  const hit = hits[0];

  // Recover block position from InstancedMesh
  if (hit.object.isInstancedMesh && hit.instanceId !== undefined) {
    dummyObj.getWorldPosition(_v);
    hit.object.getMatrixAt(hit.instanceId, dummyObj.matrix);
    dummyObj.matrix.decompose(_v, dummyObj.quaternion, dummyObj.scale);
    const bx = Math.floor(_v.x - 0.5);
    const by = Math.floor(_v.y - 0.5);
    const bz = Math.floor(_v.z - 0.5);
    return {
      x: bx, y: by, z: bz,
      type: getB(bx, by, bz),
      normal: hit.face.normal.clone().round(),
    };
  }
  return null;
}

const dummyObj = new THREE.Object3D();

// ─── Block breaking / placing ────────────────────────────────
function breakBlock() {
  const t = intersectBlocks();
  if (!t) return;
  setB(t.x, t.y, t.z, 0);
  rebuildMeshes();
}

function placeBlock() {
  const t = intersectBlocks();
  if (!t) return;
  const px = t.x + t.normal.x;
  const py = t.y + t.normal.y;
  const pz = t.z + t.normal.z;

  // Don't place inside player
  const pp = blockKey(camera.position);
  if (px === pp.x && py === pp.y && pz === pp.z) return;
  // Or inside player's head
  if (px === pp.x && py === pp.y + 1 && pz === pp.z) return;

  if (!isSolid(px, py, pz)) {
    setB(px, py, pz, HOTBAR[selectedSlot]);
    rebuildMeshes();
  }
}

// ─── Pointer lock ────────────────────────────────────────────
function initPointerLock() {
  const blocker = document.getElementById('blocker');
  blocker.addEventListener('click', () => {
    renderer.domElement.requestPointerLock();
  });

  document.addEventListener('pointerlockchange', () => {
    pointerLocked = document.pointerLockElement === renderer.domElement;
    blocker.style.display = pointerLocked ? 'none' : 'flex';
  });

  document.addEventListener('mousemove', (e) => {
    if (!pointerLocked) return;
    player.yaw   -= e.movementX * 0.002;
    player.pitch -= e.movementY * 0.002;
    player.pitch = Math.max(-Math.PI / 2.2, Math.min(Math.PI / 2.2, player.pitch));
  });
}

// ─── Keyboard ────────────────────────────────────────────────
function initKeyboard() {
  document.addEventListener('keydown', (e) => {
    keys.add(e.code);
    if (e.code.startsWith('Digit') && !e.repeat) {
      const n = parseInt(e.code[5], 10);
      if (n >= 1 && n <= HOTBAR.length) { selectedSlot = n - 1; updateHotbar(); }
    }
  });
  document.addEventListener('keyup', (e) => keys.delete(e.code));
}

// ─── Player movement (per frame) ─────────────────────────────
function updatePlayer(dt) {
  if (!pointerLocked) return;

  // Clamp delta to avoid physics blowup on tab-away
  dt = Math.min(dt, 0.05);

  // Movement direction (XZ plane, relative to yaw)
  const forward = new THREE.Vector3(-Math.sin(player.yaw), 0, -Math.cos(player.yaw));
  const right   = new THREE.Vector3( Math.cos(player.yaw), 0, -Math.sin(player.yaw));

  const move = new THREE.Vector3();
  if (keys.has('KeyW') || keys.has('ArrowUp'))    move.add(forward);
  if (keys.has('KeyS') || keys.has('ArrowDown'))   move.sub(forward);
  if (keys.has('KeyA') || keys.has('ArrowLeft'))   move.sub(right);
  if (keys.has('KeyD') || keys.has('ArrowRight'))  move.add(right);
  if (move.lengthSq() > 0) move.normalize();

  const speed = keys.has('ShiftLeft') || keys.has('ShiftRight') ? SNEAK_SPEED : WALK_SPEED;
  move.multiplyScalar(speed * dt);

  // Jump
  if ((keys.has('Space')) && player.onGround) {
    player.vel.y = JUMP_SPEED;
    player.onGround = false;
  }

  // Gravity
  player.vel.y += GRAVITY * dt;

  // ── Collision (axis-separated) ──
  const pos = player.pos;
  const r = PLAYER_RADIUS;
  const h = PLAYER_HEIGHT;

  // Helper: AABB overlap test against world blocks
  function collide(px, py, pz) {
    const minX = Math.floor(px - r), maxX = Math.floor(px + r);
    const minY = Math.floor(py),     maxY = Math.floor(py + h);
    const minZ = Math.floor(pz - r), maxZ = Math.floor(pz + r);
    for (let x = minX; x <= maxX; x++) {
      for (let y = minY; y <= maxY; y++) {
        for (let z = minZ; z <= maxZ; z++) {
          if (isSolid(x, y, z)) return true;
        }
      }
    }
    return false;
  }

  // Try X
  const nx = pos.x + move.x;
  if (!collide(nx, pos.y, pos.z)) pos.x = nx;

  // Try Z
  const nz = pos.z + move.z;
  if (!collide(pos.x, pos.y, nz)) pos.z = nz;

  // Try Y (gravity + jump)
  const ny = pos.y + player.vel.y * dt;
  if (!collide(pos.x, ny, pos.z)) {
    pos.y = ny;
    player.onGround = false;
  } else {
    if (player.vel.y < 0) player.onGround = true;
    player.vel.y = 0;
  }

  // Don't fall below world
  if (pos.y < -10) {
    // Respawn at spawn point
    const sh = terrainHeight(0, 0);
    pos.set(0, sh + 3, 0);
    player.vel.set(0, 0, 0);
  }
}

// ─── Camera ──────────────────────────────────────────────────
function updateCamera() {
  // Camera at eye level
  camera.position.set(player.pos.x, player.pos.y + PLAYER_HEIGHT, player.pos.z);

  // Apply yaw + pitch
  const euler = new THREE.Euler(player.pitch, player.yaw, 0, 'YXZ');
  camera.quaternion.setFromEuler(euler);
}

// ─── Highlight ───────────────────────────────────────────────
function updateHighlight() {
  const t = intersectBlocks();
  if (t) {
    highlightMesh.position.set(t.x + 0.5, t.y + 0.5, t.z + 0.5);
    highlightMesh.visible = true;
  } else {
    highlightMesh.visible = false;
  }
}

// ─── UI ──────────────────────────────────────────────────────
function buildHotbar() {
  const el = document.getElementById('hotbar');
  el.innerHTML = '';
  HOTBAR.forEach((type, i) => {
    const info = BLOCK_INFO[type];
    const slot = document.createElement('div');
    slot.className = 'slot' + (i === selectedSlot ? ' active' : '');
    slot.dataset.index = i;

    const keyLbl = document.createElement('span');
    keyLbl.className = 'key-label';
    keyLbl.textContent = i + 1;
    slot.appendChild(keyLbl);

    const preview = document.createElement('div');
    preview.className = 'block-preview';
    preview.style.background = '#' + info.color.toString(16).padStart(6, '0');
    slot.appendChild(preview);

    const nameLbl = document.createElement('span');
    nameLbl.className = 'slot-name';
    nameLbl.textContent = info.name;
    slot.appendChild(nameLbl);

    // Click to select
    slot.addEventListener('click', () => {
      selectedSlot = i;
      updateHotbar();
    });

    el.appendChild(slot);
  });
}

function updateHotbar() {
  const slots = document.querySelectorAll('.slot');
  slots.forEach((s, i) => s.classList.toggle('active', i === selectedSlot));
}

const debugEl = document.getElementById('debug');

function updateDebug() {
  const p = player.pos;
  debugEl.textContent =
    `XYZ: ${p.x.toFixed(1)} / ${p.y.toFixed(1)} / ${p.z.toFixed(1)}  |  ` +
    `Blocks: ${blocks.size}  |  ` +
    `Meshes: ${meshGroup.children.length}`;
}

// ─── Mouse events (from outside pointer lock) ────────────────
function initMouseActions() {
  renderer.domElement.addEventListener('mousedown', (e) => {
    if (!pointerLocked) return;
    if (e.button === 0) breakBlock();   // left
    if (e.button === 2) placeBlock();   // right
  });
  renderer.domElement.addEventListener('contextmenu', (e) => e.preventDefault());
}

// ─── Init ────────────────────────────────────────────────────
function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x87ceeb); // sky blue
  scene.fog = new THREE.Fog(0x87ceeb, 50, 80);

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 200);
  camera.position.set(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.prepend(renderer.domElement);

  // Lights
  const ambient = new THREE.AmbientLight(0x6688aa, 0.6);
  scene.add(ambient);

  const sun = new THREE.DirectionalLight(0xffeedd, 1.4);
  sun.position.set(50, 80, 30);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.near = 0.5;
  sun.shadow.camera.far = 200;
  sun.shadow.camera.left = -60;
  sun.shadow.camera.right = 60;
  sun.shadow.camera.top = 60;
  sun.shadow.camera.bottom = -60;
  scene.add(sun);

  const hemi = new THREE.HemisphereLight(0x87ceeb, 0x3a4a2e, 0.3);
  scene.add(hemi);

  // Highlight overlay
  scene.add(highlightMesh);

  // Ground grid — decorative, not essential
  scene.add(meshGroup);

  // Generate world
  generateWorld();

  // Place player above terrain centre
  const sh = terrainHeight(0, 0);
  player.pos.set(0, sh + 3, 0);

  // Events
  initPointerLock();
  initKeyboard();
  initMouseActions();
  buildHotbar();

  // Resize
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  debugEl.textContent = 'Ready — click to play';
}

// ─── Game loop ────────────────────────────────────────────────
let prevTime = performance.now();

function animate(time) {
  requestAnimationFrame(animate);
  const dt = (time - prevTime) / 1000;
  prevTime = time;

  updatePlayer(dt);
  updateCamera();
  updateHighlight();
  updateDebug();

  renderer.render(scene, camera);
}

// ─── Go ──────────────────────────────────────────────────────
init();
animate(performance.now());
