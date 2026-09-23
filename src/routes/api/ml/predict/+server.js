import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { mlService } from '$lib/server/services/mlService.js';
import { SurveyResponse } from '$lib/server/models/SurveyResponse.js';
import { AssessmentResult } from '$lib/server/models/AssessmentResult.js';

export async function POST({ request, locals }) {
  // 1. Participant authentication check
  if (!locals.user) {
    return json({ success: false, error: 'Authentication required' }, { status: 401 });
  }

  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ success: false, error: 'Invalid JSON payload' }, { status: 400 });
  }

  // Accept { assessment: { ... } } or { answers: { ... } } or top-level assessment dict
  const assessment = body?.assessment || body?.answers || (body && typeof body === 'object' && !body.assessment ? body : null);

  if (!assessment || typeof assessment !== 'object' || Object.keys(assessment).length === 0) {
    return json({ success: false, error: 'Questionnaire responses are required' }, { status: 400 });
  }

  // 2. Execute ML model inference and SHAP explainability
  let mlResult;
  try {
    mlResult = await mlService.predict(assessment);
  } catch (mlErr) {
    console.error('[API ml/predict] ML service error:', mlErr.message);
    return json({
      success: false,
      error: 'Unable to analyze your responses right now. Please try again.'
    }, { status: 503 });
  }

  // 3. Connect to MongoDB and persist assessment and ML prediction
  try {
    await connectDB();

    // Store raw survey responses
    const surveyDoc = await SurveyResponse.create({
      userId: locals.user.id,
      responses: assessment,
      submittedAt: new Date()
    });

    // Store ML prediction result and SHAP feature contributions
    await AssessmentResult.create({
      userId: locals.user.id,
      responseId: surveyDoc._id,
      classification: mlResult.prediction.class,
      probabilities: mlResult.prediction.probabilities,
      topFeatures: mlResult.explanation.top_features || [],
      modelVersion: mlResult.model_version || 'MindSafe Primary Random Forest (Scenario B)',
      disclaimer: mlResult.disclaimer || 'This is an analytical result from the project ML model and is not a medical diagnosis.',
      createdAt: new Date()
    });

    // 4. Return clean structured JSON response
    return json({
      success: true,
      prediction: {
        class: mlResult.prediction.class,
        probabilities: mlResult.prediction.probabilities
      },
      explanation: {
        top_features: mlResult.explanation.top_features || []
      },
      disclaimer: mlResult.disclaimer || 'This is an analytical result from the project ML model and is not a medical diagnosis.'
    });

  } catch (dbErr) {
    console.error('[API ml/predict] Database storage error:', dbErr.message);
    // Even if DB fails, return prediction with a notice if available or safe error
    return json({
      success: false,
      error: 'Unable to save assessment records right now. Please try again.'
    }, { status: 500 });
  }
}
