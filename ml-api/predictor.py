import logging
from typing import Dict, Any, List, Union
import pandas as pd
import numpy as np

try:
    from .model_loader import model_loader
    from .shap_explainer import ShapExplainerManager
except (ImportError, ValueError):
    from model_loader import model_loader
    from shap_explainer import ShapExplainerManager

logger = logging.getLogger("mindsafe.ml_api.predictor")

TARGET_CLASSES = ["Not at all", "Slightly", "Moderately", "Severely"]

class Predictor:
    """
    Inference orchestrator for MindSafe Primary Classifier.
    Transforms raw assessment dictionary into feature matrix and performs
    multiclass classification with Tree SHAP explainability.
    """
    def __init__(self):
        self.explainer_manager = None

    def initialize_explainer(self):
        if self.explainer_manager is None and model_loader.is_loaded:
            self.explainer_manager = ShapExplainerManager(model_loader.model)

    def normalize_input(self, assessment: Dict[str, Any]) -> Dict[str, str]:
        """
        Normalizes various questionnaire key representations into the exact column
        keys expected by the saved primary preprocessor pipeline.
        """
        prep = model_loader.preprocessor
        col_names = prep.col_names

        # Key mapping aliases
        key_alias_map = {
            'age': ['age', 'ageGroup', '1. What is your age?', col_names['age']],
            'gender': ['gender', '2. What is your gender?', col_names['gender']],
            'platforms': ['platforms', 'platformsUsed', 'socialMediaPlatform', '3. Which social media', col_names['platforms']],
            'usage': ['usage', 'usageHours', 'dailyUsage', '4. How many hours', col_names['usage']],
            'q5_exp': ['q5_exp', 'experiencedCyberbullying', 'cyberbullyingExperience', '5. Have you personally experienced', col_names['q5_exp']],
            'q6_wit': ['q6_wit', 'witnessedCyberbullying', '6. Have you ever witnessed', col_names['q6_wit']],
            'q7_post': ['q7_post', 'postedOffensiveContent', '7. Have you ever posted', col_names['q7_post']],
            'q9_types': ['q9_types', 'cyberbullyingTypes', 'activityType', '9. What type of cyberbullying', col_names['q9_types']],
            'q10_plat': ['q10_plat', 'incidentPlatform', '10. On which social media platform', col_names['q10_plat']],
            'q11_freq': ['q11_freq', 'frequency', 'cyberbullyingFrequency', '11. How often have you', col_names['q11_freq']],
            'q15_help': ['q15_help', 'soughtHelp', '15. Did you seek help', col_names['q15_help']],
            'q17_area': ['q17_area', 'harassmentContextArea', 'contextArea', '17. In which area', col_names['q17_area']],
            'q18_act': ['q18_act', 'actionTaken', '18. What action did you take', col_names['q18_act']]
        }

        row_dict = {}

        for canonical_key, aliases in key_alias_map.items():
            val = None
            for alias in aliases:
                if alias in assessment:
                    val = assessment[alias]
                    break
                # Partial match in assessment keys
                for k, v in assessment.items():
                    if alias.lower() in k.lower():
                        val = v
                        break
                if val is not None:
                    break

            target_col = col_names[canonical_key]

            # If value is a list (multiselect), join with comma
            if isinstance(val, (list, tuple, set)):
                val_str = ", ".join([str(item).strip() for item in val if item])
            elif val is not None:
                val_str = str(val).strip()
            else:
                val_str = ""

            # Value normalization for robust matching
            # Age normalization
            if canonical_key == 'age':
                if val_str in ['Under 18', '< 18', 'below 18', 'Below 18']:
                    val_str = 'Below 18'
                elif '18' in val_str and '22' in val_str:
                    val_str = '18–22'
                elif '23' in val_str and '30' in val_str:
                    val_str = '23–30'
                elif val_str in ['27+', 'Above 30', '> 30', '31–40', '41–50']:
                    val_str = 'Above 30'

            # Usage normalization
            elif canonical_key == 'usage':
                if '<' in val_str or 'Less than 1' in val_str:
                    val_str = 'Less than 1 hour'
                elif '1' in val_str and '3' in val_str:
                    val_str = '1–3 hours'
                elif '2.5' in val_str or ('3' in val_str and '5' in val_str) or '4.5' in val_str:
                    val_str = '3–5 hours'
                elif '>' in val_str or 'More than 5' in val_str or '6.5' in val_str:
                    val_str = 'More than 5 hours'

            # Binary normalization
            elif canonical_key in ['q5_exp', 'q6_wit']:
                if val_str.lower() in ['yes', 'true', '1']:
                    val_str = 'Yes'
                else:
                    val_str = 'No'

            # Offensive content normalization
            elif canonical_key == 'q7_post':
                if val_str.lower() in ['yes', 'true']:
                    val_str = 'Yes'
                elif val_str.lower() in ['not sure', 'unsure']:
                    val_str = 'Not Sure'
                else:
                    val_str = 'No'

            row_dict[target_col] = val_str

        return row_dict

    def predict(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs feature transformation, multiclass prediction, and SHAP explanation.
        """
        if not model_loader.is_loaded:
            model_loader.load()

        if self.explainer_manager is None:
            self.initialize_explainer()

        # 1. Normalize questionnaire inputs
        normalized_row = self.normalize_input(assessment)
        df_input = pd.DataFrame([normalized_row])

        # 2. Transform through fitted training preprocessor
        try:
            X_transformed = model_loader.preprocessor.transform(df_input)
        except Exception as e:
            logger.error(f"Preprocessing pipeline transformation error: {e}")
            raise ValueError(f"Feature preprocessing error: {e}")

        # 3. Model inference
        try:
            pred_class_idx = int(model_loader.model.predict(X_transformed)[0])
            pred_class_name = TARGET_CLASSES[pred_class_idx]
            probs_raw = model_loader.model.predict_proba(X_transformed)[0]
        except Exception as e:
            logger.error(f"Model prediction inference error: {e}")
            raise RuntimeError(f"Model execution error: {e}")

        # Map probabilities strictly from model output
        probabilities = {
            TARGET_CLASSES[i]: round(float(probs_raw[i]), 4)
            for i in range(len(TARGET_CLASSES))
        }

        # 4. Generate local SHAP explanation
        try:
            top_features = self.explainer_manager.explain_instance(
                X_transformed,
                predicted_class_idx=pred_class_idx,
                predicted_class_name=pred_class_name,
                top_k=5
            )
        except Exception as e:
            logger.error(f"SHAP explanation generation error: {e}")
            top_features = []

        return {
            "success": True,
            "model_name": "MindSafe Primary Random Forest Classifier",
            "model_version": "1.0.0-ScenarioB",
            "prediction": {
                "class": pred_class_name,
                "predicted_class_index": pred_class_idx,
                "probabilities": probabilities
            },
            "explanation": {
                "top_features": top_features,
                "method": "SHAP TreeExplainer (Additive Feature Attributions)",
                "note": "SHAP values quantify model decision weights for this response pattern and do not indicate clinical causation."
            },
            "disclaimer": "This is an analytical result from the project ML model and is not a medical diagnosis."
        }

predictor = Predictor()
