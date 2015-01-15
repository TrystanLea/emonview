import mosquitto
import time
from pyfina import pyfina
from configobj import ConfigObj

pyfina = pyfina("data/")

conffile="/home/trystan/Desktop/pi/emonview/emonview.conf"
settings = ConfigObj(conffile, file_error=True)

# itterate through node setting and create feeds if required
for node in settings["nodes"]:
    if "record" in settings["nodes"][node]["Rx"]:
        nodename = settings["nodes"][node]["nodename"]
        
        i = 0
        for name in settings["nodes"][node]["Rx"]["names"]:
            record = int(settings["nodes"][node]["Rx"]["record"][i])
            interval = int(settings["nodes"][node]["Rx"]["interval"][i])
            
            if record: 
                filename = nodename+"."+name
                print "create: "+filename+" "+str(interval)
                pyfina.create(filename,interval)
                
            i += 1
            
def on_message(mosq, obj, msg):
    key = msg.topic
    parts = key.split("/")
    value = msg.payload*1
    
    if len(parts)>3:
        filename = parts[1]+"."+parts[2]
        
        pyfina.prepare(filename,time.time(),value)
        
        bytes = pyfina.save()
        
        if bytes:
            print str(bytes)+" bytes written to "+filename+" "+value

# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1",1883, 60, True)
mqttc.subscribe("rx/#", 0)

while mqttc.loop() == 0:
    pass
