
from email.mime import image
from pyexpat import model
from urllib import request
from flask import Flask,render_template,flash,session,request
from passlib.hash import sha256_crypt
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pandas as pd
import tensorflow as tf
import numpy as np
import keras
import os
import os.path
from keras import backend as K






app = Flask(__name__)

app.config['SECRET_KEY'] ='secretkey'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] =  'tb_detection_system'
UPLODED_IMAGES = r'C:\xampp\htdocs\TB_det_CNN\static\uploaded'
db=MySQL(app)




@app.route('/homepage')
def homepage():
    return render_template('index.html')     
        


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/logout')
def logout():
# Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('doc_id', None)
   session.pop('username', None)
   # Redirect to login page
   return render_template('login.html')

@app.route('/login',methods=['GET','POST'])
def login():
    render_template ('login.html')
    
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        
        password = request.form['password']
        
        hashed_pass=sha256_crypt.hash(password)
        unhashed_pass=sha256_crypt.verify("password",hashed_pass)

        
        # Check if account exists in DB using MySQL
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctors WHERE username = %s AND password = %s', (username, unhashed_pass,))
        # Fetch one record and return result
        user = cursor.fetchone()
        # If account exists in users table in out database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['doc_id']
            session['username'] = user['username']
            # Redirect to home page
            flash ('Logged in successfully!')
            return render_template('index.html')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/register',methods=['GET','POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form  and 'full_name' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access

         
        username = request.form['username']
        full_name=request.form['full_name']
        password = request.form['password']
        hashed_password=sha256_crypt.hash(password)
        email = request.form['email']
        # Check if account exists using MySQL
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM doctors WHERE username = %s', (username,))
        user = cursor.fetchone()
        # If account exists show error and validation checks
        if user:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # if user doesnt exists and the form data is valid, now insert new account into user table
            cursor.execute('INSERT INTO doctors VALUES (NULL,%s, %s, %s, %s)', (full_name,username,hashed_password, email,))
            db.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # if  Form is empty... (no  data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

#@app.route('/profile')
#def profile():
 #   return render_template("profile.html")



@app.route("/upload")
def upload():
    return render_template("form.html")

@app.route('/predict',methods=['GET','POST'])
def predict():
 #imagefile=request.form.get('imagefile')
 #image_path= "./static/uploaded"
 #imagefile.save(image_path)
     if request.method == 'POST':
        image_file = request.files['image']
        if image_file:
            image_path= os.path.join(UPLODED_IMAGES, image_file.filename)
            image_file.save(image_path)

     return render_template ('index.html')


     

if __name__ == '__main__':
        app.run(debug=True)
