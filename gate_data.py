#gate_data

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import random, string
from sqlalchemy.orm import sessionmaker
from flask.wrappers import Response
from os import path
from sqlalchemy.exc import IntegrityError 
from datetime import datetime
import requests
from flask import Flask, request
from flask import jsonify
import json
from sqlalchemy.sql.elements import Null

from sqlalchemy.sql.sqltypes import Boolean



############################################################################################
############################################################################################
############################################################################################

# AUXILIARY METHODS


# this method generates and returns a random gate secret
def generateSecret():
    letters = string.digits
    secret = (''.join(random.choice(letters) for i in range(4)))
    return secret

# this method generates and returns a random user code
def generateUserCode():
    letters = string.digits
    codedigits = (''.join(random.choice(letters) for i in range(5)))
    code= str(codedigits) + str(random.choice(string.ascii_uppercase))
    return code

# this method checks if a user_code, created in certain_date, has, or not, expired
def hasCodeExpired(certain_date):
    now =datetime.now()
    difference = now - certain_date
    minutes = difference.total_seconds() / 60
    if (abs(minutes)<1):
        #print("Code has not expired")
        return "1"
    else:
        #print("Code has expired")
        return "-1"



############################################################################################
############################################################################################
############################################################################################

Base = declarative_base()

#SLQ access layer initialization
DATABASE_FILE = "gate_database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls


# TABLES 
class Gate(Base):
    __tablename__ = 'gate'
    gateID = Column(Integer, primary_key=True) # integer that uniquely identifies a specific gate
    gateSecret = Column(String, nullable=False) # string that describes the gate's secret
    gateLocation = Column(String, nullable=False) # string that describes the gate's location
    gateOpens = Column(Integer, nullable=False) # integer with the number of times a gate was opened
    def __repr__(self):
        return "<Gate(gateID=%d, gateSecret='%s', gateLocation='%s', gateOpens=%d)>" % (
                                self.gateID, self.gateSecret, self.gateLocation, self.gateOpens)
    def to_json(self): # method used to make a Gate object iterable, in order to be converted to json 
        return {
            "gateID": int(self.gateID),
            "gateSecret": self.gateSecret,
            "gateLocation": self.gateLocation,
            "gateOpens": int(self.gateOpens)
        }

class GateAccessLog(Base):
    __tablename__ = 'gate_access_log'
    gateID = Column(Integer, primary_key=True) # integer that uniquely identifies a specific gate
    userID = Column(String, nullable=True) # string that describes the gate's secret
    accessTime = Column(DateTime, primary_key=True) # string that describes the gate's location
    successfulAccess = Column(String, nullable=False) # integer with the number of times a gate was opened
    def __repr__(self):
        return "<GateAccessLog(gateID=%d, userID='%s', accessTime='%s', successfulAccess='%s')>" % (
                                self.gateID, self.userID, str(self.accessTime), str(self.successfulAccess))
    def to_json(self): # method used to make a GateAccessLog object iterable, in order to be converted to json 
        return {
            "gateID": int(self.gateID),
            "userID": self.userID,
            "accessTime": self.accessTime,
            "successfulAccess": (self.successfulAccess)
        }

Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()



############################################################################################
############################################################################################
############################################################################################

# QUERIES

# GATE

# GET

# lists all gates on the Gate Table
def queryListGates():
    return session.query(Gate).distinct().all()

# lists the gate of ID gate_id on the Gate Table
def queryGetGate(gate_id):
    return session.query(Gate).filter(Gate.gateID==gate_id).first()

# gets the location of gate with ID gate_id on the Gate Table
def queryGetGateLocationfromGate(gateID):
    gateLocation = session.query(Gate).filter(Gate.gateID==gateID).first()
    return Gate.gateLocation

# gets the secret of gate with ID gate_id on the Gate Table
def queryGetGateSecretfromGate(gateID):
    gate_secret = session.query(Gate).filter(Gate.gateID==gateID).first()
    return gate_secret.gateSecret

# SET

# inserts a new gate, with gateID id and gateLocation location on the Gate Table
def queryNewGate(id, location):
    try:
        qresult = session.query(Gate).filter(Gate.gateID==id).first()
        if qresult is None: # if a gate with this id doesnt exist yet, do the following
            secret = generateSecret()
            gate1 = Gate(gateID = id, gateSecret = secret, gateLocation=location, gateOpens = 0)
            session.add(gate1)
            session.commit() 
            return "1"
        else:
            return "-1"
    except IntegrityError:
        session.rollback()    
        return "-1"

# changes the location of a gate with ID gateID on the Gate Table
def queryChangeGateLocation(gateID, newGateLocation):
    b = queryGetGate(gateID)
    b.gateLocation = newGateLocation
    session.commit()

# changes the secret of a gate with ID gateID on the Gate Table
def queryChangeGateSecret(gateID, newGateSecret):
    b = queryGetGate(gateID)
    b.gateSecret = newGateSecret
    session.commit()

# GATE ACCESS LOG

# GET

# lists all gates accesses on the GateAccessLog Table
def queryListGateAccessLog():
    return session.query(GateAccessLog).all()

# lists all gates a user with ID userID accessed on the GateAccessLog Table
def queryListUserAccessLog(user_id):
    return session.query(GateAccessLog).where(GateAccessLog.userID==(user_id)).all()

# SET

# lists all gates accesses of a gate with ID gateID on the GateAccessLog Table
def querySetSucessfulAccess(gate_id,user_id):
    try:
        log1 = GateAccessLog(gateID = gate_id, userID = user_id, accessTime=datetime.now(), successfulAccess = "Access Granted")
        session.add(log1)
        session.commit() 
    except IntegrityError:
        session.rollback()     
        return "-1"

# lists all gates accesses of a gate with ID gateID on the GateAccessLog Table
def querySetUnsucessfulAccess(gate_id):
    try:
        log1 = GateAccessLog(gateID = gate_id, userID = str(-1), accessTime=datetime.now(), successfulAccess = "Access Denied")
        session.add(log1)
        session.commit() 
    except IntegrityError:
        session.rollback()     
        return "-1"

############################################################################################
############################################################################################
############################################################################################

# REST API
app = Flask(__name__)

# this GET endpoint is reached from the AdminWebApp, in the service.py file. 
# it lists all gates stored on the Gate Table, and returns them as json
@app.route('/API/gates', methods = ['GET'])
def getGateList():
    try:
        gates = queryListGates()
        content = [z.to_json() for z in gates]
        # Return query in json format
        return jsonify(content), 200
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503)

# this GET endpoint is reached from the AdminWebApp, in the service.py file. 
# it receives the id aa gate and returns its content as json
@app.route('/API/gates/<path:gate_id>', methods = ['GET'])
def getGateInfo(gate_id):
    try:
        gate = queryGetGate(gate_id)
        content = gate.to_json()
        # Return query in json format
        return jsonify(content), 200
    except:
        error_message = {"error": f"Gate {gate_id} not found"}
        return Response(response= json.dumps(error_message), status=404)

# this POST endpoint is reached from the AdminWebApp, in the service.py file. 
# it receives a json payload, with the gateID and gateLocation, and creates a new gate on the Gate Table, returning the newly created gate as json
@app.route('/API/gates', methods = ['POST'])
def postGate():
    try:
        content = request.get_json(force=False, silent=False, cache=True)
        # Verify json format
        queryNewGate(content["gateID"],content["gateLocation"])
        return Response(json.dumps(content,indent = 4), status=200)
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503)


# this GET endpoint is reached from the Service, in the service.py file. 
# it receives the id and secret of a gate, in order to verify if the secret belongs to the given gate
@app.route('/API/gates/<path:gate_id>/<path:gate_secret>', methods = ['GET'])
def checkGate(gate_id, gate_secret):
    try:
        gate = queryGetGate(gate_id)
        if gate_secret == gate.gateSecret:
            content = "True"
            return jsonify(content), 200
        else:
            content = "False"
            return jsonify(content), 200
    except:
        error_message = {"error": f"Gate {gate_id} not found"}
        return Response(response= json.dumps(error_message), status=404)


# this PUT endpoint is reached from the Service, in the service.py file. 
# it receives the gate_id, and increments its number of opens
@app.route('/API/gateOpens/<path:gate_id>', methods = ['PUT'])
def incrementGateOpens(gate_id):
    try:
        gate = queryGetGate(gate_id)
        gate.gateOpens += 1
        content = "True"
        return jsonify(content), 200
    except:
        error_message = {"error": f"Gate {gate_id} not found"}
        return Response(response= json.dumps(error_message), status=404)

# this GET endpoint is reached from the Service, in the service.py file. 
# it returns a json object with the gate access records stored in the GateAccessLog table
@app.route('/API/gateAccessLog', methods = ['GET'])
def getGateAccessLogList():
    try:
        gates = queryListGateAccessLog()
        content = [z.to_json() for z in gates]
        # Return query in json format
        return jsonify(content), 200
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503)   

# this GET endpoint is reached from the Service, in the service.py file. 
# it returns a json object with the current user's access records stored in the GateAccessLog table
@app.route('/API/userAccessLog/<path:current_user>', methods = ['GET'])
def getUserAccessLogList(current_user):
    try:
        gates = queryListUserAccessLog(current_user)
        content = [z.to_json() for z in gates]
        # Return query in json format
        return jsonify(content), 200
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503)           

# this POST endpoint is reached from the Service, in the service.py file. 
# it stores a successful (1) or unsuccessful (0) access to a gate in the GateAccessLog table, resending the recieved json content with a status message
@app.route('/API/gateAccess/<path:state>', methods = ['POST'])
def postGateAccess(state):
    try:
        if state == "1": # Sucessful Gate Access
            content = request.get_json(force=False, silent=False, cache=True)
            querySetSucessfulAccess(content["gateID"],content["userID"])
            return Response(json.dumps(content,indent = 2), status=200)
        else: # Unsucessful Gate Access
            content = request.get_json(force=False, silent=False, cache=True)
            querySetUnsucessfulAccess(content["gateID"])
            return Response(json.dumps(content,indent = 2), status=200)       
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503) 

############################################################################################
############################################################################################
############################################################################################

if __name__ == "__main__":
    try:
        url = f'http://127.0.0.1:8013/API/gates'
        r = requests.get(url)
        try:
            url = f'http://127.0.0.1:8012/API/gates'
            r = requests.get(url)
            try:
                url = f'http://127.0.0.1:8011/API/gates'
                r = requests.get(url)
            except:
                app.run(host='127.0.0.1', port=8011, debug=True)
        except:
            app.run(host='127.0.0.1', port=8012, debug=True)
    except:
        app.run(host='127.0.0.1', port=8013, debug=True)
    