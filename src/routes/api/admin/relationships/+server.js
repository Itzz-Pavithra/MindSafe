import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { statisticsService } from '$lib/server/services/statisticsService.js';

export async function GET({ url, locals }) {
  if (!locals.user || locals.user.role !== 'admin') {
    return json({ success: false, error: 'Access restricted to administrators' }, { status: 403 });
  }

  const varX = url.searchParams.get('varX') || 'frequency';
  const varY = url.searchParams.get('varY') || 'mentalHealthImpact';

  try {
    try {
      await connectDB();
    } catch (dbErr) {
      return json({ success: false, hasData: false, error: 'Database unavailable' }, { status: 503 });
    }

    const data = await statisticsService.getRelationships(varX, varY);
    return json({
      success: true,
      ...data
    });
  } catch (error) {
    console.error('Admin relationships analysis error:', error);
    return json({ success: false, error: 'Failed to compute relationship statistics' }, { status: 500 });
  }
}
