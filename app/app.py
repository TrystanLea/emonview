#!/usr/bin/env python

from gevent import monkey
monkey.patch_all()

import time
from threading import Thread
from flask import Flask, render_template, session, request, redirect, Response
from flask.ext.socketio import SocketIO, emit
import mosquitto
import os
import subprocess
import signal
import sys
import json

from pyfina import pyfina

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
mqtt_thread = None
username="demo"
password="demo"
conffile="/etc/emonhub/emonhub.conf"

pyfina = pyfina("data/")

## =================================================
class MQTT_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop = False
        
    def run(self):
        while not self.stop and mqttc.loop() == 0:
            pass
            
        sys.exit(0)
            
        #print "MQTT Thread Closed"
# ==================================================

def signal_handler(signal, frame):
    mqtt_thread.stop = True
    #print('==== Ctrl+C EXIT ====')
    sys.exit(0)

def on_message(mosq, obj, msg):
    socketio.emit('my response',{'topic':msg.topic,'payload':msg.payload},namespace='/test') 
    
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
    
@app.route('/conf',methods = ['POST','GET'])
def conf():
    if not session['valid']:
        redirect("/")
        
    if request.method == 'POST':
        # might be good to do some input checking/sanitization here!
        with open(conffile,'w') as f:
            f.write(request.data)
        return "ok"
    else:
        with open(conffile, 'rb') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')

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
    
    
@app.route('/api/<path:path>',methods = ['GET'])
def api(path):
    if not session['valid']:
        redirect("/")
    print path
    return 'You want path: %s' % path
    
@app.route('/data/<path:path>',methods = ['GET'])
def data(path):
    if not session['valid']:
        redirect("/")
    
    filename = path.replace("/",".")
    start = request.args.get('start')
    end = request.args.get('end')
    interval = request.args.get('interval')
    
    data = json.dumps(pyfina.data(filename,start,end,interval))
    return Response(data, mimetype='text/plain')

@socketio.on('my event', namespace='/test')
def test_message(message):
    pass

@socketio.on('connect', namespace='/test')
def test_connect():
    pass

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    pass 

  


# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1",1883, 60, True)
mqttc.subscribe("log", 0)
mqttc.subscribe("rx/#", 0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    mqtt_thread = MQTT_Thread()
    mqtt_thread.start()
    
    socketio.run(app,host='0.0.0.0',port=8000)

