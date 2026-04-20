# PeenQi’s Yarn 🎮

## Overview

**PeenQi’s Yarn** is a Python-based top-down adventure game inspired by classic *The Legend of Zelda* titles. Built using **Pygame**, this project explores core game development concepts such as rendering, player movement, collision detection, camera systems, and tile-based level design.

This project began as a creative experiment to recreate the feel of classic Zelda games, combining the nostalgia of NES-era design with the visual inspiration of *A Link to the Past*.

---

## Current Status

🚧 **Work in Progress (Paused)**
Estimated completion: ~25%

Development paused due to the time-intensive nature of manual map and level creation. The project currently serves as a functional prototype and learning milestone.

---

## Features (Implemented)

* Player movement system (keyboard input)
* Collision detection with obstacles
* Tile-based world map rendering
* Camera system with Y-axis sprite sorting
* Modular game architecture (separated into multiple files)
* Basic game loop and rendering pipeline

---

## Tech Stack

* **Python**
* **Pygame**

---

## Project Structure

```
PeenQi-s-Yarn/
│
├── code/
│   ├── main.py        # Game entry point
│   ├── level.py       # Level and map handling
│   ├── player.py      # Player movement and collision
│   ├── tile.py        # Tile/obstacle objects
│   ├── settings.py    # Game configuration (map, resolution, etc.)
│   ├── debug.py       # Debug rendering
│
├── graphics/
│   └── test/          # Game assets (sprites)
│
└── .gitignore
```

---

## How to Run

1. Install dependencies:

```bash
pip install pygame
```

2. Run the game:

```bash
python code/main.py
```

---

## Known Limitations

* Hardcoded file paths for assets (non-portable)
* Minimal gameplay systems (no combat, NPCs, inventory, etc.)
* No level progression or map transitions
* Basic placeholder assets
* No packaging or executable build

---

## Future Improvements (If Resumed)

* Replace hardcoded asset paths with relative paths
* Implement proper asset management system
* Add multiple maps and level transitions
* Introduce enemies, combat, and interaction systems
* Add animations for player and world elements
* Build UI (health, inventory, dialogue)
* Save/load game system
* Sound and music integration

---

## ⚙️ Developer Notes (For Future Me)

If you come back to this project, start here:

### 🔹 Repository Cleanup

* Remove all `__pycache__` folders
* Ensure `.gitignore` includes:

```
__pycache__/
*.pyc
```

### 🔹 File Structure Improvements

* Rename:

  * `graphics/test/` → `assets/` or `sprites/`
* Standardize asset organization (player, tiles, UI, etc.)

### 🔹 Code Improvements

* Replace absolute paths like:

```
F:/Code/Python/Zelda Game/...
```

with relative paths using `os.path`

* Consider centralizing asset loading into a dedicated module

### 🔹 Gameplay Direction (Important)

⚠️ Do NOT rebuild entire Zelda maps manually again
→ That approach caused burnout

Instead:

* Create **smaller custom maps**
* Or build a **procedural / modular map system**
* Focus on gameplay systems first, content second

---

## Project Purpose

This project was built to:

* Practice Python in a real-world, multi-file application
* Learn fundamentals of game development
* Experiment with rendering systems, collision logic, and camera behavior
* Explore creative software development beyond standard applications

---

## Author

Kenneth Lloyd Boller
