#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json

buffer = ""  # Buffer to store the base64 string chunks

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


hostname = socket.gethostname()
IPAddr = get_ip()
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
print(
    "* Enter {0}:5000 in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.".format(IPAddr))


async def echo(websocket, path):
    async for message in websocket:
        if path == '/accelerometer':
            data = await websocket.recv()
            print(data)
            f = open("accelerometer.txt", "a")
            f.write(data+"\n")

        if path == '/gyroscope':
            data = await websocket.recv()
            print(data)
            f = open("gyroscope.txt", "a")
            f.write(data+"\n")

        if path == '/magnetometer':
            data = await websocket.recv()
            print(data)
            f = open("magnetometer.txt", "a")
            f.write(data+"\n")

        if path == '/orientation':
            data = await websocket.recv()
            print(data)
            f = open("orientation.txt", "a")
            f.write(data+"\n")

        if path == '/stepcounter':
            data = await websocket.recv()
            print(data)
            f = open("stepcounter.txt", "a")
            f.write(data+"\n")

        if path == '/thermometer':
            data = await websocket.recv()
            print(data)
            f = open("thermometer.txt", "a")
            f.write(data+"\n")

        if path == '/lightsensor':
            print("connected")
            data = await websocket.recv()
            print(data)
            f = open("lightsensor.txt", "a")
            f.write(data+"\n")

        if path == '/proximity':
            data = await websocket.recv()
            print(data)
            f = open("proximity.txt", "a")
            f.write(data+"\n")

        if path == '/geolocation':
            data = await websocket.recv()
            print(data)
            f = open("geolocation.txt", "a")
            f.write(data+"\n")

        if path == '/camera':
            try:
                print("Device connected to camera endpoint")
                data = await websocket.recv()
                print("Image received for parsing")
                parsed_response = json.loads(data)
                fh = open(str(parsed_response['Timestamp']) + ".png", "wb")
                fh.write(b64decode(parsed_response['Base64Data']))
                print("Wrote image with timestamp " +str(parsed_response['Timestamp']))
            except Exception:
                print('Connection closed due to error')
                await websocket.close()

        if path == '/audio':
            print("Device connected to unchunked audio endpoint")
            try:
                print("Audio Received")
                print(websocket)
                print(message)
                print(len(message))
                decoded_data = b64decode(message)
                with open('temp.3gp', 'ab') as gp3:
                    gp3.write(decoded_data)
                with open('temp.3gp', 'rb') as gp3:
                    gp3_data = gp3.read()
                with wave.open('audio.wav', 'wb') as wav:
                    wav.setnchannels(2)
                    wav.setsampwidth(2)
                    wav.setframerate(44100)
                    wav.setcomptype('NONE', 'NONE')
                    wav.writeframesraw(gp3_data)
                    print("Wrote to audio.wav")
                websocket.send("Audio received and processed successfully")
            except e:
                print(f"Error processing audio: {e}")
        
        if path == "/chunkedaudio":
            print("Device connected to audio endpoint")
            try:
                print(websocket)
                print(message)
                data = await websocket.recv()
                print("Audio Chunked Received")
                # Decode the complete base64 string
                decoded_data = b64decode(data)
                print("Audio Decoded")
                # Process the decoded data (e.g., save to file)
                with wave.open('audio.wav', 'wb') as wav:
                    wav.setnchannels(2)
                    wav.setsampwidth(2)
                    wav.setframerate(44100)
                    wav.writeframesraw(decoded_data)
                await websocket.send("Audio received and processed successfully")
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed unexpectedly")
            except Exception as e:
                print(f"Error processing audio: {e}")
           


# Contribution by Evan Johnston
async def main():
    async with websockets.serve(echo, '0.0.0.0', 5000, max_size=1_000_000_000):
        await asyncio.Future()
    

asyncio.run(main())
