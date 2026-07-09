# Advanced Games — Unity Project

## Project Info
- Unity Version: 2022.3 LTS (or Unity 6 LTS)
- Template: 3D Core
- Scripting Backend: Mono
- Target Platform: Standalone (PC/Mac/Linux)

## Setup Guide

### 1. Install Unity Hub + Editor

#### Option A: APT (Ubuntu/Debian with sudo)
```bash
curl -fsSL https://hub.unity3d.com/linux/keys/public | sudo gpg --dearmor -o /etc/apt/keyrings/unityhub.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/unityhub.gpg] https://hub.unity3d.com/linux/repos/deb stable main" | sudo tee /etc/apt/sources.list.d/unityhub.list
sudo apt update && sudo apt install unityhub
```
Launch Unity Hub, sign in, install Unity 2022.3 LTS or Unity 6 LTS.

#### Option B: AppImage (no sudo)
```bash
wget https://public-cdn.cloud.unity3d.com/hub/prod/UnityHubSetup.AppImage
chmod +x UnityHubSetup.AppImage
./UnityHubSetup.AppImage
```

### 2. Create the Unity Project
- Open Unity Hub → Projects → New → 3D Core → name "AdvancedGames"
- Set location to: `advanced-games-unity/`
- Wait for asset database import

### 3. Install MCP for Unity
In Unity Editor:
- Window → Package Manager → + → Add package from git URL:
  ```
  https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity
  ```
- Window → MCP for Unity → Configure All Detected Clients
- Verify MCP status shows "Connected"

### 4. Connect OpenCode to Unity
- The root `opencode.json` already contains the unity3d-mcp config
- OpenCode → `/mcp` → toggle unity3d-mcp to Enabled
- Test: "List all GameObjects in the current scene"

### 5. Attach PlayerController
- Create an empty GameObject named "Player"
- Add Component → Rigidbody
- Drag `Assets/Scripts/PlayerController.cs` onto the Player
- Set up Camera as child of Player (or assign in inspector)
- Add a ground plane (scale 10,10,10 at y=0)

## C# Script Reference

### PlayerController.cs
- `speed` (float): movement speed, default 8
- `jumpForce` (float): jump impulse, default 5
- `airControlMultiplier` (float): air movement factor, default 0.4
- `mouseSensitivity` (float): look sensitivity, default 2
- `maxLookAngle` (float): vertical look clamp, default 80

Controller pattern: Rigidbody with VelocityChange force for responsive movement,
SphereCast ground check, cursor lock for FPS-style camera.

## Game Design Notes
- Start scene: open field with obstacles for testing movement/jumping
- Player respawns at origin if falling out of bounds
- Use `RequireComponent(typeof(Rigidbody))` — the component auto-adds on attach

## MCP Tools Available
When the MCP server is running, OpenCode can:
- Create and modify GameObjects
- Add components and edit properties
- Generate C# scripts
- Run Unity editor commands
- Analyze scene hierarchy
- Build and test the project
