# Advanced Games — Unity Project

## Project Info
- Unity Version: Unity 6 LTS (`6000.5.3f1`)
- Template: 3D Core
- Render Pipeline: Universal Render Pipeline (URP)
- Scripting Backend: Mono
- Target Platform: Standalone (PC/Mac/Linux)
- Theme: Ancient Ruins (First-Person Exploration)

## Quick Start

The game bootstraps entirely at runtime via `GameBootstrap.cs`. No manual scene setup required.
1. Open the project in Unity
2. Create an empty scene (or use any scene)
3. Add an empty GameObject with `GameBootstrap` component
4. Press Play — environment, player, and all systems are created automatically

## Setup Guide

### 1. Install Unity Hub + Editor

#### Option A: APT (Ubuntu/Debian with sudo)
```bash
curl -fsSL https://hub.unity3d.com/linux/keys/public | sudo gpg --dearmor -o /etc/apt/keyrings/unityhub.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/unityhub.gpg] https://hub.unity3d.com/linux/repos/deb stable main" | sudo tee /etc/apt/sources.list.d/unityhub.list
sudo apt update && sudo apt install unityhub
```
Launch Unity Hub, sign in, install Unity 6 LTS.

#### Option B: AppImage (no sudo)
```bash
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage
chmod +x UnityHubSetup.AppImage
./UnityHubSetup.AppImage
```

### 2. Install MCP for Unity
In Unity Editor:
- Window → Package Manager → + → Add package from git URL:
  ```
  https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity
  ```
- Window → MCP for Unity → Configure All Detected Clients
- Verify MCP status shows "Connected"

### 3. Connect OpenCode to Unity
- The root `opencode.json` already contains the unity3d-mcp config
- OpenCode → `/mcp` → toggle unity3d-mcp to Enabled
- Test: "List all GameObjects in the current scene"

## C# Script Reference

### Core Scripts

#### GameBootstrap.cs
Runtime scene assembler. Attach to any GameObject in an empty scene and press Play.
Creates: Player (with camera, controller, HUD, interaction), EnvironmentManager, GameManager, AudioManager.

#### PlayerController.cs
First-person Rigidbody controller with sprint and crouch.
- `speed` (float): walk speed, default 8
- `sprintSpeed` (float): sprint speed, default 14
- `crouchSpeed` (float): crouch speed, default 3
- `jumpForce` (float): jump impulse, default 5
- `airControlMultiplier` (float): air movement factor, default 0.4
- `maxStamina` (float): sprint stamina pool, default 100
- `staminaDrainRate` (float): stamina drain per second, default 20
- `staminaRegenRate` (float): stamina regen per second, default 15
- `crouchHeight` (float): collider height when crouched, default 0.8
- `standHeight` (float): collider height when standing, default 1.8
- `mouseSensitivity` (float): look sensitivity, default 2
- `maxLookAngle` (float): vertical look clamp, default 80

Controls: WASD move, Space jump, Shift sprint, Ctrl crouch, Mouse look.

#### InteractionSystem.cs
Raycast-based interaction from camera forward.
- `interactionRange` (float): max interaction distance, default 5
- Requires: Camera reference (auto-assigned by GameBootstrap)

Controls: E to interact with any `Interactable` object in range.

#### Interactable.cs
Base component for interactable world objects. Attach to any GameObject.
- `interactionPrompt` (string): text shown on hover, default "Interact"
- Override `OnInteract(GameObject interactor)` for custom behavior

### UI & Feedback

#### PlayerHUD.cs
IMGUI-based HUD drawn at runtime.
- Crosshair (centered, changes color when looking at interactable)
- Stamina bar (bottom-left, red when depleted)
- Interaction prompt (centered below crosshair)
- Discovery counter (top-right)

### Environment

#### EnvironmentManager.cs
Procedurally generates the ancient ruins environment at runtime.
- Ground plane (120x120 units)
- Stone path network (cross pattern)
- 18 pillars (varying heights, some broken)
- 8 wall segments (scattered ruins)
- 25 trees (trunk + sphere canopy)
- 12 ruin piles (scattered rocks)
- Central altar with 4 posts
- Directional light, fog, ambient lighting

### Managers

#### GameManager.cs
Singleton. Tracks discovery progress.
- `Discoveries` (int): current count
- `TotalDiscoveries` (int): registered count
- `RegisterDiscoverable()`: add a discovery point
- `Discover()`: mark one as found

#### AudioManager.cs
Singleton. Handles footstep and ambient audio.
- `footstepClips` (AudioClip[]): footstep sounds (assign in inspector)
- `ambientClip` (AudioClip): ambient loop
- `walkStepInterval` / `sprintStepInterval`: timing
- `PlaySFX(AudioClip, float)`: one-shot sounds
- `SetAmbientClip(AudioClip)`: swap ambient loop

## Architecture Notes

- **Runtime-first**: All systems are created via `GameBootstrap` at runtime. No scene hierarchy is required.
- **Singleton pattern**: `GameManager` and `AudioManager` use `Instance` for global access.
- **Extensibility**: Subclass `Interactable` to create custom interactive objects (doors, notes, collectibles).
- **URP materials**: All generated materials use URP Lit shader. Colors can be tweaked in `EnvironmentManager.CreateMaterials()`.

## MCP Tools Available
When the MCP server is running, OpenCode can:
- Create and modify GameObjects
- Add components and edit properties
- Generate C# scripts
- Run Unity editor commands
- Analyze scene hierarchy
- Build and test the project
