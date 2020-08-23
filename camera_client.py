from imutils.video import VideoStream
from datetime import datetime
import imutils
import time
import cv2
import socket
import paho.mqtt.client as mqtt
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-b", "--broker", required=True,
        help="MQTT broker address")
ap.add_argument("-p", "--port", default=1883,
        help="MQTT broker port")
ap.add_argument("-u", "--username",
	help="MQTT broker user name")
ap.add_argument("-P", "--password",
	help="MQTT broker password")
args = vars(ap.parse_args())


# variables
frame_rate = 4
hostname = socket.gethostname()
is_streaming = False
print('Initializing ' + hostname)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    with open('settings.json') as settings_json:
        data = json.load(settings_json)
        client.publish('camera/connected/' + hostname, True, retain=True)
        cameraConnectionPayload = json.dumps({"name": hostname, **data})
        client.publish('camera/settingsupdate/' + hostname,
                       cameraConnectionPayload, retain=True)
    client.subscribe('camera/settingsupdate/' + hostname)
    client.subscribe('camera/requestframe/' + hostname)
    client.subscribe('camera/{}/stream/#'.format(hostname))  


def on_disconnect(client, userdata, rc=0):
    print('Disconnected. Reconnecting' + str(rc))   

def on_message(client, userdata, msg):
    print(msg.topic)
    payload = msg.payload.decode("utf-8")
    global is_streaming
    if msg.topic == 'camera/{}/stream/on'.format(hostname):
        print('start streaming')        
        is_streaming = True
    if msg.topic == 'camera/{}/stream/off'.format(hostname):
        print('stop streaming')        
        is_streaming = False
    if msg.topic == 'camera/settingsupdate/' + hostname:
        print('incoming settings update')
        print(json.loads(payload))

        with open('settings.json', 'w') as settings_json:
            json.dump(json.loads(payload), settings_json)

    if msg.topic == 'camera/requestframe/' + hostname:
        print('requesting camera frame')
        ret, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
        client.publish("camera/frame/" + hostname, bytes(jpg_buffer), 0)


client = mqtt.Client()
client.username_pw_set(username=args["username"], password=args["password"])
mqtt_broker_addr = args["broker"]
mqtt_broker_port = args["port"]
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.will_set('camera/connected/' + hostname, False, qos=0, retain=True)

client.connect(mqtt_broker_addr, mqtt_broker_port, 60)

vs = VideoStream(usePiCamera=True, resolution=(
    640, 480), framerate=frame_rate).start()

time.sleep(2)  # wait for camera to initialize
print('...initialized')
prev_time = 0
client.loop_start()

while True:    
    frame = vs.read()
    current_time = time.time()
    if current_time - prev_time > 0.5 and is_streaming == True:
        ret, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        client.publish("camera/frame/" + hostname, bytes(jpg_buffer), 0)
        prev_time = current_time
    
vs.stop()
client.publish(connection_topic, False, retain=True)
client.disconnect()
print('terminated')

