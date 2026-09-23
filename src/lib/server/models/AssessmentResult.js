import mongoose from 'mongoose';

const assessmentResultSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
    index: true
  },
  responseId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'SurveyResponse',
    default: null
  },
  classification: {
    type: String,
    enum: ['Not at all', 'Slightly', 'Moderately', 'Severely', null],
    default: null
  },
  probabilities: {
    type: mongoose.Schema.Types.Mixed,
    default: null
  },
  topFeatures: {
    type: Array,
    default: []
  },
  modelVersion: {
    type: String,
    default: 'MindSafe Primary Random Forest (Scenario B)'
  },
  disclaimer: {
    type: String,
    default: 'This is an analytical result from the project ML model and is not a medical diagnosis.'
  },
  indicators: {
    type: Array,
    default: []
  },
  createdAt: {
    type: Date,
    default: Date.now,
    index: true
  }
});

export const AssessmentResult = mongoose.models.AssessmentResult || mongoose.model('AssessmentResult', assessmentResultSchema);
