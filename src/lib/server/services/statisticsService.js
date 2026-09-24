import { SurveyResponse } from '../models/SurveyResponse.js';
import { AssessmentResult } from '../models/AssessmentResult.js';

/**
 * MindSafe Statistical Analysis Engine
 * Computes descriptive and inferential statistics strictly from real MongoDB survey data.
 * Zero synthetic, fake, or mocked numbers.
 * Non-causal academic phrasing adhered to throughout.
 */

// ==========================================
// MATHEMATICAL & STATISTICAL HELPER FUNCTIONS
// ==========================================

function logGamma(x) {
  const p = [
    676.5203681287751, -1259.1392167224028,
    771.32342877765313, -176.61502916214059,
    12.507343278686905, -0.13857109583111912,
    9.9843695780195716e-6, 1.5056327351493116e-7
  ];
  if (x < 0.5) {
    return Math.log(Math.PI / Math.sin(Math.PI * x)) - logGamma(1 - x);
  }
  x -= 1;
  let a = 0.99999999999980993;
  const t = x + 7.5;
  for (let i = 0; i < p.length; i++) {
    a += p[i] / (x + i + 1);
  }
  return 0.5 * Math.log(2 * Math.PI) + (x + 0.5) * Math.log(t) - t + Math.log(a);
}

// Incomplete Gamma Series / Continued Fraction
function gammp(s, x) {
  if (x <= 0) return 0;
  if (x < s + 1) {
    let ap = s;
    let sum = 1 / s;
    let del = sum;
    for (let n = 1; n <= 100; n++) {
      ap += 1;
      del *= x / ap;
      sum += del;
      if (Math.abs(del) < Math.abs(sum) * 1e-10) break;
    }
    return sum * Math.exp(-x + s * Math.log(x) - logGamma(s));
  } else {
    let b = x + 1 - s;
    let c = 1 / 1e-30;
    let d = 1 / b;
    let h = d;
    for (let i = 1; i <= 100; i++) {
      const an = -i * (i - s);
      b += 2;
      d = an * d + b;
      if (Math.abs(d) < 1e-30) d = 1e-30;
      c = b + an / c;
      if (Math.abs(c) < 1e-30) c = 1e-30;
      d = 1 / d;
      const del = d * c;
      h *= del;
      if (Math.abs(del - 1) < 1e-10) break;
    }
    return 1 - Math.exp(-x + s * Math.log(x) - logGamma(s)) * h;
  }
}

function chiSquarePValue(chiSq, df) {
  if (chiSq <= 0 || df <= 0) return 1.0;
  const p = 1 - gammp(df / 2, chiSq / 2);
  return Math.max(0.0001, Math.min(1.0, Number(p.toFixed(4))));
}

// Continued fraction for regularized incomplete beta
function betacf(a, b, x) {
  const maxIt = 100;
  const eps = 3.0e-10;
  const qab = a + b;
  const qap = a + 1;
  const qam = a - 1;
  let c = 1;
  let d = 1 - qab * x / qap;
  if (Math.abs(d) < 1e-30) d = 1e-30;
  d = 1 / d;
  let h = d;
  for (let m = 1; m <= maxIt; m++) {
    const m2 = 2 * m;
    let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < 1e-30) d = 1e-30;
    c = 1 + aa / c;
    if (Math.abs(c) < 1e-30) c = 1e-30;
    d = 1 / d;
    h *= d * c;
    aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
    d = 1 + aa * d;
    if (Math.abs(d) < 1e-30) d = 1e-30;
    c = 1 + aa / c;
    if (Math.abs(c) < 1e-30) c = 1e-30;
    d = 1 / d;
    const del = d * c;
    h *= del;
    if (Math.abs(del - 1) < eps) break;
  }
  return h;
}

function incBeta(a, b, x) {
  if (x <= 0) return 0;
  if (x >= 1) return 1;
  const bt = Math.exp(logGamma(a + b) - logGamma(a) - logGamma(b) + a * Math.log(x) + b * Math.log(1 - x));
  if (x < (a + 1) / (a + b + 2)) {
    return bt * betacf(a, b, x) / a;
  } else {
    return 1 - bt * betacf(b, a, 1 - x) / b;
  }
}

function tTestPValue(tStat, df) {
  if (df <= 0) return 1.0;
  const t = Math.abs(tStat);
  const x = df / (df + t * t);
  const p = incBeta(df / 2, 0.5, x);
  return Math.max(0.0001, Math.min(1.0, Number(p.toFixed(4))));
}

function calcMean(arr) {
  if (!arr.length) return 0;
  const sum = arr.reduce((a, b) => a + b, 0);
  return Number((sum / arr.length).toFixed(2));
}

function calcMedian(arr) {
  if (!arr.length) return 0;
  const sorted = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 !== 0 ? sorted[mid] : Number(((sorted[mid - 1] + sorted[mid]) / 2).toFixed(2));
}

function calcMode(arr) {
  if (!arr.length) return 'N/A';
  const frequency = {};
  let maxFreq = 0;
  let mode = arr[0];
  for (const val of arr) {
    frequency[val] = (frequency[val] || 0) + 1;
    if (frequency[val] > maxFreq) {
      maxFreq = frequency[val];
      mode = val;
    }
  }
  return mode;
}

function calcStdDev(arr, mean) {
  if (arr.length <= 1) return 0;
  const variance = arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (arr.length - 1);
  return Number(Math.sqrt(variance).toFixed(2));
}

function calcVariance(arr, mean) {
  if (arr.length <= 1) return 0;
  return arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (arr.length - 1);
}

function calcCorrelation(arrX, arrY) {
  if (arrX.length !== arrY.length || arrX.length < 2) return 0;
  const n = arrX.length;
  const meanX = calcMean(arrX);
  const meanY = calcMean(arrY);

  let num = 0;
  let denX = 0;
  let denY = 0;

  for (let i = 0; i < n; i++) {
    const dx = arrX[i] - meanX;
    const dy = arrY[i] - meanY;
    num += dx * dy;
    denX += dx * dx;
    denY += dy * dy;
  }

  const den = Math.sqrt(denX * denY);
  if (den === 0) return 0;
  return Number((num / den).toFixed(3));
}

function calcRanks(arr) {
  const indexed = arr.map((val, idx) => ({ val, idx })).sort((a, b) => a.val - b.val);
  const ranks = new Array(arr.length);
  let i = 0;
  while (i < indexed.length) {
    let j = i;
    while (j < indexed.length - 1 && indexed[j + 1].val === indexed[j].val) {
      j++;
    }
    const avgRank = (i + 1 + j + 1) / 2;
    for (let k = i; k <= j; k++) {
      ranks[indexed[k].idx] = avgRank;
    }
    i = j + 1;
  }
  return ranks;
}

function calcSpearman(arrX, arrY) {
  if (arrX.length !== arrY.length || arrX.length < 2) return 0;
  return calcCorrelation(calcRanks(arrX), calcRanks(arrY));
}

// ==========================================
// VARIABLE DEFINITIONS & CATALOGUE
// ==========================================

export const VARIABLE_CATALOGUE = {
  ageGroup: {
    key: 'ageGroup',
    label: 'Age Category',
    type: 'categorical',
    categories: ['Under 18', '18–22', '23–26', '27+'],
    extract: (r) => r.ageGroup
  },
  gender: {
    key: 'gender',
    label: 'Gender Identity',
    type: 'binary_categorical',
    categories: ['Female', 'Male', 'Non-binary', 'Prefer not to say'],
    binaryCategories: ['Female', 'Male'],
    extract: (r) => r.gender
  },
  socialMediaPlatform: {
    key: 'socialMediaPlatform',
    label: 'Primary / Incident Platform',
    type: 'categorical',
    categories: ['Instagram', 'YouTube', 'TikTok / Reels', 'X (Twitter)', 'Snapchat', 'Discord', 'WhatsApp'],
    extract: (r) => r.socialMediaPlatform
  },
  usageHours: {
    key: 'usageHours',
    label: 'Daily Social Media Usage (Hours)',
    type: 'numerical_ordinal',
    unit: 'Hours',
    categories: ['< 2.5 hrs', '2.5–4.5 hrs', '4.5–6.5 hrs', '> 6.5 hrs'],
    mapping: { '< 2.5 hrs': 1.5, '2.5–4.5 hrs': 3.5, '4.5–6.5 hrs': 5.5, '> 6.5 hrs': 7.5 },
    extract: (r) => r.usageHours,
    extractNumeric: (r) => {
      const map = { '< 2.5 hrs': 1.5, '2.5–4.5 hrs': 3.5, '4.5–6.5 hrs': 5.5, '> 6.5 hrs': 7.5 };
      return map[r.usageHours] ?? 3.5;
    }
  },
  cyberbullyingExperience: {
    key: 'cyberbullyingExperience',
    label: 'Cyberbullying Experience',
    type: 'binary',
    categories: ['Yes', 'No'],
    extract: (r) => r.cyberbullyingExperience,
    extractNumeric: (r) => (r.cyberbullyingExperience === 'Yes' ? 1 : 0)
  },
  frequency: {
    key: 'frequency',
    label: 'Harassment Frequency (Scale 0–4)',
    type: 'numerical_ordinal',
    unit: 'Scale 0–4',
    categories: ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often'],
    mapping: { 'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4 },
    extract: (r) => r.frequency,
    extractNumeric: (r) => {
      const map = { 'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4 };
      return map[r.frequency] ?? 0;
    }
  },
  activityType: {
    key: 'activityType',
    label: 'Harassment Category',
    type: 'categorical',
    categories: ['Offensive Comments & Trolling', 'Body Shaming', 'Hate Speech', 'Threats & Intimidation', 'Fake Rumors / Impersonation', 'None'],
    extract: (r) => r.activityType
  },
  emotionalWellbeing: {
    key: 'emotionalWellbeing',
    label: 'Mental Health Impact (Scale 0–3)',
    type: 'numerical_ordinal',
    isPrimaryTarget: true,
    unit: 'Scale 0–3',
    categories: ['Not at all', 'Slightly', 'Moderately', 'Severely'],
    mapping: { 'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3 },
    extract: (r) => r.emotionalWellbeing,
    extractNumeric: (r) => {
      const map = { 'Not at all': 0, 'Slightly': 1, 'Moderately': 2, 'Severely': 3 };
      return map[r.emotionalWellbeing] ?? 0;
    }
  },
  emotionalSymptom: {
    key: 'emotionalSymptom',
    label: 'Prominent Stress Symptom',
    type: 'categorical',
    categories: ['Minimal Impact', 'Stress', 'Anxiety', 'Sleep Loss', 'Social Withdrawal', 'Anger & Frustration'],
    extract: (r) => r.emotionalSymptom
  },
  actionTaken: {
    key: 'actionTaken',
    label: 'Response Action Taken',
    type: 'categorical',
    categories: ['Blocked User', 'Reported Account', 'Told Friends/Family', 'Ignored it', 'Confronted the Person'],
    extract: (r) => r.actionTaken
  }
};

// Aliases for research exploration compatibility
VARIABLE_CATALOGUE.experience = VARIABLE_CATALOGUE.cyberbullyingExperience;
VARIABLE_CATALOGUE.platform = VARIABLE_CATALOGUE.socialMediaPlatform;
VARIABLE_CATALOGUE.incidentPlatform = VARIABLE_CATALOGUE.socialMediaPlatform;
VARIABLE_CATALOGUE.usage = VARIABLE_CATALOGUE.usageHours;
VARIABLE_CATALOGUE.cyberbullyingFrequency = VARIABLE_CATALOGUE.frequency;
VARIABLE_CATALOGUE.mentalHealthImpact = VARIABLE_CATALOGUE.emotionalWellbeing;

// ==========================================
// CORE STATISTICS SERVICE
// ==========================================

export const statisticsService = {
  // Extract standardized fields from MongoDB response document
  getStandardized(doc) {
    const a = doc.responses || {};
    return {
      ageGroup: a.ageGroup || a.age || 'Not specified',
      gender: a.gender || 'Not specified',
      socialMediaPlatform: a.socialMediaPlatform || a.platform || 'Not specified',
      usageHours: a.usageHours || a.socialMediaUsage || '2.5–4.5 hrs',
      cyberbullyingExperience: a.cyberbullyingExperience || 'No',
      frequency: a.frequency || a.cyberbullyingFrequency || 'Never',
      activityType: a.activityType || a.harassmentType || 'None',
      emotionalWellbeing: a.emotionalWellbeing || a.mentalHealthImpact || 'Not at all',
      emotionalSymptom: a.emotionalSymptom || 'Minimal Impact',
      actionTaken: a.actionTaken || 'Did Not Report'
    };
  },

  // 1. Overview Analytics
  async getOverview() {
    const responses = await SurveyResponse.find({}).lean();
    if (!responses.length) {
      return {
        hasData: false,
        totalResponses: 0,
        message: 'No survey data available yet.'
      };
    }

    const total = responses.length;
    const cleaned = responses.map(this.getStandardized);

    const experiencedCount = cleaned.filter(r => r.cyberbullyingExperience === 'Yes').length;
    const experiencedPct = Math.round((experiencedCount / total) * 100);

    const modSevCount = cleaned.filter(r => r.emotionalWellbeing === 'Moderately' || r.emotionalWellbeing === 'Severely').length;
    const mentalImpactPct = Math.round((modSevCount / total) * 100);

    return {
      hasData: true,
      totalResponses: total,
      cyberbullyingExposurePct: experiencedPct,
      mentalHealthImpactPct: mentalImpactPct,
      experiencedCount,
      moderateSevereCount: modSevCount
    };
  },

  // 2. Demographic and Cyberbullying Distributions
  async getSurveyStatistics() {
    const responses = await SurveyResponse.find({}).lean();
    if (!responses.length) {
      return {
        hasData: false,
        totalResponses: 0,
        message: 'No survey data available yet.'
      };
    }

    const total = responses.length;
    const cleaned = responses.map(this.getStandardized);

    const countBy = (field) => {
      const counts = {};
      cleaned.forEach(item => {
        const val = item[field] || 'Not specified';
        counts[val] = (counts[val] || 0) + 1;
      });
      return counts;
    };

    return {
      hasData: true,
      totalResponses: total,
      ageDistribution: countBy('ageGroup'),
      genderDistribution: countBy('gender'),
      platformUsage: countBy('socialMediaPlatform'),
      usageDuration: countBy('usageHours'),
      cyberbullyingExperience: countBy('cyberbullyingExperience'),
      cyberbullyingFrequency: countBy('frequency'),
      harassmentTypes: countBy('activityType'),
      reportingBehavior: countBy('actionTaken')
    };
  },

  // 3. Primary ML Outcome: Mental Health Impact
  async getMentalHealthAnalysis() {
    const assessments = await AssessmentResult.find({}).lean();
    if (!assessments.length) {
      return {
        hasData: false,
        totalResponses: 0,
        message: 'No assessment data available yet.',
        targetVariable: 'Mental Health Impact',
        targetClasses: ['Not at all', 'Slightly', 'Moderately', 'Severely'],
        distribution: {
          'Not at all': 0,
          'Slightly': 0,
          'Moderately': 0,
          'Severely': 0
        },
        percentages: {
          'Not at all': 0,
          'Slightly': 0,
          'Moderately': 0,
          'Severely': 0
        }
      };
    }

    const total = assessments.length;
    const targetClasses = ['Not at all', 'Slightly', 'Moderately', 'Severely'];
    const distribution = {
      'Not at all': 0,
      'Slightly': 0,
      'Moderately': 0,
      'Severely': 0
    };

    assessments.forEach(a => {
      const cls = a.classification;
      if (cls && distribution[cls] !== undefined) {
        distribution[cls]++;
      }
    });

    const percentages = {};
    for (const [k, v] of Object.entries(distribution)) {
      percentages[k] = total > 0 ? Math.round((v / total) * 100) : 0;
    }

    // Cross-tabulation with cyberbullying experience if survey responses exist
    const crossWithExperience = {
      experienced: { 'Not at all': 0, 'Slightly': 0, 'Moderately': 0, 'Severely': 0 },
      notExperienced: { 'Not at all': 0, 'Slightly': 0, 'Moderately': 0, 'Severely': 0 }
    };

    try {
      const surveyIds = assessments.map(a => a.responseId).filter(Boolean);
      if (surveyIds.length > 0) {
        const surveys = await SurveyResponse.find({ _id: { $in: surveyIds } }).lean();
        const surveyMap = new Map();
        surveys.forEach(s => surveyMap.set(s._id.toString(), s));

        assessments.forEach(a => {
          const s = a.responseId ? surveyMap.get(a.responseId.toString()) : null;
          const exp = (s?.responses?.q5_exp === 'Yes' || s?.responses?.cyberbullyingExperience === 'Yes')
            ? 'experienced'
            : 'notExperienced';
          const cls = a.classification;
          if (cls && crossWithExperience[exp][cls] !== undefined) {
            crossWithExperience[exp][cls]++;
          }
        });
      }
    } catch (crossErr) {
      console.warn('[MentalHealthAnalysis] Cross-tabulation notice:', crossErr.message);
    }

    return {
      hasData: true,
      totalResponses: total,
      targetVariable: 'Mental Health Impact',
      targetClasses,
      distribution,
      percentages,
      crossWithExperience,
      records: assessments.map(a => ({
        id: a._id.toString(),
        classification: a.classification,
        createdAt: a.createdAt
      }))
    };
  },

  // 4. Descriptive Statistics (Numerical and Categorical separated)
  async getDescriptiveStatistics(cleanedData) {
    const total = cleanedData.length;
    if (!total) return null;

    // Numerical / Ordinal variables
    const numericalVariables = ['usageHours', 'frequency', 'emotionalWellbeing'];
    const numerical = {};

    numericalVariables.forEach(key => {
      const def = VARIABLE_CATALOGUE[key];
      const values = cleanedData.map(def.extractNumeric);
      const mean = calcMean(values);
      const median = calcMedian(values);
      const mode = calcMode(values);
      const stdDev = calcStdDev(values, mean);
      const min = Math.min(...values);
      const max = Math.max(...values);

      numerical[key] = {
        variable: def.label,
        key,
        unit: def.unit,
        sampleSize: total,
        mean,
        median,
        mode,
        stdDev,
        min,
        max
      };
    });

    // Categorical variables (Frequencies, Percentages, and Mode Category)
    const categoricalVariables = [
      'ageGroup', 'gender', 'socialMediaPlatform', 'cyberbullyingExperience', 
      'activityType', 'emotionalSymptom', 'actionTaken'
    ];
    const categorical = {};

    categoricalVariables.forEach(key => {
      const def = VARIABLE_CATALOGUE[key];
      const counts = {};
      let maxCount = 0;
      let modeCategory = 'None';

      cleanedData.forEach(r => {
        const val = def.extract(r);
        counts[val] = (counts[val] || 0) + 1;
        if (counts[val] > maxCount) {
          maxCount = counts[val];
          modeCategory = val;
        }
      });

      const percentages = {};
      for (const [k, v] of Object.entries(counts)) {
        percentages[k] = Math.round((v / total) * 100);
      }

      categorical[key] = {
        variable: def.label,
        key,
        sampleSize: total,
        modeCategory,
        modeFrequency: maxCount,
        modePercentage: Math.round((maxCount / total) * 100),
        frequencies: counts,
        percentages
      };
    });

    return { numerical, categorical };
  },

  // 5. Complete Statistical Analysis Overview (with catalogue & default tests)
  async getStatisticalAnalysis() {
    const responses = await SurveyResponse.find({}).lean();
    if (!responses.length) {
      return {
        hasData: false,
        totalResponses: 0,
        message: 'No survey data available yet.'
      };
    }

    const cleaned = responses.map(this.getStandardized);
    const descriptive = await this.getDescriptiveStatistics(cleaned);

    // Run baseline representative inferential tests
    const defaultChiSquare = await this.runCustomAnalysis('chi_square', 'frequency', 'emotionalWellbeing');
    const defaultTTest = await this.runCustomAnalysis('t_test', 'cyberbullyingExperience', 'emotionalWellbeing');
    const defaultCorrelation = await this.runCustomAnalysis('correlation', 'frequency', 'emotionalWellbeing');

    return {
      hasData: true,
      totalResponses: responses.length,
      variableCatalogue: Object.values(VARIABLE_CATALOGUE).map(v => ({
        key: v.key,
        label: v.label,
        type: v.type,
        categories: v.categories || []
      })),
      descriptive,
      defaultTests: {
        chiSquare: defaultChiSquare,
        tTest: defaultTTest,
        correlation: defaultCorrelation
      }
    };
  },

  // 6. Dynamic Custom Inferential Analysis Runner
  async runCustomAnalysis(testType, var1Key, var2Key) {
    const responses = await SurveyResponse.find({}).lean();
    if (!responses.length) {
      return {
        hasData: false,
        totalResponses: 0,
        applicable: false,
        message: 'No survey data available yet.'
      };
    }

    const total = responses.length;
    const cleaned = responses.map(this.getStandardized);

    const def1 = VARIABLE_CATALOGUE[var1Key];
    const def2 = VARIABLE_CATALOGUE[var2Key];

    if (!def1 || !def2) {
      return {
        applicable: false,
        reason: 'Selected variable does not exist in the research catalogue.'
      };
    }

    // ==========================================
    // A. CHI-SQUARE TEST OF INDEPENDENCE
    // ==========================================
    if (testType === 'chi_square') {
      if (var1Key === var2Key) {
        return {
          applicable: false,
          reason: 'Chi-Square test requires two distinct categorical variables.'
        };
      }

      // Check categorical suitability
      const cat1List = def1.categories || [...new Set(cleaned.map(def1.extract))];
      const cat2List = def2.categories || [...new Set(cleaned.map(def2.extract))];

      if (cat1List.length < 2 || cat2List.length < 2) {
        return {
          applicable: false,
          reason: 'Test not applicable for the selected variable types. (Requires at least 2 distinct categories per variable).'
        };
      }

      // Build Observed contingency matrix
      const observedMatrix = cat1List.map(c1 => {
        return cat2List.map(c2 => {
          return cleaned.filter(r => def1.extract(r) === c1 && def2.extract(r) === c2).length;
        });
      });

      // Filter out entirely empty rows or columns
      const rowTotals = observedMatrix.map(row => row.reduce((a, b) => a + b, 0));
      const colTotals = Array(cat2List.length).fill(0);
      for (let r = 0; r < cat1List.length; r++) {
        for (let c = 0; c < cat2List.length; c++) {
          colTotals[c] += observedMatrix[r][c];
        }
      }

      const activeRows = cat1List.filter((_, i) => rowTotals[i] > 0);
      const activeCols = cat2List.filter((_, j) => colTotals[j] > 0);

      if (activeRows.length < 2 || activeCols.length < 2) {
        return {
          applicable: false,
          reason: 'Current sample does not span multiple distinct categories across both variables to construct a valid 2x2+ contingency matrix.'
        };
      }

      // Calculate Expected frequencies & Chi-Square
      let chiSquare = 0;
      const expectedMatrix = [];

      for (let r = 0; r < cat1List.length; r++) {
        const expectedRow = [];
        for (let c = 0; c < cat2List.length; c++) {
          const expected = total > 0 ? (rowTotals[r] * colTotals[c]) / total : 0;
          expectedRow.push(Number(expected.toFixed(2)));
          if (expected > 0) {
            chiSquare += Math.pow(observedMatrix[r][c] - expected, 2) / expected;
          }
        }
        expectedMatrix.push(expectedRow);
      }

      const df = (activeRows.length - 1) * (activeCols.length - 1);
      const minDim = Math.min(activeRows.length - 1, activeCols.length - 1);
      const cramersV = minDim > 0 && total > 0 ? Number(Math.sqrt(chiSquare / (total * minDim)).toFixed(3)) : 0;
      const pValue = chiSquarePValue(chiSquare, df);

      const isSignificant = pValue < 0.05;
      const interpretation = isSignificant
        ? `Statistically significant association detected between ${def1.label} and ${def2.label} at the α = 0.05 level (χ² = ${chiSquare.toFixed(2)}, df = ${df}, p = ${pValue}, Cramér's V = ${cramersV}). This reflects observed statistical dependence and does not imply causation.`
        : `No statistically significant association detected between ${def1.label} and ${def2.label} at the α = 0.05 level (χ² = ${chiSquare.toFixed(2)}, df = ${df}, p = ${pValue}). Fail to reject the null hypothesis of independence.`;

      return {
        applicable: true,
        testType: 'chi_square',
        testName: 'Chi-Square Test of Independence',
        variables: `${def1.label} × ${def2.label}`,
        sampleSize: total,
        testStatistic: Number(chiSquare.toFixed(2)),
        statisticName: 'Chi-Square (χ²)',
        degreesOfFreedom: df,
        pValue,
        effectSizeName: "Cramér's V",
        effectSize: cramersV,
        rowLabels: cat1List,
        colLabels: cat2List,
        observedMatrix,
        expectedMatrix,
        interpretation,
        isSignificant
      };
    }

    // ==========================================
    // B. INDEPENDENT SAMPLES T-TEST
    // ==========================================
    if (testType === 't_test') {
      // Must have ONE binary grouping variable and ONE continuous/numerical variable
      let binaryDef = null;
      let numericDef = null;

      if ((def1.type === 'binary' || def1.type === 'binary_categorical') && def2.type === 'numerical_ordinal') {
        binaryDef = def1;
        numericDef = def2;
      } else if ((def2.type === 'binary' || def2.type === 'binary_categorical') && def1.type === 'numerical_ordinal') {
        binaryDef = def2;
        numericDef = def1;
      } else {
        return {
          applicable: false,
          reason: 'T-test cannot be performed with the currently available variable types. (Independent T-Test requires one binary grouping variable [e.g., Cyberbullying Experience or Gender] and one numerical/ordinal continuous variable [e.g., Mental Health Impact Score or Daily Usage Hours]).'
        };
      }

      // Extract binary groups (e.g. ['Yes', 'No'] or ['Female', 'Male'])
      const groupLabels = binaryDef.key === 'gender' ? ['Female', 'Male'] : ['Yes', 'No'];
      const group1Name = groupLabels[0];
      const group2Name = groupLabels[1];

      const group1Values = cleaned
        .filter(r => binaryDef.extract(r) === group1Name)
        .map(numericDef.extractNumeric);

      const group2Values = cleaned
        .filter(r => binaryDef.extract(r) === group2Name)
        .map(numericDef.extractNumeric);

      if (group1Values.length < 1 || group2Values.length < 1) {
        return {
          applicable: false,
          reason: `Insufficient sample size to perform T-test. Group "${group1Name}" has ${group1Values.length} records and Group "${group2Name}" has ${group2Values.length} records.`
        };
      }

      const mean1 = calcMean(group1Values);
      const mean2 = calcMean(group2Values);
      const var1 = calcVariance(group1Values, mean1);
      const var2 = calcVariance(group2Values, mean2);
      const n1 = group1Values.length;
      const n2 = group2Values.length;

      const se = Math.sqrt((var1 / n1) + (var2 / n2));
      const tStat = se > 0 ? Number(((mean1 - mean2) / se).toFixed(2)) : 0;

      // Welch-Satterthwaite degrees of freedom
      let df = n1 + n2 - 2;
      if (var1 > 0 || var2 > 0) {
        const num = Math.pow((var1 / n1) + (var2 / n2), 2);
        const den = (Math.pow(var1 / n1, 2) / Math.max(1, n1 - 1)) + (Math.pow(var2 / n2, 2) / Math.max(1, n2 - 1));
        df = den > 0 ? Math.max(1, Math.round(num / den)) : n1 + n2 - 2;
      }

      const pValue = tTestPValue(tStat, df);
      const isSignificant = pValue < 0.05;
      const difference = Number((mean1 - mean2).toFixed(2));

      const interpretation = isSignificant
        ? `Statistically significant difference between ${group1Name} (Mean = ${mean1}) and ${group2Name} (Mean = ${mean2}) on ${numericDef.label} detected at the α = 0.05 level (t = ${tStat}, df = ${df}, p = ${pValue}). Mean difference is ${difference}. This denotes an observed statistical difference between cohorts and does not establish causation.`
        : `No statistically significant difference between ${group1Name} (Mean = ${mean1}) and ${group2Name} (Mean = ${mean2}) detected on ${numericDef.label} at the α = 0.05 level (t = ${tStat}, df = ${df}, p = ${pValue}). Mean difference is ${difference}.`;

      return {
        applicable: true,
        testType: 't_test',
        testName: 'Two-Sample Independent T-Test (Welch)',
        variables: `${numericDef.label} across ${binaryDef.label} (${group1Name} vs ${group2Name})`,
        sampleSize: n1 + n2,
        testStatistic: tStat,
        statisticName: 'T-Statistic (t)',
        degreesOfFreedom: df,
        pValue,
        effectSizeName: 'Mean Difference (Δ)',
        effectSize: difference,
        group1: { name: group1Name, sampleSize: n1, mean: mean1, stdDev: calcStdDev(group1Values, mean1) },
        group2: { name: group2Name, sampleSize: n2, mean: mean2, stdDev: calcStdDev(group2Values, mean2) },
        interpretation,
        isSignificant
      };
    }

    // ==========================================
    // C. CORRELATION ANALYSIS (PEARSON & SPEARMAN)
    // ==========================================
    if (testType === 'correlation' || testType === 'spearman') {
      if ((def1.type !== 'numerical_ordinal' && def1.type !== 'binary') || 
          (def2.type !== 'numerical_ordinal' && def2.type !== 'binary')) {
        return {
          applicable: false,
          reason: 'Test not applicable for the selected variable types. (Correlation analysis requires two ordinal, numerical, or binary scaled variables with defined rank order).'
        };
      }

      if (!def1.extractNumeric || !def2.extractNumeric) {
        return {
          applicable: false,
          reason: 'Test not applicable: missing numeric mapping for selected variables.'
        };
      }

      const arrX = cleaned.map(def1.extractNumeric);
      const arrY = cleaned.map(def2.extractNumeric);

      if (arrX.length < 2) {
        return {
          applicable: false,
          reason: 'Sample size must be at least N = 2 to compute correlation.'
        };
      }

      const isSpearman = testType === 'spearman';
      const rCoeff = isSpearman ? calcSpearman(arrX, arrY) : calcCorrelation(arrX, arrY);
      const statName = isSpearman ? 'Spearman ρ' : 'Pearson r';
      const testTitle = isSpearman ? 'Spearman Rank-Order Correlation Analysis' : 'Pearson Bivariate Correlation Analysis';
      const df = total - 2;
      const tStat = df > 0 && Math.abs(rCoeff) < 1
        ? Number((rCoeff * Math.sqrt(df / (1 - rCoeff * rCoeff))).toFixed(2))
        : 0;

      const pValue = df > 0 ? tTestPValue(tStat, df) : 1.0;
      const isSignificant = pValue < 0.05;

      const direction = rCoeff > 0.05 ? 'positive' : rCoeff < -0.05 ? 'negative' : 'near-zero';
      const strength = Math.abs(rCoeff) > 0.5 ? 'strong' : Math.abs(rCoeff) > 0.3 ? 'moderate' : 'weak';

      const interpretation = isSignificant
        ? `Statistically significant ${direction} rank-order association detected between ${def1.label} and ${def2.label} (${statName} = ${rCoeff}, p = ${pValue}, df = ${df}). Correlation indicates an observed co-movement between measures and does not imply causation.`
        : `No statistically significant rank-order correlation detected between ${def1.label} and ${def2.label} at the α = 0.05 level (${statName} = ${rCoeff}, p = ${pValue}, df = ${df}).`;

      return {
        applicable: true,
        testType: isSpearman ? 'spearman' : 'correlation',
        testName: testTitle,
        variables: `${def1.label} & ${def2.label}`,
        sampleSize: total,
        testStatistic: rCoeff,
        statisticName: statName,
        degreesOfFreedom: df,
        pValue,
        effectSizeName: 'Coefficient of Determination (r² / ρ²)',
        effectSize: Number((rCoeff * rCoeff).toFixed(3)),
        direction,
        strength,
        interpretation,
        isSignificant
      };
    }

    return {
      applicable: false,
      reason: `Unknown statistical test type "${testType}".`
    };
  },

  // 7. Interactive Relationship Explorer
  async getRelationships(varX = 'frequency', varY = 'emotionalWellbeing') {
    const responses = await SurveyResponse.find({}).lean();
    if (!responses.length) {
      return {
        hasData: false,
        totalResponses: 0,
        message: 'No survey data available yet.',
        labels: [],
        datasets: []
      };
    }

    const total = responses.length;
    const cleaned = responses.map(this.getStandardized);

    const targetClasses = ['Not at all', 'Slightly', 'Moderately', 'Severely'];
    const palette = ['#601D49', '#BD5579', '#EA9D9D', '#FFEBB8'];

    const defX = VARIABLE_CATALOGUE[varX] || VARIABLE_CATALOGUE.frequency;
    const defY = VARIABLE_CATALOGUE[varY] || VARIABLE_CATALOGUE.emotionalWellbeing;
    const labelsX = defX.categories || ['Never', 'Rarely', 'Sometimes', 'Often', 'Very Often'];

    const datasets = targetClasses.map((tClass, idx) => {
      const data = labelsX.map(lbl => {
        return cleaned.filter(r => defX.extract(r) === lbl && defY.extract(r) === tClass).length;
      });

      return {
        label: tClass,
        data,
        backgroundColor: palette[idx],
        borderRadius: 4
      };
    });

    const associationStats = await this.runCustomAnalysis('chi_square', defX.key, defY.key);

    let spearmanStats = null;
    if (defX.extractNumeric && defY.extractNumeric) {
      const arrX = cleaned.map(defX.extractNumeric);
      const arrY = cleaned.map(defY.extractNumeric);
      const rho = calcSpearman(arrX, arrY);
      const df = total - 2;
      const tStat = df > 0 && Math.abs(rho) < 1
        ? Number((rho * Math.sqrt(df / (1 - rho * rho))).toFixed(2))
        : 0;
      const pValue = df > 0 ? tTestPValue(tStat, df) : 1.0;
      spearmanStats = {
        rho,
        pValue,
        isSignificant: pValue < 0.05,
        degreesOfFreedom: df
      };
    }

    return {
      hasData: true,
      totalResponses: total,
      varX,
      varY,
      labels: labelsX,
      datasets,
      associationStats: associationStats.applicable ? associationStats : null,
      spearmanStats,
      interpretation: associationStats.applicable
        ? associationStats.interpretation
        : 'Association calculation ready.'
    };
  }
};
