import json
import uuid
from flask import Flask, jsonify, redirect, request, render_template, send_file, url_for, session, send_from_directory
from flask_restful import Api, Resource
from pymongo import MongoClient
from models import  verify_password,createMember, addCharger, addVehicle, create_booking_slot
from dotenv import load_dotenv
load_dotenv()
import os
from datetime import datetime



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
    chargerkeys=['id','lat','long','capacity','chargerType','chargerName']
    vehicleKeys=['model','make','EVchargerType']

    # Create a new dictionary with only the specified keys
    member_data = {key: user_data[key] for key in memberkeys if key in user_data}
    user_id = createMember(member_data)

    username=db.members.find_one({'name':member_data['name']})
    charger_data = {key: user_data[key] for key in chargerkeys if key in user_data}
    charger_data['id'] = str(uuid.uuid4())
    ChargerAddreply=addCharger(charger_data,username['name'])

    vehicle_data = {key: user_data[key] for key in vehicleKeys if key in user_data}
    vehicleAddreply=addVehicle(vehicle_data,username['name'])

    userData=db.members.find_one({'name':member_data['name']})
    userData['_id']=str(userData['_id'])
    userDict=dict(userData)
    session['userData']=userDict #need to change something here
    return redirect(url_for('dash'))

@app.route('/addcharger' ,methods=['GET','POST'])
def addcharger():
    user_data = request.form.to_dict(flat=True)
    chargerkeys=['capacity','chargerType','chargerName'] #add lat long when map is done
    charger_data = {key: user_data[key] for key in chargerkeys if key in user_data}
    userData=session.get('userData',None)
    addCharger(charger_data,userData['name'])
    userData=db.members.find_one({'name':userData['name']})
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
    

@app.route('/booking')
def booking():
    userData=session.get('userData',None)
    return render_template("booking.html",data=userData)

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
    chargers_list = []
    for member in members:
        for charger in member.get('chargingStations', []):
            # Add variables only if they exist
            if 'id' in charger:
                charger['id'] = charger['id']
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
    return jsonify(chargers_list)

@app.route('/getEVDashboardHTML')
def getEVDashboardHTML():
    userData=session.get('userData',None)
    render_template_data=render_template('evDashBoard.html',data=userData)
    tempfile='temp.html'
    with open(tempfile,'w',encoding='utf-8') as temp_file:
        temp_file.write(render_template_data)
    return send_file(tempfile)


@app.route('/create_booking', methods=['POST'])
def create_booking():

    # Get the raw request data
    raw_data = request.get_data()

    # Check if the request has JSON content
    if request.is_json:
        # Parse JSON data
        request_data = json.loads(raw_data)
    else:
        # If not JSON, parse as form data
        request_data = request.form.to_dict(flat=True)

    # Extract data from the request
    charging_id = request_data.get('charging_id')
    date = request_data.get('date')
    start_time = request_data.get('start_time')
    end_time = request_data.get('end_time')
    user_id = request_data.get('user_id')

    # Validate the required data
    if any(value is None for value in [user_id, charging_id, date, start_time, end_time]):
        return jsonify({"error": "Missing required data"}), 400

    # Convert date, start_time, and end_time to datetime objects
    date = datetime.strptime(date, "%Y-%m-%d")
    start_time = datetime.strptime(start_time, "%H:%M:%S")
    end_time = datetime.strptime(end_time, "%H:%M:%S")

    #first check whether the charging id exists or not in the DB
    # userData=db.bookingslot.find_one({'_id':charging_id})
    owner_data = db.members.find_one({"chargingStations.id": charging_id})
    if not owner_data:
        return jsonify({"error": "Owner not found"}), 404
    
    # Check if the same time slot is already taken
    existing_booking = db.bookingslots.find_one({
        "charging_id": charging_id,
        "date": date,
        "user_id": user_id,
        "$or": [
            {"start_time": {"$lt": end_time}, "end_time": {"$gt": start_time}},
            {"start_time": {"$gte": start_time, "$lt": end_time}},
            {"start_time": {"$lte": start_time}, "end_time": {"$gte": end_time}}
        ]
    })

    if existing_booking:
        return jsonify({"error": "Time slot already taken for the given date and charging station ID"}), 409

    # Create a BookingSlot object
    booking_slot = create_booking_slot(charging_id, date, start_time, end_time, user_id)

    return jsonify({"success": True}), 200
    

@app.route('/charger_bookings/<charging_id>', methods=['GET'])
def charger_bookings(charging_id):

    charging_station_data = db.bookingslots.find({"charging_id": charging_id})

    charging_stations = []
    for charging_station in charging_station_data:
        charging_station['_id'] = str(charging_station['_id'])
        charging_stations.append(charging_station)

        return jsonify({"data": charging_stations}), 200


@app.route('/user_bookings/<user_id>', methods=['GET'])
def user_bookings(user_id):

    user_bookings_cursor = db.bookingslots.find({"user_id": user_id})

    user_bookings = []
    for booking in user_bookings_cursor:
        booking['_id'] = str(booking['_id'])
        user_bookings.append(booking)

    return jsonify({"data": user_bookings}), 200


if __name__ == '__main__':
    app.run(debug=True)

