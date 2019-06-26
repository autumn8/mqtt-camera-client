from imutils.video import VideoStream
from datetime import datetime
import imutils
import time
import cv2
import socket
import paho.mqtt.client as mqtt
import json

#variables
frame_rate = 6
mqtt_broker_addr = "192.168.8.202"
mqtt_broker_port = 1883
hostname = socket.gethostname()
print('Initializing ' + hostname)

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))   	
	with open('settings.json') as settings_json:		
		data = json.load(settings_json)		 
		client.publish('camera/connected/' + hostname, True, retain=True) 
		cameraConnectionPayload =  json.dumps({"name" : hostname, **data})		
		client.publish('camera/settingsupdate/' + hostname, cameraConnectionPayload, retain=True)
	client.subscribe('camera/settingsupdate/' + hostname)     	

def on_message(client, userdata, msg):	
	payload = msg.payload.decode("utf-8")
	if msg.topic == 'camera/settingsupdate/' + hostname:
		print('incoming settings update')    
		print(json.loads(payload))

		with open('settings.json', 'w') as settings_json:  
			json.dump(json.loads(payload), settings_json)            

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.will_set('camera/connected/' + hostname, False, qos=0, retain=True) 

client.connect(mqtt_broker_addr, mqtt_broker_port, 60)

vs = VideoStream(usePiCamera=True,resolution=(320, 240),framerate=frame_rate).start()

def publish_mqtt_message(topic):
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S") 
	data = json.dumps({"time": current_time , "location": hostname})
	print("publishing message" + topic)
	client.publish(topic, data)
   

time.sleep(2) #wait for camera to initialize
print('...initialized')

while True:    
	client.loop()
	frame = vs.read()	
	ret, jpg_buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70]) 	 	    
	client.publish("camera/frame/" + hostname, bytes(jpg_buffer),0)  	
	time.sleep(1/frame_rate)        
vs.stop()
client.publish(connection_topic, False,retain=True)
client.disconnect()
print('terminated')
