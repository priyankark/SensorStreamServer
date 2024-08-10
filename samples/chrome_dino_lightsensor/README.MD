# Light Sensor-Controlled Dinosaur Game

## Overview

This project is a Python-based game inspired by Chrome's dinosaur game, but with a unique twist: it's controlled using your mobile device's light sensor! The game runs on your computer while your mobile device sends light sensor data to control the dinosaur's jumps.

## Requirements

- Python 3.7 or higher
- Pygame
- Websockets
- A mobile device with a light sensor and capability to stream sensor data

## Setup

1. Clone this repository or download the source code.

2. Install the required Python packages:
pip install pygame websockets
Copy
3. Run the server script:
python light_sensor_dino_game.py
Copy
4. Note the IP address and port displayed in the console.

5. On your mobile device, use a sensor streaming app that can send light sensor data via WebSocket. Configure the app with the IP address and port from step 4.

## How to Play

1. Start the game server on your computer.
2. Connect your mobile device and start streaming light sensor data.
3. The game will display "Change light level to start". Make a significant change in the light level around your device's sensor to begin the game.
4. Once started, the dinosaur will run automatically.
5. To make the dinosaur jump, quickly change the light level around your device's sensor. This can be done by:
- Covering and uncovering the light sensor
- Moving between light and dark areas
- Flashing a light source near the sensor
6. Try to jump over the obstacles and survive as long as possible!
7. If you collide with an obstacle, the game ends. Press SPACE to restart.

## Game Mechanics

- The game responds to changes in light level, not absolute brightness.
- Any significant change in light level (brighter or darker) will trigger a jump.
- The dinosaur can only jump when it's on the ground.
- The score increases the longer you survive.
- Obstacles appear randomly and move from right to left.

## Customization

You can adjust various game parameters in the `DinoGame` class:

- `change_threshold`: How big a change in light level is needed to trigger a jump.
- `jump_strength`: How high the dinosaur jumps.
- `obstacle_speed`: How fast the obstacles move.
- `obstacle_frequency`: How often new obstacles appear.

## Troubleshooting

- If the game doesn't respond to light changes, check the console output to ensure light sensor data is being received.
- If the dinosaur is jumping too frequently or not enough, try adjusting the `change_threshold` value.
- If you encounter any "Address already in use" errors, try changing the port number in the code.

## Demo
Youtube Demo: [Demo](https://www.youtube.com/watch?v=PPdUmr5KMjQ)
