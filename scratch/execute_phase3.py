import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Matplotlib setup with compatibility check
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

# Ensure models directory is in sys.path so preprocessor can be imported
sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

# Create output directories
os.makedirs(os.path.join('results', 'ml', 'plots'), exist_ok=True)
os.makedirs('models', exist_ok=True)

# 1. Load Data
data_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
df = pd.read_csv(data_path, encoding='utf-8')
print(f"Loaded Phase 2 analytical dataset: {df.shape}")

# 2. Filter out records where target is missing
target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df[target_col].notna() & (df[target_col] != '')
usable_df = df[valid_mask].reset_index(drop=True)

print(f"Total Phase 2 records     : {len(df)}")
print(f"Missing target records    : {(~valid_mask).sum()}")
print(f"Final usable ML records   : {len(usable_df)}")
assert len(usable_df) == 514, f"Expected 514 usable records, got {len(usable_df)}"

# Target classes
classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
idx_to_class = {i: c for i, c in enumerate(classes)}
y = usable_df[target_col].map(class_to_idx).values

# 3. Stratified Train/Test Split (80/20)
train_idx, test_idx = train_test_split(
    np.arange(len(usable_df)),
    test_size=0.20,
    random_state=42,
    stratify=y
)
df_train = usable_df.iloc[train_idx].copy().reset_index(drop=True)
df_test = usable_df.iloc[test_idx].copy().reset_index(drop=True)
y_train = y[train_idx]
y_test = y[test_idx]

print(f"\nTrain Split: {len(df_train)} records (Class distribution: {dict(pd.Series(y_train).value_counts().sort_index())})")
print(f"Test Split : {len(df_test)} records (Class distribution: {dict(pd.Series(y_test).value_counts().sort_index())})")

# 4. Preprocessing
# Scenario B (Leakage-Controlled Primary Model)
prep_b = SurveyFeaturePreprocessor(scenario='B')
prep_b.fit(df_train)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)
print(f"Scenario B feature dimensions: Train {X_train_b.shape}, Test {X_test_b.shape}")

# Scenario A (Full Benchmark)
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)
print(f"Scenario A feature dimensions: Train {X_train_a.shape}, Test {X_test_a.shape}")

# Save preprocessors
joblib.dump(prep_b, os.path.join('models', 'mindsafe_primary_preprocessor.joblib'))
joblib.dump(prep_a, os.path.join('models', 'mindsafe_full_preprocessor.joblib'))
print("Saved preprocessors to models/")

# 5. Baseline Model
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train_b, y_train)
y_pred_dummy = dummy.predict(X_test_b)
dummy_acc = accuracy_score(y_test, y_pred_dummy)
dummy_wf1 = f1_score(y_test, y_pred_dummy, average='weighted', zero_division=0)
dummy_mf1 = f1_score(y_test, y_pred_dummy, average='macro', zero_division=0)
print(f"\nBaseline Dummy (Most Frequent) - Acc: {dummy_acc:.4f}, Weighted F1: {dummy_wf1:.4f}, Macro F1: {dummy_mf1:.4f}")

# 6. Train Models
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

# Save models
joblib.dump(rf_b, os.path.join('models', 'mindsafe_primary_model.joblib'))
joblib.dump(rf_a, os.path.join('models', 'mindsafe_full_benchmark.joblib'))
print("Saved models to models/")

# 7. Cross-Validation (5-Fold Stratified on Training Set)
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores_b = cross_validate(rf_b, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
cv_scores_a = cross_validate(rf_a, X_train_a, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])

cv_results_df = pd.DataFrame([
    {
        'Model': 'Primary Model B (Leakage-Controlled)',
        'CV_Accuracy_Mean': round(cv_scores_b['test_accuracy'].mean(), 4),
        'CV_Accuracy_Std': round(cv_scores_b['test_accuracy'].std(), 4),
        'CV_Weighted_F1_Mean': round(cv_scores_b['test_f1_weighted'].mean(), 4),
        'CV_Weighted_F1_Std': round(cv_scores_b['test_f1_weighted'].std(), 4),
        'CV_Macro_F1_Mean': round(cv_scores_b['test_f1_macro'].mean(), 4),
        'CV_Macro_F1_Std': round(cv_scores_b['test_f1_macro'].std(), 4)
    },
    {
        'Model': 'Full Benchmark Model A (With Q13 & Q14)',
        'CV_Accuracy_Mean': round(cv_scores_a['test_accuracy'].mean(), 4),
        'CV_Accuracy_Std': round(cv_scores_a['test_accuracy'].std(), 4),
        'CV_Weighted_F1_Mean': round(cv_scores_a['test_f1_weighted'].mean(), 4),
        'CV_Weighted_F1_Std': round(cv_scores_a['test_f1_weighted'].std(), 4),
        'CV_Macro_F1_Mean': round(cv_scores_a['test_f1_macro'].mean(), 4),
        'CV_Macro_F1_Std': round(cv_scores_a['test_f1_macro'].std(), 4)
    }
])
cv_results_path = os.path.join('results', 'ml', 'cross_validation_results.csv')
cv_results_df.to_csv(cv_results_path, index=False, encoding='utf-8')
print(f"Saved cross-validation results to: {cv_results_path}")

# 8. Test Set Evaluation & Comparison
metrics_b = {
    'Accuracy': round(accuracy_score(y_test, y_pred_b), 4),
    'Macro_Precision': round(precision_score(y_test, y_pred_b, average='macro', zero_division=0), 4),
    'Macro_Recall': round(recall_score(y_test, y_pred_b, average='macro', zero_division=0), 4),
    'Macro_F1': round(f1_score(y_test, y_pred_b, average='macro', zero_division=0), 4),
    'Weighted_Precision': round(precision_score(y_test, y_pred_b, average='weighted', zero_division=0), 4),
    'Weighted_Recall': round(recall_score(y_test, y_pred_b, average='weighted', zero_division=0), 4),
    'Weighted_F1': round(f1_score(y_test, y_pred_b, average='weighted', zero_division=0), 4)
}

metrics_a = {
    'Accuracy': round(accuracy_score(y_test, y_pred_a), 4),
    'Macro_Precision': round(precision_score(y_test, y_pred_a, average='macro', zero_division=0), 4),
    'Macro_Recall': round(recall_score(y_test, y_pred_a, average='macro', zero_division=0), 4),
    'Macro_F1': round(f1_score(y_test, y_pred_a, average='macro', zero_division=0), 4),
    'Weighted_Precision': round(precision_score(y_test, y_pred_a, average='weighted', zero_division=0), 4),
    'Weighted_Recall': round(recall_score(y_test, y_pred_a, average='weighted', zero_division=0), 4),
    'Weighted_F1': round(f1_score(y_test, y_pred_a, average='weighted', zero_division=0), 4)
}

metrics_dummy = {
    'Accuracy': round(dummy_acc, 4),
    'Macro_Precision': round(precision_score(y_test, y_pred_dummy, average='macro', zero_division=0), 4),
    'Macro_Recall': round(recall_score(y_test, y_pred_dummy, average='macro', zero_division=0), 4),
    'Macro_F1': round(dummy_mf1, 4),
    'Weighted_Precision': round(precision_score(y_test, y_pred_dummy, average='weighted', zero_division=0), 4),
    'Weighted_Recall': round(recall_score(y_test, y_pred_dummy, average='weighted', zero_division=0), 4),
    'Weighted_F1': round(dummy_wf1, 4)
}

model_comp_df = pd.DataFrame([
    {'Model': 'Primary Model (Random Forest)', 'Feature_Scenario': 'Scenario B (Leakage-Controlled)', **metrics_b},
    {'Model': 'Benchmark Model (Random Forest)', 'Feature_Scenario': 'Scenario A (Full Features)', **metrics_a},
    {'Model': 'Baseline (Dummy Classifier)', 'Feature_Scenario': 'Most Frequent Class', **metrics_dummy}
])
model_comp_path = os.path.join('results', 'ml', 'model_comparison.csv')
model_comp_df.to_csv(model_comp_path, index=False, encoding='utf-8')
print(f"Saved model comparison to: {model_comp_path}")

# Classification Report Table for Primary Model B
clf_rep_dict = classification_report(y_test, y_pred_b, target_names=classes, output_dict=True, zero_division=0)
clf_rep_rows = []
for c in classes:
    clf_rep_rows.append({
        'Class': c,
        'Precision': round(clf_rep_dict[c]['precision'], 4),
        'Recall': round(clf_rep_dict[c]['recall'], 4),
        'F1_Score': round(clf_rep_dict[c]['f1-score'], 4),
        'Support': int(clf_rep_dict[c]['support'])
    })
clf_rep_rows.append({
    'Class': 'Macro Average',
    'Precision': round(clf_rep_dict['macro avg']['precision'], 4),
    'Recall': round(clf_rep_dict['macro avg']['recall'], 4),
    'F1_Score': round(clf_rep_dict['macro avg']['f1-score'], 4),
    'Support': int(clf_rep_dict['macro avg']['support'])
})
clf_rep_rows.append({
    'Class': 'Weighted Average',
    'Precision': round(clf_rep_dict['weighted avg']['precision'], 4),
    'Recall': round(clf_rep_dict['weighted avg']['recall'], 4),
    'F1_Score': round(clf_rep_dict['weighted avg']['f1-score'], 4),
    'Support': int(clf_rep_dict['weighted avg']['support'])
})
clf_rep_df = pd.DataFrame(clf_rep_rows)
clf_rep_path = os.path.join('results', 'ml', 'classification_report.csv')
clf_rep_df.to_csv(clf_rep_path, index=False, encoding='utf-8')
print(f"Saved classification report to: {clf_rep_path}")

# 9. Confusion Matrices (Raw & Normalized)
cm_raw_b = confusion_matrix(y_test, y_pred_b, labels=[0, 1, 2, 3])
cm_norm_b = confusion_matrix(y_test, y_pred_b, labels=[0, 1, 2, 3], normalize='true')

cm_rows = []
for i, act_cls in enumerate(classes):
    row = {'Actual_Class': act_cls}
    for j, pred_cls in enumerate(classes):
        row[f'Pred_{pred_cls}_Raw'] = cm_raw_b[i, j]
        row[f'Pred_{pred_cls}_Norm'] = round(cm_norm_b[i, j], 4)
    cm_rows.append(row)
cm_df = pd.DataFrame(cm_rows)
cm_csv_path = os.path.join('results', 'ml', 'confusion_matrix.csv')
cm_df.to_csv(cm_csv_path, index=False, encoding='utf-8')
print(f"Saved confusion matrix CSV to: {cm_csv_path}")

# 10. Feature Importance (Random Forest MDI)
fi = rf_b.feature_importances_
fi_df = pd.DataFrame({
    'Feature': prep_b.feature_names_,
    'Importance': fi
}).sort_values(by='Importance', ascending=False).reset_index(drop=True)
fi_csv_path = os.path.join('results', 'ml', 'feature_importance.csv')
fi_df.to_csv(fi_csv_path, index=False, encoding='utf-8')
print(f"Saved feature importance to: {fi_csv_path}")

# 11. SHAP TreeExplainer & Global Explainability
explainer = shap.TreeExplainer(rf_b)
shap_vals = explainer.shap_values(X_test_b)

# shap_vals has shape (n_samples, n_features, n_classes) in newer shap or list of (n_samples, n_features)
if isinstance(shap_vals, list):
    # list of 4 arrays
    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_vals], axis=0)
    per_class_mean_abs = {classes[i]: np.abs(shap_vals[i]).mean(axis=0) for i in range(4)}
else:
    # 3D array (n_samples, n_features, n_classes)
    mean_abs_shap = np.abs(shap_vals).mean(axis=(0, 2))
    per_class_mean_abs = {classes[i]: np.abs(shap_vals[:, :, i]).mean(axis=0) for i in range(4)}

shap_fi_dict = {
    'Feature': prep_b.feature_names_,
    'Mean_Abs_SHAP_Overall': mean_abs_shap
}
for c in classes:
    shap_fi_dict[f'Mean_Abs_SHAP_{c}'] = per_class_mean_abs[c]

shap_fi_df = pd.DataFrame(shap_fi_dict).sort_values(by='Mean_Abs_SHAP_Overall', ascending=False).reset_index(drop=True)
shap_fi_csv = os.path.join('results', 'ml', 'shap_feature_importance.csv')
shap_fi_df.to_csv(shap_fi_csv, index=False, encoding='utf-8')
print(f"Saved SHAP feature importance to: {shap_fi_csv}")

# 12. Test Predictions Table (NO PII)
test_pred_rows = []
for i in range(len(df_test)):
    test_pred_rows.append({
        'Test_Record_Index': int(test_idx[i]),
        'Actual_Mental_Health_Impact': idx_to_class[y_test[i]],
        'Predicted_Mental_Health_Impact': idx_to_class[y_pred_b[i]],
        'Correct_Prediction': bool(y_test[i] == y_pred_b[i]),
        'Prob_Not_at_all': round(y_proba_b[i, 0], 4),
        'Prob_Slightly': round(y_proba_b[i, 1], 4),
        'Prob_Moderately': round(y_proba_b[i, 2], 4),
        'Prob_Severely': round(y_proba_b[i, 3], 4)
    })
test_pred_df = pd.DataFrame(test_pred_rows)
test_pred_csv = os.path.join('results', 'ml', 'test_predictions.csv')
test_pred_df.to_csv(test_pred_csv, index=False, encoding='utf-8')
print(f"Saved test predictions to: {test_pred_csv}")

# 13. Model Metadata JSON
metadata = {
    'model_name': 'MindSafe Primary Multiclass Classifier',
    'model_type': 'RandomForestClassifier',
    'library': 'scikit-learn',
    'library_version': '1.1.3',
    'training_timestamp': datetime.utcnow().isoformat() + 'Z',
    'target_variable': 'Mental_Health_Impact',
    'target_classes': classes,
    'class_distribution_total': {c: int((usable_df[target_col] == c).sum()) for c in classes},
    'train_sample_size': len(df_train),
    'test_sample_size': len(df_test),
    'train_test_split': {'test_size': 0.20, 'random_state': 42, 'stratified': True},
    'cross_validation': {'method': 'StratifiedKFold', 'n_splits': 5, 'shuffle': True, 'random_state': 42},
    'hyperparameters': {
        'n_estimators': 100,
        'class_weight': 'balanced',
        'random_state': 42,
        'criterion': 'gini',
        'max_depth': None
    },
    'feature_scenario': 'Scenario B (Leakage-Controlled)',
    'feature_count': len(prep_b.feature_names_),
    'feature_list': prep_b.feature_names_,
    'excluded_features': [
        'Timestamp (Metadata/Identifier)',
        'Negative_Emotional_Symptoms (Q13 - Excluded to prevent target leakage)',
        'Emotional_Impact_Severity (Q14 - Excluded to prevent target leakage)',
        'Offensive_Action_Reason (Q8 - Skip sparsity)',
        'Reason_Not_Reported (Q16 - Skip sparsity)'
    ],
    'test_metrics': metrics_b,
    'cv_metrics': {
        'accuracy_mean': round(cv_scores_b['test_accuracy'].mean(), 4),
        'accuracy_std': round(cv_scores_b['test_accuracy'].std(), 4),
        'weighted_f1_mean': round(cv_scores_b['test_f1_weighted'].mean(), 4),
        'weighted_f1_std': round(cv_scores_b['test_f1_weighted'].std(), 4)
    }
}
meta_path = os.path.join('models', 'model_metadata.json')
with open(meta_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

metrics_summary_path = os.path.join('results', 'ml', 'model_metrics.json')
with open(metrics_summary_path, 'w', encoding='utf-8') as f:
    json.dump({'primary_model': metrics_b, 'full_benchmark': metrics_a, 'baseline_dummy': metrics_dummy}, f, indent=2)
print("Saved metadata and model metrics JSON.")

# 14. Visualizations
plots_dir = os.path.join('results', 'ml', 'plots')

# 14.1 Raw Confusion Matrix Plot
fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.matshow(cm_raw_b, cmap='Blues')
fig.colorbar(cax)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(classes, rotation=25, ha='left')
ax.set_yticklabels(classes)
ax.set_xlabel('Predicted Mental Health Impact', fontweight='bold', labelpad=10)
ax.set_ylabel('Actual Mental Health Impact', fontweight='bold')
ax.set_title('Raw Confusion Matrix (Primary Model B)', fontweight='bold', pad=25)
for i in range(4):
    for j in range(4):
        val = cm_raw_b[i, j]
        color = 'white' if val > cm_raw_b.max() / 2 else 'black'
        ax.text(j, i, str(val), ha='center', va='center', color=color, fontweight='bold', fontsize=11)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'confusion_matrix_raw.png'), dpi=300)
plt.close()

# 14.2 Normalized Confusion Matrix Plot
fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.matshow(cm_norm_b, cmap='Greens', vmin=0, vmax=1)
fig.colorbar(cax)
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(classes, rotation=25, ha='left')
ax.set_yticklabels(classes)
ax.set_xlabel('Predicted Mental Health Impact', fontweight='bold', labelpad=10)
ax.set_ylabel('Actual Mental Health Impact', fontweight='bold')
ax.set_title('Normalized Confusion Matrix (Primary Model B)', fontweight='bold', pad=25)
for i in range(4):
    for j in range(4):
        val = cm_norm_b[i, j]
        color = 'white' if val > 0.5 else 'black'
        ax.text(j, i, f"{val:.2f}", ha='center', va='center', color=color, fontweight='bold', fontsize=11)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'confusion_matrix_normalized.png'), dpi=300)
plt.close()

# 14.3 Per-Class F1 Score Chart
fig, ax = plt.subplots(figsize=(7, 4.5))
f1_vals = [clf_rep_dict[c]['f1-score'] for c in classes]
bars = ax.bar(classes, f1_vals, color=['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728'], edgecolor='black', alpha=0.85, width=0.55)
ax.set_ylabel('F1-Score', fontweight='bold')
ax.set_ylim(0, 1.0)
ax.set_title('Per-Class F1-Score (Primary Model B)', fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='--', alpha=0.5)
for b in bars:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 0.03, f"{y:.3f}", ha='center', fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'per_class_f1.png'), dpi=300)
plt.close()

# 14.4 Feature Importance Top 20
fig, ax = plt.subplots(figsize=(9, 7))
top20_fi = fi_df.head(20).iloc[::-1]
bars = ax.barh(top20_fi['Feature'], top20_fi['Importance'], color='#2b5c8f', edgecolor='black', alpha=0.85)
ax.set_xlabel('Random Forest MDI Importance', fontweight='bold')
ax.set_title('Top 20 Feature Importances (Primary Model B)', fontweight='bold', pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.5)
for b in bars:
    w = b.get_width()
    ax.text(w + 0.002, b.get_y() + b.get_height()/2, f"{w:.3f}", va='center', ha='left', fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'feature_importance_top20.png'), dpi=300)
plt.close()

# 14.5 SHAP Bar Plot (Top 20 Features)
fig, ax = plt.subplots(figsize=(9, 7))
top20_shap = shap_fi_df.head(20).iloc[::-1]
bars = ax.barh(top20_shap['Feature'], top20_shap['Mean_Abs_SHAP_Overall'], color='#d9534f', edgecolor='black', alpha=0.85)
ax.set_xlabel('Mean |SHAP Value| (Impact on Model Output Magnitude)', fontweight='bold')
ax.set_title('Top 20 Global SHAP Feature Importances (Primary Model B)', fontweight='bold', pad=15)
ax.grid(axis='x', linestyle='--', alpha=0.5)
for b in bars:
    w = b.get_width()
    ax.text(w + 0.001, b.get_y() + b.get_height()/2, f"{w:.3f}", va='center', ha='left', fontsize=8)
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'shap_bar_plot.png'), dpi=300)
plt.close()

# 14.6 Cross-Validation Performance Comparison
fig, ax = plt.subplots(figsize=(7, 4.5))
cv_models = ['Primary (Scenario B)', 'Benchmark (Scenario A)']
cv_accs = [cv_scores_b['test_accuracy'].mean(), cv_scores_a['test_accuracy'].mean()]
cv_errs = [cv_scores_b['test_accuracy'].std(), cv_scores_a['test_accuracy'].std()]
bars = ax.bar(cv_models, cv_accs, yerr=cv_errs, capsize=5, color=['#2980b9', '#7f8c8d'], edgecolor='black', alpha=0.85, width=0.45)
ax.axhline(dummy_acc, color='red', linestyle='--', label=f'Baseline Dummy ({dummy_acc:.3f})')
ax.set_ylabel('5-Fold CV Accuracy', fontweight='bold')
ax.set_ylim(0, 0.7)
ax.set_title('5-Fold Cross-Validation Accuracy Comparison', fontweight='bold', pad=15)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend()
for b in bars:
    y = b.get_height()
    ax.text(b.get_x() + b.get_width()/2, y + 0.03, f"{y:.3f}", ha='center', fontweight='bold')
plt.tight_layout()
fig.savefig(os.path.join(plots_dir, 'cross_validation_scores.png'), dpi=300)
plt.close()

print(f"All visualization plots saved to: {plots_dir}")

print("\n>>> PHASE 3 ML PIPELINE EXECUTED AND ARTIFACTS SAVED SUCCESSFULLY! <<<")
