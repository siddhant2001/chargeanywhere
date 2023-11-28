import json
from flask import Flask, jsonify, redirect, request, render_template, url_for
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


@app.route('/loginAuth', methods=['GET','POST'])
def loginAuth():
    data=request.form.to_dict(flat=False)
    user = db.users.find_one({"email": data["email"]})

    if user and verify_password(data["password"], user["password"]):
        # Login successful
        dashData=jsonify({"message": "User logged in successfully", "user_id": str(user["_id"])})
        return  render_template('dash.html',data=dashData),200
    else:
        # Login failed
        faildata=jsonify({"message": "Invalid username or password"})
        return render_template('login.html',message=faildata), 401


@app.route('/register_user', methods=['GET','POST'])
def register_user():
    user_data = request.form.to_dict(flat=False)
    print(user_data)
    user_id = create_user(user_data)
    print(user_id)
    return jsonify({"user_id": user_id}), 201

if __name__ == '__main__':
    app.run(debug=True)