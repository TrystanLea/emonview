#!/usr/bin/env python

import mosquitto, time

# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.connect("127.0.0.1",1883, 60, True)

val = 12.0
asc = 1

# Main loop
while 1:
    
    # A 'non blocking' call to mqtt loop
    # mqttc.loop(0)
    
    if asc==1:
        val += 0.1 
    else:
        val -= 0.1
        
    if val>22.0: asc = 0
    if val<12.0: asc = 1
    
    mqttc.publish("rx/EmonTxV3n10/PowerCT1/value",val,retain=True)
    mqttc.publish("rx/EmonTxV3n10/PowerCT2/value",val,retain=True)
    mqttc.publish("rx/EmonTxV3n10/PowerCT3/value",val,retain=True)   
    # Main loop sleep control
    time.sleep(1.0)
