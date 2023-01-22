

############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################

from os import abort
from flask import json
from flask.wrappers import Response
import requests
from requests_oauthlib.oauth2_session import OAuth2Session
import qrcode
from flask import Flask, request, redirect, render_template, session, url_for
from flask.json import jsonify
import os
import fenixedu

url_base = 'http://127.0.0.1:8000' # service  url
url_base_user = 'http://127.0.0.1:8014' # user data  url
url_base_gate_1 = 'http://127.0.0.1:8013' # gate data  url
url_base_gate_2 = 'http://127.0.0.1:8012' # gate data  url
url_base_gate_3 = 'http://127.0.0.1:8011' # gate data  url


############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################


url_base = 'http://127.0.0.1:8000' # service  url
admin_list = ["ist190196"]
client_id = "570015174623400"
client_secret = "GAxCodOkvMRlwBz4a7hZRpcUFuTdbgD+B/jreNiZFO10pGJtNUakd9hM+YkyVeKNbRwZ2O0na8Frdd12g5d1sA=="
authorization_base_url = 'https://fenix.tecnico.ulisboa.pt/oauth/userdialog'
token_url = 'https://fenix.tecnico.ulisboa.pt/oauth/access_token'

############################################################################################
############################################################################################

# AUXILIARY METHODS

# guarantees that an admin user is authenticated when accessing certain webpages
def admin_access(function):
    def wrapper(*args, **kwargs):
        try:
            fenix = OAuth2Session(client_id, token=session['oauth_token'])
            data = fenix.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
            user = data["username"]
            if (user in admin_list):
                return function()
            else:
                return demo()
        except:
            return demo()
    wrapper.__name__=function.__name__
    return wrapper

# guarantees that an user is authenticated when accessing certain webpages
def user_access(function):
    def wrapper(*args, **kwargs):
        try:
            fenix = OAuth2Session(client_id, token=session['oauth_token'])
            data = fenix.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
            user = data["username"]
            return function()
        except:
            return demo()
    wrapper.__name__=function.__name__
    return wrapper


############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################


# user and admin_web_app


############################################################################################
############################################################################################
############################################################################################



# AUXILIARY METHODS

#GET METHODS

# requests a gate list to GateData 
def requestGateList():
    try:
        url = f'{url_base_gate_1}/API/gates'
        r = requests.get(url)
        data = r.json()
        return data
    except:
        try:
            url = f'{url_base_gate_2}/API/gates'
            r = requests.get(url)
            data = r.json()
            return data
        except:
            try:
                url = f'{url_base_gate_3}/API/gates'
                r = requests.get(url)
                data = r.json()
                return data
            except:
                return "-1"

# requests a gate access log list to GateData 
def requestGateAccessLogList():
    try:
        url = f'{url_base_gate_1}/API/gateAccessLog'
        r = requests.get(url)
        data = r.json()
        return data
    except:
        try:
            url = f'{url_base_gate_2}/API/gateAccessLog'
            r = requests.get(url)
            data = r.json()
            return data
        except:
            try:
                url = f'{url_base_gate_3}/API/gateAccessLog'
                r = requests.get(url)
                data = r.json()
                return data
            except:
                return "-1"



# requests an user access log list to GateData 
def requestUserAccessLogList(current_user):
    try:
        url = f'{url_base_gate_1}/API/userAccessLog/{current_user}'
        r = requests.get(url)
        data = r.json()
        return data
    except:
        try:
            url = f'{url_base_gate_2}/API/userAccessLog/{current_user}'
            r = requests.get(url)
            data = r.json()
            return data
        except:
            try:
                url = f'{url_base_gate_2}/API/userAccessLog/{current_user}'
                r = requests.get(url)
                data = r.json()
                return data
            except:
                return "-1"


# requests the information of gate of id gate_id to GateData 
def getGateInfo(gate_id):
    try:
        url = f'{url_base_gate_1}/API/gates/{gate_id}'
        r = requests.get(url)
        data = r.json()
        return data
    except:
        try:
            url = f'{url_base_gate_2}/API/gates/{gate_id}'
            r = requests.get(url)
            data = r.json()
            return data
        except:
            try:
                url = f'{url_base_gate_3}/API/gates/{gate_id}'
                r = requests.get(url)
                data = r.json()
                return data
            except:
                return "-1"

# asks UserData if a given user_code is valid and sends to GateData the gate_id, to increment the number of opens, in case user_code is valid
def checkUserCode(user_code, gate_id):
    url_user_code = f'{url_base_user}/API/user_code/{user_code}'
    r= requests.get(url_user_code)
    data=r.json()
    if data == "True":
        try:
            url_gate_id = f'{url_base_gate_1}/API/gateOpens/{gate_id}'
            r_2= requests.put(url_gate_id)
            data=r_2.json()
            if data == "True":
                return "True"
            else:
                return "False"
        except:
            try:
                url_gate_id = f'{url_base_gate_2}/API/gateOpens/{gate_id}'
                r_3= requests.put(url_gate_id)
                data=r_3.json()
                if data == "True":
                    return "True"
                else:
                    return "False"
            except:
                try:
                    url_gate_id = f'{url_base_gate_3}/API/gateOpens/{gate_id}'
                    r_4= requests.put(url_gate_id)
                    data=r_4.json()
                    if data == "True":
                        return "True"
                    else:
                        return "False"
                except:
                    return "-1"
    else:
        return "False"

# asks GateData if a given gate_secret belongs to a gate of a given gate_id
def checkGate(gate_id, gate_secret):
    try:
        url = f'{url_base_gate_1}/API/gates/{gate_id}/{gate_secret}'
        r= requests.get(url)
        data = r.json()
        if data == "True":
            return "True"
        else:
            return "False"
    except:
        try:
            url = f'{url_base_gate_1}/API/gates/{gate_id}/{gate_secret}'
            r= requests.get(url)
            data = r.json()
            if data == "True":
                return "True"
            else:
                return "False"
        except:
            try:
                url = f'{url_base_gate_1}/API/gates/{gate_id}/{gate_secret}'
                r= requests.get(url)
                data = r.json()
                if data == "True":
                    return "True"
                else:
                    return "False"
            except:
                return "False"

# requests a user code from UserData and, if valid, returning it to the UserWebApp
def requestUserCodeFromServer(user_id):
    try:
        url = f'{url_base_user}/API/users/{user_id}/user_code'
        r = requests.get(url)
        if r.status_code == 503:
            return "-1"
        else:
            return str(r.text.strip('\n'))
    except:
        return "-1"

# POST METHODS

# requests GateData if it can create a new gate of id gate_id and location gateLocation
def postGate(gateID, gateLocation):
    payload = {"gateID": gateID, "gateLocation": gateLocation}
    try:
        r = requests.post(f'{url_base_gate_1}/API/gates', json = payload)
    except:
        try:
            r = requests.post(f'{url_base_gate_2}/API/gates', json = payload)
        except:
            try:
                r = requests.post(f'{url_base_gate_3}/API/gates', json = payload)
            except:
                return 
    return

# requests GateData if it can register a successful gate access on the gate access log
def postSuccessfulGateAccess(gateID, userID):
    payload = {"gateID": gateID, "userID": userID}
    try:
        r = requests.post(f'{url_base_gate_1}/API/gateAccess/{1}', json = payload)
    except:
        try:
            r = requests.post(f'{url_base_gate_2}/API/gateAccess/{1}', json = payload)
        except:
            try:
                r = requests.post(f'{url_base_gate_3}/API/gateAccess/{1}', json = payload)
            except:
                return 

# requests GateData if it can register an unsuccessful gate access on the gate access log
def postUnsuccessfulGateAccess(gateID):
    payload = {"gateID": gateID}
    try:
        r = requests.post(f'{url_base_gate_1}/API/gateAccess/{0}', json = payload)
    except:
        try:
            r = requests.post(f'{url_base_gate_2}/API/gateAccess/{0}', json = payload)
        except:
            try:
                r = requests.post(f'{url_base_gate_3}/API/gateAccess/{0}', json = payload)
            except:
                return 
    return

############################################################################################
############################################################################################
############################################################################################

# WebApp

app = Flask(__name__)

# for when an authentication error occurs
@app.route("/error")
def error():
    try:
        authe = OAuth2Session(client_id, redirect_uri="http://127.0.0.1:8000/callback")
        authorization_url, state = authe.authorization_url(authorization_base_url)
        session['oauth_state'] = state
        return redirect(authorization_url)
    except:
        return render_template("index_error.html", message="Not Able to Connect to the FENIX Authentication Service!")

# main page, redirects the user to the authentication proccess
@app.route("/")
def demo():
    try:
        authe = OAuth2Session(client_id, redirect_uri="http://127.0.0.1:8000/callback")
        authorization_url, state = authe.authorization_url(authorization_base_url)
        session['oauth_state'] = state
        return redirect(authorization_url)
    except:
        return render_template("index_error.html", message="Not Able to Connect to the FENIX Authentication Service!")

# callback page, in order to fetch the user's token
@app.route("/callback", methods=["GET"])
def callback():
    try:


        authe = OAuth2Session(client_id=client_id, scope=None, state=session['oauth_state'], redirect_uri="http://127.0.0.1:8000/callback")

        token = authe.fetch_token(token_url, client_secret=client_secret,
                                authorization_response=request.url)

        # At this point you can fetch protected resources but lets save
        # the token and show how this is done from a persisted token
        # in /profile.
        session['oauth_token'] = token

        return redirect(url_for('.profile'))
    except:
        return render_template("index_error.html", message="Not Able to Connect to the FENIX Authentication Service!")


# profile page, in order to fetch the user's id and redirect him to its respective web_app
@app.route("/profile", methods=["GET"])
def profile():
    try:
        authe = OAuth2Session(client_id, token=session['oauth_token'])
        authe_profile = authe.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
        user_id = authe_profile["username"]
        if user_id in admin_list:
            return render_template("index_admin.html", message="Welcome to the AdminWebApp!")   
        else:
            return render_template("index_user.html", message="Welcome to the UserWebApp!")  
    except:
        return render_template("index_error.html", message="Not Able to Connect to the FENIX Authentication Service!")

# UserWebApp
@app.route('/user_web_app')
@user_access
def user_index():
    return render_template("index_user.html", message="Welcome to the UserWebApp!")   

# Generate and display qrcode with the user code
@app.route('/qrcode')
@user_access
def userQRCode():
    try:
        authe = OAuth2Session(client_id, token=session['oauth_token'])
        authe_profile = authe.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
        user_id = authe_profile["username"]
        userCode = requestUserCodeFromServer(user_id)
        qr_code_message = user_id + " " + str(userCode.strip('"'))
        if (userCode == "-1"):
            return render_template("index_user.html", message="QR Code couldn't be generated, check your connection!")
        else:
            return render_template("qrcode_user.html", qr_code = qr_code_message)
    except:
        return render_template("index_user.html", message="QR Code couldn't be generated, check your connection!")

# this page lists all gates successfully accessed by the user
@app.route("/userLog")
@user_access
def listUserLog():
    try:
        authe = OAuth2Session(client_id, token=session['oauth_token'])
        authe_profile = authe.get('https://fenix.tecnico.ulisboa.pt/api/fenix/v1/person').json()
        user_id = authe_profile["username"]
        current_user = user_id
        queryresult=requestUserAccessLogList(current_user)
        if queryresult != "-1":
            return render_template("listUserLog_user.html", list = queryresult)
        else: 
            return render_template("index_user.html", message="Connection to the database was lost!") 
    except:
        return render_template("index_user.html", message="Connection to the database was lost!")

# GateWebApp
@app.route("/gate_web_app")
def index_gate():
    return app.send_static_file('index_gate.html')



# AdminWebApp

# admin home page
@app.route('/admin_web_app')
@admin_access
def admin_index():
    return render_template("index_admin.html", message="Welcome to the AdminWebApp!")   

# this page lists all gates stored in GateData
@app.route("/listGates")
@admin_access
def listGates():
    try:
        queryresult=requestGateList()
        if queryresult != "-1":
            return render_template("listGates_admin.html", list = queryresult)
        else:
            return render_template("index_admin.html", message="Connection to the database was lost!") 
    except:
        return render_template("index_admin.html", message="Connection to the database was lost!")


# this page has 2 submission text areas for the gateID and gateLocation
@app.route("/newGate", methods = ['GET','POST'])
@admin_access
def newGate():
    return render_template("newGate_admin.html")

# this page is used after the user clicks on the gate submit button, in the page newGate
# it tries to store the created gate on GateData and then, if it does so, it redirects the user to the showGate page, where the created gate is shown
# if an already existing gate_id is submitted, then, the page simply shows the already existing gate, and does not update it
@app.route("/createGate", methods = ['GET', 'POST'])
@admin_access
def createGate():
    try:
        if request.method == 'POST':
            result = request.form
            gateID = result["gateID"]
            gateLocation = result["gateLocation"]
            postGate(gateID, gateLocation)
            queryresult=getGateInfo(gateID)
            if queryresult != "-1":
                return render_template("showGate_admin.html", dict = queryresult) 
            else:
                return render_template("index_admin.html", message="Invalid Input!") 
    except:
        return render_template("index_admin.html", message="Connection to the database was lost!")

# this page lists all gates stored in GateData
@app.route("/listGateLog")
@admin_access
def listGateLog():
    try:
        queryresult=requestGateAccessLogList()
        if queryresult != "-1":
            return render_template("listGateLog_admin.html", list = queryresult) 
        else:
            return render_template("index_admin.html", message="Connection to the database was lost!")
    except:
        return render_template("index_admin.html", message="Connection to the database was lost!")




###############################################################################################
###############################################################################################
###############################################################################################



# Service


# REST API 

# this endpoint is reached from the GateWebApp. it receives the id and secret of a gate and sends them to the checkGate method, in order to verify if the secret corresponds to the given gate
@app.route("/API/checkGateExists", methods = ['GET', 'POST'])
def checkGateExists():
    try:
        gate_id = request.args.get('gateID')
        gate_secret = request.args.get('gateSecret')
        validation = checkGate(gate_id, gate_secret)
        return jsonify(validation), 200
    except:
        error_message = {"error": "Gate not found"}
        return Response(response= json.dumps(error_message), status=404)

# this endpoint is reached from the GateWebApp. it receives the user code and a gate ID and sends them to the checkUserCode method, in order to verify if the user_code is valid and, if so,
# to increment the gate opens of gate with id gate_id
@app.route("/API/checkUserCodeExists", methods = ['GET', 'POST'])
def checkUserCodeExists():
    try:
        user_code = request.args.get('user_code')
        gate_id = request.args.get('gate_id')
        user_id = request.args.get('user_id')
        validation = checkUserCode(user_code, gate_id)
        if validation == "True":
            postSuccessfulGateAccess(gate_id, user_id)
        elif validation == "False":
            postUnsuccessfulGateAccess(gate_id)
        return jsonify(validation), 200
    except:
        error_message = {"error": "User not found"}
        return Response(response= json.dumps(error_message), status=404)

############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################


# Main

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.secret_key = os.urandom(24)
    app.run(host='127.0.0.1', port=8000, debug=True)


############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
############################################################################################
