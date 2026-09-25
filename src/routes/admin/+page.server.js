import { redirect } from '@sveltejs/kit';
import { connectDB } from '$lib/server/db.js';
import { AssessmentResult } from '$lib/server/models/AssessmentResult.js';
import { SurveyResponse } from '$lib/server/models/SurveyResponse.js';

export async function load({ locals }) {
  // 1. Enforce Administrator Authentication
  if (!locals.user) {
    throw redirect(303, '/login');
  }

  if (locals.user.role !== 'admin') {
    // Normal respondents cannot access admin pages
    throw redirect(303, '/dashboard');
  }

  // 2. Fetch live counts directly from MongoDB
  try {
    await connectDB();

    const [totalSurveys, assessmentDocs] = await Promise.all([
      SurveyResponse.countDocuments(),
      AssessmentResult.find({}, 'classification').lean()
    ]);

    // Total respondents who submitted responses
    const totalRespondents = Math.max(totalSurveys, assessmentDocs.length);

    // Dynamic count for each of the four target prediction classes
    const distribution = {
      'Not at all': 0,
      'Slightly': 0,
      'Moderately': 0,
      'Severely': 0
    };

    for (const doc of assessmentDocs) {
      if (doc.classification && Object.prototype.hasOwnProperty.call(distribution, doc.classification)) {
        distribution[doc.classification]++;
      }
    }

    // Determine which of the four classes currently has the highest number
    let mostCommonClass = 'Not at all';
    let maxCount = -1;
    for (const [cls, count] of Object.entries(distribution)) {
      if (count > maxCount) {
        maxCount = count;
        mostCommonClass = cls;
      }
    }

    if (assessmentDocs.length === 0) {
      mostCommonClass = 'No predictions recorded yet';
    }

    return {
      adminUser: {
        name: locals.user.name || 'Administrator',
        email: locals.user.email
      },
      summary: {
        totalRespondents,
        distribution,
        mostCommonClass,
        totalClassified: assessmentDocs.length
      }
    };
  } catch (err) {
    console.error('[Admin Server Load] Error querying respondent data:', err.message);
    return {
      adminUser: {
        name: locals.user.name || 'Administrator',
        email: locals.user.email
      },
      summary: {
        totalRespondents: 0,
        distribution: {
          'Not at all': 0,
          'Slightly': 0,
          'Moderately': 0,
          'Severely': 0
        },
        mostCommonClass: 'Unavailable',
        totalClassified: 0
      },
      error: 'Database connection unavailable'
    };
  }
}
