from pymongo import MongoClient
from bson import ObjectId
import bcrypt 

# Initialize MongoDB Client
client = MongoClient("mongodb+srv://chargeanywhere:chargeanywhere@cluster0.meajul2.mongodb.net/?retryWrites=true&w=majority")
db = client['ev_charging_db']

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

class ChargingStation:
    def __init__(self, location, owner_id, capacity, available_slots):
        self.location = location
        self.owner_id = ObjectId(owner_id)  # Reference to an Owner document
        self.capacity = capacity
        self.available_slots = available_slots
        # Todo - More details for each station

class Vehicle:
    def __init__(self, owner_id, model, make, charging_spec):
        self.owner_id = ObjectId(owner_id)  # Reference to a User document
        self.model = model
        self.make = make
        self.charging_spec = charging_spec

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

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

