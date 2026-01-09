import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getGSheet } from '$lib/gsheet-helper';
import { writeFile, unlink } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { randomBytes } from 'crypto';

export async function POST({ request }: { request: Request }) {
  try {
    const formData = await request.formData();
    const helper = getGSheet();

    // Generate inspection ID
    const inspectionId = randomBytes(4).toString('hex');
    const timestamp = new Date().toISOString().slice(0, 19).replace('T', ' ');

    // Handle file uploads
    const fileLinks: any[] = [];
    const uploadPromises: Promise<void>[] = [];

    for (const [key, value] of formData.entries()) {
      if (value instanceof File && value.size > 0) {
        const uploadPromise = (async () => {
          try {
            // Save file temporarily
            const tempPath = join(tmpdir(), `${Date.now()}_${value.name}`);
            const buffer = await value.arrayBuffer();
            await writeFile(tempPath, Buffer.from(buffer));

            // Upload to Google Drive
            const uploadResult = await helper.uploadFile(tempPath);

            if (uploadResult) {
              fileLinks.push({
                questionId: key.replace('file_', ''),
                fileName: value.name,
                fileUrl: uploadResult.link,
                fileId: uploadResult.fileId
              });
            }

            // Clean up temp file
            await unlink(tempPath);
          } catch (error) {
            console.error(`Error uploading file ${value.name}:`, error);
          }
        })();

        uploadPromises.push(uploadPromise);
      }
    }

    // Wait for all uploads to complete
    await Promise.all(uploadPromises);

    // Prepare form data
    const formDataObj: any = {};
    for (const [key, value] of formData.entries()) {
      if (!(value instanceof File)) {
        formDataObj[key] = value;
      }
    }

    // Save files to Inspection_Files sheet
    for (const fileInfo of fileLinks) {
      const fileRow = [
        inspectionId,
        fileInfo.questionId,
        fileInfo.fileName,
        fileInfo.fileUrl
      ];
      await helper.appendRow('Inspection_Files!A:D', fileRow);
    }

    // Get questions for processing answers
    const questions = await helper.getSheetData('Master_Q!A:D');

    // Prepare summary row for Inspections sheet
    const primaryLink = fileLinks.length > 0 ? fileLinks[0].fileUrl : '';

    const row = [
      inspectionId,
      formDataObj.saja_name || '',
      formDataObj.vro_name || '',
      formDataObj.registration_date || '',
      timestamp,
      'Pending',
      primaryLink
    ];

    await helper.appendRow('Inspections!A:G', row);

    // Save answers and remarks
    const questionIds = questions.map(q => q.ID) || ['1', '2'];

    for (const qId of questionIds) {
      const answer = formDataObj[`q_${qId}`] || '';
      const remark = formDataObj[`remark_${qId}`] || '';

      // Save to Inspection_Answers sheet
      const answersRow = [
        inspectionId,
        qId,
        answer,
        remark
      ];
      await helper.appendRow('Inspection_Answers!A:D', answersRow);

      // Save to Compliance sheet if remark exists
      if (remark) {
        const complianceRow = [
          inspectionId,
          remark,
          '',
          '',
          'Pending'
        ];
        await helper.appendRow('Compliance!A:E', complianceRow);
      }
    }

    return json({
      success: true,
      inspectionId,
      message: 'तपासणी यशस्वीरित्या जतन केली आहे!'
    });

  } catch (error) {
    console.error('Error processing inspection:', error);
    return json({
      success: false,
      error: 'त्रुटी: तपासणी जतन करण्यात अयशस्वी.'
    }, { status: 500 });
  }
}