import fs from 'node:fs';
import path from 'node:path';
import { error } from '@sveltejs/kit';

function parseCsv(content) {
  const lines = content.trim().split('\n').map(l => l.trim()).filter(Boolean);
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim());
  return lines.slice(1).map(line => {
    // Simple CSV parser supporting standard commas
    const vals = line.split(',').map(v => v.trim());
    const obj = {};
    headers.forEach((h, i) => {
      const v = vals[i];
      const num = Number(v);
      obj[h] = isNaN(num) || v === '' ? v : num;
    });
    return obj;
  });
}

export async function load({ locals }) {
  // Enforce Administrator Authentication
  if (!locals.user || locals.user.role !== 'admin') {
    throw error(403, 'Unauthorized: Administrator authentication required to view ML Research Analytics.');
  }

  const resultsDir = path.resolve('results', 'ml');

  try {
    const metricsPath = path.join(resultsDir, 'model_metrics.json');
    const classReportPath = path.join(resultsDir, 'classification_report.csv');
    const modelCompPath = path.join(resultsDir, 'model_comparison.csv');
    const cvPath = path.join(resultsDir, 'cross_validation_results.csv');
    const featImpPath = path.join(resultsDir, 'feature_importance.csv');
    const shapImpPath = path.join(resultsDir, 'shap_feature_importance.csv');

    const metrics = fs.existsSync(metricsPath) ? JSON.parse(fs.readFileSync(metricsPath, 'utf-8')) : {};
    const classificationReport = fs.existsSync(classReportPath) ? parseCsv(fs.readFileSync(classReportPath, 'utf-8')) : [];
    const modelComparison = fs.existsSync(modelCompPath) ? parseCsv(fs.readFileSync(modelCompPath, 'utf-8')) : [];
    const cvResults = fs.existsSync(cvPath) ? parseCsv(fs.readFileSync(cvPath, 'utf-8')) : [];
    const featureImportance = fs.existsSync(featImpPath) ? parseCsv(fs.readFileSync(featImpPath, 'utf-8')) : [];
    const shapImportance = fs.existsSync(shapImpPath) ? parseCsv(fs.readFileSync(shapImpPath, 'utf-8')) : [];

    return {
      modelInfo: {
        modelName: 'MindSafe Primary Multiclass Classifier',
        algorithm: 'Random Forest Classifier (100 estimators, balanced class weights)',
        scenario: 'Scenario B (Leakage-Controlled)',
        targetVariable: 'Mental_Health_Impact',
        targetClasses: ['Not at all', 'Slightly', 'Moderately', 'Severely'],
        trainSize: 411,
        testSize: 103,
        totalDatasetSize: 514,
        featureCount: 54
      },
      metrics,
      classificationReport,
      modelComparison,
      cvResults,
      featureImportance: featureImportance.slice(0, 15),
      shapImportance: shapImportance.slice(0, 15)
    };
  } catch (err) {
    console.error('Failed to load ML analysis data from results/ml:', err);
    throw error(500, 'Failed to load model research artifacts.');
  }
}
