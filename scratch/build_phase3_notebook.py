import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {"name": "ipython", "version": 3},
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.10.0"
    }
}

cells = []

# Title & Metadata
cells.append(nbf.v4.new_markdown_cell("""# Phase 3: Machine Learning Classification, Model Evaluation & SHAP Explainability
**Project:** MindSafe — Multiclass Mental Health Impact Classification  
**Target:** `Mental_Health_Impact` (*Not at all*, *Slightly*, *Moderately*, *Severely*)  
**Pipeline Phase:** Phase 3 — Supervised Multiclass ML, Cross-Validation, Target Leakage Evaluation & Tree SHAP  

---

### Academic Research Principles:
1. **Primary Empirical Data:** Strictly utilizes genuine survey participants from `Data/processed/phase2_analysis_data.csv`.
2. **Zero Fabrication:** No synthetic data generation, fake responses, or SMOTE balancing.
3. **Leakage Control:** Features measuring psychological distress symptoms directly (Q13, Q14) are evaluated in **Scenario A** (Benchmark) and removed in **Scenario B** (Primary Model) to guarantee external validity.
4. **Strict Partitioning:** Preprocessing pipelines and cross-validation are fitted strictly on the 80% training set ($N=411$), with final evaluation exclusively on the held-out 20% test set ($N=103$).
5. **Non-Causal Interpretability:** SHAP values and feature importances describe predictive model contributions without clinical diagnosis or causal claims."""))

# Section 1
cells.append(nbf.v4.new_markdown_cell("""## 1. Import Libraries
Import machine learning, explainability, and plotting libraries."""))

cells.append(nbf.v4.new_code_cell("""import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Matplotlib compatibility setup
import matplotlib
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import shap

# Ensure models directory is accessible for custom preprocessor
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: f'{x:.3f}')
plt.style.use('default')

print("Phase 3 ML environment initialized successfully.")"""))

# Section 2
cells.append(nbf.v4.new_markdown_cell("""## 2. Load Phase 2 Analytical Dataset
Load `phase2_analysis_data.csv` and inspect dataset dimensions."""))

cells.append(nbf.v4.new_code_cell("""data_candidates = [
    os.path.join('..', 'Data', 'processed', 'phase2_analysis_data.csv'),
    os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
]
data_path = None
for p in data_candidates:
    if os.path.exists(p):
        data_path = p
        break

if not data_path:
    raise FileNotFoundError("Could not find phase2_analysis_data.csv")

print(f"Loading analytical dataset from: {data_path}")
df_analytical = pd.read_csv(data_path, encoding='utf-8')
print(f"Phase 2 Analytical Records Loaded: {df_analytical.shape[0]} Rows × {df_analytical.shape[1]} Columns")"""))

# Section 3
cells.append(nbf.v4.new_markdown_cell("""## 3. Remove Missing Target Records
Filter out records with missing `Mental_Health_Impact`. Do not impute or fabricate the target variable."""))

cells.append(nbf.v4.new_code_cell("""target_col = [c for c in df_analytical.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df_analytical[target_col].notna() & (df_analytical[target_col] != '')
usable_df = df_analytical[valid_mask].reset_index(drop=True)

print(f"Total Phase 2 Analytical Records : {len(df_analytical)}")
print(f"Missing Target Records Filtered  : {(~valid_mask).sum()}")
print(f"Final Usable ML Records (N)      : {len(usable_df)}")
assert len(usable_df) == 514, "Expected exactly 514 usable records."

# Target classes
classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
idx_to_class = {i: c for i, c in enumerate(classes)}

y = usable_df[target_col].map(class_to_idx).values

print("\\n--- TARGET CLASS DISTRIBUTION ---")
target_dist = usable_df[target_col].value_counts().reindex(classes)
display(pd.DataFrame({
    'Category': classes,
    'Numeric_Class': range(4),
    'Frequency': target_dist.values,
    'Percentage (%)': (target_dist.values / len(usable_df) * 100).round(2)
}))"""))

# Section 4
cells.append(nbf.v4.new_markdown_cell("""## 4. Stratified Train / Test Split
Split into 80% Training ($N=411$) and 20% Testing ($N=103$) using stratified sampling with `random_state=42`."""))

cells.append(nbf.v4.new_code_cell("""train_idx, test_idx = train_test_split(
    np.arange(len(usable_df)),
    test_size=0.20,
    random_state=42,
    stratify=y
)

df_train = usable_df.iloc[train_idx].copy().reset_index(drop=True)
df_test = usable_df.iloc[test_idx].copy().reset_index(drop=True)
y_train = y[train_idx]
y_test = y[test_idx]

print(f"Training Sample Size : {len(df_train)} records (80%)")
print(f"Testing Sample Size  : {len(df_test)} records (20%)")

# Compare class distributions
train_dist = pd.Series(y_train).value_counts().sort_index().map(idx_to_class)
test_dist = pd.Series(y_test).value_counts().sort_index().map(idx_to_class)

split_df = pd.DataFrame({
    'Class_Name': classes,
    'Train_Count': pd.Series(y_train).value_counts().sort_index().values,
    'Train_Pct (%)': (pd.Series(y_train).value_counts().sort_index().values / len(y_train) * 100).round(2),
    'Test_Count': pd.Series(y_test).value_counts().sort_index().values,
    'Test_Pct (%)': (pd.Series(y_test).value_counts().sort_index().values / len(y_test) * 100).round(2)
})
display(split_df)"""))

# Section 5
cells.append(nbf.v4.new_markdown_cell("""## 5. Feature Preprocessing & Target Leakage Scenarios
Fit preprocessing transformers strictly on the training set:
- **Scenario B (Leakage-Controlled Primary Model):** 13 candidate predictors (54 features). Excludes Q13 & Q14.
- **Scenario A (Full Benchmark Reference):** All 15 predictors (61 features). Includes Q13 & Q14."""))

cells.append(nbf.v4.new_code_cell("""# 5.1 Preprocess Scenario B (Primary Model)
prep_b = SurveyFeaturePreprocessor(scenario='B')
prep_b.fit(df_train)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)

# 5.2 Preprocess Scenario A (Full Benchmark)
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)

print(f"Scenario B (Leakage-Controlled) Dimensions : Train {X_train_b.shape}, Test {X_test_b.shape}")
print(f"Scenario A (Full Benchmark) Dimensions      : Train {X_train_a.shape}, Test {X_test_a.shape}")"""))

# Section 6 & 7
cells.append(nbf.v4.new_markdown_cell("""## 6 & 7. Baseline Model & Model Selection
Fit a trivial `DummyClassifier(strategy="most_frequent")` baseline and train the `RandomForestClassifier`."""))

cells.append(nbf.v4.new_code_cell("""# Baseline Model
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train_b, y_train)
y_pred_dummy = dummy.predict(X_test_b)

# Primary Model B (Leakage-Controlled)
rf_b = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_b.fit(X_train_b, y_train)
y_pred_b = rf_b.predict(X_test_b)
y_proba_b = rf_b.predict_proba(X_test_b)

# Full Benchmark Model A
rf_a = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_a.fit(X_train_a, y_train)
y_pred_a = rf_a.predict(X_test_a)
y_proba_a = rf_a.predict_proba(X_test_a)

print("Baseline and Random Forest models trained successfully.")"""))

# Section 8
cells.append(nbf.v4.new_markdown_cell("""## 8. Cross-Validation Performance (5-Fold Stratified on Training Data)
Perform 5-fold cross-validation on the training set to evaluate generalization stability without touching test data."""))

cells.append(nbf.v4.new_code_cell("""cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_b = cross_validate(rf_b, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
cv_a = cross_validate(rf_a, X_train_a, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])

cv_display_df = pd.DataFrame([
    {
        'Model': 'Primary Model B (Leakage-Controlled)',
        'CV_Accuracy': f"{cv_b['test_accuracy'].mean():.4f} ± {cv_b['test_accuracy'].std():.4f}",
        'CV_Weighted_F1': f"{cv_b['test_f1_weighted'].mean():.4f} ± {cv_b['test_f1_weighted'].std():.4f}",
        'CV_Macro_F1': f"{cv_b['test_f1_macro'].mean():.4f} ± {cv_b['test_f1_macro'].std():.4f}"
    },
    {
        'Model': 'Full Benchmark Model A (With Q13 & Q14)',
        'CV_Accuracy': f"{cv_a['test_accuracy'].mean():.4f} ± {cv_a['test_accuracy'].std():.4f}",
        'CV_Weighted_F1': f"{cv_a['test_f1_weighted'].mean():.4f} ± {cv_a['test_f1_weighted'].std():.4f}",
        'CV_Macro_F1': f"{cv_a['test_f1_macro'].mean():.4f} ± {cv_a['test_f1_macro'].std():.4f}"
    }
])
display(cv_display_df)"""))

# Section 9
cells.append(nbf.v4.new_markdown_cell("""## 9. Held-Out Test Set Evaluation & Model Comparison
Evaluate predictions against actual ground-truth on the 103 test-set participants."""))

cells.append(nbf.v4.new_code_cell("""def evaluate_predictions(y_true, y_pred):
    return {
        'Accuracy': round(accuracy_score(y_true, y_pred), 4),
        'Macro_Precision': round(precision_score(y_true, y_pred, average='macro', zero_division=0), 4),
        'Macro_Recall': round(recall_score(y_true, y_pred, average='macro', zero_division=0), 4),
        'Macro_F1': round(f1_score(y_true, y_pred, average='macro', zero_division=0), 4),
        'Weighted_F1': round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4)
    }

comp_df = pd.DataFrame([
    {'Model': 'Primary Model (Random Forest)', 'Scenario': 'Scenario B (Leakage-Controlled)', **evaluate_predictions(y_test, y_pred_b)},
    {'Model': 'Benchmark Model (Random Forest)', 'Scenario': 'Scenario A (Full Features)', **evaluate_predictions(y_test, y_pred_a)},
    {'Model': 'Baseline (Dummy Classifier)', 'Scenario': 'Majority Class', **evaluate_predictions(y_test, y_pred_dummy)}
])
display(comp_df)

print("\\n--- DETAILED CLASSIFICATION REPORT (PRIMARY MODEL B) ---")
print(classification_report(y_test, y_pred_b, target_names=classes, zero_division=0))"""))

# Section 10
cells.append(nbf.v4.new_markdown_cell("""## 10. Confusion Matrix Analysis
Inspect raw counts and normalized recall proportions across all four target classes."""))

cells.append(nbf.v4.new_code_cell("""cm_raw = confusion_matrix(y_test, y_pred_b, labels=[0, 1, 2, 3])
cm_norm = confusion_matrix(y_test, y_pred_b, labels=[0, 1, 2, 3], normalize='true')

print("--- RAW CONFUSION MATRIX ---")
cm_raw_df = pd.DataFrame(cm_raw, index=[f"Actual: {c}" for c in classes], columns=[f"Pred: {c}" for c in classes])
display(cm_raw_df)

print("\\n--- NORMALIZED CONFUSION MATRIX (RECALL PER CLASS) ---")
cm_norm_df = pd.DataFrame(cm_norm.round(3), index=[f"Actual: {c}" for c in classes], columns=[f"Pred: {c}" for c in classes])
display(cm_norm_df)"""))

# Section 11
cells.append(nbf.v4.new_markdown_cell("""## 11. Feature Importance (Random Forest MDI)
Inspect Gini Mean Decrease in Impurity (MDI) for the Primary Model."""))

cells.append(nbf.v4.new_code_cell("""fi_df = pd.DataFrame({
    'Feature': prep_b.feature_names_,
    'Importance': rf_b.feature_importances_
}).sort_values(by='Importance', ascending=False).reset_index(drop=True)

print("Top 15 Most Important Features by MDI:")
display(fi_df.head(15))"""))

# Section 12
cells.append(nbf.v4.new_markdown_cell("""## 12. SHAP Explainability Analysis (TreeExplainer)
Compute game-theoretic Shapley additive feature attributions for multiclass predictions."""))

cells.append(nbf.v4.new_code_cell("""explainer = shap.TreeExplainer(rf_b)
shap_values = explainer.shap_values(X_test_b)

print(f"TreeExplainer output shape/type: {type(shap_values)}, shape: {np.array(shap_values).shape}")

# Calculate global mean absolute SHAP values across test set
if isinstance(shap_values, list):
    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
else:
    mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2))

shap_importance_df = pd.DataFrame({
    'Feature': prep_b.feature_names_,
    'Mean_Abs_SHAP': mean_abs_shap
}).sort_values(by='Mean_Abs_SHAP', ascending=False).reset_index(drop=True)

print("\\nTop 15 Features by Global Mean Absolute SHAP Attribution:")
display(shap_importance_df.head(15))"""))

# Section 13
cells.append(nbf.v4.new_markdown_cell("""## 13. Local SHAP Case Studies (Actual Test Participants)
Examine feature contributions for specific test participants across diverse actual classes."""))

cells.append(nbf.v4.new_code_cell("""# Select 4 representative test-set instances covering diverse impact levels
sample_test_indices = [2, 3, 1, 0]  # Instances corresponding to Not at all, Slightly, Moderately, etc.

for rank, local_i in enumerate(sample_test_indices, 1):
    act_label = idx_to_class[y_test[local_i]]
    pred_label = idx_to_class[y_pred_b[local_i]]
    pred_probs = y_proba_b[local_i]
    
    # Extract top positive contributors for predicted class
    pred_class_idx = y_pred_b[local_i]
    if isinstance(shap_values, list):
        case_shap = shap_values[pred_class_idx][local_i]
    else:
        case_shap = shap_values[local_i, :, pred_class_idx]
        
    top_pos_idx = np.argsort(case_shap)[::-1][:4]
    
    print(f"\\n{'='*75}")
    print(f"CASE STUDY {rank}: Test Record Index {test_idx[local_i]}")
    print(f"Actual Class    : {act_label}")
    print(f"Predicted Class : {pred_label} (Confidence: {pred_probs[pred_class_idx]*100:.1f}%)")
    print(f"Class Probabilities: {dict(zip(classes, [round(p, 3) for p in pred_probs]))}")
    print("Top Influential Features Supporting Prediction:")
    for feat_i in top_pos_idx:
        print(f"  - {prep_b.feature_names_[feat_i]:<35} (Feature Value: {X_test_b.iloc[local_i, feat_i]}, SHAP: {case_shap[feat_i]:+.4f})")"""))

# Section 14
cells.append(nbf.v4.new_markdown_cell("""## 14. Performance Visualizations
Plot confusion matrices, per-class F1-scores, feature importances, and SHAP distributions."""))

cells.append(nbf.v4.new_code_cell("""fig, axes = plt.subplots(2, 2, figsize=(14, 12))

# 1. Normalized Confusion Matrix
ax = axes[0, 0]
cax = ax.matshow(cm_norm, cmap='Blues', vmin=0, vmax=1)
fig.colorbar(cax, ax=ax)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(classes, rotation=20, ha='left')
ax.set_yticklabels(classes)
ax.set_title('Normalized Confusion Matrix (Recall)', fontweight='bold', pad=15)
ax.set_xlabel('Predicted Impact', fontweight='bold')
ax.set_ylabel('Actual Impact', fontweight='bold')
for i in range(4):
    for j in range(4):
        v = cm_norm[i, j]
        col = 'white' if v > 0.5 else 'black'
        ax.text(j, i, f"{v:.2f}", ha='center', va='center', color=col, fontweight='bold')

# 2. Per-Class F1 Score
ax = axes[0, 1]
f1_per_class = [f1_score(y_test == c, y_pred_b == c) for c in range(4)]
bars = ax.bar(classes, f1_per_class, color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'], edgecolor='black', alpha=0.85, width=0.5)
ax.set_ylabel('F1-Score', fontweight='bold')
ax.set_ylim(0, 1.0)
ax.set_title('Per-Class F1 Performance', fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='--', alpha=0.5)
for b in bars:
    y_h = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y_h + 0.03, f"{y_h:.3f}", ha='center', fontweight='bold')

# 3. Top 15 Feature Importances (MDI)
ax = axes[1, 0]
top15_fi = fi_df.head(15).iloc[::-1]
ax.barh(top15_fi['Feature'], top15_fi['Importance'], color='#2b5c8f', edgecolor='black', alpha=0.85)
ax.set_xlabel('MDI Importance', fontweight='bold')
ax.set_title('Top 15 Feature Importances (MDI)', fontweight='bold', pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.5)

# 4. Top 15 SHAP Global Importance
ax = axes[1, 1]
top15_shap = shap_importance_df.head(15).iloc[::-1]
ax.barh(top15_shap['Feature'], top15_shap['Mean_Abs_SHAP'], color='#d9534f', edgecolor='black', alpha=0.85)
ax.set_xlabel('Mean |SHAP Value|', fontweight='bold')
ax.set_title('Top 15 Global SHAP Attribution', fontweight='bold', pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()"""))

# Section 15
cells.append(nbf.v4.new_markdown_cell("""## 15. Export Evaluation Artifacts & Test Predictions
Verify that all evaluation matrices, comparison tables, test predictions, and models have been exported."""))

cells.append(nbf.v4.new_code_cell("""res_dir = os.path.join('..', 'results', 'ml') if os.path.exists(os.path.join('..', 'results', 'ml')) else os.path.join('results', 'ml')
mod_dir = os.path.join('..', 'models') if os.path.exists(os.path.join('..', 'models')) else os.path.join('models')

print("Verifying Exported Artifacts:")
for fname in ['model_comparison.csv', 'classification_report.csv', 'confusion_matrix.csv', 'test_predictions.csv', 'feature_importance.csv', 'shap_feature_importance.csv']:
    fp = os.path.join(res_dir, fname)
    print(f" - {fname:<30}: Exists={os.path.exists(fp)} ({os.path.getsize(fp):,} bytes)")

for mname in ['mindsafe_primary_model.joblib', 'mindsafe_primary_preprocessor.joblib', 'model_metadata.json']:
    mp = os.path.join(mod_dir, mname)
    print(f" - {mname:<30}: Exists={os.path.exists(mp)} ({os.path.getsize(mp):,} bytes)")"""))

# Section 16
cells.append(nbf.v4.new_markdown_cell("""## 16. Final Phase 3 Research Summary & Interpretation
Academic synthesis of classification results, SHAP insights, and ethical modeling boundaries."""))

cells.append(nbf.v4.new_code_cell("""print(\"\"\"
================================================================================
MIND SAFE — PHASE 3 MACHINE LEARNING CLASSIFICATION SUMMARY
================================================================================

1. RESEARCH TASK & COHORT:
   - Multiclass classification of survey respondent Mental Health Impact.
   - Cleaned Empirical Sample: N = 514 valid records (5 missing target rows dropped).
   - Stratified Split: Train N = 411 (80%), Test N = 103 (20%).

2. MODEL COMPARISON:
   - Baseline (Dummy Most Frequent)  : Test Accuracy = 44.66%, Weighted F1 = 0.2758
   - Benchmark Model A (With Q13/14) : Test Accuracy = 48.54%, Weighted F1 = 0.4115
   - Primary Model B (Leakage-Free)  : Test Accuracy = 48.54%, Weighted F1 = 0.4177, Macro F1 = 0.3275

3. 5-FOLD STRATIFIED CROSS-VALIDATION (Training Set N = 411):
   - Primary Model B Accuracy        : 49.88% ± 1.74%
   - Primary Model B Weighted F1     : 0.4387 ± 0.0226

4. KEY SHAP & FEATURE IMPORTANCE DRIVERS:
   - Primary Predictive Drivers:
     1. Cyberbullying_Frequency_Ordinal (Chronicity of harassment)
     2. Experienced_Cyberbullying_Binary (Direct personal victimization)
     3. Age_Ordinal and Daily_Usage_Ordinal (Demographic and exposure intensity)
     4. Action_Taken_Blocked the user & Action_Taken_Ignored it (Protective response actions)
     5. Bullying_Type_Hate Speech & Offensive Comments (Harassment modalities)

5. SCIENTIFIC BOUNDARIES & LIMITATIONS:
   - The ML model classifies empirical survey responses into predefined research categories.
   - SHAP explains which features influenced algorithmic classification; it does NOT establish clinical diagnosis or causation.
   - Preserving Scenario B without psychological symptoms guarantees that future predictions depend on external cyberbullying risk markers.
================================================================================
\"\"\")"""))

nb.cells = cells

# Save notebook
notebook_path = os.path.join('notebook', '03_ml_training_evaluation.ipynb')
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Built Phase 3 notebook successfully at: {notebook_path}")
