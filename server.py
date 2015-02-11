#!/usr/bin/env python

import os, sys, signal
import json
import redis
import time
import mosquitto
from threading import Thread
from configobj import ConfigObj
from gevent import monkey
monkey.patch_all()
from flask import Flask, Response, request, redirect, url_for, session
from flask.ext.socketio import SocketIO, emit

from pyfina import pyfina
pyfina = pyfina("/home/pi/data/store/")

r = redis.Redis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
mqtt_thread = None

basedir = "/home/pi/emonview/"
conffile = basedir+"emonhub.conf"

@app.route('/')
def index():
    session['valid'] = session.get('valid',0)
    if session['valid']:
        return redirect(url_for('client'))
    else:
        with open(basedir+"login.html", 'rb') as f:
            content = f.read()
        return content
        
@app.route('/login',methods = ['POST','GET'])
def login():
    settings = ConfigObj(conffile, file_error=True)
    if request.form['username']==settings['auth']['username'] and request.form['password']==settings['auth']['password']:
        session['valid'] = session.get('valid',0)
        session['valid'] = True
    return redirect("/")
    
@app.route('/logout',methods = ['POST','GET'])
def logout():
    session.clear()
    return redirect("/")
    
@app.route('/client')
def client():
    if not session['valid']:
        return redirect("/")
    with open(basedir+"client.html", 'rb') as f:
        content = f.read()
    return content
    
@app.route('/test')
def test():
    if not session['valid']:
        return redirect("/")
    with open(basedir+"test.html", 'rb') as f:
        content = f.read()
    return content
    
# ------------------------------------------------------------------------------------    
# HTTP API
# ------------------------------------------------------------------------------------
@app.route('/api',defaults={'path': ''},methods = ['POST','GET'])    
@app.route('/api/<path:path>',methods = ['POST','GET'])
def api(path):
    if not session['valid']:
        return redirect("/")
    settings = ConfigObj(conffile, file_error=True)
    config = settings["nodes"]
    
    nodes = r.get("nodes")
    if nodes is not None:
        nodes = json.loads(nodes)
    else:
        nodes = {}
    
    result = "False"
    nodeid = False
    varid = False
    prop = False

    if path is not "":
    
        url = path.split("/")
    
        if len(url)>0 and url[0].isnumeric():
            nodeid = url[0]
            if nodeid not in config:
                nodeid = False
         
        if len(url)>1 and url[1].isnumeric():
            varid = int(url[1])
                
        if nodeid is False and varid is False and len(url)>0:
            prop = url[0]
        if nodeid is not False and varid is False and len(url)>1:
            prop = url[1]
        if nodeid is not False and varid is not False and len(url)>2:
            prop = url[2]

    # POST
    
    if request.method == "POST":
    
        inputstr = request.data
    
        if nodeid is False and varid is False and prop is not False:
            if prop=="config": 
                r.set("config",inputstr)

        if nodeid is not False and varid is False and prop is not False:
            if prop=="values":
                now = time.time()
                values = inputstr.split(",")
                
                nodes = json.loads(r.get("nodes"))
                if not nodeid in nodes: nodes[nodeid] = {}
                    
                nodes[nodeid]["time"] = now
                nodes[nodeid]["values"] = values
                r.set("nodes",json.dumps(nodes))
                
               # for varid in values:
                    # store(nodeid,varid,time,values[i])
            else:
                settings = ConfigObj(conffile, file_error=True)
                config = settings["nodes"]
                
                if config is None: config = {}
                if not nodeid in config: config[nodeid] = {}
                    
                if prop=="nodename": config[nodeid]["nodename"] = inputstr
                if prop=="hardware": config[nodeid]["hardware"] = inputstr
                if prop=="firmware": config[nodeid]["firmware"] = inputstr
                if prop=="names": config[nodeid]["names"] = inputstr.split(",")
                if prop=="units": config[nodeid]["units"] = inputstr.split(",")
                
                r.set("config",json.dumps(config))
                result = config
        
        if nodeid is not False and varid is not False and prop is not False:
            settings = ConfigObj(conffile, file_error=True)
            config = settings["nodes"]
        
            if config is None: config = {}
            if not nodeid in config: config[nodeid] = {}
            
            if prop=="name": config[nodeid]["names"][varid] = inputstr
            if prop=="unit": config[nodeid]["units"][varid] = inputstr
            
            r.set("config",json.dumps(config))
            result = config


    # GET
    if request.method == "GET":
        
        # GET ALL NODES
        if nodeid is False and varid is False and prop is False: 
            for nid in config:
                for key in config[nid]:
                    if not nid in nodes: nodes[nid] = {}
                    nodes[nid][key] = config[nid][key]
            result = nodes

        # GET NODE
        if nodeid is not False and varid is False and prop is False:
            node = config[nodeid]
            node["time"] = nodes[nodeid]["time"]
            node["values"] = nodes[nodeid]["values"]
            result = node
        
        # GET NODE:PROPERTY
        if nodeid is not False and varid is False and prop is not False:
            if prop=="nodename": result = config[nodeid]["nodename"]
            if prop=="firmware": result = config[nodeid]["firmware"]
            if prop=="hardware": result = config[nodeid]["hardware"]
            if prop=="names": result = config[nodeid]["names"]
            if prop=="units": result = config[nodeid]["units"]
            if prop=="values": result = nodes[nodeid]["values"]
                
        # GET NODE:VAR
        if nodeid is not False and varid is not False and prop is False:
            result = {}
            if len(config[nodeid]["names"])>varid:
                result["name"] = config[nodeid]["names"][varid]
            if len(nodes[nodeid]["values"])>varid:
                result["value"] = nodes[nodeid]["values"][varid]
            if len(config[nodeid]["units"])>varid:
                result["unit"] = config[nodeid]["units"][varid]
            if not len(result):
                result = "False"
        
        # GET NODE:VAR:PROPERTY        
        if nodeid is not False and varid is not False and prop is not False:
            if prop=="name" and len(config[nodeid]["names"])>varid:
                result = config[nodeid]["names"][varid]
            if prop=="unit" and len(config[nodeid]["units"])>varid:
                result = config[nodeid]["units"][varid]
            if prop=="value" and len(nodes[nodeid]["values"])>varid:
                result = nodes[nodeid]["values"][varid]
            if prop=="meta":
                filename = str(nodeid)+"_"+str(varid)
                meta = pyfina.get_meta(filename)
                meta["npoints"] = pyfina.get_npoints(filename)
                result = meta
            if prop=="data":
                filename = str(nodeid)+"_"+str(varid)
                start = request.args.get('start')
                end = request.args.get('end')
                interval = request.args.get('interval')
                data = json.dumps(pyfina.data(filename,start,end,interval))
                result = data
                
    if type(result) is dict: 
        result = json.dumps(result)
    if type(result) is list: 
        result = json.dumps(result)

    return Response(result, mimetype='text/plain')


@app.route('/conf',methods = ['POST','GET'])
def conf():
    if not session['valid']:
        return redirect("/")
        
    if request.method == 'POST':
        # might be good to do some input checking/sanitization here!
        with open(conffile,'w') as f:
            f.write(request.data)
        return "ok"
    else:
        with open(conffile, 'rb') as f:
            content = f.read()
        return Response(content, mimetype='text/plain')
# ------------------------------------------------------------------------------------    
# MQTT
# ------------------------------------------------------------------------------------
class MQTT_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.stop = False
        
    def run(self):
        while not self.stop and mqttc.loop() == 0:
            pass

def signal_handler(signal, frame):
    print "Exit on Ctrl-C"
    mqtt_thread.stop = True
    sys.exit(0)
    
def on_message(mosq, obj, msg):
    
    key = msg.topic.split("/")
    
    if key[0]=="api" and key[2]=="values":
        nodeid = str(key[1])
        
        now = int(time.time())
        values = msg.payload.split(",")
        
        nodes = r.get("nodes")
        if nodes is not None:
            nodes = json.loads(nodes)
        else:
            nodes = {}
            
        nodes[nodeid] = {"time":now, "values":values}
        r.set("nodes",json.dumps(nodes))
        
    socketio.emit('mqttrelay',{'topic':msg.topic,'payload':msg.payload},namespace='/test') 
    
# ------------------------------------------------------------------------------------    
# SOCKET IO
# ------------------------------------------------------------------------------------   
@socketio.on('my event', namespace='/test')
def test_message(message):
    pass

@socketio.on('connect', namespace='/test')
def test_connect():
    pass

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    pass 

# ------------------------------------------------------------------------------------    
# MAIN PROGRAM
# ------------------------------------------------------------------------------------
# Start MQTT (Mosquitto)
mqttc = mosquitto.Mosquitto()
mqttc.on_message = on_message
mqttc.connect("127.0.0.1",1883, 60, True)
mqttc.subscribe("log", 0)
mqttc.subscribe("api/#", 0)

signal.signal(signal.SIGINT, signal_handler)
mqtt_thread = MQTT_Thread()

if __name__ == '__main__':
    mqtt_thread.start()
    socketio.run(app,host='0.0.0.0',port=8000)
