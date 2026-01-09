import os
from gsheet_helper import GSheetHelper
sheet_id = os.environ.get('GOOGLE_SHEET_ID','11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU')
helper = GSheetHelper(sheet_id)
ins = helper.get_sheet_data('Inspections!A:F')
print('Inspections count:', len(ins))
if ins:
    print('First inspection:', ins[0])
