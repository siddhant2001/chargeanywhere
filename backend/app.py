import json
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource
from pymongo import MongoClient
from models import create_user, create_owner, verify_password
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

client = MongoClient(atlas_connection_string)
db = client['ev_charging_db']

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, World!"}

api.add_resource(HelloWorld, '/hello')

@app.route('/login')
def login():
    return render_template("login.html",message="")

@app.route('/register')
def register():
     return render_template("register.html",message="")

@app.route('/register_user', methods=['POST'])
def register_user():
    user_data = request.json
    user_id = create_user(user_data)
    return jsonify({"user_id": user_id}), 201

@app.route('/register_owner', methods=['POST'])
def register_owner():
    owner_data = request.json
    owner_id = create_owner(owner_data)
    return jsonify({"owner_id": owner_id}), 201



@app.route('/login_user', methods=['POST'])
def login_user():
    data = request.json
    user = db.users.find_one({"email": data["email"]})

    if user and verify_password(data["password"], user["password"]):
        # Login successful
        return jsonify({"message": "User logged in successfully", "user_id": str(user["_id"])}), 200
    else:
        # Login failed
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/login_owner', methods=['POST'])
def login_owner():
    data = request.json
    owner = db.owners.find_one({"email": data["email"]})

    if owner and verify_password(data["password"], owner["password"]):
        # Login successful
        return render_template("login.html",message=jsonify({"message": "Owner logged in successfully", "owner_id": str(owner["_id"])})), 200
    else:
        # Login failed
        return render_template("login.html",message=jsonify({"message": "Invalid username or password"})), 401


if __name__ == '__main__':
    app.run(debug=True)
