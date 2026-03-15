# Ballout

A fun and engaging ball game built with Pygame, featuring single-player, co-op, and LAN multiplayer modes.

## Description

Ballout is a dynamic ball game where players control characters to score goals against opponents. The game includes various skins, adjustable difficulty levels, and both local and networked multiplayer options. It features AI opponents for single-player mode and supports cooperative play.

## Features

- **Game Modes:**
  - Singleplayer (vs AI)
  - Co-op (local multiplayer)
  - LAN Multiplayer

- **Customizable Options:**
  - Player skins
  - Bot difficulty levels
  - Game duration
  - Physics settings (player mass, ball mass)

- **Settings and Saves:**
  - Persistent save data for preferences
  - Debug mode
  - Mobile-friendly controls (optional)

## Installation

1. Ensure you have Python 3.x installed.
2. Install the required dependencies:
   ```
   pip install pygame
   ```
3. Clone or download the project files.
4. Ensure the `ballout_assets/` directory is present with necessary assets (images, save files).

## Usage

Run the game by executing the main script:

```
python Ballout.py
```

This will launch the main menu where you can select your preferred game mode.

### Controls

- Use keyboard inputs to control players (specific controls may vary; check in-game settings).
- In multiplayer modes, players use different controls.

### Game Files

- `Ballout.py`: Main game file containing the core game logic and menu system.
- `ballout_classes.py`: Contains class definitions for game entities.
- `ballout_entities.py`: Defines entities like players, balls, and goals.
- `Ballout_multiplayer.py`: Handles multiplayer functionality.
- `ballout_assets/`: Directory containing game assets, save files, and AI data.

## Requirements

- Python 3.x
- Pygame library

## Contributing

Feel free to contribute to the project by submitting issues or pull requests.

## License

[Specify license if applicable, e.g., MIT License]

## Credits

Developed with Pygame. Assets and additional features as implemented.