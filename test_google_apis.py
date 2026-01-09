#!/usr/bin/env python3
"""
Test script to verify Google APIs setup for the VRO Daptar application.
This script checks:
1. Credentials file validity
2. Google Sheets API access
3. Google Drive API access
4. Service account permissions
"""

import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def test_credentials():
    """Test if credentials file exists and is valid."""
    print("=== Testing Credentials ===")

    credentials_path = 'credentials.json'
    if not os.path.exists(credentials_path):
        print("credentials.json not found!")
        return False

    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)

        print("credentials.json found and valid JSON")

        # Check required fields
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in creds_data:
                print(f"Missing required field: {field}")
                return False

        print(f"Service Account: {creds_data['client_email']}")
        print(f"Project ID: {creds_data['project_id']}")

        return creds_data

    except json.JSONDecodeError as e:
        print(f"Invalid JSON in credentials.json: {e}")
        return False
    except Exception as e:
        print(f"Error reading credentials.json: {e}")
        return False

def test_sheets_api(creds_data):
    """Test Google Sheets API access."""
    print("\n=== Testing Google Sheets API ===")

    try:
        # Create credentials object
        creds = service_account.Credentials.from_service_account_info(creds_data)

        # Build service
        service = build('sheets', 'v4', credentials=creds)
        print("Google Sheets API service created")

        # Test with the spreadsheet ID from app.py
        spreadsheet_id = '11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU'

        # Try to get spreadsheet metadata
        sheet = service.spreadsheets()
        result = sheet.get(spreadsheetId=spreadsheet_id).execute()

        print(f"Successfully accessed spreadsheet: {result.get('properties', {}).get('title', 'Unknown')}")
        print(f"   Spreadsheet URL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

        return True

    except HttpError as e:
        if e.resp.status == 403:
            print("Access denied to Google Sheets API")
            print("   Possible causes:")
            print("   - Google Sheets API not enabled in Google Cloud Console")
            print("   - Service account not authorized for the spreadsheet")
            print("   - Wrong spreadsheet ID")
        elif e.resp.status == 404:
            print("Spreadsheet not found")
            print("   Check if the spreadsheet ID is correct")
        else:
            print(f"Google Sheets API error: {e}")
        return False
    except Exception as e:
        print(f"Error testing Sheets API: {e}")
        return False

def test_drive_api(creds_data):
    """Test Google Drive API access."""
    print("\n=== Testing Google Drive API ===")

    try:
        # Create credentials with Drive scope
        drive_scopes = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_info(creds_data, scopes=drive_scopes)

        # Build service
        service = build('drive', 'v3', credentials=creds)
        print("Google Drive API service created")

        # Try to list files (should work if API is enabled)
        results = service.files().list(pageSize=1, fields="files(id, name)").execute()
        files = results.get('files', [])

        print("Google Drive API access successful")
        print(f"   Found {len(files)} files in Drive (showing first 1)")

        if files:
            for file in files:
                print(f"   - {file['name']} (ID: {file['id']})")

        # Try to upload a test file
        print("\n--- Testing File Upload ---")
        from googleapiclient.http import MediaFileUpload
        import tempfile

        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test file for API verification")
            test_file_path = f.name

        try:
            # Upload test file
            file_metadata = {'name': 'test_api_verification.txt'}
            media = MediaFileUpload(test_file_path, mimetype='text/plain')
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

            file_id = file.get('id')
            print(f"Test file uploaded successfully: {file_id}")

            # Clean up test file
            service.files().delete(fileId=file_id).execute()
            print("Test file cleaned up")

        except HttpError as e:
            if e.resp.status == 403:
                print("Drive API access denied")
                print("   Possible causes:")
                print("   - Google Drive API not enabled in Google Cloud Console")
                print("   - Insufficient Drive permissions for service account")
            else:
                print(f"Drive upload error: {e}")
        finally:
            # Clean up local file
            try:
                os.unlink(test_file_path)
            except:
                pass

        return True

    except HttpError as e:
        if e.resp.status == 403:
            print("Access denied to Google Drive API")
            print("   This usually means:")
            print("   1. Google Drive API is not enabled in Google Cloud Console")
            print("   2. Service account lacks Drive permissions")
        else:
            print(f"Google Drive API error: {e}")
        return False
    except Exception as e:
        print(f"Error testing Drive API: {e}")
        return False

def main():
    """Main test function."""
    print("Testing Google APIs setup for VRO Daptar application\n")

    # Test credentials
    creds_data = test_credentials()
    if not creds_data:
        print("\nCredentials test failed. Please fix credentials.json")
        return

    # Test Sheets API
    sheets_ok = test_sheets_api(creds_data)

    # Test Drive API
    drive_ok = test_drive_api(creds_data)

    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)

    if sheets_ok and drive_ok:
        print("All tests passed! Google APIs are properly configured.")
    else:
        print("Some tests failed. Please check the issues above.")

    print(f"Google Sheets API: {'PASS' if sheets_ok else 'FAIL'}")
    print(f"Google Drive API: {'PASS' if drive_ok else 'FAIL'}")

    if not sheets_ok or not drive_ok:
        print("\nFIXING INSTRUCTIONS:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Select project: sdmoffice")
        print("3. Enable APIs:")
        print("   - Google Sheets API")
        print("   - Google Drive API")
        print("4. Verify service account permissions")
        print("5. Share spreadsheet with service account if needed")

if __name__ == '__main__':
    main()