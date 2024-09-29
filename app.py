from flask import Flask, render_template, request, redirect
import gspread
import random
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load credentials path from environment variable
credentials_path = os.getenv("GOOGLE_CREDENTIALS")
if not credentials_path:
    raise ValueError("Google credentials path not found. Please set the GOOGLE_CREDENTIALS environment variable.")

# Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
client = gspread.authorize(creds)

# Open your Google Sheet
DS_Clients = client.open("DSALA Client Database").sheet1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create-client')
def create_client():
    return render_template('create_client.html')

@app.route('/edit-client')
def edit_client():
    return render_template('edit_client.html')

def generate_unique_id(existing_ids):
    while True:
        # Generate a random 6-digit ID
        random_id = random.randint(100000, 999999)
        # Check if the generated ID is unique
        if random_id not in existing_ids:
            return random_id

@app.route('/submit', methods=['POST'])
def submit():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    dob = request.form['dob']

    # Check if the user already exists
    existing_users = DS_Clients.get_all_records()
    existing_ids = [user['ID'] for user in existing_users if 'ID' in user]

    for i, user in enumerate(existing_users):
        if user['Email'] == email:
            return "this email is already associated with an existing client"

    # If user doesn't exist, generate a unique random ID
    unique_id = generate_unique_id(existing_ids)

    # Append new user with the unique ID
    DS_Clients.append_row([unique_id, first_name, last_name, email, dob])
    return redirect('/success')

@app.route('/edit', methods=['POST'])
def edit():
    email = request.form['email']
    new_name = request.form['name']
    
    existing_users = DS_Clients.get_all_records()
    for i, user in enumerate(existing_users):
        if user['Email'] == email:
            DS_Clients.update_cell(i+2, 1, new_name)
            return redirect('/success')

    return redirect('/notfound')

@app.route('/success')
def success():
    return "Your information has been saved!"

@app.route('/notfound')
def notfound():
    return "No user found with that email!"

if __name__ == "__main__":
    app.run(debug=True)
