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

DS_Clients = client.open("DSALA Client Database").sheet1
Contacts_Sheet = client.open("DSALA Client Database").get_worksheet(1)

def get_contacts(ID):
    print("hello")
    all_contacts = Contacts_Sheet.get_all_records()
    contacts = []
    for contact in all_contacts:
        print(int(contact['Index']))
    for contact in all_contacts:
        if int(contact["DS Client's ID"]) - int(ID) == 0:
            contacts.append([contact['First Name'], contact['Index']])
            print("hello")
    return contacts

def get_client_info(ID):
    first_name = ''
    last_name = ''
    dob = ''
    email = ''
    
    existing_users = DS_Clients.get_all_records()

    user = next((user for user in existing_users if (int(user['ID']) - int(ID) == 0)), None)
    if user:
        print(user.keys())
        first_name = user['First Name']
        last_name = user['Last Name']
        dob = user['DOB']
        email = user['Email']
        return([first_name, last_name, email, dob])
    else:
        return 'error'

def get_contact_info(ID, index):
    all_contacts = Contacts_Sheet.get_all_records()
    contact_info = []
    for contact in all_contacts:
        if int(contact["DS Client's ID"]) - int(ID) == 0 and int(contact["Index"]) - int(index) == 0:
            contact_info.append(contact['First Name'])
            contact_info.append(contact['Last Name'])
            contact_info.append(contact['Email'])
            contact_info.append(contact['Relationship'])
    return contact_info
    

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/find-client')
def find_client():
    return render_template('find_client.html')

@app.route('/create-client')
def create_client():
    return render_template('create_client.html')

@app.route('/create-contact')
def create_connection():
    ID = request.args.get('ID')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    return render_template('create_contact.html', ID=ID, first_name=first_name, last_name=last_name)


@app.route('/test')
def test():
    test_list = ["test 1", "test 2", "test 3"]
    return render_template('test.html', list=test_list)


@app.route('/entered_id', methods=['POST'])
def entered_id():
    ID = request.form.get('ID')
    
    return render_template('edit_client.html', ID=ID, info=get_client_info(ID), contacts=get_contacts(ID))
        

def generate_unique_id(existing_ids):
    while True:
        # Generate a random 6-digit ID
        random_id = random.randint(100000, 999999)
        # Check if the generated ID is unique
        if random_id not in existing_ids:
            return random_id

@app.route('/edit-contact-button')
def edit_contact_button():
    ID = request.args.get('ID')
    index = request.args.get('index')
    info = get_contact_info(ID, index)

    return render_template('edit_contact.html', ID=ID, index=index, info=get_contact_info(ID, index))


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
    ID = generate_unique_id(existing_ids)

    # Append new user with the unique ID
    DS_Clients.append_row([ID, first_name, last_name, email, dob])
    return render_template('edit_client.html', ID=ID, info=get_client_info(ID), contacts=get_contacts(ID))


@app.route('/submit-contact', methods=['POST'])
def submit_connection():
    ID = request.form['ID']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    relationship = request.form['relationship']

    existing_contacts = get_contacts(ID)
    indexes = []
    for contact in existing_contacts:
        indexes.append(int(contact[1]))

    new_index = 0
    if len(indexes) > 0:
        new_index = max(indexes) + 1

    Contacts_Sheet.append_row([ID, new_index, first_name, last_name, email, relationship])
    return render_template('edit_client.html', ID=ID, info=get_client_info(ID), contacts=get_contacts(ID))

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

@app.route('/edit-contact', methods=['POST'])
def edit_contact():
        ID = request.form['ID']
        index = request.form['index']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        relationship = request.form['relationship']

        existing_contacts = Contacts_Sheet.get_all_records()
        row_to_update = None
        for count, contact in enumerate(existing_contacts):
            if int(contact["DS Client's ID"]) == int(ID) and int(contact['Index']) == int(index):
                row_to_update = count + 2
                break

        if row_to_update:
            new_values = [ID, index, first_name, last_name, email, relationship]
       
            Contacts_Sheet.update(f'A{row_to_update}:F{row_to_update}', [new_values])
            return render_template('edit_client.html', ID=ID, info=get_client_info(ID), contacts=get_contacts(ID))
        else:
            return "User not found."

@app.route('/success')
def success():
    return "Your information has been saved!"


if __name__ == "__main__":
    app.run(debug=True)





#    all_connections = Connections_Sheet.get_all_records()
#    associated_connections = [connection in all_connections if (int(connection["DS Client's ID"]) - int(ID) == 0))]
