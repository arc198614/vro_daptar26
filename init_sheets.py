import os
from gsheet_helper import GSheetHelper
from googleapiclient.errors import HttpError

def initialize_sheets():
    # Configuration
    SHEET_ID = '11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU'
    
    try:
        helper = GSheetHelper(SHEET_ID)
        print("Connected to Google Sheets successfully.")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    sheets_to_init = {
        "Master_Q": ["ID", "विभाग", "प्रश्न", "अपलोड आवश्यक"],
        "Inspections": ["ID", "सजा", "नाव", "तारीख", "एकूण ग्रेड", "फाईल लिंक"],
        "Compliance": ["Log_ID", "अधिकारी शेरा", "वरिष्ठ मत", "स्पष्टीकरण", "स्थिती"],
        "Inspection_Answers": ["Inspection_ID", "Question_ID", "Answer", "Remark"]
    }

    for sheet_name, headers in sheets_to_init.items():
        try:
            # Check if sheet exists by trying to get its data
            result = helper.service.spreadsheets().get(spreadsheetId=SHEET_ID).execute()
            sheet_titles = [s['properties']['title'] for s in result.get('sheets', [])]
            
            if sheet_name not in sheet_titles:
                print(f"Creating sheet: {sheet_name}")
                body = {
                    'requests': [{
                        'addSheet': {
                            'properties': {'title': sheet_name}
                        }
                    }]
                }
                helper.service.spreadsheets().batchUpdate(spreadsheetId=SHEET_ID, body=body).execute()

            # Check if headers already exist
            existing = helper.get_sheet_data(f"{sheet_name}!A1:E1")
            if not existing:
                print(f"Adding headers to {sheet_name}...")
                helper.append_row(f"{sheet_name}!A1", headers)
                
                # Add sample data for Master_Q if it's new
                if sheet_name == "Master_Q":
                    sample_q = [
                        ["1", "सामान्य माहिती", "गाव नमुना ७/१२ अद्ययावत आहे का?", "हो"],
                        ["2", "दप्तर तपासणी", "नोंदवही क्र. ६ पूर्ण आहे का?", "नाही"]
                    ]
                    for q in sample_q:
                        helper.append_row(f"{sheet_name}!A2", q)
                
            else:
                print(f"Headers already exist in {sheet_name}.")

        except HttpError as err:
            print(f"Error initializing {sheet_name}: {err}")

    print("\nInitialization complete!")

if __name__ == "__main__":
    initialize_sheets()
