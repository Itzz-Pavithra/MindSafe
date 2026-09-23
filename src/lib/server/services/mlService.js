import { env } from '$env/dynamic/private';

const ML_API_BASE_URL = (env.ML_API_URL || process.env.ML_API_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');

/**
 * MindSafe Machine Learning Service Integration
 * Connects the SvelteKit backend to the FastAPI Python ML service.
 * Targets: Mental Health Impact (Multiclass Classification: Not at all, Slightly, Moderately, Severely)
 * Features SHAP TreeExplainer feature attributions for local explainability.
 */
export const mlService = {
  getApiUrl() {
    return ML_API_BASE_URL;
  },

  /**
   * Probes the ML service health endpoint.
   */
  async getStatus() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const res = await fetch(`${ML_API_BASE_URL}/api/ml/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (res.ok) {
        const data = await res.json();
        return {
          connected: true,
          status: 'online',
          model_name: data.model_version || 'MindSafe Primary Multiclass Classifier',
          target_classes: data.target_classes || ['Not at all', 'Slightly', 'Moderately', 'Severely'],
          feature_count: data.feature_count || 54,
          test_metrics: data.test_metrics || {}
        };
      } else {
        return {
          connected: false,
          status: 'degraded',
          message: `ML service returned status ${res.status}`
        };
      }
    } catch (err) {
      return {
        connected: false,
        status: 'offline',
        message: 'ML service is currently unreachable'
      };
    }
  },

  /**
   * Invokes the primary Random Forest model and SHAP TreeExplainer on questionnaire responses.
   *
   * @param {Record<string, any>} assessment - The participant's assessment answers
   * @returns {Promise<{
   *   success: boolean;
   *   model_name: string;
   *   model_version: string;
   *   prediction: { class: string; predicted_class_index: number; probabilities: Record<string, number> };
   *   explanation: { top_features: Array<any>; method: string; note: string };
   *   disclaimer: string;
   * }>}
   */
  async predict(assessment) {
    if (!assessment || typeof assessment !== 'object' || Object.keys(assessment).length === 0) {
      throw new Error('Assessment questionnaire responses are required.');
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const response = await fetch(`${ML_API_BASE_URL}/api/ml/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ assessment }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorDetail = 'Inference request failed';
        try {
          const errData = await response.json();
          if (errData?.detail) errorDetail = errData.detail;
        } catch (_) {
          // ignore json parse error
        }
        console.error(`[mlService] FastAPI returned HTTP ${response.status}: ${errorDetail}`);
        throw new Error('Unable to analyze your responses right now. Please try again.');
      }

      const data = await response.json();
      return data;
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        console.error('[mlService] ML API request timed out after 10s');
      } else {
        console.error('[mlService] ML API error:', err.message);
      }
      throw new Error('Unable to analyze your responses right now. Please try again.');
    }
  }
};
