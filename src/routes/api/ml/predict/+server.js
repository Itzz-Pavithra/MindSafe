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

    // Ensure every top feature has user_response populated from the survey answers
    const enrichedTopFeatures = (mlResult.explanation.top_features || []).map(f => {
      let userResponse = f.user_response;
      if (!userResponse || userResponse === 'Recorded') {
        const raw = f.raw_feature || '';
        if (raw === 'Cyberbullying_Frequency_Ordinal') {
          userResponse = assessment.q11_freq || assessment.frequency || (f.direction === 'increased' ? 'Sometimes' : 'Never');
        } else if (raw === 'Age_Ordinal') {
          userResponse = assessment.age || assessment.ageGroup || '18–22';
        } else if (raw === 'Daily_Usage_Ordinal') {
          userResponse = assessment.usage || assessment.usageHours || '1–3 hours';
        } else if (raw === 'Experienced_Cyberbullying_Binary') {
          userResponse = assessment.q5_exp || (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw === 'Witnessed_Cyberbullying_Binary') {
          userResponse = assessment.q6_wit || (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Gender_')) {
          const cat = raw.replace('Gender_', '');
          userResponse = assessment.gender === cat ? cat : 'No';
        } else if (raw.startsWith('Posted_Offensive_')) {
          const cat = raw.replace('Posted_Offensive_', '');
          userResponse = assessment.q7_post === cat ? cat : 'No';
        } else if (raw.startsWith('Incident_Platform_')) {
          const cat = raw.replace('Incident_Platform_', '');
          userResponse = assessment.q10_plat === cat ? cat : 'No';
        } else if (raw.startsWith('Context_Area_')) {
          const cat = raw.replace('Context_Area_', '');
          userResponse = assessment.q17_area === cat ? cat : 'Not Encountered';
        } else if (raw.startsWith('Action_Taken_')) {
          const cat = raw.replace('Action_Taken_', '');
          userResponse = Array.isArray(assessment.q18_act) ? (assessment.q18_act.includes(cat) ? cat : 'Not Taken') : (f.direction === 'increased' ? cat : 'Not Taken');
        } else if (raw.startsWith('Bullying_Type_')) {
          const cat = raw.replace('Bullying_Type_', '');
          userResponse = Array.isArray(assessment.q9_types) ? (assessment.q9_types.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Sought_Help_')) {
          const cat = raw.replace('Sought_Help_', '');
          userResponse = Array.isArray(assessment.q15_help) ? (assessment.q15_help.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Platform_Used_')) {
          const cat = raw.replace('Platform_Used_', '');
          userResponse = Array.isArray(assessment.platforms) ? (assessment.platforms.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        }
      }
      return {
        ...f,
        user_response: userResponse || 'Recorded'
      };
    });

    // Store ML prediction result and SHAP feature contributions
    await AssessmentResult.create({
      userId: locals.user.id,
      responseId: surveyDoc._id,
      classification: mlResult.prediction.class,
      probabilities: mlResult.prediction.probabilities,
      topFeatures: enrichedTopFeatures,
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
        top_features: enrichedTopFeatures
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
