import json
from flask import Flask, jsonify, redirect, request, render_template, send_file, url_for, session, send_from_directory
from flask_restful import Api, Resource
from pymongo import MongoClient
from models import  verify_password,createMember, addCharger,addVehicle
from dotenv import load_dotenv
load_dotenv()
import os



atlas_connection_string = os.environ.get('DATABASE_URL', 'default_secret_key')

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_url_path='/frontend/static',
            static_folder='../frontend/static'
            )
api = Api(app)
app.secret_key='assignementfor_TSE'
client = MongoClient(atlas_connection_string)
db = client['ev_charging_db']

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, World!"}

api.add_resource(HelloWorld, '/hello')


@app.route('/login')
def login():
    session.pop('userData', None)
    return render_template("login.html",message="")

@app.route('/register')
def register():
     session.pop('userData', None)
     return render_template("register.html",message="")


@app.route('/loginAuth', methods=['POST'])
def loginAuth():
    dataIN = request.form.to_dict(flat=True)
    #user = db.users.find_one({"email": dataIN.get("email")})
    #session['userdata']=user

    userData=db.members.find_one({'email':dataIN['email']})
    if userData:
        userData['_id']=str(userData['_id'])
        userDict=dict(userData)
        session['userData']=userDict #need to change something here
    else:
        faildata = {"message": "Invalid username or password"}
        return render_template('login.html', message=faildata), 401
    
    if userData and verify_password(dataIN.get("password")[0], userData.get("password")[0]):
        # Login successful
        #dashData = jsonify({"message": "User logged in successfully"})
        return redirect(url_for('dash'))
    else:
        # Login failed
        faildata = {"message": "Invalid username or password"}
        return render_template('login.html', message=faildata), 401


@app.route('/register_user', methods=['GET','POST'])
def register_user():
    user_data = request.form.to_dict(flat=True)

    memberkeys = ['name', 'email', 'password','contact']
    chargerkeys=['lat','long','capacity','chargerType','chargerName']
    vehicleKeys=['model','make','EVchargerType']

    # Create a new dictionary with only the specified keys
    member_data = {key: user_data[key] for key in memberkeys if key in user_data}
    user_id = createMember(member_data)

    username=db.members.find_one({'name':member_data['name']})
    charger_data = {key: user_data[key] for key in chargerkeys if key in user_data}
    ChargerAddreply=addCharger(charger_data,username['name'])

    vehicle_data = {key: user_data[key] for key in vehicleKeys if key in user_data}
    vehicleAddreply=addVehicle(vehicle_data,username['name'])

    userData=db.members.find_one({'name':member_data['name']})
    userData['_id']=str(userData['_id'])
    userDict=dict(userData)
    session['userData']=userDict #need to change something here
    return redirect(url_for('dash'))

@app.route('/dash')
def dash():
    userData=session.get('userData',None)
    if userData:
    #print(userData)
        return render_template("dash.html",data=userData)
    else:
        return render_template("login.html",message="")

@app.route('/logout')
def logout():
    session.pop('userData', None)
    return redirect(url_for('login'))



@app.route('/')
def index():
    return "Welcome to the ChargeAnywhere App!"

@app.route('/getChargerHTML')
def getChargerHTML():
    userData=session.get('userData',None)
    render_template_data=render_template('ChargerDash.html',data=userData)
    tempfile='temp2.html'
    with open(tempfile,'w',encoding='utf-8') as temp_file:
        temp_file.write(render_template_data)
    return send_file(tempfile)

@app.route('/getChargers', methods=['GET'])
def getChargers():
    members = db.members.find()
    #print(members,"members")
    chargers_list = []
    for member in members:
        # print(members,"members 2")
        # print(members.get('chargers'),"adf")
        for charger in member.get('chargingStations', []):
            #print(charger, "charger")

            # Add variables only if they exist
            if 'lat' in charger:
                charger['lat'] = charger['lat']
            if 'long' in charger:
                charger['long'] = charger['long']
            if 'capacity' in charger:
                charger['capacity'] = charger['capacity']
            if 'chargerType' in charger:
                charger['chargerType'] = charger['chargerType']
            if 'chargerName' in charger:
                charger['chargerName'] = charger['chargerName']

            chargers_list.append(charger)
        # self.longitude = longitude
        # #self.owner_id = ObjectId(owner_id)  # Reference to an Owner document
        # self.capacity = capacity
        # self.available_slots = available_slots
        # self.chargerType = chargerType
        #     charger['_id'] = str(charger['_id'])
            chargers_list.append(charger)
    return jsonify(chargers_list)

@app.route('/getEVDashboardHTML')
def getEVDashboardHTML():
    userData=session.get('userData',None)
    render_template_data=render_template('evDashBoard.html',data=userData)
    tempfile='temp.html'
    with open(tempfile,'w',encoding='utf-8') as temp_file:
        temp_file.write(render_template_data)
    return send_file(tempfile)


if __name__ == '__main__':
    app.run(debug=True)

