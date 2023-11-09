import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .types import Spreadsheet, BestComps, FormattedActiveFieldIndices, FormattedSoldFieldIndices,get_active_from_sheets,get_sold_from_sheets

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# SPREADSHEET_ID = '164gOXHhooDOVOOZDGWjzfWZzqq4bkPgQApTRs8EOixk'

SOLD_SHEET_ID = '1S8HXWayHcro3O_xMCjaFuMiVWjAgdjyhObqCVtKXJaQ'
ACTIVE_SHEET_ID = '1l_vdszegyTa7FCPqL8WcZ-iV_FzQWFFyE6uggZYV22A'
DASHBOARD_SHEET_ID = '1GxSKElRyVSRlh8rQzthN9KPPNhQM3IGDCXWsya4X6Fw'
MASTER_SOLDS_SHEET_ID = '1c-TvmHyjhzTCDT4nj78avuk1pDPbgmyM86ZfpRZlH9U'


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

def load_properties(desired_sheet: Spreadsheet):
    credentials = get_credentials()
    try:
        # pylint: disable=no-member
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        desired_sheet_obj = desired_sheet.value

        cell_info = service.get(spreadsheetId=desired_sheet_obj.Id, range=f"{PROGRAM_INFO}B1").execute()
        number_of_properties = cell_info.get('values', [])[0][0]

        if int(number_of_properties) == 0:
            number_of_properties = 2

        raw_property_data = service.get(spreadsheetId=desired_sheet_obj.Id,range=f"{desired_sheet_obj.info_sheet}{desired_sheet_obj.range}{number_of_properties}").execute()

        property_data_rows = raw_property_data.get('values', [])

        properties = []

        get_from_sheets = lambda prop: prop

        if desired_sheet == Spreadsheet.ACTIVE:
            get_from_sheets = get_active_from_sheets
        elif desired_sheet == Spreadsheet.SOLD or desired_sheet == Spreadsheet.MASTER_SOLDS:
            get_from_sheets = get_sold_from_sheets

        for i, property_excel_row in enumerate(property_data_rows):
            print(f"loading property #{i} from {desired_sheet_obj.name}")
            properties.append(get_from_sheets(property_excel_row))

        service.close()
        return properties
    except HttpError as err:
        print(err)

    return []

def write_result_array(comp : list[BestComps]):

    credentials = get_credentials()
    try:
        # pylint: disable=no-member
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        values = [result.get_result_array() for result in comp]

        body = {
            'values' : values
        }

        result = service.append(
                spreadsheetId=Spreadsheet.OUTPUT.value.Id, range=f"{Spreadsheet.OUTPUT.value.name[:-1]}",
                    valueInputOption="USER_ENTERED", body=body).execute()

        service.close()
        return result

    except HttpError as err:
        print(err)

# were assuming properties have been loaded
def clean_solds():
    credentials = get_credentials()
    try:
        # pylint: disable=no-member
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()

        service.clear(spreadsheetId=Spreadsheet.SOLD.value.Id, range=f"{Spreadsheet.SOLD.value.name}A:XFD").execute()

    except HttpError as err:
        print(err)



def append_solds_to_master():
    credentials = get_credentials()
    try:
        # pylint: disable=no-member
        service = build('sheets', 'v4', credentials=credentials).spreadsheets().values()
        cell_info = service.get(spreadsheetId=Spreadsheet.SOLD.value.Id, range=f"{PROGRAM_INFO}B1").execute()
        number_of_properties = cell_info.get('values', [])[0][0]
        
        if int(number_of_properties) == 0:
            number_of_properties = 2

        raw_property_data = service.get(spreadsheetId=Spreadsheet.SOLD.value.Id,range=f"{Spreadsheet.SOLD.value.info_sheet}{Spreadsheet.SOLD.value.range}{number_of_properties}").execute()
        property_data_rows = raw_property_data.get('values', [])

        body = {
            'values' : property_data_rows
        }

        service.append(
                spreadsheetId=Spreadsheet.MASTER_SOLDS.value.Id, range=f"{Spreadsheet.MASTER_SOLDS.value.name[:-1]}",
                    valueInputOption="USER_ENTERED", body=body
        ).execute()

        service.close()
    except HttpError as err:
        print(err)


def get_all_solds():
    properties = []
    properties.extend(load_properties(Spreadsheet.SOLD))
    properties.extend(load_properties(Spreadsheet.MASTER_SOLDS))
    return properties
