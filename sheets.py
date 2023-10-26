import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .types import Spreadsheet, get_from_sheets_array

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '164gOXHhooDOVOOZDGWjzfWZzqq4bkPgQApTRs8EOixk'
GOOGLE_API_KEY = 'AIzaSyC22y_wJabYLGr1ZX44LF22xLqaCy1ZfOU'
PROGRAM_INFO = 'ProgramInfo!'

DISTANCE_MULTPLIER = 100
SQUARE_FOOTAGE_MULTIPLIER = 25
BEDROOM_MULTIPLIER = 75
BATHROOM_MULTIPLIER = 75
MILES_P_SQFT = 1
MAX_COMP_MILEAGE = 1

# The ID and range of a sample spreadsheet.

def get_credentials():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w', encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds

def load_properties(spreadsheet_id : str, desired_sheet: Spreadsheet):
    credentials = get_credentials()
    try:
        # pylint: disable=no-member
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        cell_to_pick = 'X'        
    
        if desired_sheet == Spreadsheet.ACTIVE:
            cell_to_pick = 'A'
        elif desired_sheet == Spreadsheet.SOLD:
            cell_to_pick = 'B'

        cell_info = service.get(spreadsheetId=spreadsheet_id, range=f"{PROGRAM_INFO}{cell_to_pick}2").execute()
        number_of_properties = cell_info.get('values', [])[0][0]

        raw_property_data = service.get(spreadsheetId=spreadsheet_id ,range=f"{desired_sheet.value}A2:CT{number_of_properties}").execute()
        property_data_rows = raw_property_data.get('values', [])

        properties = []

        for i,property_excel_row in enumerate(property_data_rows):
            print(f"loading property #{i}")
            properties.append(get_from_sheets_array(property_excel_row))

        service.close()

        return properties
    except HttpError as err:
        print(err)

    return []
