import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { getGSheet } from '$lib/gsheet-helper';

export async function GET({ url }: { url: URL }) {
  try {
    const helper = getGSheet();
    const inspections = await helper.getSheetData('Inspections!A:F');

    return json({
      success: true,
      inspections
    });
  } catch (error) {
    console.error('Error fetching inspections:', error);
    return json({
      success: false,
      error: 'Failed to fetch inspections'
    }, { status: 500 });
  }
}