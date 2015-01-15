#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request, redirect, Response
from flask.ext.socketio import SocketIO, emit
import os
import sys
import signal
import mosquitto
import json
import subprocess
from configobj import ConfigObj

from pyfina import pyfina
pyfina = pyfina("data/")

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
mqtt_thread = None

conffile="/home/trystan/Desktop/pi/emonview/emonview.conf"
settings = ConfigObj(conffile, file_error=True)
username = settings["emonview"]["username"]
password = settings["emonview"]["password"]

@app.route('/')
def index():
    session['valid'] = session.get('valid',0)
    if session['valid']:
        return render_template('index.html')
    else:
        return render_template('login.html')
        
@app.route('/login',methods = ['POST','GET'])
def login():
    if request.form['username']==username and request.form['password']==password:
        session['valid'] = session.get('valid',0)
        session['valid'] = True
    return redirect("/")
    
@app.route('/logout',methods = ['POST','GET'])
def logout():
    session.clear()
    return redirect("/")

# =====================================================
# LOAD AND SAVE CONFIGURATION FILE:
# =====================================================
@app.route('/conf',methods = ['POST','GET'])
def conf():
    if not session['valid']:
        redirect("/")
    
    # Save config to file:
    if request.method == 'POST':
        with open(conffile,'w') as f:
            f.write(request.data)
        settings.reload()
        return "ok"
    
    # Load config from file:
    if request.method == 'GET':
        with open(conffile, 'rb') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')

# =====================================================
# DATA STORE:
# =====================================================  
@app.route('/data/<path:path>',methods = ['GET'])
def data(path):
    if not session['valid']:
        redirect("/")
    
    filename = path.replace("/",".")
    
    
    start = request.args.get('start')
    end = request.args.get('end')
    interval = request.args.get('interval')
    
    print "DATA: "+filename+" "+start+" "+end+" "+interval
    
    data = json.dumps(pyfina.data(filename,start,end,interval))
    return Response(data, mimetype='text/plain')

# =====================================================
# API:
# =====================================================
@app.route('/api/<path:path>',methods = ['POST','GET'])
def api(path):
    if not session['valid']:
        redirect("/")
        
    if request.method == 'POST':
        print path+" "+request.data
    
    if request.method == 'GET':
        if path=="nodes":
            return Response(json.dumps(settings['nodes']), mimetype='text/plain')
        
    return 'You want path: %s' % path

# =====================================================
# SERVICE:
# =====================================================
@app.route('/service/<path:path>',methods = ['POST'])
def service(path):
    if not session['valid']:
        redirect("/")
        
    parts = path.split("/")
    service = parts[0]
    action = parts[1]
    
    if not action=="status":
        cmd = 'sudo service '+service+' '+action
        proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
        output = proc.stdout.read()
        socketio.emit('my response',{'topic':'service-log','payload':service+"/"+action},namespace='/test') 
    
    cmd = 'sudo service '+service+' status'    
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    output = proc.stdout.read() 

    status = "stopped"
    if "is running" in output:
        status = "running" 

    socketio.emit('my response',{'topic':'service-log','payload':service+"/"+status},namespace='/test') 
   
    return cmd
        
# =====================================================
# MQTT:
# =====================================================
class MQTT_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop = False
        
    def run(self):
        while not self.stop and mqttc.loop() == 0:
            pass  
        sys.exit(0)
        
# =====================================================
# MQTT -> SOCKET IO DIRECT LINK
# =====================================================
def on_message(mosq, obj, msg):
    socketio.emit('my response',{'topic':msg.topic,'payload':msg.payload},namespace='/test') 
    
    # use rx topic to populate nodes object with last values (used in loading the initial view)
    if msg.topic=="rx":
        node = json.loads(msg.payload)    
        settings["nodes"][node["nodeid"]]["Rx"]["values"] = node["values"]

# =====================================================
# SOCKET IO
# =====================================================
@socketio.on('my event', namespace='/test')
def test_message(message):
    pass

@socketio.on('connect', namespace='/test')
def test_connect():
    pass

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    pass

    
def signal_handler(signal, frame):
    mqtt_thread.stop = True
    #print('==== Ctrl+C EXIT ====')
    sys.exit(0)

# =====================================================
# MAIN
# =====================================================
# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1",1883, 60, True)
mqttc.subscribe("log", 0)
mqttc.subscribe("rx/#", 0)
mqttc.subscribe("rx", 0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    mqtt_thread = MQTT_Thread()
    mqtt_thread.start()
    
    socketio.run(app,host='0.0.0.0',port=8000)

