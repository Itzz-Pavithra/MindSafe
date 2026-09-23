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
      return json({ success: false, hasResult: false, error: 'Database unavailable' }, { status: 503 });
    }

    const latestResponse = await SurveyResponse.findOne({ userId: locals.user.id })
      .sort({ submittedAt: -1 })
      .lean();

    if (!latestResponse) {
      return json({
        success: true,
        hasAssessment: false,
        hasResult: false,
        message: 'No completed assessment found. Please complete the assessment first.'
      });
    }

    // Check if an assessmentResult exists (from future ML model)
    const latestResult = await AssessmentResult.findOne({ userId: locals.user.id })
      .sort({ createdAt: -1 })
      .lean();

    return json({
      success: true,
      hasAssessment: true,
      submittedAt: latestResponse.submittedAt,
      // In this phase: No fake predictions are returned.
      hasResult: !!latestResult && !!latestResult.classification,
      result: latestResult ? {
        classification: latestResult.classification,
        indicators: latestResult.indicators,
        createdAt: latestResult.createdAt
      } : null,
      mlStatus: {
        connected: false,
        message: 'Prediction will be available after the ML model is connected.'
      }
    });
  } catch (error) {
    console.error('Fetch my-result error:', error);
    return json({ success: false, error: 'Failed to retrieve assessment results' }, { status: 500 });
  }
}
