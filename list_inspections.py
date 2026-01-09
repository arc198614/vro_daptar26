import os, json
from gsheet_helper import GSheetHelper
sheet_id = os.environ.get('GOOGLE_SHEET_ID','11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU')
helper = GSheetHelper(sheet_id)
ins = helper.get_sheet_data('Inspections!A:F')
with open('inspections.json','w',encoding='utf-8') as f:
    json.dump(ins, f, ensure_ascii=False, indent=2)
print('Wrote', len(ins), 'inspections to inspections.json')
