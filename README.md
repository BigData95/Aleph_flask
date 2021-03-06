# Aleph Simulator


[![Deep Source](https://static.deepsource.io/deepsource-badge-light.svg)](https://deepsource.io/gh/BigData95/Aleph_flask/)

[![Website shields.io](https://img.shields.io/website-up-down-green-red/http/shields.io.svg)](https://aleph-simulator.herokuapp.com/)



It's a web app created with Flask, it allows you to:
  - Simulate failures with recovery on any node at a given time.
  - Watch the trace of the different internal components
  - Choose the nodes selected by the Oracle. 
  
And if you use it locally it allows you to change:
  - The network topology
  - Internal timers for every operation. 
  - Roles of the nodes. 
  - Service policies of the queues managed by the Qmanager.


### Installation

Aleph simulator requires Python 3.x to run. 

Clone the repo and create your virtual environment.
```
$ python3 -m venv .env 
```
Install the dependencies.
```sh
$ source .env/bin/active
$ pip install -r requirements.txt
```
For development environments...
```sh
$ export FLASK_DEBUG=1
```
Start the server.
```sh
$ export FLASK_APP=main.py
$ flask run
```
