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

@app.route('/edit-client-enter-id')
def edit_client_enter_id():
    return render_template('edit_client_enter_id.html', )

@app.route('/entered_id', methods=['POST'])
def entered_id():
    ID = request.form.get('ID')
    first_name = ''
    last_name = ''
    dob = ''
    email = ''
    
    existing_users = DS_Clients.get_all_records()

    print(ID)
    for user in existing_users:
        print(user['ID'])
    user = next((user for user in existing_users if (int(user['ID']) - int(ID) == 0)), None)
    if user:
        print(user.keys())
        first_name = user['First Name']
        last_name = user['Last Name']
        dob = user['DOB']
        email = user['Email']
        return render_template('edit_client.html', ID=ID, first_name=first_name, last_name=last_name, dob=dob, email=email)
        
    else:
        return "User not found. Try again."

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
        ID = request.form['ID']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        dob = request.form['dob']

        existing_users = DS_Clients.get_all_records()
        row_to_update = None
        for index, user in enumerate(existing_users):
            if int(user['ID']) == int(ID):
                row_to_update = index + 2
                break

        if row_to_update:
            new_values = [ID, first_name, last_name, email, dob]
       
            DS_Clients.update(f'A{row_to_update}:E{row_to_update}', [new_values])
            return "User updated successfully."
        else:
            return "User not found."

@app.route('/success')
def success():
    return "Your information has been saved!"


if __name__ == "__main__":
    app.run(debug=True)
