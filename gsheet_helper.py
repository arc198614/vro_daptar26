import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GSheetHelper:
    def __init__(self, spreadsheet_id, credentials_path='credentials.json'):
        self.spreadsheet_id = spreadsheet_id
        self.credentials_path = credentials_path
        self.creds = self._authenticate()
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)

    def _authenticate(self):
        # Option 1: Try Environment Variable (Best for Vercel/Render)
        json_creds = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if json_creds:
            import json
            import base64
            import binascii
            
            try:
                # Try to decode base64 first
                try:
                    decoded_bytes = base64.b64decode(json_creds)
                    decoded_str = decoded_bytes.decode('utf-8')
                    # If it looks like JSON, use it
                    if decoded_str.strip().startswith('{'):
                         json_creds = decoded_str
                except binascii.Error:
                    pass # Not base64, assume raw JSON string

                info = json.loads(json_creds)
                
                # Fix: Handle private_key newlines which can be escaped on Vercel/Env
                if 'private_key' in info:
                    info['private_key'] = info['private_key'].replace('\\n', '\n')

                # Add Drive scope for file uploads
                DRIVE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
                return service_account.Credentials.from_service_account_info(info, scopes=DRIVE_SCOPES)
            except Exception as e:
                print(f"Error loading creds from env: {e}")

        # Option 2: Fallback to local file
        if not os.path.exists(self.credentials_path):
            # Generate a helpful error if neither is found
            raise FileNotFoundError(f"Credentials not found. Set GOOGLE_CREDENTIALS_JSON env var or place {self.credentials_path}")
        
        # Add Drive scope for file uploads
        DRIVE_SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=DRIVE_SCOPES)
        return creds

    def upload_file(self, file_path, folder_id=None):
        """Uploads a file to Google Drive and returns the file ID and webViewLink."""
        try:
            from googleapiclient.http import MediaFileUpload

            # Use the specified folder ID if provided, otherwise upload to root
            upload_folder_id = folder_id or os.environ.get('GOOGLE_DRIVE_FOLDER_ID')

            file_metadata = {'name': os.path.basename(file_path)}
            if upload_folder_id:
                file_metadata['parents'] = [upload_folder_id]

            media = MediaFileUpload(file_path, resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            # Make file readable by anyone with the link
            file_id = file.get('id')
            permission_set = False

            try:
                # First, try to set permissions
                self.drive_service.permissions().create(
                    fileId=file_id,
                    body={
                        'type': 'anyone',
                        'role': 'reader',
                        'allowFileDiscovery': False
                    }
                ).execute()
                permission_set = True
                print(f"Successfully set permissions for file {file_id}")
            except Exception as perm_error:
                print(f"Warning: Could not set file permissions: {perm_error}")

            # Generate the most reliable link format
            if permission_set:
                # Use the standard sharing link format
                final_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
            else:
                # Fallback to alternative formats if permissions failed
                final_link = f"https://drive.google.com/uc?id={file_id}"

            print(f"Generated link for file {file_id}: {final_link}")

            return file_id, final_link
        except Exception as e:
            print(f"Error uploading to Drive: {e}")
            return None, None

    def get_sheet_data(self, range_name):
        """Reads data from the specified range and returns a list of dicts."""
        try:
            sheet = self.service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            if not values:
                return []
            
            headers = values[0]
            rows = []
            for row in values[1:]:
                # Ensure row has same length as headers
                row_dict = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                rows.append(row_dict)
            return rows
        except HttpError as err:
            print(f"An error occurred: {err}")
            return []

    def append_row(self, range_name, values):
        """Appends a row of data to the specified range."""
        try:
            body = {'values': [values]}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return result
        except HttpError as err:
            print(f"An error occurred: {err}")
            return None

    def update_compliance_row(self, log_id, remark, updates):
        """Updates a row in the Compliance sheet matching log_id and remark."""
        try:
            # 1. Get all data to find the row index
            values = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id, range='Compliance!A:E').execute().get('values', [])
            
            if not values:
                return False
            
            row_idx = -1
            for i, row in enumerate(values):
                if i == 0: continue # Skip header
                # Match Log_ID (Col A) and Remark (Col B)
                if len(row) >= 2 and row[0] == log_id and row[1] == remark:
                    row_idx = i + 1 # Sheets is 1-indexed
                    break
            
            if row_idx == -1:
                print(f"Could not find row for ID {log_id}")
                return False

            # 2. Update the row. updates should be a list starting from Column C ( वरिष्ठ मत)
            # Range: C{row_idx}:E{row_idx}
            range_name = f'Compliance!C{row_idx}:E{row_idx}'
            body = {'values': [updates]}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"Error updating compliance: {e}")
            return False
