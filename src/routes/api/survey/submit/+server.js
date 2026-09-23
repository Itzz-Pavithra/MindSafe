import { json } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { SurveyResponse } from '$lib/server/models/SurveyResponse.js';

export async function POST({ request, locals }) {
  if (!locals.user) {
    return json({ success: false, error: 'Authentication required' }, { status: 401 });
  }

  try {
    const answers = await request.json();

    if (!answers || Object.keys(answers).length === 0) {
      return json({ success: false, error: 'No survey answers provided' }, { status: 400 });
    }

    try {
      await connectDB();
    } catch (dbErr) {
      return json({ 
        success: false, 
        error: 'Database connection error. Please ensure MongoDB is operational.' 
      }, { status: 503 });
    }

    // Persist real participant response to MongoDB
    const surveyDoc = await SurveyResponse.create({
      userId: locals.user.id,
      responses: answers,
      submittedAt: new Date()
    });

    return json({
      success: true,
      message: 'Survey response recorded successfully',
      responseId: surveyDoc._id.toString()
    });
  } catch (error) {
    console.error('Survey submit error:', error);
    return json({ success: false, error: 'Failed to record survey response' }, { status: 500 });
  }
}
