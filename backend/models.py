from pymongo import MongoClient
from bson import ObjectId
import bcrypt 
from dotenv import load_dotenv
load_dotenv()
import os

# Initialize MongoDB Client
client = MongoClient(os.environ.get('DATABASE_URL', 'default_secret_key'))
db = client['ev_charging_db']

#class for a member of the system
class Member:
    def __init__(self,name, email, contact_number, password, ChargingStations=None,EVs=None):
        self.name = name
        self.email = email
        self.contact_number = contact_number
        self.password = password
        self.chargingStations=ChargingStations if ChargingStations is not None else []
        self.ev=EVs if EVs is not None else []

#create a member
def createMember(memberData):
    # add validations here
    user_id = db.members.insert_one(memberData).inserted_id
    return str(user_id)


class ChargingStation:
    def __init__(self, latitude, longitude, capacity, chargerType, available_slots=None):
        self.latitude = latitude
        self.longitude = longitude
        #self.owner_id = ObjectId(owner_id)  # Reference to an Owner document
        self.capacity = capacity
        self.available_slots = available_slots
        self.chargerType = chargerType
        # Todo - More details for each station    

def addCharger(ChargingStation,username):
    newStation=db.members.update_one(
        {'name':username},
        {'$push':{'chargingStations':ChargingStation}})
    
    if newStation.modified_count > 0:
        return(f"Charging station Entry was added")
    else:
        return(f"some thing went wrong")
    
class Vehicle:
    def __init__(self, model, make, chargerType):
        #self.owner_id = ObjectId(owner_id)  # Reference to a User document
        self.model = model
        self.make = make
        self.chargerType = chargerType

def addVehicle(vehicle,username):
    newVehicle=db.members.update_one(
        {'name':username},
        {'$push':{'ev':vehicle}})
    
    if newVehicle.modified_count > 0:
        return(f"EV Entry was added")
    else:
        return(f"some thing went wrong")




class Owner:
    def __init__(self, name, email, contact_number, password, stations=None):
        self.name = name
        self.email = email
        self.contact_number = contact_number
        self.password = password
        self.stations = stations if stations is not None else []
class User:
    def __init__(self, name, email, contact_number, password, vehicle_ids=None, charging_history=None):
        self.name = name
        self.email = email
        self.contact_number = contact_number
        self.password = password
        self.vehicle_id = vehicle_ids if vehicle_ids is not None else []  # Reference to a Vehicle document
        self.charging_history = charging_history if charging_history is not None else []



class Vehicle:
    def __init__(self, owner_id, model, make, chargerType):
        self.owner_id = ObjectId(owner_id)  # Reference to a User document
        self.model = model
        self.make = make
        self.chargerType = chargerType

# Example function to create a user
def create_user(user_data):
    # TODO: valid all data.
    user_id = db.users.insert_one(user_data).inserted_id
    return str(user_id)

def create_owner(owner_data):
    # TODO: Validate all data
    owner_id = db.owners.insert_one(owner_data).inserted_id
    return str(owner_id)

# Example function to get a user by ID
def get_user(user_id):
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    return user_data

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed_password):
    # add encriptyon here
    #salt=hashed_password[:29].encode('utf-8')
    #salted_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password==hashed_password

def get_user(username):
    user_data = db.users.find_one({"username": username})
    return user_data