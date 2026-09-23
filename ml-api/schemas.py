from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class AssessmentPayload(BaseModel):
    """
    Standardized questionnaire input containing the 13 Scenario B predictor features.
    Accepts strings or lists (for multiselect fields) and flexible key aliases.
    """
    age: Optional[str] = Field(None, description="Age group (e.g., '18–22', 'Below 18', '23–30', 'Above 30')")
    gender: Optional[str] = Field(None, description="Gender identity (e.g., 'Female', 'Male', 'Non-binary', 'Prefer not to say')")
    platforms: Optional[Union[str, List[str]]] = Field(None, description="Platforms used regularly (Select all that apply)")
    usage: Optional[str] = Field(None, description="Daily social media usage (e.g., 'Less than 1 hour', '1–3 hours', '3–5 hours', 'More than 5 hours')")
    q5_exp: Optional[str] = Field(None, description="Experienced cyberbullying personally ('Yes' or 'No')")
    q6_wit: Optional[str] = Field(None, description="Witnessed cyberbullying ('Yes' or 'No')")
    q7_post: Optional[str] = Field(None, description="Posted hurtful/offensive content online ('No', 'Not Sure', 'Yes')")
    q9_types: Optional[Union[str, List[str]]] = Field(None, description="Types of cyberbullying observed or experienced (Select all that apply)")
    q10_plat: Optional[str] = Field(None, description="Platform where incident occurred ('Instagram', 'WhatsApp', 'Facebook', 'YouTube', 'Others')")
    q11_freq: Optional[str] = Field(None, description="Frequency of cyberbullying encounters ('Never', 'Rarely', 'Sometimes', 'Often', 'Very Often')")
    q15_help: Optional[Union[str, List[str]]] = Field(None, description="Did you seek help (Select all that apply)")
    q17_area: Optional[str] = Field(None, description="Context area of harassment ('Friends Circle', 'Social Media Community', 'Workplace', etc.)")
    q18_act: Optional[Union[str, List[str]]] = Field(None, description="Action taken after incident (Select all that apply)")

    class Config:
        extra = "allow"

class PredictRequest(BaseModel):
    assessment: Dict[str, Any] = Field(..., description="Map of survey question responses")

class FeatureContribution(BaseModel):
    feature: str = Field(..., description="Human-readable feature label")
    raw_feature: str = Field(..., description="Internal encoded feature name")
    shap_value: float = Field(..., description="SHAP attribution value for the predicted class")
    direction: str = Field(..., description="'increased' or 'decreased' relative to class probability")
    description: str = Field(..., description="Carefully worded explanation adhering to non-causal standard")

class PredictionDetail(BaseModel):
    predicted_class: str = Field(..., alias="class", description="Predicted mental health impact class")
    predicted_class_index: int = Field(..., description="Zero-based class index (0 to 3)")
    probabilities: Dict[str, float] = Field(..., description="Model class probability estimates across the 4 classes")

    class Config:
        populate_by_name = True

class ExplanationDetail(BaseModel):
    top_features: List[FeatureContribution] = Field(..., description="Top contributing features calculated via SHAP TreeExplainer")
    method: str = Field("SHAP TreeExplainer (Additive Feature Attributions)", description="Explainability method used")
    note: str = Field("SHAP values quantify model decision weights for this response pattern and do not indicate clinical causation.", description="Methodological note")

class PredictResponse(BaseModel):
    success: bool = True
    model_name: str = "MindSafe Primary Random Forest Classifier"
    model_version: str = "1.0.0-ScenarioB"
    prediction: PredictionDetail
    explanation: ExplanationDetail
    disclaimer: str = "This is an analytical result from the project ML model and is not a medical diagnosis."

class HealthResponse(BaseModel):
    status: str
    connected: bool
    model_loaded: bool
    preprocessor_loaded: bool
    model_version: str
    target_classes: List[str]
    feature_count: int
    test_metrics: Dict[str, Any]
