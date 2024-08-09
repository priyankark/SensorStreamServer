#!/usr/bin/env python

import asyncio
import websockets
import socket
from base64 import b64decode
import wave
import json
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image
import librosa
import librosa.display
from pydub import AudioSegment
import os
import pygame

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

class SensorSoundLandscape:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
        self.channels = [pygame.mixer.Channel(i) for i in range(3)]
        self.sounds = [self.create_sine_wave(440), self.create_sine_wave(550), self.create_sine_wave(660)]
        for channel, sound in zip(self.channels, self.sounds):
            channel.play(sound, loops=-1)
            channel.set_volume(0.3)

    def create_sine_wave(self, freq, duration=1.0, volume=0.5):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, num_samples, False)
        wave = np.sin(2 * np.pi * freq * t) * volume
        stereo_wave = np.column_stack((wave, wave))  # Create a 2D array
        sound_array = (stereo_wave * 32767).astype(np.int16)
        # Ensure the array is C-contiguous
        sound_array = np.ascontiguousarray(sound_array)
        sound = pygame.sndarray.make_sound(sound_array)
        return sound

    def update_sound(self, data):
        try:
            x = float(data.get('x', 0))
            y = float(data.get('y', 0))
            z = float(data.get('z', 0))
            
            freqs = [220 + (x + 1) * 220, 440 + (y + 1) * 220, 660 + (z + 1) * 220]
            magnitude = np.mean([abs(x), abs(y), abs(z)])
            amplitude = magnitude * 0.5
            
            for i, (channel, freq) in enumerate(zip(self.channels, freqs)):
                new_sound = self.create_sine_wave(freq)
                channel.play(new_sound, loops=-1, fade_ms=50)
                channel.set_volume(amplitude)
            
            print(f"Updated sound: f1={freqs[0]:.2f}, f2={freqs[1]:.2f}, f3={freqs[2]:.2f}, amp={amplitude:.2f}")
        except Exception as e:
            print(f"Error updating sound: {e}")

    def stop(self):
        pygame.mixer.quit()

class SensorServer:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_addr = get_ip()
        self.port = 8989
        self.sound_landscape = SensorSoundLandscape()
        self.sensor_data = {sensor: [] for sensor in ['accelerometer', 'gyroscope', 'magnetometer', 'orientation', 'stepcounter', 'thermometer', 'lightsensor', 'proximity', 'geolocation']}

    async def handle_sensor_data(self, websocket, sensor_type):
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received {sensor_type} data: {data}")
                
                self.sensor_data[sensor_type].append(data)
                if len(self.sensor_data[sensor_type]) > 100:
                    self.sensor_data[sensor_type] = self.sensor_data[sensor_type][-100:]
                
                with open(f"{sensor_type}.txt", "a") as f:
                    json.dump(data, f)
                    f.write("\n")
                
                if sensor_type in ['accelerometer', 'gyroscope', 'magnetometer']:
                    self.sound_landscape.update_sound(data)
                
                if len(self.sensor_data[sensor_type]) % 50 == 0:
                    self.generate_visualization(sensor_type)
            
            except json.JSONDecodeError:
                print(f"Error parsing JSON data for {sensor_type}: {message}")

    def generate_visualization(self, sensor_type):
        data = self.sensor_data[sensor_type]
        plt.figure(figsize=(12, 6))
        for key in ['x', 'y', 'z']:
            if key in data[0]:
                values = [float(d[key]) for d in data]
                plt.plot(range(len(values)), values, label=key)
        plt.title(f"{sensor_type.capitalize()} Data Visualization")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{sensor_type}_visualization.png")
        plt.close()
        print(f"Generated visualization for {sensor_type}")

    async def handle_camera(self, websocket):
        try:
            data = await websocket.recv()
            print("Image received for parsing")
            parsed_response = json.loads(data)
            with open(f"{parsed_response['Timestamp']}.png", "wb") as fh:
                fh.write(b64decode(parsed_response['Base64Data']))
            print(f"Wrote image with timestamp {parsed_response['Timestamp']}")
        except Exception as e:
            print(f'Error processing camera data: {e}')
            await websocket.close()

    async def handle_audio(self, websocket):
        data = await websocket.recv()
        decoded_data = b64decode(data, ' /')
        with open('temp.pcm', 'wb') as pcm:
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
        self.generate_audio_visualization('audio.wav')

    async def handle_pro_audio(self, websocket):
        try:
            data = await websocket.recv()
            decoded_data = b64decode(data)
            with open('audio.3gp', 'wb') as gp3:
                gp3.write(decoded_data)
            print("Saved 3GP audio file")
            self.process_3gp_audio('audio.3gp')
        except Exception as e:
            print(f"Error processing 3GP audio: {e}")

    def process_3gp_audio(self, file_path):
        audio = AudioSegment.from_file(file_path, format="3gp")
        wav_path = file_path.replace('.3gp', '.wav')
        audio.export(wav_path, format="wav")
        print(f"Converted 3GP to WAV: {wav_path}")
        self.generate_audio_visualization(wav_path)

    def generate_audio_visualization(self, audio_path):
        y, sr = librosa.load(audio_path)
        plt.figure(figsize=(12, 8))
        librosa.display.waveshow(y, sr=sr)
        plt.title('Audio Waveform')
        plt.tight_layout()
        plt.savefig(f"{audio_path}_waveform.png")
        plt.close()
        
        D = librosa.stft(y)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        plt.figure(figsize=(12, 8))
        librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
        plt.colorbar(format='%+2.0f dB')
        plt.title('Audio Spectrogram')
        plt.tight_layout()
        plt.savefig(f"{audio_path}_spectrogram.png")
        plt.close()
        print(f"Generated audio visualizations for {audio_path}")

    async def main(self):
        print(f"Your Computer Name is: {self.hostname}")
        print(f"Your Computer IP Address is: {self.ip_addr}")
        print(f"* Enter {self.ip_addr}:{self.port} in the app.")
        print("* Press the 'Set IP Address' button.")
        print("* Select the sensors to stream.")
        print("* Update the 'update interval' by entering a value in ms.")

        async with websockets.serve(self.router, '0.0.0.0', self.port, max_size=1_000_000_000):
            await asyncio.Future()  # run forever

    async def router(self, websocket, path):
        if path in ['/accelerometer', '/gyroscope', '/magnetometer', '/orientation', '/stepcounter', '/thermometer', '/lightsensor', '/proximity', '/geolocation']:
            await self.handle_sensor_data(websocket, path[1:])
        elif path == '/camera':
            await self.handle_camera(websocket)
        elif path == '/audio':
            await self.handle_audio(websocket)
        elif path == '/pro/audio':
            await self.handle_pro_audio(websocket)

if __name__ == "__main__":
    server = SensorServer()
    try:
        asyncio.run(server.main())
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.sound_landscape.stop()