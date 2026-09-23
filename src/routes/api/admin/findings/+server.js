import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { statisticsService } from '$lib/server/services/statisticsService.js';

export async function GET({ locals }) {
  if (!locals.user || locals.user.role !== 'admin') {
    return json({ success: false, error: 'Access restricted to administrators' }, { status: 403 });
  }

  try {
    try {
      await connectDB();
    } catch (dbErr) {
      return json({ success: false, hasData: false, error: 'Database unavailable' }, { status: 503 });
    }

    const data = await statisticsService.getFindings();
    return json({
      success: true,
      ...data
    });
  } catch (error) {
    console.error('Admin findings error:', error);
    return json({ success: false, error: 'Failed to retrieve findings' }, { status: 500 });
  }
}
