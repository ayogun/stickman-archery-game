# Stickman Archery Game

A simple 2-player turn-based archery game where stickman archers battle across hilly terrain with realistic physics and wind effects.

## Features

- **2-Player Turn-Based Combat**: Players alternate turns shooting arrows at each other
- **Realistic Physics**: Arrows follow parabolic trajectories affected by gravity and wind
- **Wind System**: Dynamic wind that changes direction and strength each turn
- **Health System**: 100 HP per player, with headshots dealing extra damage (50 vs 25)
- **Terrain**: Randomly generated hilly terrain that blocks arrows
- **Visual Feedback**: Health bars, wind indicators, power charging, and arrow trails

## How to Play

1. **Taking Turns**: Players alternate turns (Player 1 starts)
2. **Aiming**: Move your mouse to aim at your opponent
3. **Charging Power**: Click and hold the left mouse button to charge your shot
   - Watch the power bar at the bottom of the screen
   - Green = low power, Yellow = medium power, Red = high power
4. **Shooting**: Release the mouse button to fire the arrow
5. **Wind Effects**: Pay attention to the wind indicator - it affects arrow flight
6. **Winning**: Reduce your opponent's health to 0 to win

## Controls

- **Mouse**: Aim and shoot arrows
- **Left Click + Hold**: Charge power
- **Release**: Fire arrow
- **R Key**: Restart game (when game over)
- **Space**: Skip turn (optional)

## Damage System

- **Body Shot**: 25 damage
- **Head Shot**: 50 damage (extra damage for precision!)

## Installation and Running

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install Pygame**:
   ```bash
   pip install pygame
   ```
   
   Or using the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Game**:
   ```bash
   python stickman_archery.py
   ```

### Alternative Installation (using virtual environment - recommended):

```bash
# Create virtual environment
python -m venv game_env

# Activate virtual environment
# On macOS/Linux:
source game_env/bin/activate
# On Windows:
game_env\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Run the game
python stickman_archery.py
```

## Code Structure

The game is organized into several classes for easy understanding and modification:

- **`Terrain`**: Handles terrain generation and collision detection
- **`Player`**: Represents each stickman archer with health and drawing
- **`Arrow`**: Manages arrow physics, movement, and collision
- **`Game`**: Main game class that coordinates everything

## Customization

You can easily modify the game by changing constants at the top of the file:

```python
# Game Constants
SCREEN_WIDTH = 1200      # Screen width
SCREEN_HEIGHT = 700      # Screen height
PLAYER_HEALTH = 100      # Starting health
BODY_DAMAGE = 25         # Body shot damage
HEAD_DAMAGE = 50         # Head shot damage
GRAVITY = 0.5            # Gravity strength
MAX_POWER = 20           # Maximum shot power
```

## Troubleshooting

**Game won't start:**
- Make sure Python is installed correctly
- Ensure Pygame is installed: `pip install pygame`
- Check that you're in the correct directory

**Performance issues:**
- Lower the FPS constant if the game runs slowly
- Reduce SCREEN_WIDTH and SCREEN_HEIGHT for better performance

**Controls not working:**
- Make sure the game window has focus (click on it)
- Try clicking and holding more deliberately for charging

## Future Enhancements

Some ideas for extending the game:
- Add sound effects for shooting and hits
- Implement different arrow types (fire arrows, explosive arrows)
- Add power-ups or special abilities
- Create multiple terrain types
- Add AI opponent option
- Implement online multiplayer

Enjoy the game!
