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

    const data = await statisticsService.getStatisticalAnalysis();
    return json({
      success: true,
      ...data
    });
  } catch (error) {
    console.error('Admin statistical analysis error:', error);
    return json({ success: false, error: 'Failed to compute statistical analysis' }, { status: 500 });
  }
}

export async function POST({ request, locals }) {
  if (!locals.user || locals.user.role !== 'admin') {
    return json({ success: false, error: 'Access restricted to administrators' }, { status: 403 });
  }

  try {
    try {
      await connectDB();
    } catch (dbErr) {
      return json({ success: false, hasData: false, error: 'Database unavailable' }, { status: 503 });
    }

    const body = await request.json();
    const { testType, var1, var2 } = body;

    if (!testType || !var1 || !var2) {
      return json({ success: false, error: 'Test type and two variables are required' }, { status: 400 });
    }

    const result = await statisticsService.runCustomAnalysis(testType, var1, var2);
    return json({
      success: true,
      result
    });
  } catch (error) {
    console.error('Admin custom statistical test error:', error);
    return json({ success: false, error: 'Failed to execute statistical test' }, { status: 500 });
  }
}
