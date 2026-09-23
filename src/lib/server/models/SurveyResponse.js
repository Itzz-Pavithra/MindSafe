import mongoose from 'mongoose';

const surveyResponseSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  responses: {
    type: mongoose.Schema.Types.Mixed,
    required: true
  },
  submittedAt: {
    type: Date,
    default: Date.now,
    index: true
  }
});

export const SurveyResponse = mongoose.models.SurveyResponse || mongoose.model('SurveyResponse', surveyResponseSchema);
