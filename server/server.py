#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


hostname = socket.gethostname()
IPAddr = get_ip()
# Using 5000 as the default port but you can change based on your requirements
port = 5000
print("Your Computer Name is: " + hostname)
print("Your Computer IP Address is: " + IPAddr)
print(
    "* Enter {0}:{1} in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.".format(IPAddr, port))


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
            print("Device connected to audio endpoint")
            data = await websocket.recv()
            print(data)
            decoded_data = b64decode(data, ' /')
            with open('temp.pcm', 'ab') as pcm:
                pcm.write(decoded_data)
            with open('temp.pcm', 'rb') as pcm:
                pcmdata = pcm.read()
            with wave.open('audio.wav', 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(48000)
                wav.setcomptype('NONE', 'NONE')
                wav.writeframesraw(pcmdata)
            print("Wrote to audio.wav")
        
        if path == '/pro/audio':
            print("Device connected to unchunked audio endpoint")
            try:
                print("Audio Received")
                print(websocket)
                print(message)
                print(len(message))
                decoded_data = b64decode(message)
                with open('temp.3gp', 'ab') as gp3:
                    gp3.write(decoded_data)
            except e:
                print(f"Error processing audio: {e}")
        

# Contribution by Evan Johnston
async def main():
    async with websockets.serve(echo, '0.0.0.0', port, max_size=1_000_000_000):
        await asyncio.Future()
    

asyncio.run(main())
