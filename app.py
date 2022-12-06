# create a login page and register page in flask 
# we have a database in mysql with the schema as follows:
# Users table:
# UserId | Name | Email | Password | Role | Category

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
import json
import mysql.connector as mysql
from decouple import config
import openai

user = config("user")
password = config("password")
host = config("host")
database = config("database")
secret_key = config("SECRET_KEY")
openaiKey = config("OPENAI_KEY")


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"
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
        query = "SELECT * FROM Users WHERE UserId = %s"
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
    query = "SELECT * FROM Users WHERE UserId = %s"
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("signup.html")
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
                response=json.dumps({"message": "Invalid data", "status": "error"}),
                status=400,
                mimetype='application/json'
            )
        
        # This if block is to check if we got any empty data or not
        # if we got any empty data then we will send a 400 error and appropriate message

        if name == "" or email == "" or password == "" or confirm_password == "" or role == "" or category == "":
            return app.response_class(
                response=json.dumps({"message": "All fields are required", "status": "error"}),
                status=400,
                mimetype='application/json'
            )

        # This else if block is to check if the password and confirm password are same or not
        # if they are not same then we will send a 400 error and appropriate message

        elif password != confirm_password:
            return app.response_class(
                response=json.dumps({"message": "Passwords do not match", "status": "error"}),
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
                    response=json.dumps({"message": "Error connecting to database", "status": "error"}),
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
                    response=json.dumps({"message": "User already exists", "status": "error"}),
                    status=400,
                    mimetype='application/json'
                )
            else:
                            # The below code will check if the password is of atleast 8 characters or not and atleast one uppercase, lowercase, digit and special character
                # if it is not of atleast 8 characters then we will send a 400 error and appropriate message

                if len(password) < 8:
                    return app.response_class(
                        response=json.dumps({"message": "Password should be atleast 8 characters", "status": "error"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one uppercase character then we will send a 400 error and appropriate message

                elif not any(char.isupper() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one uppercase character", "status": "error"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one lowercase character then we will send a 400 error and appropriate message

                elif not any(char.islower() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one lowercase character", "status": "error"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                
                # if it is not of atleast one digit then we will send a 400 error and appropriate message

                elif not any(char.isdigit() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one digit", "status": "error"}),
                        status=400,
                        mimetype='application/json'
                    )
                
                # if it is not of atleast one special character then we will send a 400 error and appropriate message

                elif not any(not char.isalnum() for char in password):
                    return app.response_class(
                        response=json.dumps({"message": "Password should have atleast one special character", "status": "error"}),
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
                        response=json.dumps({"message": "Error inserting data into database", "status": "error"}),
                        status=500,
                        mimetype='application/json'
                    )
            
            return app.response_class(
                response=json.dumps({"message": "User registered successfully", "status": "success"}),
                status=200,
                mimetype='application/json'
            )

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect(url_for('conversation'))
        return render_template("login.html")
    else:
        # This try block is to check if the data we got is in a vaild format or not
        # if the data is not in a valid format then we will send a 400 error and appropriate message
        try:
            data = request.get_json()
            email = data["email"]
            password = data["password"]
        except:
            return app.response_class(
                response=json.dumps({"message": "Invalid data", "status": "error"}),
                status=400,
                mimetype='application/json'
            )
        
        # This if block is to check if we got any empty data or not
        # if we got any empty data then we will send a 400 error and appropriate message

        if email == "" or password == "":
            return app.response_class(
                response=json.dumps({"message": "All fields are required", "status": "error"}),
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
                    response=json.dumps({"message": "Error connecting to database", "status": "error"}),
                    status=500,
                    mimetype='application/json'
                )
            
            # This will check if the email is registered or not
            # if the email is not registered then we will send a 400 error and appropriate message

            cursor = conn.cursor()
            query = "SELECT * FROM Users WHERE Email = %s"
            cursor.execute(query, (email,))
            result = cursor.fetchall()

            if len(result) == 0:
                return app.response_class(
                    response=json.dumps({"message": "User does not exist", "status": "error"}),
                    status=400,
                    mimetype='application/json'
                )
            else:
                # This will check if the password is correct or not
                # if the password is not correct then we will send a 400 error and appropriate message

                if result[0][3] != password:
                    return app.response_class(
                        response=json.dumps({"message": "Incorrect password", "status": "error"}),
                        status=400,
                        mimetype='application/json'
                    )
                else:
                    # This try block is to check if the data is inserted into the database or not
                    # if the data is not inserted into the database then we will send a 500 error and appropriate message
                    try:
                        user = IndividualUser(result[0][0], result[0][1], result[0][2])
                        login_user(user)
                        # strore the user id in the session
                        return app.response_class(
                            response=json.dumps({"message": "User logged in successfully", "status": "success"}),
                            status=200,
                            mimetype='application/json'
                        )
                    except:
                        return app.response_class(
                            response=json.dumps({"message": "Error While logging user Please try again", "status": "error"}),
                            status=500,
                            mimetype='application/json'
                        )


@app.route("/conversation", methods = ["GET", "POST"])
@login_required
def conversation():
    if request.method == "GET":
        return render_template("conversation.html")
    else:
        # get the current user id from the login session
        # This post method will get a data from front end which a message form the user 
        # we have to check if the message is not a empty message then we will insert the message into the database
        # In the databse we have a table named conversation which has 4 columns
        # 1. ConversationId - This is the primary key of the table and it is auto incremented
        # 2. UserId - This is the user id of the user who sent the message which is a foreign key of the table Users
        # 3. UserMessage - This is a message sent by the user
        # 4. AIBotMessage - This is a message sent by the AI bot
        # and we have to generate a string in a format of "Human: {message}\nAI:", and send it to the OpenAI API
        # and we have to get the response from the OpenAI API and store it in the database and send it to the front end
        # if the message is empty then we will send a 400 error and appropriate message

        try:
            data = request.get_json()
            message = data["message"]
        except:
            return app.response_class(
                response=json.dumps({"message": "Invalid data", "status": "error"}),
                status=400,
                mimetype='application/json'
            )
        
        if message == "":
            return app.response_class(
                response=json.dumps({"message": "Message cannot be empty", "status": "error"}),
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
                    response=json.dumps({"message": "Error connecting to database", "status": "error"}),
                    status=500,
                    mimetype='application/json'
                )
            
            # This try block is to check if the data is inserted into the database or not
            # if the data is not inserted into the database then we will send a 500 error and appropriate message
            try:
                cursor = conn.cursor()
                query = "INSERT INTO conversation (UserId, UserMessage) VALUES (%s, %s)"
                cursor.execute(query, (current_user.id, message))
                conn.commit()
                conn.close()
            except:
                return app.response_class(
                    response=json.dumps({"message": "Error inserting data into database", "status": "error"}),
                    status=500,
                    mimetype='application/json'
                )
            
            # This try block is to check if the data is inserted into the database or not
            # if the data is not inserted into the database then we will send a 500 error and appropriate message
            try:
                conn = mysql.connect(**config)
            except:
                return app.response_class(
                    response=json.dumps({"message": "Error connecting to database", "status": "error"}),
                    status=500,
                    mimetype='application/json'
                )
            
            # and we have to generate a string in a format of "Human: {message}\nAI:", and send it to the OpenAI API
            # and we have to get the response from the OpenAI API and store it in the database and send it to the front end
            # try:
            conversation = "Human: " + message + "\nAI:"
            # set the api key
            openai.api_key = openaiKey
            start_sequence = "\nAI:"
            restart_sequence = "\nHuman: "

            # In emergency situations use text-davinci-003
            response = openai.Completion.create(
            model="text-curie-001",
            prompt=conversation,
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
            )

            # get the conversation Id from the database and store it in a variable
            cursor = conn.cursor()
            query = "SELECT ConversationId FROM conversation ORDER BY ConversationId DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchall()
            conversationId = result[0][0]

            # now we have to insert the response from the OpenAI API into the database
            cursor = conn.cursor()
            query = "UPDATE conversation SET AIBotMessage = %s WHERE ConversationId = %s"
            cursor.execute(query, (response["choices"][0]["text"], conversationId))
            conn.commit()
            conn.close()
            return app.response_class(
                response=json.dumps({"message": response["choices"][0]["text"], "status": "success"}),
                status=200,
                mimetype='application/json'
            )
            # except:
            #     return app.response_class(
            #         response=json.dumps({"message": "Error while getting response from OpenAI API"}),
            #         status=500,
            #         mimetype='application/json'
            #     )
            
@app.route("/aboutus")
def aboutus():
    return render_template("about.html")           


if __name__ == "__main__":
    app.run(debug=True)