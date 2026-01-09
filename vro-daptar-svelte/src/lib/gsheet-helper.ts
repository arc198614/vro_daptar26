import { google } from 'googleapis';
import { GoogleAuth } from 'google-auth-library';

export class GSheetHelper {
  private spreadsheetId: string;
  private auth: GoogleAuth;
  private sheets: any;
  private drive: any;

  constructor(spreadsheetId: string, credentialsPath: string = 'credentials.json') {
    this.spreadsheetId = spreadsheetId;

    // Initialize auth
    this.auth = new GoogleAuth({
      keyFilename: credentialsPath,
      scopes: [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
      ],
    });

    // Initialize clients
    this.sheets = google.sheets({ version: 'v4', auth: this.auth });
    this.drive = google.drive({ version: 'v3', auth: this.auth });
  }

  async getSheetData(range: string): Promise<any[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range,
      });

      const values = response.data.values;
      if (!values || values.length === 0) {
        return [];
      }

      const headers = values[0];
      const rows = values.slice(1).map((row: any[]) => {
        const rowDict: any = {};
        headers.forEach((header, i) => {
          rowDict[header] = i < row.length ? row[i] : '';
        });
        return rowDict;
      });

      return rows;
    } catch (error) {
      console.error('Error getting sheet data:', error);
      return [];
    }
  }

  async appendRow(range: string, values: any[]): Promise<any> {
    try {
      const resource = {
        values: [values],
      };

      const response = await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range,
        valueInputOption: 'RAW',
        resource,
      });

      return response.data;
    } catch (error) {
      console.error('Error appending row:', error);
      return null;
    }
  }

  async updateComplianceRow(logId: string, remark: string, updates: any[]): Promise<boolean> {
    try {
      // Get all data to find the row index
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Compliance!A:E',
      });

      const values = response.data.values;
      if (!values) return false;

      let rowIdx = -1;
      for (let i = 1; i < values.length; i++) { // Skip header
        const row = values[i];
        if (row.length >= 2 && row[0] === logId && row[1] === remark) {
          rowIdx = i + 1; // Sheets is 1-indexed
          break;
        }
      }

      if (rowIdx === -1) {
        console.error(`Could not find row for ID ${logId}`);
        return false;
      }

      // Update the row - updates should be for columns C, D, E
      const range = `Compliance!C${rowIdx}:E${rowIdx}`;
      const resource = {
        values: [updates],
      };

      await this.sheets.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range,
        valueInputOption: 'RAW',
        resource,
      });

      return true;
    } catch (error) {
      console.error('Error updating compliance:', error);
      return false;
    }
  }

  async uploadFile(filePath: string, folderId?: string): Promise<{ fileId: string; link: string } | null> {
    try {
      const fs = await import('fs');

      // Use specified folder ID or environment variable, otherwise upload to root
      const uploadFolderId = folderId || process.env.GOOGLE_DRIVE_FOLDER_ID;

      const fileMetadata: any = {
        name: require('path').basename(filePath),
      };

      if (uploadFolderId) {
        fileMetadata.parents = [uploadFolderId];
      }

      const media = {
        mimeType: 'application/octet-stream',
        body: fs.createReadStream(filePath),
      };

      const response = await this.drive.files.create({
        resource: fileMetadata,
        media,
        fields: 'id,webViewLink',
      });

      const fileId = response.data.id!;
      console.log(`File uploaded successfully: ${fileId}`);

      // Set permissions to allow anyone with link to view
      try {
        await this.drive.permissions.create({
          fileId,
          resource: {
            type: 'anyone',
            role: 'reader',
            allowFileDiscovery: false,
          },
        });
        console.log(`Permissions set for file ${fileId}`);
      } catch (permError) {
        console.warn('Could not set file permissions:', permError);
      }

      // Generate sharing link
      const link = `https://drive.google.com/file/d/${fileId}/view?usp=sharing`;

      return { fileId, link };
    } catch (error) {
      console.error('Error uploading file:', error);
      return null;
    }
  }
}

// Singleton instance
let gsheetInstance: GSheetHelper | null = null;

export function getGSheet(): GSheetHelper {
  if (!gsheetInstance) {
    const spreadsheetId = process.env.GOOGLE_SHEET_ID || '11NCa_DbttL6x4Fq_oHRFooweNfNPNPq6nIlPl7OUQVU';
    gsheetInstance = new GSheetHelper(spreadsheetId);
  }
  return gsheetInstance;
}