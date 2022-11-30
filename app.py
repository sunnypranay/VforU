# create a login page and register page in flask 
# we have a database in mysql with the schema as follows:
# Users table:
# UserId | Name | Email | Password | Role | Category

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
import json
import mysql.connector as mysql
from decouple import config

user = config("user")
password = config("password")
host = config("host")
database = config("database")


app = Flask(__name__)
app.config["SECRET_KEY"] = "3ba690099520ffabb4f49adba0769cfac42be0c5"
login_manager = LoginManager()
login_manager.init_app(app)

# database config
config = {
    'user': user,
    'password': password,
    'host': host,
    'database': database,
    'raise_on_warnings': True
}


class User(UserMixin):
    pass

class IndividualUser:
    def __init__(self, id = None, username = None, email = None):
        self.id = id
        self.username = username
        self.email = email
    
    @property
    def is_authenticated(self):
        conn = mysql.connect(**config)
        cursor = conn.cursor()
        query = "SELECT * FROM Users WHERE Id = %s"
        cursor.execute(query, (self.id,))
        result = cursor.fetchall()
        conn.close()
        if len(result) > 0:
            return True
        else:
            return False
    
    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

def get_user(id):
    conn = mysql.connect(**config)
    cursor = conn.cursor()
    query = "SELECT * FROM Users WHERE Id = %s"
    cursor.execute(query, (id,))
    result = cursor.fetchall()
    conn.close()
    if len(result) > 0:
        return IndividualUser(result[0][0], result[0][1], result[0][2])
    else:
        return None

@login_manager.user_loader
def user_loader(id):
    return get_user(id)

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/register/<string:role>", methods = ["GET", "POST"])
def register(role):
    if request.method == "GET":
        return render_template("register.html")
    else:
        # This try block is to check if the data we got is in a vaild format or not
        # if the data is not in a valid format then we will send a 400 error and appropriate message
        try:
            data = request.get_json()
            name = data["name"]
            email = data["email"]
            password = data["password"]
            confirm_password = data["confirm_password"]
            role = data["role"]
            category = data["category"]
        except:
            return app.response_class(
                response=json.dumps({"message": "Invalid data"}),
                status=400,
                mimetype='application/json'
            )
        
        # This if block is to check if we got any empty data or not
        # if we got any empty data then we will send a 400 error and appropriate message

        if name == "" or email == "" or password == "" or confirm_password == "" or role == "" or category == "":
            return app.response_class(
                response=json.dumps({"message": "All fields are required"}),
                status=400,
                mimetype='application/json'
            )

        # This else if block is to check if the password and confirm password are same or not
        # if they are not same then we will send a 400 error and appropriate message

        elif password != confirm_password:
            return app.response_class(
                response=json.dumps({"message": "Passwords do not match"}),
                status=400,
                mimetype='application/json'
            )

        
        
        else:
            # This try block is to check if the database connection is successful or not
            # if the connection is not successful then we will send a 500 error and appropriate message
            try:
                conn = mysql.connect(**config)
            except:
                return app.response_class(
                    response=json.dumps({"message": "Error connecting to database"}),
                    status=500,
                    mimetype='application/json'
                )
            
            # This will check if the email is already registered or not
            # if the email is already registered then we will send a 400 error and appropriate message

            cursor = conn.cursor()
            query = "SELECT * FROM Users WHERE Email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchall()

            if len(result) > 0:
                return app.response_class(
                    response=json.dumps({"message": "User already exists"}),
                    status=400,
                    mimetype='application/json'
                )
            else:
                            # The below code will check if the password is of atleast 8 characters or not and atleast one uppercase, lowercase, digit and special character
                # if it is not of atleast 8 characters then we will send a 400 error and appropriate message

                if len(password) < 8:
                    return app.response_class(
                        response=json.dumps({"message": "Password should be atleast 8 characters"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one uppercase character then we will send a 400 error and appropriate message

                elif not any(char.isupper() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one uppercase character"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one lowercase character then we will send a 400 error and appropriate message

                elif not any(char.islower() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one lowercase character"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                
                # if it is not of atleast one digit then we will send a 400 error and appropriate message

                elif not any(char.isdigit() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one digit"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one special character then we will send a 400 error and appropriate message

                elif not any(not char.isalnum() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one special character"}),
                        status=400,
                        mimetype='application/json'
                    )
                # This try block is to check if the data is inserted into the database or not
                # if the data is not inserted into the database then we will send a 500 error and appropriate message
                try:
                    
                    query = "INSERT INTO Users (Name, Email, Password, Role, Category) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(query, (name, email, password, role, category))
                    conn.commit()
                    conn.close()
                except:
                    return app.response_class(
                        response=json.dumps({"message": "Error inserting data into database"}),
                        status=500,
                        mimetype='application/json'
                    )
            
            return app.response_class(
                response=json.dumps({"message": "User registered successfully"}),
                status=200,
                mimetype='application/json'
            )

if __name__ == "__main__":
    app.run(debug=True)