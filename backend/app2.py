import json
from flask import Flask, jsonify, redirect, request, render_template, url_for, session
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
app.secret_key='assignementfor_TSE'
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


@app.route('/loginAuth', methods=['POST'])
def loginAuth():
    dataIN = request.form.to_dict(flat=False)
    user = db.users.find_one({"email": dataIN.get("email")})
    if user and verify_password(dataIN.get("password")[0], user.get("password")[0]):
        # Login successful
        dashData = jsonify({"message": "User logged in successfully"})
        return render_template('dash.html', data=dashData), 200
    else:
        # Login failed
        faildata = jsonify({"message": "Invalid username or password"})
        return render_template('login.html', message=faildata), 401


@app.route('/register_user', methods=['GET','POST'])
def register_user():
    user_data = request.form.to_dict(flat=False)
    user_id = create_user(user_data)
    userData=({"user_id": user_id})
    session['userData']=userData
    return redirect(url_for('dash'))

@app.route('/dash')
def dash():
    userData=session.get('userData',None)
    return render_template("dash.html",data=userData)

@app.route('/logout')
def logout():
    session.pop('userData', None)
    return redirect(url_for('index'))



@app.route('/')
def index():
    return "Welcome to the ChargeAnywhere App!"


if __name__ == '__main__':
    app.run(debug=True)

