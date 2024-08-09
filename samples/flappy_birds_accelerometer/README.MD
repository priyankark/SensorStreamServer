# Accelerometer-Controlled Flappy Bird

This project is a Python implementation of the classic Flappy Bird game, controlled using a mobile device's accelerometer. The game runs on a computer, while a mobile device sends accelerometer data to control the bird's jumps.

## Requirements

- Python 3.7 or higher
- Pygame
- Websockets
- A mobile device with an accelerometer and capability to stream sensor data

## Setup

1. Clone this repository or download the source code.

2. Install the required Python packages:
pip install -r requirements.txt
Copy
3. Run the server script:
python accelerometer_flappy_bird.py
Copy
4. Note the IP address and port displayed in the console.

5. On your mobile device, use a sensor streaming app that can send accelerometer data via WebSocket. Configure the app with the IP address and port from step 4.

## How to Play

1. Start the game server on your computer.
2. Connect your mobile device and start streaming accelerometer data.
3. The game will display "Tilt to Start". Tilt your device to begin the game.
4. The bird will start falling due to gravity. Tilt your device to the left (positive z-acceleration) to make the bird jump and avoid obstacles.
5. Try to navigate through as many pipes as possible without colliding!

## Caveats and Considerations

1. **Accelerometer Sensitivity**: The game's responsiveness may vary depending on your mobile device's accelerometer sensitivity. You might need to adjust the `jump_strength`, `gravity`, or jump threshold in the code for optimal gameplay.

2. **Axis Orientation**: Different devices may report accelerometer data differently. If tilting left doesn't make the bird jump, try changing the condition in the `control_bird` method:
```python
if acceleration < -2:  # For devices that report negative z when tilting left
    self.bird_velocity = self.jump_strength
```

3. **Latency**: Depending on your network conditions, there might be a slight delay between tilting your device and seeing the bird jump. A stable and fast connection is recommended for the best experience. Reduce the delay to 100ms to stream faster.

4. **Compatibility**: Ensure your sensor streaming app is compatible with the WebSocket protocol and can send data in the expected JSON format.

5. **Firewall Settings**: If you're having trouble connecting, check your computer's firewall settings. You may need to allow incoming connections on the port used by the game server.

6. **Continuous Data Stream**: The game expects a continuous stream of accelerometer data. If your app has a "pause" or "stop" feature, be aware that it might affect gameplay.

7. **Device Orientation**: For consistent control, maintain a consistent orientation of your mobile device while playing. Sudden changes in device orientation may lead to unexpected bird movements.

## Troubleshooting

* If the game doesn't respond to tilting, check the console output to ensure accelerometer data is being received.
* If the controls feel reversed, try inverting the acceleration check as mentioned in the "Axis Orientation" caveat.
* If you encounter any "Address already in use" errors, try changing the port number in the code.

## Customization
Feel free to adjust game parameters like pipe speed, gap size, or screen dimensions in the FlappyBird class to customize the gameplay experience.