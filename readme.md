# EmonView
An open source python, flask, socketio, js web application for monitoring and control

![emonview.png](emonview.png)

# Todo

- name? is there a better name than emonview
- show/hide graph
- zoom/pan graph
- graph statistics
- load config info such as units
- create node list from config first then populate with mqtt values
- wh elapsed processor
- full http rest api
- record button
- last updated value
- emonhub integration
- service based dispatchers listening on mqtt?
- complete concept apps:
    - my electric
    - heating controller
- mobile/tablet/responsive views
- services page

# Install

    sudo pip install Flask
    sudo pip install Flask-SocketIO
    sudo pip install mosquitto
    
Installation of Flask-SocketIO can be slow on a raspberrypi.

see: https://flask-socketio.readthedocs.org/en/latest/

Code is based on the flask-socketio example

# Login

Username: demo, password: demo
