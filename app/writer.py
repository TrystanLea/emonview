import mosquitto
import time
from pyfina import pyfina

pyfina = pyfina("data/")

# CREATE FIRST:
# pyfina.create("EmonTxV3.PowerCT1",10)

def on_message(mosq, obj, msg):
    key = msg.topic
    parts = key.split("/")
    value = msg.payload*1
    
    if len(parts)>3:
        filename = parts[1]+"."+parts[2]
        print filename+" "+value
        
        
        
        pyfina.prepare(filename,time.time(),value)
        print "Bytes written: "+str(pyfina.save())

# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1",1883, 60, True)
mqttc.subscribe("rx/#", 0)

while mqttc.loop() == 0:
    pass
