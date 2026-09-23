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
  indicators: {
    type: Array,
    default: []
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

export const AssessmentResult = mongoose.models.AssessmentResult || mongoose.model('AssessmentResult', assessmentResultSchema);
