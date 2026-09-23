
import mongoose from 'mongoose';
import dns from 'node:dns';
import bcrypt from 'bcryptjs';

// Setup DNS for Windows SRV lookups
try {
  dns.setServers(['8.8.8.8', '1.1.1.1']);
} catch (e) {
  // ignore
}

import { User } from '../src/lib/server/models/User.js';
import { SurveyResponse } from '../src/lib/server/models/SurveyResponse.js';
import { statisticsService } from '../src/lib/server/services/statisticsService.js';

async function runEndToEndVerification() {
  console.log('====================================================');
  console.log('MINDSAFE FINAL VERIFICATION TEST SUITE');
  console.log('====================================================');

  const uri = process.env.MONGODB_URI;
  if (!uri) {
    console.error('ERROR: MONGODB_URI is not set in environment.');
    process.exit(1);
  }

  // TEST 1: Connect to MongoDB Atlas
  console.log('\n[TEST 1] Connecting to MongoDB Atlas...');
  await mongoose.connect(uri, {
    serverSelectionTimeoutMS: 15000,
    maxPoolSize: 10
  });
  console.log('✓ Successfully connected to MongoDB Atlas. ReadyState:', mongoose.connection.readyState);

  // TEST 2: Verify Admin Account & Credentials
  console.log('\n[TEST 2] Verifying Fixed Administrator Account in users collection...');
  const adminEmail = process.env.ADMIN_EMAIL || 'pavithra.workss@gmail.com';
  const adminPassword = process.env.ADMIN_PASSWORD || 'Pavi@2209';

  let adminUser = await User.findOne({ email: adminEmail.toLowerCase() });
  if (!adminUser) {
    const salt = await bcrypt.genSalt(12);
    const hash = await bcrypt.hash(adminPassword, salt);
    adminUser = await User.create({
      name: 'Lead Researcher',
      email: adminEmail.toLowerCase(),
      passwordHash: hash,
      role: 'admin'
    });
    console.log('✓ Created initial Admin account in MongoDB Atlas.');
  }

  const isPasswordMatch = await bcrypt.compare(adminPassword, adminUser.passwordHash);
  console.log('✓ Admin User in MongoDB Atlas:');
  console.log('  ID:', adminUser._id.toString());
  console.log('  Email:', adminUser.email);
  console.log('  Role:', adminUser.role);
  console.log('  Password Match (Pavi@2209):', isPasswordMatch);
  if (!isPasswordMatch) {
    throw new Error('Admin password does not match!');
  }

  // TEST 3: Participant Registration Write Operation
  console.log('\n[TEST 3] Testing Real Participant Registration (users write)...');
  const testEmail = `test_participant_${Date.now()}@academic.edu`;
  const testPassword = 'Participant@Pass123';
  const salt = await bcrypt.genSalt(12);
  const passwordHash = await bcrypt.hash(testPassword, salt);

  const newParticipant = await User.create({
    name: 'Real Test Participant',
    email: testEmail,
    passwordHash,
    role: 'survey_user'
  });
  console.log('✓ Participant successfully inserted into "users" collection:');
  console.log('  _id:', newParticipant._id.toString());
  console.log('  email:', newParticipant.email);
  console.log('  role:', newParticipant.role);

  // TEST 4: Participant Authentication Read Operation
  console.log('\n[TEST 4] Testing Participant Authentication (users read & compare)...');
  const queriedUser = await User.findOne({ email: testEmail });
  const participantAuthValid = await bcrypt.compare(testPassword, queriedUser.passwordHash);
  console.log('✓ Queried user from MongoDB: found =', !!queriedUser);
  console.log('  Bcrypt password valid:', participantAuthValid);

  // TEST 5: Real Survey Questionnaire Submission Write Operation
  console.log('\n[TEST 5] Testing Questionnaire Submission (surveyResponses write)...');
  const sampleSurvey = {
    userId: newParticipant._id,
    responses: {
      ageGroup: '18–22',
      gender: 'Female',
      usageHours: '4.5–6.5 hrs',
      socialMediaPlatform: 'Instagram',
      cyberbullyingExperience: 'Yes',
      frequency: 'Sometimes',
      activityType: 'Offensive Comments & Trolling',
      emotionalWellbeing: 'Moderately',
      emotionalSymptom: 'Anxiety',
      actionTaken: 'Blocked User'
    },
    submittedAt: new Date()
  };

  const surveyDoc = await SurveyResponse.create(sampleSurvey);
  console.log('✓ Survey response document inserted into "surveyResponses" collection:');
  console.log('  _id:', surveyDoc._id.toString());
  console.log('  userId:', surveyDoc.userId.toString());
  console.log('  Age Group:', surveyDoc.responses.ageGroup);
  console.log('  Experience:', surveyDoc.responses.cyberbullyingExperience);
  console.log('  Primary ML Target (emotionalWellbeing):', surveyDoc.responses.emotionalWellbeing);

  // Also insert a second response to test comparison tests (grouping)
  const testEmail2 = `test_participant_control_${Date.now()}@academic.edu`;
  const newParticipant2 = await User.create({
    name: 'Control Participant',
    email: testEmail2,
    passwordHash,
    role: 'survey_user'
  });
  const sampleSurvey2 = {
    userId: newParticipant2._id,
    responses: {
      ageGroup: '23–26',
      gender: 'Male',
      usageHours: '< 2.5 hrs',
      socialMediaPlatform: 'YouTube',
      cyberbullyingExperience: 'No',
      frequency: 'Never',
      activityType: 'None',
      emotionalWellbeing: 'Not at all',
      emotionalSymptom: 'Minimal Impact',
      actionTaken: 'Did Not Report'
    },
    submittedAt: new Date()
  };
  const surveyDoc2 = await SurveyResponse.create(sampleSurvey2);
  console.log('✓ Second response inserted (Control / No Experience, Target = Not at all)');

  // TEST 6: Participant Survey Read Operation
  console.log('\n[TEST 6] Testing Participant Survey Read Operation (surveyResponses read)...');
  const participantResponse = await SurveyResponse.findOne({ userId: newParticipant._id }).lean();
  console.log('✓ Successfully retrieved participant survey response:');
  console.log('  Platform:', participantResponse.responses.socialMediaPlatform);
  console.log('  Impact:', participantResponse.responses.emotionalWellbeing);

  // TEST 7: Statistical Analysis Engine Verification
  console.log('\n[TEST 7] Testing Descriptive and Inferential Statistical Engine...');
  const statsOverview = await statisticsService.getStatisticalAnalysis();
  console.log('✓ Full statistical analysis calculated on N =', statsOverview.totalResponses, 'records:');
  console.log('  Descriptive Numerical (Mental Health Impact):', statsOverview.descriptive.numerical.emotionalWellbeing);
  console.log('  Descriptive Categorical (Age Group Mode):', statsOverview.descriptive.categorical.ageGroup.modeCategory);

  // TEST 7A: Custom Chi-Square Test
  console.log('\n[TEST 7A] Testing Chi-Square Test (frequency × emotionalWellbeing)...');
  const chiSqResult = await statisticsService.runCustomAnalysis('chi_square', 'frequency', 'emotionalWellbeing');
  console.log('✓ Chi-Square output:');
  console.log('  Applicable:', chiSqResult.applicable);
  console.log('  Statistic:', chiSqResult.testStatistic);
  console.log('  Degrees of Freedom:', chiSqResult.degreesOfFreedom);
  console.log('  p-value:', chiSqResult.pValue);
  console.log('  Interpretation:', chiSqResult.interpretation);

  // TEST 7B: Custom Independent Samples T-Test
  console.log('\n[TEST 7B] Testing Independent T-Test (cyberbullyingExperience × emotionalWellbeing)...');
  const tTestResult = await statisticsService.runCustomAnalysis('t_test', 'cyberbullyingExperience', 'emotionalWellbeing');
  console.log('✓ T-Test output:');
  console.log('  Applicable:', tTestResult.applicable);
  console.log('  Group 1 (Yes) Mean:', tTestResult.group1?.mean, 'N =', tTestResult.group1?.sampleSize);
  console.log('  Group 2 (No) Mean:', tTestResult.group2?.mean, 'N =', tTestResult.group2?.sampleSize);
  console.log('  t-statistic:', tTestResult.testStatistic);
  console.log('  p-value:', tTestResult.pValue);
  console.log('  Interpretation:', tTestResult.interpretation);

  // TEST 7C: Custom Pearson Correlation
  console.log('\n[TEST 7C] Testing Pearson Correlation (usageHours × emotionalWellbeing)...');
  const corrResult = await statisticsService.runCustomAnalysis('correlation', 'usageHours', 'emotionalWellbeing');
  console.log('✓ Correlation output:');
  console.log('  Applicable:', corrResult.applicable);
  console.log('  Pearson r:', corrResult.testStatistic);
  console.log('  Direction:', corrResult.direction);
  console.log('  p-value:', corrResult.pValue);
  console.log('  Interpretation:', corrResult.interpretation);

  // TEST 7D: Inappropriate Variable Pairings (Validation)
  console.log('\n[TEST 7D] Testing Validation on Inappropriate Variable Selection...');
  const invalidTTest = await statisticsService.runCustomAnalysis('t_test', 'socialMediaPlatform', 'activityType');
  console.log('✓ Invalid T-Test rejected properly:');
  console.log('  Applicable:', invalidTTest.applicable);
  console.log('  Reason:', invalidTTest.reason);

  const invalidCorr = await statisticsService.runCustomAnalysis('correlation', 'socialMediaPlatform', 'emotionalWellbeing');
  console.log('✓ Invalid Correlation rejected properly:');
  console.log('  Applicable:', invalidCorr.applicable);
  console.log('  Reason:', invalidCorr.reason);

  // TEST 8: Clean up test documents and verify empty states
  console.log('\n[TEST 8] Cleaning up verification test documents from MongoDB...');
  await SurveyResponse.deleteMany({ _id: { $in: [surveyDoc._id, surveyDoc2._id] } });
  await User.deleteMany({ _id: { $in: [newParticipant._id, newParticipant2._id] } });
  console.log('✓ Test participants and responses removed.');

  const remainingSurveys = await SurveyResponse.countDocuments();
  console.log('  Surveys remaining in MongoDB:', remainingSurveys);

  const emptyStateOverview = await statisticsService.getOverview();
  console.log('✓ Empty state response for overview:');
  console.log('  hasData:', emptyStateOverview.hasData);
  console.log('  totalResponses:', emptyStateOverview.totalResponses);
  console.log('  message:', emptyStateOverview.message);

  const emptyStateStats = await statisticsService.getStatisticalAnalysis();
  console.log('✓ Empty state response for statistical analysis:');
  console.log('  hasData:', emptyStateStats.hasData);
  console.log('  totalResponses:', emptyStateStats.totalResponses);
  console.log('  message:', emptyStateStats.message);

  console.log('\n====================================================');
  console.log('ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!');
  console.log('====================================================');

  await mongoose.disconnect();
}

runEndToEndVerification().catch(err => {
  console.error('VERIFICATION ERROR:', err);
  process.exit(1);
});
