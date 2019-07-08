# MQTT Camera Client

Connects to an mqtt client, and sends low res video frames from a raspberry pi (as jpegs). 

These frames can be processed by a detection hub . See https://github.com/autumn8/mqtt_object_detection_hub

To run client as a service. add cameraClient.service file in /etc/systemd/system:

```bash
[Unit]
Description=Camera Client
[Service]
Type=simple
WorkingDirectory=/home/pi/mqtt-camera-client/
User=pi
ExecStart=/usr/bin/python3 /home/pi/mqtt-camera-client/camera_client.py
Restart=always
RestartSec=2
[Install]
WantedBy=multi-user.target

```

Enable with: 
```
sudo systemctl --system daemon-reload
sudo systemctl enable cameraClient
```
