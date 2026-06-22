#!/usr/bin/env python3

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json
from pathlib import Path

PORT = 5000
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Map endpoints to output files
TEXT_ENDPOINTS = {
    "/accelerometer": "accelerometer.txt",
    "/gyroscope": "gyroscope.txt",
    "/magnetometer": "magnetometer.txt",
    "/orientation": "orientation.txt",
    "/stepcounter": "stepcounter.txt",
    "/thermometer": "thermometer.txt",
    "/lightsensor": "lightsensor.txt",
    "/proximity": "proximity.txt",
    "/geolocation": "geolocation.txt",
}


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


async def handle_text_sensor(path, message):
    file_path = DATA_DIR / TEXT_ENDPOINTS[path]
    with open(file_path, "a") as f:
        f.write(message + "\n")
    print(f"[{path}] {message}")


async def handle_camera(message):
    try:
        payload = json.loads(message)
        timestamp = payload["Timestamp"]
        image_data = b64decode(payload["Base64Data"])

        filename = DATA_DIR / f"{timestamp}.png"
        with open(filename, "wb") as f:
            f.write(image_data)

        print(f"[camera] Saved image {filename}")

    except Exception as e:
        print(f"[camera] Error: {e}")


async def handle_audio(message):
    try:
        pcm_data = b64decode(message)

        pcm_file = DATA_DIR / "temp.pcm"
        wav_file = DATA_DIR / "audio.wav"

        with open(pcm_file, "ab") as f:
            f.write(pcm_data)

        with open(pcm_file, "rb") as pcm:
            pcm_data = pcm.read()

        with wave.open(str(wav_file), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(48000)
            wav.writeframes(pcm_data)

        print("[audio] Wrote audio.wav")

    except Exception as e:
        print(f"[audio] Error: {e}")


async def handle_pro_audio(message):
    try:
        audio_data = b64decode(message)
        with open(DATA_DIR / "audio.3gp", "ab") as f:
            f.write(audio_data)
        print("[pro/audio] Appended audio data")

    except Exception as e:
        print(f"[pro/audio] Error: {e}")


async def websocket_handler(websocket, path=None):
    # websockets >= 14 calls the handler with only `websocket` and exposes the
    # path via websocket.request.path. Older versions pass `path` directly.
    if path is None:
        path = websocket.request.path

    print(f"Client connected to {path}")

    async for message in websocket:

        if path in TEXT_ENDPOINTS:
            await handle_text_sensor(path, message)

        elif path == "/camera":
            await handle_camera(message)

        elif path == "/audio":
            await handle_audio(message)

        elif path == "/pro/audio":
            await handle_pro_audio(message)

        else:
            print(f"Unknown endpoint: {path}")


async def main():
    ip = get_ip()
    print(f"Server running at ws://{ip}:{PORT}")

    async with websockets.serve(
        websocket_handler,
        "0.0.0.0",
        PORT,
        max_size=1_000_000_000
    ):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
