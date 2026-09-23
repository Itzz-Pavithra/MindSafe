import logging
from typing import List, Dict, Any, Optional
import numpy as np
import shap

logger = logging.getLogger("mindsafe.ml_api.shap")

# Human-readable label dictionary for all 54 trained Scenario B features
FEATURE_LABEL_MAP: Dict[str, str] = {
    "Age_Ordinal": "Age Group",
    "Daily_Usage_Ordinal": "Daily Social Media Usage",
    "Experienced_Cyberbullying_Binary": "Experienced Cyberbullying",
    "Witnessed_Cyberbullying_Binary": "Witnessed Cyberbullying",
    "Cyberbullying_Frequency_Ordinal": "Cyberbullying Frequency",
    "Gender_Female": "Gender (Female)",
    "Gender_Male": "Gender (Male)",
    "Gender_Non-binary": "Gender (Non-binary)",
    "Gender_Prefer not to say": "Gender (Undisclosed)",
    "Posted_Offensive_No": "Posted Hurtful Content (No)",
    "Posted_Offensive_Not Sure": "Posted Hurtful Content (Not Sure)",
    "Posted_Offensive_Yes": "Posted Hurtful Content (Yes)",
    "Incident_Platform_Facebook": "Incident Platform (Facebook)",
    "Incident_Platform_Instagram": "Incident Platform (Instagram)",
    "Incident_Platform_Others": "Incident Platform (Other Platforms)",
    "Incident_Platform_WhatsApp": "Incident Platform (WhatsApp)",
    "Incident_Platform_YouTube": "Incident Platform (YouTube)",
    "Context_Area_Family": "Harassment Context (Family)",
    "Context_Area_Friends Circle": "Harassment Context (Friends Circle)",
    "Context_Area_Online Gaming": "Harassment Context (Online Gaming)",
    "Context_Area_Other": "Harassment Context (Other)",
    "Context_Area_School / College": "Harassment Context (School / College)",
    "Context_Area_Social Media Community": "Harassment Context (Social Media Community)",
    "Context_Area_Unknown Stranger": "Harassment Context (Unknown Stranger)",
    "Context_Area_Workplace": "Harassment Context (Workplace)",
    "Platform_Used_Facebook": "Active Platform: Facebook",
    "Platform_Used_Instagram": "Active Platform: Instagram",
    "Platform_Used_Others": "Active Platform: Other Networks",
    "Platform_Used_WhatsApp": "Active Platform: WhatsApp",
    "Platform_Used_X (Twitter)": "Active Platform: X (Twitter)",
    "Platform_Used_YouTube": "Active Platform: YouTube",
    "Bullying_Type_Body Shaming": "Observed: Body Shaming",
    "Bullying_Type_Fake Profile": "Observed: Fake Profile",
    "Bullying_Type_Fake Rumors": "Observed: Fake Rumors",
    "Bullying_Type_Hate Speech": "Observed: Hate Speech",
    "Bullying_Type_Impersonation": "Observed: Impersonation",
    "Bullying_Type_Offensive Comments": "Observed: Offensive Comments",
    "Bullying_Type_Other": "Observed: Other Harassment",
    "Bullying_Type_Sexual Harassment": "Observed: Sexual Harassment",
    "Bullying_Type_Stalking": "Observed: Stalking",
    "Bullying_Type_Threats": "Observed: Direct Threats",
    "Sought_Help_Counselor": "Sought Help: Counselor",
    "Sought_Help_Family": "Sought Help: Family",
    "Sought_Help_Friends": "Sought Help: Friends",
    "Sought_Help_Helpline": "Sought Help: National Helpline",
    "Sought_Help_No": "Sought Help: None / No Support",
    "Sought_Help_Psychologist": "Sought Help: Psychologist",
    "Sought_Help_Teacher": "Sought Help: Teacher / Faculty",
    "Action_Taken_Blocked the user": "Action Taken: Blocked the User",
    "Action_Taken_Ignored it": "Action Taken: Ignored It",
    "Action_Taken_Reported the account": "Action Taken: Reported the Account",
    "Action_Taken_Sought Professional Help": "Action Taken: Sought Professional Help",
    "Action_Taken_Told Friends / Family": "Action Taken: Told Friends / Family",
    "Action_Taken_Took No Action": "Action Taken: Took No Action"
}

def clean_feature_label(raw_feature: str) -> str:
    """Translates an internal pipeline feature name to an accessible user-facing label."""
    if raw_feature in FEATURE_LABEL_MAP:
        return FEATURE_LABEL_MAP[raw_feature]
    # Fallback formatting if an unknown token appears
    cleaned = raw_feature.replace("_Ordinal", "").replace("_Binary", "").replace("_", " ")
    return cleaned

class ShapExplainerManager:
    """
    Manager for TreeExplainer on the Random Forest Classifier.
    Computes local feature contributions for the predicted class.
    Adheres strictly to academic non-causal explanation wording.
    """
    def __init__(self, model):
        self.model = model
        self.explainer = None
        self._init_explainer()

    def _init_explainer(self):
        try:
            logger.info("Initializing SHAP TreeExplainer for primary Random Forest model...")
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP TreeExplainer successfully initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize SHAP TreeExplainer: {e}")
            raise RuntimeError(f"SHAP initialization error: {e}")

    def explain_instance(
        self,
        X_df,
        predicted_class_idx: int,
        predicted_class_name: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Calculates top contributing features for a single transformed observation.
        
        Args:
            X_df: Transformed DataFrame with shape (1, n_features)
            predicted_class_idx: Integer index of predicted class (0..3)
            predicted_class_name: String label of predicted class
            top_k: Number of highest-magnitude contributing features to return
        """
        if self.explainer is None:
            raise RuntimeError("SHAP TreeExplainer is not initialized.")

        # Compute SHAP values for the instance
        # For multiclass RF, shap_values has shape (n_samples, n_features, n_classes)
        shap_values = self.explainer.shap_values(X_df)
        
        if isinstance(shap_values, list):
            # List of (n_samples, n_features) arrays per class
            class_shaps = shap_values[predicted_class_idx][0]
        elif isinstance(shap_values, np.ndarray):
            if shap_values.ndim == 3:
                # Shape (1, 54, 4)
                class_shaps = shap_values[0, :, predicted_class_idx]
            else:
                class_shaps = shap_values[0]
        else:
            raise ValueError(f"Unexpected SHAP values type: {type(shap_values)}")

        feature_names = list(X_df.columns)
        num_features = len(feature_names)

        # Sort indices by absolute SHAP magnitude descending
        sorted_indices = np.argsort(np.abs(class_shaps))[::-1]

        top_contributions = []
        for idx in sorted_indices[:top_k]:
            raw_feature = feature_names[idx]
            val = float(class_shaps[idx])
            direction = "increased" if val > 0 else "decreased"
            friendly_label = clean_feature_label(raw_feature)

            # Strict non-causal explanation text
            if direction == "increased":
                desc = f"The model placed positive analytical weight on {friendly_label} toward predicting '{predicted_class_name}'."
            else:
                desc = f"The model placed countervailing weight on {friendly_label} relative to predicting '{predicted_class_name}'."

            top_contributions.append({
                "feature": friendly_label,
                "raw_feature": raw_feature,
                "shap_value": round(val, 4),
                "direction": direction,
                "description": desc
            })

        return top_contributions
