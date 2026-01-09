import os, json, sys
from gsheet_helper import GSheetHelper

sheet_id = os.environ.get('GOOGLE_SHEET_ID','11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU')
helper = GSheetHelper(sheet_id)
ins = helper.get_sheet_data('Inspections!A:F')
print('Inspections count:', len(ins))
if ins:
    # Ensure the console can handle Marathi characters on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass  # fallback for older Python versions
    print(json.dumps(ins[0], ensure_ascii=False, indent=2))
