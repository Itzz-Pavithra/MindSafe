import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import shap

# Ensure root directory in sys.path
sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

print("==================================================")
print("PHASE 3: MACHINE LEARNING PIPELINE REGENERATION")
print("==================================================")

# 1. Output directories
os.makedirs(os.path.join('results', 'ml', 'plots'), exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs(os.path.join('Data', 'processed'), exist_ok=True)

# 2. Load Phase 2 analytical dataset
data_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
df = pd.read_csv(data_path, encoding='utf-8')
print(f"Loaded Phase 2 analytical dataset: {df.shape}")

target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df[target_col].notna() & (df[target_col] != '')
usable_df = df[valid_mask].reset_index(drop=True)
N_total = len(usable_df)
print(f"Total usable records for ML: {N_total}")

classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
idx_to_class = {i: c for i, c in enumerate(classes)}
y = usable_df[target_col].map(class_to_idx).values

# 3. 80/20 Stratified Train/Test Split (random_state=42)
train_idx, test_idx = train_test_split(
    np.arange(N_total),
    test_size=0.20,
    random_state=42,
    stratify=y
)

df_train = usable_df.iloc[train_idx].copy().reset_index(drop=True)
df_test = usable_df.iloc[test_idx].copy().reset_index(drop=True)
y_train = y[train_idx]
y_test = y[test_idx]

print(f"\n--- STRATIFIED TRAIN/TEST SPLIT (80/20, random_state=42) ---")
print(f"Training instances (N_train) : {len(df_train)} ({len(df_train)/N_total*100:.1f}%)")
print(f"Testing instances  (N_test)  : {len(df_test)} ({len(df_test)/N_total*100:.1f}%)")

print("\nClass distribution in Training Set:")
for c, idx in class_to_idx.items():
    cnt = (y_train == idx).sum()
    print(f"  {c:12s}: {cnt:4d} ({cnt/len(y_train)*100:.2f}%)")

print("\nClass distribution in Testing Set:")
for c, idx in class_to_idx.items():
    cnt = (y_test == idx).sum()
    print(f"  {c:12s}: {cnt:4d} ({cnt/len(y_test)*100:.2f}%)")

# 4. Fit Preprocessors STRICTLY on Training Set
print("\nFitting SurveyFeaturePreprocessor (Scenario B: Leakage-Controlled) on training set only...")
prep_b = SurveyFeaturePreprocessor(scenario='B')
prep_b.fit(df_train)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)

feature_names_b = prep_b.feature_names_
print(f"Scenario B feature count: {len(feature_names_b)}")

# Save Scenario B preprocessor
joblib.dump(prep_b, os.path.join('models', 'mindsafe_primary_preprocessor.joblib'))

# Fit Scenario A Benchmark Preprocessor
print("Fitting SurveyFeaturePreprocessor (Scenario A: Full Benchmark) on training set only...")
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)
feature_names_a = prep_a.feature_names_
print(f"Scenario A feature count: {len(feature_names_a)}")
joblib.dump(prep_a, os.path.join('models', 'mindsafe_full_preprocessor.joblib'))

# Save train/test partitions
for out_dir in [os.path.join('Data', 'processed'), 'results']:
    X_train_b.to_csv(os.path.join(out_dir, 'X_train.csv'), index=False, encoding='utf-8')
    X_test_b.to_csv(os.path.join(out_dir, 'X_test.csv'), index=False, encoding='utf-8')
    pd.DataFrame({'Mental_Health_Impact': y_train}).to_csv(os.path.join(out_dir, 'y_train.csv'), index=False, encoding='utf-8')
    pd.DataFrame({'Mental_Health_Impact': y_test}).to_csv(os.path.join(out_dir, 'y_test.csv'), index=False, encoding='utf-8')

# 5. Hyperparameter Tuning on Training Data via 5-Fold Stratified CV
print("\n--- HYPERPARAMETER TUNING (Random Forest on 5-Fold CV, Training Set Only) ---")
cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

param_grid = {
    'n_estimators': [100, 200],
    'max_depth': [None, 10, 15],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'class_weight': ['balanced', 'balanced_subsample']
}

rf_base = RandomForestClassifier(random_state=42)
grid_search = GridSearchCV(
    rf_base,
    param_grid,
    cv=cv5,
    scoring='f1_macro',
    n_jobs=-1,
    verbose=0
)
grid_search.fit(X_train_b, y_train)
best_rf_params = grid_search.best_params_
best_cv_score = grid_search.best_score_
print(f"Best RF Parameters: {best_rf_params}")
print(f"Best RF 5-Fold CV Macro F1: {best_cv_score:.4f}")

# 6. Model Benchmark Evaluation on 5-Fold Stratified CV (Training Data)
print("\n--- 5-FOLD STRATIFIED CROSS-VALIDATION ON TRAINING SET ---")

candidate_models = {
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest (Default balanced)': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'Random Forest (Tuned)': RandomForestClassifier(**best_rf_params, random_state=42),
    'Dummy Classifier': DummyClassifier(strategy='most_frequent')
}

scoring_metrics = ['accuracy', 'f1_macro', 'f1_weighted', 'precision_macro', 'recall_macro']

cv_summary_rows = []
for name, model in candidate_models.items():
    cv_res = cross_validate(model, X_train_b, y_train, cv=cv5, scoring=scoring_metrics)
    cv_summary_rows.append({
        'Model': name,
        'CV_Accuracy_Mean': round(np.mean(cv_res['test_accuracy']), 4),
        'CV_Accuracy_Std': round(np.std(cv_res['test_accuracy']), 4),
        'CV_Macro_F1_Mean': round(np.mean(cv_res['test_f1_macro']), 4),
        'CV_Macro_F1_Std': round(np.std(cv_res['test_f1_macro']), 4),
        'CV_Weighted_F1_Mean': round(np.mean(cv_res['test_f1_weighted']), 4),
        'CV_Weighted_F1_Std': round(np.std(cv_res['test_f1_weighted']), 4),
        'CV_Macro_Precision_Mean': round(np.mean(cv_res['test_precision_macro']), 4),
        'CV_Macro_Recall_Mean': round(np.mean(cv_res['test_recall_macro']), 4)
    })
    print(f"  {name:32s}: Acc = {np.mean(cv_res['test_accuracy']):.4f} ± {np.std(cv_res['test_accuracy']):.4f} | Macro F1 = {np.mean(cv_res['test_f1_macro']):.4f} ± {np.std(cv_res['test_f1_macro']):.4f}")

cv_df = pd.DataFrame(cv_summary_rows)
cv_df.to_csv(os.path.join('results', 'ml', 'cross_validation_results.csv'), index=False, encoding='utf-8')

# 7. Final Model Selection & Evaluation on Untouched Test Set
# Standard MindSafe models to evaluate and compare on held-out test set
eval_models = {
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest': RandomForestClassifier(**best_rf_params, random_state=42),
    'Dummy Classifier': DummyClassifier(strategy='most_frequent')
}

test_comparison_rows = []
detailed_comparison_rows = []
confusion_matrices_dict = {}

print("\n--- FINAL TEST SET EVALUATION (N = 263, UNTOUCHED) ---")

for name, model in eval_models.items():
    model.fit(X_train_b, y_train)
    y_pred = model.predict(X_test_b)
    
    acc = accuracy_score(y_test, y_pred)
    mp = precision_score(y_test, y_pred, average='macro', zero_division=0)
    mr = recall_score(y_test, y_pred, average='macro', zero_division=0)
    mf1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    wp = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    wr = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    wf1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
    confusion_matrices_dict[name] = cm
    
    test_comparison_rows.append({
        'Model': name,
        'Accuracy': round(acc, 4),
        'Macro Precision': round(mp, 4),
        'Macro Recall': round(mr, 4),
        'Macro F1': round(mf1, 4),
        'Weighted Precision': round(wp, 4),
        'Weighted Recall': round(wr, 4),
        'Weighted F1': round(wf1, 4)
    })
    
    # Matching CV metrics for detailed table
    cv_match = cv_df[cv_df['Model'].str.startswith(name.split()[0])]
    acc_mean = cv_match['CV_Accuracy_Mean'].values[0] if len(cv_match) > 0 else acc
    acc_std = cv_match['CV_Accuracy_Std'].values[0] if len(cv_match) > 0 else 0.0
    f1_mean = cv_match['CV_Weighted_F1_Mean'].values[0] if len(cv_match) > 0 else wf1
    f1_std = cv_match['CV_Weighted_F1_Std'].values[0] if len(cv_match) > 0 else 0.0
    
    detailed_comparison_rows.append({
        'Model': name,
        'Accuracy': round(acc, 4),
        'Macro Precision': round(mp, 4),
        'Macro Recall': round(mr, 4),
        'Macro F1': round(mf1, 4),
        'Weighted Precision': round(wp, 4),
        'Weighted Recall': round(wr, 4),
        'Weighted F1': round(wf1, 4),
        'CV_Accuracy_Mean': acc_mean,
        'CV_Accuracy_Std': acc_std,
        'CV_Weighted_F1_Mean': f1_mean,
        'CV_Weighted_F1_Std': f1_std
    })
    
    print(f"  {name:30s}: Acc = {acc*100:.2f}%, Macro F1 = {mf1:.4f}, Weighted F1 = {wf1:.4f}")

# Also train & evaluate Scenario A Benchmark Model (Random Forest on 61 features)
rf_bench = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_bench.fit(X_train_a, y_train)
y_pred_a = rf_bench.predict(X_test_a)
acc_a = accuracy_score(y_test, y_pred_a)
mf1_a = f1_score(y_test, y_pred_a, average='macro', zero_division=0)
wf1_a = f1_score(y_test, y_pred_a, average='weighted', zero_division=0)
print(f"  Benchmark Scenario A (61 feat): Acc = {acc_a*100:.2f}%, Macro F1 = {mf1_a:.4f}, Weighted F1 = {wf1_a:.4f}")

# Save Benchmark Model
joblib.dump(rf_bench, os.path.join('models', 'mindsafe_full_benchmark.joblib'))

# Save Model Comparison Tables
comp_df = pd.DataFrame(test_comparison_rows)
comp_df.to_csv(os.path.join('results', 'ml', 'model_comparison.csv'), index=False, encoding='utf-8')

detailed_df = pd.DataFrame(detailed_comparison_rows)
detailed_df.to_csv(os.path.join('results', 'ml', 'model_comparison_detailed.csv'), index=False, encoding='utf-8')

# Save all models confusion matrices
all_cm_rows = []
for mname, cm_arr in confusion_matrices_dict.items():
    for true_idx, true_cls in enumerate(classes):
        row_dict = {'Model': mname, 'Actual_Class': true_cls}
        for pred_idx, pred_cls in enumerate(classes):
            row_dict[f'Pred_{pred_cls}'] = cm_arr[true_idx, pred_idx]
        all_cm_rows.append(row_dict)
all_cm_df = pd.DataFrame(all_cm_rows)
all_cm_df.to_csv(os.path.join('results', 'ml', 'all_models_confusion_matrices.csv'), index=False, encoding='utf-8')

# Save individual confusion matrices
for mname, cm_arr in confusion_matrices_dict.items():
    slug = mname.lower().replace(' ', '_').replace('(', '').replace(')', '')
    cm_sub_df = pd.DataFrame(cm_arr, index=classes, columns=classes)
    cm_sub_df.to_csv(os.path.join('results', 'ml', f'confusion_matrix_{slug}.csv'), encoding='utf-8')

# 8. Primary Model: Random Forest
primary_rf = eval_models['Random Forest']
joblib.dump(primary_rf, os.path.join('models', 'mindsafe_primary_model.joblib'))

# Evaluate primary model in full detail
y_pred_primary = primary_rf.predict(X_test_b)
y_proba_primary = primary_rf.predict_proba(X_test_b)

primary_acc = accuracy_score(y_test, y_pred_primary)
primary_mp = precision_score(y_test, y_pred_primary, average='macro', zero_division=0)
primary_mr = recall_score(y_test, y_pred_primary, average='macro', zero_division=0)
primary_mf1 = f1_score(y_test, y_pred_primary, average='macro', zero_division=0)
primary_wp = precision_score(y_test, y_pred_primary, average='weighted', zero_division=0)
primary_wr = recall_score(y_test, y_pred_primary, average='weighted', zero_division=0)
primary_wf1 = f1_score(y_test, y_pred_primary, average='weighted', zero_division=0)

primary_cm = confusion_matrix(y_test, y_pred_primary, labels=[0, 1, 2, 3])
primary_cm_df = pd.DataFrame(primary_cm, index=classes, columns=classes)
primary_cm_df.to_csv(os.path.join('results', 'ml', 'confusion_matrix.csv'), encoding='utf-8')

# Per-class classification report
clf_dict = classification_report(y_test, y_pred_primary, target_names=classes, output_dict=True, zero_division=0)
clf_rows = []
for c in classes:
    clf_rows.append({
        'Class': c,
        'Precision': round(clf_dict[c]['precision'], 4),
        'Recall': round(clf_dict[c]['recall'], 4),
        'F1-Score': round(clf_dict[c]['f1-score'], 4),
        'Support': int(clf_dict[c]['support'])
    })
clf_rows.append({
    'Class': 'Macro Avg',
    'Precision': round(clf_dict['macro avg']['precision'], 4),
    'Recall': round(clf_dict['macro avg']['recall'], 4),
    'F1-Score': round(clf_dict['macro avg']['f1-score'], 4),
    'Support': int(clf_dict['macro avg']['support'])
})
clf_rows.append({
    'Class': 'Weighted Avg',
    'Precision': round(clf_dict['weighted avg']['precision'], 4),
    'Recall': round(clf_dict['weighted avg']['recall'], 4),
    'F1-Score': round(clf_dict['weighted avg']['f1-score'], 4),
    'Support': int(clf_dict['weighted avg']['support'])
})
clf_df = pd.DataFrame(clf_rows)
clf_df.to_csv(os.path.join('results', 'ml', 'classification_report.csv'), index=False, encoding='utf-8')

print("\n--- PRIMARY RANDOM FOREST CLASSIFICATION REPORT ---")
print(clf_df.to_string(index=False))

# Save test predictions
pred_df = pd.DataFrame({
    'True_Class': [idx_to_class[i] for i in y_test],
    'Predicted_Class': [idx_to_class[i] for i in y_pred_primary],
    'Correct': [t == p for t, p in zip(y_test, y_pred_primary)]
})
for i, c in enumerate(classes):
    pred_df[f'Prob_{c}'] = y_proba_primary[:, i].round(4)
pred_df.to_csv(os.path.join('results', 'ml', 'test_predictions.csv'), index=False, encoding='utf-8')

# Gini feature importances
gini_importances = pd.DataFrame({
    'Feature': feature_names_b,
    'Importance': primary_rf.feature_importances_
}).sort_values(by='Importance', ascending=False).reset_index(drop=True)
gini_importances.to_csv(os.path.join('results', 'ml', 'feature_importance.csv'), index=False, encoding='utf-8')

# 9. Tree SHAP Analysis
print("\n--- COMPUTING TREE SHAP EXPLANATIONS ---")
explainer = shap.TreeExplainer(primary_rf)
shap_values = explainer.shap_values(X_test_b)

if isinstance(shap_values, list):
    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
    per_class_shap = [np.abs(shap_values[i]).mean(axis=0) for i in range(len(classes))]
elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
    mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2))
    per_class_shap = [np.abs(shap_values[:, :, i]).mean(axis=0) for i in range(len(classes))]
else:
    raise ValueError(f"Unexpected shap_values format: {type(shap_values)}")

shap_imp_df = pd.DataFrame({
    'Feature': feature_names_b,
    'Mean_Abs_SHAP': mean_abs_shap
}).sort_values(by='Mean_Abs_SHAP', ascending=False).reset_index(drop=True)

for i, c in enumerate(classes):
    feat_order_map = dict(zip(feature_names_b, per_class_shap[i]))
    shap_imp_df[f'Mean_Abs_SHAP_{c}'] = shap_imp_df['Feature'].map(feat_order_map)

shap_imp_df.to_csv(os.path.join('results', 'ml', 'shap_feature_importance.csv'), index=False, encoding='utf-8')
print("Top 15 Global Features by Mean Absolute SHAP:")
for idx, r in shap_imp_df.head(15).iterrows():
    print(f"  {idx+1:2d}. {r['Feature']:35s}: {r['Mean_Abs_SHAP']:.4f}")

# 10. Save Model Metrics JSON & Model Metadata JSON
rf_cv_match = cv_df[cv_df['Model'] == 'Random Forest (Tuned)']
metrics_json = {
    'Accuracy': round(primary_acc, 4),
    'Macro_Precision': round(primary_mp, 4),
    'Macro_Recall': round(primary_mr, 4),
    'Macro_F1': round(primary_mf1, 4),
    'Weighted_Precision': round(primary_wp, 4),
    'Weighted_Recall': round(primary_wr, 4),
    'Weighted_F1': round(primary_wf1, 4),
    'Cross_Validation': {
        'n_splits': 5,
        'accuracy_mean': float(rf_cv_match['CV_Accuracy_Mean'].values[0]),
        'accuracy_std': float(rf_cv_match['CV_Accuracy_Std'].values[0]),
        'macro_f1_mean': float(rf_cv_match['CV_Macro_F1_Mean'].values[0]),
        'macro_f1_std': float(rf_cv_match['CV_Macro_F1_Std'].values[0]),
        'weighted_f1_mean': float(rf_cv_match['CV_Weighted_F1_Mean'].values[0]),
        'weighted_f1_std': float(rf_cv_match['CV_Weighted_F1_Std'].values[0])
    }
}
with open(os.path.join('results', 'ml', 'model_metrics.json'), 'w', encoding='utf-8') as f:
    json.dump(metrics_json, f, indent=2)

# Full model metadata
class_dist_dict = {c: int((y == idx).sum()) for c, idx in class_to_idx.items()}
model_metadata = {
    "model_name": "MindSafe Primary Multiclass Classifier",
    "model_type": "RandomForestClassifier",
    "library": "scikit-learn",
    "library_version": "1.1.3",
    "training_timestamp": datetime.utcnow().isoformat() + "Z",
    "target_variable": "Mental_Health_Impact",
    "target_classes": classes,
    "class_distribution_total": class_dist_dict,
    "train_sample_size": len(df_train),
    "test_sample_size": len(df_test),
    "train_test_split": {
        "test_size": 0.2,
        "random_state": 42,
        "stratified": True
    },
    "cross_validation": {
        "method": "StratifiedKFold",
        "n_splits": 5,
        "shuffle": True,
        "random_state": 42
    },
    "hyperparameters": {
        "n_estimators": best_rf_params.get('n_estimators', 100),
        "class_weight": best_rf_params.get('class_weight', 'balanced'),
        "random_state": 42,
        "criterion": "gini",
        "max_depth": best_rf_params.get('max_depth', None),
        "min_samples_split": best_rf_params.get('min_samples_split', 2),
        "min_samples_leaf": best_rf_params.get('min_samples_leaf', 1)
    },
    "feature_scenario": "Scenario B (Leakage-Controlled)",
    "feature_count": len(feature_names_b),
    "feature_list": feature_names_b,
    "excluded_features": [
        "Timestamp (Metadata/Identifier)",
        "Negative_Emotional_Symptoms (Q13 - Excluded to prevent target leakage)",
        "Emotional_Impact_Severity (Q14 - Excluded to prevent target leakage)",
        "Offensive_Action_Reason (Q8 - Skip sparsity)",
        "Reason_Not_Reported (Q16 - Skip sparsity)"
    ],
    "test_metrics": {
        "Accuracy": round(primary_acc, 4),
        "Macro_Precision": round(primary_mp, 4),
        "Macro_Recall": round(primary_mr, 4),
        "Macro_F1": round(primary_mf1, 4),
        "Weighted_Precision": round(primary_wp, 4),
        "Weighted_Recall": round(primary_wr, 4),
        "Weighted_F1": round(primary_wf1, 4)
    },
    "cv_metrics": {
        "accuracy_mean": float(rf_cv_match['CV_Accuracy_Mean'].values[0]),
        "accuracy_std": float(rf_cv_match['CV_Accuracy_Std'].values[0]),
        "macro_f1_mean": float(rf_cv_match['CV_Macro_F1_Mean'].values[0]),
        "macro_f1_std": float(rf_cv_match['CV_Macro_F1_Std'].values[0]),
        "weighted_f1_mean": float(rf_cv_match['CV_Weighted_F1_Mean'].values[0]),
        "weighted_f1_std": float(rf_cv_match['CV_Weighted_F1_Std'].values[0])
    }
}
with open(os.path.join('models', 'model_metadata.json'), 'w', encoding='utf-8') as f:
    json.dump(model_metadata, f, indent=2)

print("Saved model_metadata.json and model_metrics.json!")

# 11. Plot Generation
print("\n--- GENERATING ML RESEARCH PLOTS ---")

# Plot 1: Model Comparison Bar Chart
fig, ax = plt.subplots(figsize=(10, 6))
comp_plot_df = comp_df.melt(id_vars=['Model'], value_vars=['Accuracy', 'Macro F1', 'Weighted F1'], var_name='Metric', value_name='Score')
sns.barplot(data=comp_plot_df, x='Model', y='Score', hue='Metric', ax=ax, palette=['#601D49', '#BD5579', '#EA9D9D'])
ax.set_title(f'Machine Learning Model Comparison on Held-Out Test Set (N = {len(df_test):,})', fontsize=12, fontweight='bold')
ax.set_ylabel('Score (0.0 to 1.0)')
ax.set_ylim(0, 1.0)
ax.tick_params(axis='x', rotation=15)
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'model_comparison_bar_chart.png'), dpi=300)
plt.close()

# Plot 2: Raw Confusion Matrix
fig, ax = plt.subplots(figsize=(7, 6))
sns.heatmap(primary_cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax)
ax.set_title(f'Primary Random Forest: Raw Confusion Matrix (Test Set N = {len(df_test):,})', fontsize=11, fontweight='bold')
ax.set_ylabel('True Label')
ax.set_xlabel('Predicted Label')
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'confusion_matrix_raw.png'), dpi=300)
plt.close()

# Plot 3: Normalized Confusion Matrix
fig, ax = plt.subplots(figsize=(7, 6))
cm_norm = primary_cm.astype('float') / primary_cm.sum(axis=1)[:, np.newaxis]
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax)
ax.set_title('Primary Random Forest: Normalized Confusion Matrix', fontsize=11, fontweight='bold')
ax.set_ylabel('True Label')
ax.set_xlabel('Predicted Label')
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'confusion_matrix_normalized.png'), dpi=300)
plt.close()

# Plot 4: 5-Fold Cross-Validation Scores
fig, ax = plt.subplots(figsize=(9, 5))
cv_plot_models = [r['Model'] for r in cv_summary_rows if not r['Model'].startswith('Random Forest (Default')]
cv_means = [r['CV_Accuracy_Mean'] for r in cv_summary_rows if not r['Model'].startswith('Random Forest (Default')]
cv_stds = [r['CV_Accuracy_Std'] for r in cv_summary_rows if not r['Model'].startswith('Random Forest (Default')]
y_pos = np.arange(len(cv_plot_models))
ax.barh(y_pos, cv_means, xerr=cv_stds, align='center', alpha=0.8, color='#BD5579', ecolor='#601D49', capsize=5)
ax.set_yticks(y_pos)
ax.set_yticklabels(cv_plot_models)
ax.set_xlabel('Mean Accuracy (5-Fold Stratified CV)')
ax.set_title(f'5-Fold Cross-Validation Performance (Training Set N = {len(df_train):,})', fontsize=11, fontweight='bold')
ax.set_xlim(0, 1.0)
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'cross_validation_scores.png'), dpi=300)
plt.close()

# Plot 5: Top 20 Gini Feature Importance
fig, ax = plt.subplots(figsize=(10, 8))
top20_gini = gini_importances.head(20)
sns.barplot(data=top20_gini, y='Feature', x='Importance', ax=ax, palette='mako')
ax.set_title('Top 20 Features by Gini Impurity Importance (Primary Random Forest)', fontsize=11, fontweight='bold')
ax.set_xlabel('Feature Importance')
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'feature_importance_top20.png'), dpi=300)
plt.close()

# Plot 6: Per-Class F1 Score
fig, ax = plt.subplots(figsize=(7, 5))
per_class_f1s = [clf_dict[c]['f1-score'] for c in classes]
sns.barplot(x=classes, y=per_class_f1s, ax=ax, palette='rocket')
ax.set_title(f'Per-Class F1-Score (Primary Random Forest, Test Set N = {len(df_test):,})', fontsize=11, fontweight='bold')
ax.set_ylabel('F1-Score')
ax.set_ylim(0, 1.0)
for p in ax.patches:
    ax.annotate(f"{p.get_height():.3f}",
                (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                ha='center', va='center', color='white', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'per_class_f1.png'), dpi=300)
plt.close()

# Plot 7: Top 15 SHAP Global Importance Bar Plot
fig, ax = plt.subplots(figsize=(10, 7))
top15_shap = shap_imp_df.head(15)
sns.barplot(data=top15_shap, y='Feature', x='Mean_Abs_SHAP', ax=ax, palette='viridis')
ax.set_title(f'Top 15 Features by Mean Absolute SHAP Value (Test Set N = {len(df_test):,})', fontsize=11, fontweight='bold')
ax.set_xlabel('Mean |SHAP Value| (Average Analytical Impact across Classes)')
plt.tight_layout()
plt.savefig(os.path.join('results', 'ml', 'plots', 'shap_bar_plot.png'), dpi=300)
plt.close()

print("\n>>> ALL PHASE 3 ML MODELS, METRICS, SHAP, AND PLOTS GENERATED SUCCESSFULLY! <<<")
