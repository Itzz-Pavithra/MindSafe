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

    // Retrieve latest ML assessment result
    const latestResult = await AssessmentResult.findOne({ userId: locals.user.id })
      .sort({ createdAt: -1 })
      .lean();

    const hasResult = !!latestResult && !!latestResult.classification;

    return json({
      success: true,
      hasAssessment: true,
      submittedAt: latestResponse.submittedAt,
      hasResult,
      result: hasResult ? {
        classification: latestResult.classification,
        probabilities: latestResult.probabilities || null,
        topFeatures: latestResult.topFeatures || [],
        modelVersion: latestResult.modelVersion || 'MindSafe Primary Random Forest (Scenario B)',
        disclaimer: latestResult.disclaimer || 'This is an analytical result from the project ML model and is not a medical diagnosis.',
        createdAt: latestResult.createdAt
      } : null,
      mlStatus: {
        connected: hasResult,
        message: hasResult ? 'Primary ML model inference active.' : 'Assessment recorded. Prediction pending execution.'
      }
    });
  } catch (error) {
    console.error('Fetch my-result error:', error);
    return json({ success: false, error: 'Failed to retrieve assessment results' }, { status: 500 });
  }
}
