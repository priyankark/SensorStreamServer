# Sensor Stream App

Sensor Stream allows you to convert your phone into a complete sensor hub and stream real-time sensor information from your phone to the provided open source server over wifi/local network. The server can be modified as per your use-case. The app can be used to build IoT applications, for data science projects and many more use cases!

# Sensor Stream Server
These are simple servers with WebSocket support that accept the sensor data and write it to a text file. These are companion sample servers for the Sensor Stream app.

# Steps:
* Clone the repository or download the zip file and unzip it to a directory of your choice.
* Make sure you have given the app all the necessary access permissions (especially if you wish to use audio streaming/image streaming)

## To Run the Python Server (version >= Python 3.0)

* Make sure you have python (version >=3) installed and you can access both pip and python from the command line/ terminal
* To check the same open command line/terminal and type `python --version` and `pip --version`
* cd to the directory where the folder was extracted in the command line
* Optional Step: It's highly recommended, you create a virtual env before installing dependencies. Activate the virtual environment and proceed. OS specific steps are available in the docs [https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/]

**Brief Summary of steps to follow to create virtual env [Optional Step]**
```
cd Python
cd server
py -m venv env # Create virtual env
source env/bin/activate (On Linux or Mac) or .\env\Scripts\activate (On Windows)
```

**Final Installation and run steps**
 ```
 cd SensorStreamServer
 cd server
 pip install -r requirements.txt 
 python3 server.py
 ```


## To use the app
* Make sure both your phone and the laptop/raspi/other device are on same network.
* Find the internal ip address of the raspi/laptop. The server should be showing you the same.
* Simply type the ip address:5000.Example: 192.168.1.24:5000 in the app's input bar. 
* Switch on whatever sensor's data you want to stream.

You can make any changes you want to to server.py

## Data Format Cheat sheet:
* Accelerometer: x,y,z
* Gyroscope: x,y,z
* Magnetometer: x,y,z
* Orientation: azimuth,pitch,roll
* Step Counter: steps
* Thermometer: temperature
* Light Sensor: light
* Proximity: isNear, value, maxRange
* Link: https://github.com/kprimice/react-native-sensor-manager
* Camera and Audio: base64 encoded strings

## Contribution guidelines (Optional)
This repository is open to contributions. 
On the server side, we are looking to support sample servers in more languages and frameworks such as node.js, Go etc.
Please feel free to raise PRs!

### For more support, please e-mail priyankar.kumar98@gmail.com and I will get back to you ASAP.
