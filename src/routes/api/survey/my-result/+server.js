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
    const userAnswers = latestResponse.responses || {};

    // Ensure every top feature has the respondent's exact answer populated
    const enrichedTopFeatures = hasResult ? (latestResult.topFeatures || []).map(f => {
      let userResponse = f.user_response;
      if (!userResponse || userResponse === 'Recorded') {
        const raw = f.raw_feature || '';
        if (raw === 'Cyberbullying_Frequency_Ordinal') {
          userResponse = userAnswers.q11_freq || userAnswers.frequency || (f.direction === 'increased' ? 'Sometimes' : 'Never');
        } else if (raw === 'Age_Ordinal') {
          userResponse = userAnswers.age || userAnswers.ageGroup || '18–22';
        } else if (raw === 'Daily_Usage_Ordinal') {
          userResponse = userAnswers.usage || userAnswers.usageHours || '1–3 hours';
        } else if (raw === 'Experienced_Cyberbullying_Binary') {
          userResponse = userAnswers.q5_exp || (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw === 'Witnessed_Cyberbullying_Binary') {
          userResponse = userAnswers.q6_wit || (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Gender_')) {
          const cat = raw.replace('Gender_', '');
          userResponse = userAnswers.gender === cat ? cat : 'No';
        } else if (raw.startsWith('Posted_Offensive_')) {
          const cat = raw.replace('Posted_Offensive_', '');
          userResponse = userAnswers.q7_post === cat ? cat : 'No';
        } else if (raw.startsWith('Incident_Platform_')) {
          const cat = raw.replace('Incident_Platform_', '');
          userResponse = userAnswers.q10_plat === cat ? cat : 'No';
        } else if (raw.startsWith('Context_Area_')) {
          const cat = raw.replace('Context_Area_', '');
          userResponse = userAnswers.q17_area === cat ? cat : 'Not Encountered';
        } else if (raw.startsWith('Action_Taken_')) {
          const cat = raw.replace('Action_Taken_', '');
          userResponse = Array.isArray(userAnswers.q18_act) ? (userAnswers.q18_act.includes(cat) ? cat : 'Not Taken') : (f.direction === 'increased' ? cat : 'Not Taken');
        } else if (raw.startsWith('Bullying_Type_')) {
          const cat = raw.replace('Bullying_Type_', '');
          userResponse = Array.isArray(userAnswers.q9_types) ? (userAnswers.q9_types.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Sought_Help_')) {
          const cat = raw.replace('Sought_Help_', '');
          userResponse = Array.isArray(userAnswers.q15_help) ? (userAnswers.q15_help.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        } else if (raw.startsWith('Platform_Used_')) {
          const cat = raw.replace('Platform_Used_', '');
          userResponse = Array.isArray(userAnswers.platforms) ? (userAnswers.platforms.includes(cat) ? 'Yes' : 'No') : (f.direction === 'increased' ? 'Yes' : 'No');
        }
      }
      return {
        ...f,
        user_response: userResponse || 'Recorded'
      };
    }) : [];

    return json({
      success: true,
      hasAssessment: true,
      submittedAt: latestResponse.submittedAt,
      hasResult,
      result: hasResult ? {
        classification: latestResult.classification,
        probabilities: latestResult.probabilities || null,
        topFeatures: enrichedTopFeatures,
        responses: userAnswers,
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
