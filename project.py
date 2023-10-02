
import os
import webbrowser
from flask import Flask, request, render_template, redirect, url_for
from googleapiclient.discovery import build
from google.oauth2 import service_account

app = Flask(__name__)

# Configure the folder where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

credential_path = 'credentials.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to your Google Sheets API credentials JSON file
CREDENTIALS_FILE = 'credentials.json'  # Update with your credentials file path


# Helper function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Load Google Sheets API credentials
credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', credentials=credentials)

# Sample HTML form for file upload
upload_form = """
<!doctype html>
<title>CSV to Google Sheets</title>
<h1>Upload CSV File</h1>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
"""


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has a file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # Save the uploaded file to the UPLOAD_FOLDER
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)

            # Create a new Google Sheets spreadsheet
            spreadsheet = service.spreadsheets().create(body={'properties': {'title': 'Uploaded CSV Data'}}).execute()
            spreadsheet_id = spreadsheet['spreadsheetId']

            # Read the CSV data and write it to the Google Sheets spreadsheet
            with open(filename, 'r') as csv_file:
                data = csv_file.read()
                values = [line.split(',') for line in data.split('\n')]
                request_body = {
                    'values': values
                }
                service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range='A1', valueInputOption='RAW',
                                                       body=request_body).execute()

            # Open the new Google Sheets spreadsheet in a new browser tab
            url = 'https://docs.google.com/spreadsheets'
            webbrowser.open(url)

            return "CSV data uploaded and opened in Google Sheets for further analysis!"

    return upload_form


if __name__ == '_main_':
    credential_path = 'credentials.json'
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path 
    app.run(debug=True)
