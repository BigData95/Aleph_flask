# Aleph Simulator


[![Deep Source](https://static.deepsource.io/deepsource-badge-light.svg)](https://deepsource.io/gh/BigData95/Aleph_flask/)



It's a web app created with Flask, it allow you to:
  - Simulate failures with recovery on any node at a given time.
  - Watch the trace of the diferente internal components
  
And if you use it localy it allow you to change:
  - The network topology
  - Internal timers for every operation. 
  - Roles of the nodes. 
  - Service policies of the queues managed by the Qmanager.


### Installation

Aleph simulator requires Python 3.x to run. 

Clone the repo and create your virtual enviroment.
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
