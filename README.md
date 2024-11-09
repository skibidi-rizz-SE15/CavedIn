# Caved-In

**Caved-In** is a sensor-driven game developed using Pygame. In this game, players must dodge falling rocks by tilting and maneuvering a breadboard with sensors connected to a Raspberry Pi 400. The game combines interactive gameplay with physical control through hardware, creating a unique and immersive experience.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [How to Play](#how-to-play)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)
- [Contributors](#contributors)

## Overview
*Caved-In* integrates a Pygame-based game interface with hardware inputs from a sensor-equipped breadboard. The player controls the character’s movement by tilting the breadboard, dodging rocks that fall from the top of the screen.

## Features
- Real-time interaction using sensors on a breadboard connected to Raspberry Pi
- Rock evasion gameplay, requiring quick and accurate movement
- Interrupt-driven input handling for responsive controls

## System Requirements
- **Hardware**: Raspberry Pi 400, breadboard, and motion-detecting sensors (e.g., accelerometer)
- **Software**: 
  - Python 3.x
  - Pygame library
  - Raspberry Pi GPIO library for sensor integration

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/CavedIn.git
    cd CavedIn
    ```

2. **Install Required Libraries**:
    ```
    pip install -r requirements.txt
    ```

3. **Connect Sensors**:
   - Attach sensors to the breadboard and connect them to the GPIO pins on the Raspberry Pi 400 according to the pin configuration in `sensor_config.jpg`.

4. **Run the Game**:
    ```
    python game.py
    ```

## How to Play
1. Hold and tilt the breadboard to control the character.
2. Dodge the rocks falling from the top of the screen.
3. Survive as long as possible to earn a high score.

## Project Structure
- `game.py`: Main game script
- `notes.py, subway_surf.py`: Background music for Buzzer
- `README.md`: Project documentation
- `assets/`: Contains game assets (images, sounds, etc.)

## Technologies Used
- **Pygame**: For graphics and game development
- **Raspberry Pi GPIO**: To handle sensor inputs on Raspberry Pi

## Future Improvements
- Add AI-driven difficulty scaling to adjust the number and speed of falling rocks.
- Improve graphics and add collision effects.
- Expand sensor integration for more control options and responsiveness.
- Add a scoring system and leaderboard.

## Contributors
- **[66011231 Sorasich Lertwerasirikul]** - Lead Developer (Game mechanics, sensor integration)
- **[66011149 Phatthadon Sornplang]** - Hardware Specialist (Breadboard setup, sensor wiring, hardware welder)
- **[66011192 Rachata Phondi]** - Developer (Fixing Buggy things)
