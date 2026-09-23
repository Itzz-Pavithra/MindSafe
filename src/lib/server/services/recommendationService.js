/**
 * MindSafe Recommendation Service Architecture
 * Informational, supportive, non-diagnostic guidance mapped to mental health impact levels.
 */

export const recommendationService = {
  getRecommendations(classification) {
    const baseRecommendations = [
      {
        title: 'Maintain Healthy Screen Boundaries',
        description: 'Schedule regular offline breaks from high-engagement social platforms to prevent digital fatigue and emotional depletion.'
      },
      {
        title: 'Exercise Digital Evidence Hygiene',
        description: 'Preserve unedited screenshots, timestamps, account usernames, and permalinks before blocking abusive users.'
      },
      {
        title: 'Official Legal & Support Channels',
        description: 'In India, report serious cyber offenses through the National Cyber Crime Portal (cybercrime.gov.in) or dial national helpline 1930.'
      }
    ];

    const specificRecommendations = {
      'Not at all': [
        {
          title: 'Maintain Proactive Digital Hygiene',
          description: 'Continue utilizing privacy configurations, two-factor authentication, and selective direct messaging controls.'
        },
        {
          title: 'Support Peer Awareness',
          description: 'Share knowledge about constructive online dialogue and reporting procedures with fellow students and peers.'
        }
      ],
      'Slightly': [
        {
          title: 'Curate Your Online Feed',
          description: 'Unfollow, mute, or restrict hostile accounts. Filter offensive words in platform comment settings.'
        },
        {
          title: 'Engage in Mindful Disconnection',
          description: 'Dedicate at least 30 minutes before sleep away from social media notifications.'
        }
      ],
      'Moderately': [
        {
          title: 'Seek Supportive Conversation',
          description: 'Discuss digital stressors with trusted mentors, friends, family members, or student wellness advisors.'
        },
        {
          title: 'Enforce Strict Privacy Controls',
          description: 'Switch profiles to private mode and restrict unsolicited messages and tags to verified connections only.'
        },
        {
          title: 'Utilize Platform Moderation Tools',
          description: 'Do not hesitate to report targeted harassment directly via platform tools and block offending accounts promptly.'
        }
      ],
      'Severely': [
        {
          title: 'Professional Counseling Support',
          description: 'Consider connecting with professional campus counselors or certified mental health professionals for personalized support.'
        },
        {
          title: 'Take a Structured Digital Detox',
          description: 'Temporarily pause active accounts or delete apps from your mobile device to eliminate continuous stress triggers.'
        },
        {
          title: 'Document & Escalate Harassment',
          description: 'If you encounter threats, extortion, or systematic defamation, document all evidence and contact official authorities (1930 / cybercrime.gov.in).'
        }
      ]
    };

    const targetList = specificRecommendations[classification] || specificRecommendations['Not at all'];

    return {
      classification: classification || 'Not connected',
      recommendations: [...targetList, ...baseRecommendations],
      disclaimer: 'This is an analytical result from the project model and is not a medical diagnosis.'
    };
  }
};
