#user_data

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import random, string
from sqlalchemy.orm import sessionmaker
from os import path
from sqlalchemy.exc import IntegrityError 
from datetime import datetime
from flask import Flask, request
from flask import jsonify
import json
from flask.wrappers import Response




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
        return "1"
    else:
        return "-1"



############################################################################################
############################################################################################
############################################################################################

Base = declarative_base()

#SLQ access layer initialization
DATABASE_FILE = "user_database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine('sqlite:///%s'%(DATABASE_FILE), echo=False, connect_args={'check_same_thread': False}) #echo = True shows all SQL calls


# TABLE
class User(Base):
    __tablename__ = 'user'
    userID = Column(String, primary_key=True) # integer that uniquely identifies a specific user
    userCode = Column(String, unique=True) # code associated with a user
    codeTime = Column(DateTime, nullable=False) # time of creation of a given user code
    def __repr__(self):
        return "<User(userID='%s', userCode='%s', codeTime= '%s')>" % (
                                self.userID, self.userCode, str(self.codeTime))
    def to_json(self): # method used to make a Gate object iterable, in order to be converted to json 
        return {
            "userID": self.userID,
            "userCode": self.userCode,
            "codeTime": self.codeTime,
        }


Base.metadata.create_all(engine) #Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()



############################################################################################
############################################################################################
############################################################################################

# QUERIES

# USER

# GET

# checks if a user whose code is user_code exists, and if so, it verifies if the user_code has, or not, expired
def queryCheckIfUserCodeExists(user_code):
    try:
        qresult = session.query(User).filter(User.userCode==user_code).first()
        if qresult is None:
            return "-1"
        else:
            code_time = session.query(User).filter(User.userCode==user_code).first()
            codeValid = hasCodeExpired(code_time.codeTime)
            if codeValid == "1":    
                return "1"
            else:
                return "-1"
    except:
        return "-1"

# SET

# inserts a new user, with ID user_id and code user_code on the User Table
def queryAddNewUser(user_id, user_code):
    try:
        qresult = session.query(User).filter(User.userID==user_id).first()
        if qresult is None:
            user1 = User(userID = user_id, userCode = user_code, codeTime = datetime.now())
            session.add(user1)
            try:
                session.commit() 
                return "1"
            except IntegrityError:
                session.rollback()     # error, there already is a user using this bank address or other     # constraint failed
                return "-1"
        else:
            qresult = session.query(User).filter(User.userID==user_id).first()
            qresult.userCode = user_code
            qresult.codeTime = datetime.now()
            try:
                session.commit()
                return "1"
            except IntegrityError:
                session.rollback()
                return "-1"
    except:
        return "-1"



############################################################################################
############################################################################################
############################################################################################

# REST API
app = Flask(__name__)

# this GET endpoint is reached from the Service, in the service.py file. 
# it generates a valid user code, adding it to the User Table and then returning it as JSON. 
@app.route("/API/users/<path:user_id>/user_code", methods = ['GET'])
def getNewUserCode(user_id):
    try:
        while(1):
            userCode = generateUserCode()
            state_code = queryAddNewUser(user_id, userCode)
            if state_code != "-1":
                #content = {"userCode": userCode}
                #return Response(json.dumps(content), status=200)
                return jsonify(userCode),200
    except:
        error_message = {"error": "Database not ready to handle request"}
        return Response(response= json.dumps(error_message), status=503)     

# this GET endpoint is reached from the Service, in the service.py file. 
# it receives the user code and the gate_id, and verifies if the user code exists in the User Table. If it exists, then the number of opens of gate with id gate_id is incremented
@app.route('/API/user_code/<path:user_code>', methods = ['GET'])
def checkUserCode(user_code):
    try:
        status = queryCheckIfUserCodeExists(user_code)
        if status == "1":
            content = "True"
            return jsonify(content), 200
        else:
            content = "False"
            return jsonify(content), 200
    except:
        error_message = {"error": f"UserCode {user_code} not found"}
        return Response(response= json.dumps(error_message), status=404)

############################################################################################
############################################################################################
############################################################################################

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8014, debug=True)