import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { SurveyResponse } from '$lib/server/models/SurveyResponse.js';
import { AssessmentResult } from '$lib/server/models/AssessmentResult.js';

export async function GET({ locals }) {
  if (!locals.user) {
    return json({ success: false, error: 'Authentication required' }, { status: 401 });
  }

  try {
    try {
      await connectDB();
    } catch (dbErr) {
      return json({ success: false, hasResponse: false, error: 'Database unavailable' }, { status: 503 });
    }

    const latest = await SurveyResponse.findOne({ userId: locals.user.id })
      .sort({ submittedAt: -1 })
      .lean();

    // Query participant's assessment and ML prediction history
    const results = await AssessmentResult.find({ userId: locals.user.id })
      .sort({ createdAt: -1 })
      .limit(10)
      .lean();

    const history = results.map(r => ({
      id: r._id.toString(),
      createdAt: r.createdAt,
      classification: r.classification,
      modelVersion: r.modelVersion || 'MindSafe Primary Random Forest (Scenario B)'
    }));

    if (!latest) {
      return json({
        success: true,
        hasResponse: false,
        response: null,
        history: []
      });
    }

    return json({
      success: true,
      hasResponse: true,
      response: {
        id: latest._id.toString(),
        responses: latest.responses,
        submittedAt: latest.submittedAt
      },
      history
    });
  } catch (error) {
    console.error('Fetch my-response error:', error);
    return json({ success: false, error: 'Failed to retrieve participant survey record' }, { status: 500 });
  }
}
