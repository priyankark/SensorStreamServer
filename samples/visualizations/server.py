#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import seaborn as sns
from scipy.io import wavfile
import librosa
import librosa.display
from pydub import AudioSegment

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
port = 8989
print(f"Your Computer Name is: {hostname}")
print(f"Your Computer IP Address is: {IPAddr}")
print(f"* Enter {IPAddr}:{port} in the app.\n* Press the 'Set IP Address' button.\n* Select the sensors to stream.\n* Update the 'update interval' by entering a value in ms.")

def parse_sensor_data(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        print(f"Error parsing JSON data: {data}")
        return None

def plot_sensor_data(data_list, sensor_type):
    df = pd.DataFrame(data_list)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
    
    plt.figure(figsize=(12, 6))
    for column in ['x', 'y', 'z']:
        if column in df.columns:
            plt.plot(df['Timestamp'], df[column].astype(float), label=column)
    
    plt.title(f"{sensor_type} Data Visualization")
    plt.xlabel("Timestamp")
    plt.ylabel("Value")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

async def process_sensor_data(websocket, sensor_type):
    data_list = []
    async for message in websocket:
        parsed_data = parse_sensor_data(message)
        if parsed_data:
            print(f"Received {sensor_type} data: {parsed_data}")
            data_list.append(parsed_data)
            
            with open(f"{sensor_type.lower()}.txt", "a") as f:
                json.dump(parsed_data, f)
                f.write("\n")
            
            if len(data_list) >= 50:  # Create visualization every 50 data points
                buf = plot_sensor_data(data_list, sensor_type)
                img = Image.open(buf)
                img.save(f"{sensor_type.lower()}_visualization.png")
                print(f"Created visualization for {sensor_type}")
                data_list = data_list[-50:]  # Keep only the last 50 points for the next visualization

async def process_image(data):
    parsed_response = json.loads(data)
    image_data = b64decode(parsed_response['Base64Data'])
    img = Image.open(BytesIO(image_data))
    
    # Apply a creative filter (e.g., sepia)
    sepia_filter = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131]
    ])
    sepia_img = Image.fromarray(np.dot(np.array(img), sepia_filter.T).astype(np.uint8))
    sepia_img.save(f"sepia_{parsed_response['Timestamp']}.png")
    print(f"Processed and saved sepia image with timestamp {parsed_response['Timestamp']}")

async def process_audio(audio_data):
    with wave.open('audio.wav', 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(48000)
        wav.writeframes(audio_data)
    
    # Generate spectrogram
    y, sr = librosa.load('audio.wav')
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    plt.figure(figsize=(12, 8))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()
    plt.savefig('audio_spectrogram.png')
    plt.close()
    print("Generated audio spectrogram")

async def process_3gp_audio(file_path):
    print(f"Processing 3GP audio file: {file_path}")
    
    # Convert 3GP to WAV
    audio = AudioSegment.from_file(file_path, format="3gp")
    wav_path = file_path.replace('.3gp', '.wav')
    audio.export(wav_path, format="wav")
    print(f"Converted 3GP to WAV: {wav_path}")
    
    # Generate spectrogram
    y, sr = librosa.load(wav_path)
    D = librosa.stft(y)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    plt.figure(figsize=(12, 8))
    librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar(format='%+2.0f dB')
    plt.title('3GP Audio Spectrogram')
    plt.tight_layout()
    spectrogram_path = file_path.replace('.3gp', '_spectrogram.png')
    plt.savefig(spectrogram_path)
    plt.close()
    print(f"Generated spectrogram: {spectrogram_path}")
    
    # Generate waveform
    plt.figure(figsize=(12, 4))
    librosa.display.waveshow(y, sr=sr)
    plt.title('3GP Audio Waveform')
    plt.tight_layout()
    waveform_path = file_path.replace('.3gp', '_waveform.png')
    plt.savefig(waveform_path)
    plt.close()
    print(f"Generated waveform: {waveform_path}")

async def echo(websocket, path):
    if path in ['/accelerometer', '/gyroscope', '/magnetometer', '/orientation', '/stepcounter', '/thermometer', '/lightsensor', '/proximity', '/geolocation']:
        await process_sensor_data(websocket, path[1:])
    elif path == '/camera':
        data = await websocket.recv()
        await process_image(data)
    elif path == '/audio':
        data = await websocket.recv()
        decoded_data = b64decode(data, ' /')
        await process_audio(decoded_data)
    elif path == '/pro/audio':
        try:
            data = await websocket.recv()
            decoded_data = b64decode(data)
            file_path = 'audio.3gp'
            with open(file_path, 'wb') as gp3:
                gp3.write(decoded_data)
            print("Saved 3GP audio file")
            await process_3gp_audio(file_path)
        except Exception as e:
            print(f"Error processing audio: {e}")

async def main():
    async with websockets.serve(echo, '0.0.0.0', port, max_size=1_000_000_000):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())