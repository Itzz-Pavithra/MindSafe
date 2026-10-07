import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
if not hasattr(matplotlib.rcParams, '_get'):
    matplotlib.rcParams._get = matplotlib.rcParams.get
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import shap

sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

print("==================================================")
print("GENERATING IEEE-STANDARD PHASE 3 EXPERIMENTS")
print("==================================================")

# 1. Output directories
for d in [os.path.join('results', 'ml', 'plots'), os.path.join('notebook', 'results', 'ml', 'plots')]:
    os.makedirs(d, exist_ok=True)

# 2. Load cleaned analytical dataset (N = 1,514)
df_clean = pd.read_csv('Data/processed/cleaned_survey_data.csv', encoding='utf-8')
target_col = [c for c in df_clean.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df_clean[target_col].notna() & (df_clean[target_col] != '')
usable_df = df_clean[valid_mask].reset_index(drop=True)
N_total = len(usable_df)
print(f"Loaded analytical dataset: N = {N_total}")
assert N_total == 1514, f"Expected 1514 records, got {N_total}"

classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
y = usable_df[target_col].map(class_to_idx).values

# 3. Stratified 80/20 train/test split (random_state=42)
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

print(f"Training Set: N = {len(df_train)} (80.0%)")
print(f"Testing Set:  N = {len(df_test)} (20.0%)")
assert len(df_train) == 1211
assert len(df_test) == 303
assert len(df_train) + len(df_test) == 1514

# 4. Feature preprocessing fitted STRICTLY on training data
# Scenario B (Leakage-Controlled): 54 features
prep_b = SurveyFeaturePreprocessor(scenario='B')
prep_b.fit(df_train)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)
feature_names_b = prep_b.feature_names_
print(f"Scenario B Feature Count: {len(feature_names_b)}")
assert len(feature_names_b) == 54

# Scenario A (Benchmark Full Features): 61 features
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)
feature_names_a = prep_a.feature_names_
print(f"Scenario A Feature Count: {len(feature_names_a)}")
assert len(feature_names_a) == 61

# Save fitted preprocessors
joblib.dump(prep_b, os.path.join('models', 'mindsafe_primary_preprocessor.joblib'))
joblib.dump(prep_a, os.path.join('models', 'mindsafe_full_preprocessor.joblib'))

# Save partitions
for out_dir in [os.path.join('Data', 'processed'), 'results']:
    X_train_b.to_csv(os.path.join(out_dir, 'X_train.csv'), index=False, encoding='utf-8')
    X_test_b.to_csv(os.path.join(out_dir, 'X_test.csv'), index=False, encoding='utf-8')
    pd.DataFrame({'Mental_Health_Impact': y_train}).to_csv(os.path.join(out_dir, 'y_train.csv'), index=False, encoding='utf-8')
    pd.DataFrame({'Mental_Health_Impact': y_test}).to_csv(os.path.join(out_dir, 'y_test.csv'), index=False, encoding='utf-8')

# 5. Define EXACTLY the four classifiers for Analysis 1
models_four = {
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=5, min_samples_leaf=1, class_weight='balanced', criterion='gini', random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced')
}

cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 6. Analysis 1: 5-Fold Stratified CV on Training Set (N=1,211)
print("\n--- 5-FOLD STRATIFIED CV ON TRAINING SET (N=1,211) ---")
cv_rows = []
for name, m in models_four.items():
    cv_res = cross_validate(m, X_train_b, y_train, cv=cv5, scoring=['accuracy', 'f1_macro', 'f1_weighted'])
    cv_rows.append({
        'Model': name,
        'CV_Accuracy_Mean': round(float(cv_res['test_accuracy'].mean()), 4),
        'CV_Accuracy_Std': round(float(cv_res['test_accuracy'].std()), 4),
        'CV_Macro_F1_Mean': round(float(cv_res['test_f1_macro'].mean()), 4),
        'CV_Macro_F1_Std': round(float(cv_res['test_f1_macro'].std()), 4),
        'CV_Weighted_F1_Mean': round(float(cv_res['test_f1_weighted'].mean()), 4),
        'CV_Weighted_F1_Std': round(float(cv_res['test_f1_weighted'].std()), 4),
    })
df_cv = pd.DataFrame(cv_rows)
print(df_cv.to_string(index=False))

# 7. Analysis 1: Held-out Test Set Evaluation (N=303)
print("\n--- FOUR-MODEL HELD-OUT TEST EVALUATION (N=303) ---")
test_rows = []
fitted_models = {}
for name, m in models_four.items():
    m.fit(X_train_b, y_train)
    fitted_models[name] = m
    y_pred = m.predict(X_test_b)
    test_rows.append({
        'Model': name,
        'Accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4),
    })
df_four_test = pd.DataFrame(test_rows)
print(df_four_test.to_string(index=False))

# 8. Analysis 2: Leakage-Controlled vs Full-Feature Benchmark
print("\n--- ANALYSIS 2: LEAKAGE-CONTROLLED VS BENCHMARK FULL FEATURES ---")
rf_primary = fitted_models['Random Forest']
rf_bench = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
rf_bench.fit(X_train_a, y_train)

# CV on Benchmark
cv_res_bench = cross_validate(rf_bench, X_train_a, y_train, cv=cv5, scoring=['accuracy', 'f1_macro', 'f1_weighted'])

# Test predictions
y_pred_primary = rf_primary.predict(X_test_b)
y_pred_bench = rf_bench.predict(X_test_a)

leakage_rows = [
    {
        'Model': 'Primary Random Forest — Leakage Controlled',
        'Features': 54,
        'CV_Accuracy_Mean': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Accuracy_Mean'].values[0],
        'CV_Accuracy_Std': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Accuracy_Std'].values[0],
        'CV_Macro_F1_Mean': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Macro_F1_Mean'].values[0],
        'CV_Macro_F1_Std': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Macro_F1_Std'].values[0],
        'Accuracy': round(float(accuracy_score(y_test, y_pred_primary)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred_primary, average='weighted', zero_division=0)), 4),
    },
    {
        'Model': 'Benchmark Random Forest — Full Features / Leakage',
        'Features': 61,
        'CV_Accuracy_Mean': round(float(cv_res_bench['test_accuracy'].mean()), 4),
        'CV_Accuracy_Std': round(float(cv_res_bench['test_accuracy'].std()), 4),
        'CV_Macro_F1_Mean': round(float(cv_res_bench['test_f1_macro'].mean()), 4),
        'CV_Macro_F1_Std': round(float(cv_res_bench['test_f1_macro'].std()), 4),
        'Accuracy': round(float(accuracy_score(y_test, y_pred_bench)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred_bench, average='weighted', zero_division=0)), 4),
    }
]
df_leakage = pd.DataFrame(leakage_rows)
print(df_leakage[['Model', 'Features', 'Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']].to_string(index=False))

# 9. Primary Model Serialization
joblib.dump(rf_primary, os.path.join('models', 'mindsafe_primary_model.joblib'))
joblib.dump(rf_bench, os.path.join('models', 'mindsafe_full_benchmark.joblib'))

# Primary classification report & confusion matrix
primary_rep = classification_report(y_test, y_pred_primary, target_names=classes, digits=4, output_dict=True)
primary_cm = confusion_matrix(y_test, y_pred_primary)

clf_rows = []
for c in classes:
    clf_rows.append({
        'Class': c,
        'Precision': round(primary_rep[c]['precision'], 4),
        'Recall': round(primary_rep[c]['recall'], 4),
        'F1-Score': round(primary_rep[c]['f1-score'], 4),
        'Support': int(primary_rep[c]['support'])
    })
clf_rows.append({
    'Class': 'Macro Avg',
    'Precision': round(primary_rep['macro avg']['precision'], 4),
    'Recall': round(primary_rep['macro avg']['recall'], 4),
    'F1-Score': round(primary_rep['macro avg']['f1-score'], 4),
    'Support': int(primary_rep['macro avg']['support'])
})
clf_rows.append({
    'Class': 'Weighted Avg',
    'Precision': round(primary_rep['weighted avg']['precision'], 4),
    'Recall': round(primary_rep['weighted avg']['recall'], 4),
    'F1-Score': round(primary_rep['weighted avg']['f1-score'], 4),
    'Support': int(primary_rep['weighted avg']['support'])
})
df_clf_report = pd.DataFrame(clf_rows)

cm_df = pd.DataFrame(primary_cm, index=classes, columns=classes)

# Save CSV reports to results/ml and notebook/results/ml
for out_base in ['results', os.path.join('notebook', 'results')]:
    ml_out = os.path.join(out_base, 'ml')
    os.makedirs(ml_out, exist_ok=True)
    df_four_test.to_csv(os.path.join(ml_out, 'model_comparison.csv'), index=False)
    df_cv.to_csv(os.path.join(ml_out, 'cross_validation_results.csv'), index=False)
    df_leakage.to_csv(os.path.join(ml_out, 'leakage_comparison.csv'), index=False)
    df_clf_report.to_csv(os.path.join(ml_out, 'classification_report.csv'), index=False)
    cm_df.to_csv(os.path.join(ml_out, 'confusion_matrix.csv'))

# 10. Update model_metadata.json
rf_cv_match = df_cv.loc[df_cv['Model'] == 'Random Forest']
metadata = {
    "model_name": "MindSafe Primary Multiclass Classifier",
    "model_type": "RandomForestClassifier",
    "library": "scikit-learn",
    "library_version": "1.1.3",
    "target_variable": "Mental_Health_Impact",
    "target_classes": classes,
    "feature_scenario": "Scenario B (Leakage-Controlled)",
    "feature_count": 54,
    "feature_list": feature_names_b,
    "excluded_features": [
        "Timestamp (Metadata)",
        "Negative_Emotional_Symptoms (Q13 - Excluded to prevent target leakage)",
        "Emotional_Impact_Severity (Q14 - Excluded to prevent target leakage)",
        "Offensive_Action_Reason (Q8 - Skip sparsity)",
        "Reason_Not_Reported (Q16 - Skip sparsity)"
    ],
    "train_sample_size": 1211,
    "test_sample_size": 303,
    "train_test_split": {"test_size": 0.2, "random_state": 42, "stratified": True},
    "cross_validation": {"method": "StratifiedKFold", "n_splits": 5, "shuffle": True, "random_state": 42},
    "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 15,
        "min_samples_split": 5,
        "min_samples_leaf": 1,
        "class_weight": "balanced",
        "criterion": "gini",
        "random_state": 42
    },
    "test_metrics": {
        "Accuracy": df_four_test.loc[df_four_test['Model'] == 'Random Forest', 'Accuracy'].values[0],
        "Macro_Precision": df_four_test.loc[df_four_test['Model'] == 'Random Forest', 'Macro Precision'].values[0],
        "Macro_Recall": df_four_test.loc[df_four_test['Model'] == 'Random Forest', 'Macro Recall'].values[0],
        "Macro_F1": df_four_test.loc[df_four_test['Model'] == 'Random Forest', 'Macro F1'].values[0],
        "Weighted_F1": df_four_test.loc[df_four_test['Model'] == 'Random Forest', 'Weighted F1'].values[0]
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
    json.dump(metadata, f, indent=2)

# ==============================================================================
# RESEARCH FIGURES GENERATION (IEEE Standard, 300 DPI)
# ==============================================================================
print("\n--- GENERATING IEEE RESEARCH FIGURES 1 TO 7 ---")

def save_fig(fig, rel_path):
    for base in ['results', os.path.join('notebook', 'results')]:
        p = os.path.join(base, rel_path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fig.savefig(p, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {rel_path}")

# FIGURE 1: Overall MindSafe Architecture (System Flowchart)
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
ax.axis('off')
boxes = [
    ("Survey Data Ingestion\n(N = 1,514 Valid Responses)", (0.05, 0.55), "#e8f4f8", "#0288d1"),
    ("Feature Preprocessing\n(54 Leakage-Controlled)", (0.28, 0.55), "#e8f5e9", "#2e7d32"),
    ("Primary Classifier\n(Random Forest 100 Trees)", (0.51, 0.55), "#fff3e0", "#ef6c00"),
    ("SHAP Explainability\n(TreeExplainer Attribution)", (0.74, 0.55), "#f3e5f5", "#7b1fa2"),
    ("MindSafe Web Platform\n(FastAPI + SvelteKit)", (0.51, 0.15), "#ede7f6", "#512da8")
]
for title, (x, y), face, edge in boxes:
    ax.annotate(
        title, xy=(x+0.1, y), xytext=(x, y),
        bbox=dict(boxstyle="round,pad=0.6", facecolor=face, edgecolor=edge, linewidth=1.5),
        ha="center", va="center", fontsize=9.5, fontweight='bold', color="#222222"
    )
arrows = [
    ((0.15, 0.55), (0.19, 0.55)),
    ((0.38, 0.55), (0.42, 0.55)),
    ((0.61, 0.55), (0.65, 0.55)),
    ((0.51, 0.45), (0.51, 0.25))
]
for (x1, y1), (x2, y2) in arrows:
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#424242", mutation_scale=15))
ax.set_title("Fig. 1. End-to-end MindSafe operational and analytical architecture.", fontsize=11, fontweight='bold', pad=12)
save_fig(fig, os.path.join('ml', 'plots', 'figure1_architecture.png'))

# FIGURE 2: Target Class Distribution
target_counts = usable_df[target_col].value_counts()[classes]
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
colors = ['#2b5c8f', '#4682b4', '#d97724', '#b22222']
bars = ax.bar(classes, target_counts.values, color=colors, edgecolor='black', linewidth=0.8, width=0.55)
for bar in bars:
    h = bar.get_height()
    pct = (h / N_total) * 100
    ax.text(bar.get_x() + bar.get_width() / 2.0, h + 10, f'{h}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=9, fontweight='medium')
ax.set_title(f'Fig. 2. Distribution of survey-defined Mental Health Impact categories (N = {N_total:,}).', fontsize=11, fontweight='bold', pad=12)
ax.set_xlabel('Target Category', fontsize=10, fontweight='semibold')
ax.set_ylabel('Number of Respondents', fontsize=10, fontweight='semibold')
ax.set_ylim(0, max(target_counts.values) * 1.2)
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
save_fig(fig, os.path.join('ml', 'plots', 'figure2_target_distribution.png'))

# FIGURE 3: Four-Model Classification Comparison (SVM vs RF vs LR vs DT)
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
model_names_plot = ['SVM', 'Random Forest', 'Logistic Regression', 'Decision Tree']
metrics_to_plot = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']
x = np.arange(len(model_names_plot))
width = 0.15
palette = ['#1f77b4', '#aec7e8', '#ff7f0e', '#2ca02c', '#98df8a']

for i, m_col in enumerate(metrics_to_plot):
    offset = (i - 2) * width
    vals = df_four_test[m_col].values
    bars = ax.bar(x + offset, vals, width, label=m_col, color=palette[i], edgecolor='black', linewidth=0.7)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 0.012, f'{h:.2f}',
                ha='center', va='bottom', fontsize=7.5, rotation=90)

ax.set_title('Fig. 3. Test-set classification performance across four machine-learning models (N = 303).\nAll models evaluated on the identical 54 leakage-controlled features.', fontsize=10.5, fontweight='bold', pad=14)
ax.set_xlabel('Classification Algorithm', fontsize=10.5, fontweight='semibold')
ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10.5, fontweight='semibold')
ax.set_xticks(x)
ax.set_xticklabels(model_names_plot, fontsize=10, fontweight='semibold')
ax.set_ylim(0, 1.05)
ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9, loc='upper right', ncol=3)
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
save_fig(fig, os.path.join('ml', 'plots', 'figure3_four_model_comparison.png'))
# Also mirror to model_comparison_bar_chart.png
fig_clone, ax_clone = plt.subplots(figsize=(10, 5.5), dpi=300)
for i, m_col in enumerate(metrics_to_plot):
    offset = (i - 2) * width
    vals = df_four_test[m_col].values
    bars = ax_clone.bar(x + offset, vals, width, label=m_col, color=palette[i], edgecolor='black', linewidth=0.7)
    for bar in bars:
        h = bar.get_height()
        ax_clone.text(bar.get_x() + bar.get_width() / 2.0, h + 0.012, f'{h:.2f}',
                      ha='center', va='bottom', fontsize=7.5, rotation=90)
ax_clone.set_title('Fig. 3. Test-set classification performance across four machine-learning models (N = 303).\nAll models evaluated on the identical 54 leakage-controlled features.', fontsize=10.5, fontweight='bold', pad=14)
ax_clone.set_xlabel('Classification Algorithm', fontsize=10.5, fontweight='semibold')
ax_clone.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10.5, fontweight='semibold')
ax_clone.set_xticks(x)
ax_clone.set_xticklabels(model_names_plot, fontsize=10, fontweight='semibold')
ax_clone.set_ylim(0, 1.05)
ax_clone.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9, loc='upper right', ncol=3)
ax_clone.yaxis.grid(True, linestyle='--', alpha=0.5)
ax_clone.set_axisbelow(True)
save_fig(fig_clone, os.path.join('ml', 'model_comparison_bar_chart.png'))

# FIGURE 4: Leakage-Controlled vs Full-Feature Benchmark
fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
comp_labels = ['Primary RF\n(54 Features, Leakage-Controlled)', 'Benchmark RF\n(61 Features, Full/Leakage)']
metrics_leak = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']
x_leak = np.arange(len(comp_labels))
w_leak = 0.15
palette_leak = ['#2b5c8f', '#4682b4', '#d97724', '#2ca02c', '#98df8a']

for i, m_col in enumerate(metrics_leak):
    offset = (i - 2) * w_leak
    vals = df_leakage[m_col].values
    bars = ax.bar(x_leak + offset, vals, w_leak, label=m_col, color=palette_leak[i], edgecolor='black', linewidth=0.7)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 0.015, f'{h:.3f}',
                ha='center', va='bottom', fontsize=8.5, fontweight='bold')

ax.set_title('Fig. 4. Comparison of Primary Leakage-Controlled Random Forest vs. Full-Feature Benchmark (N = 303).\nBenchmark inclusion of Q13/Q14 inflates metrics due to direct post-outcome proxy leakage.', fontsize=9.5, fontweight='bold', pad=14)
ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10, fontweight='semibold')
ax.set_xticks(x_leak)
ax.set_xticklabels(comp_labels, fontsize=9.5, fontweight='bold')
ax.set_ylim(0, 1.05)
ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9, loc='upper left')
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
save_fig(fig, os.path.join('ml', 'plots', 'figure4_leakage_vs_benchmark.png'))

# FIGURE 5: 5-Fold Stratified Cross-Validation Comparison with Error Bars
fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
x_cv = np.arange(len(model_names_plot))
w_cv = 0.35
acc_means = df_cv['CV_Accuracy_Mean'].values
acc_stds = df_cv['CV_Accuracy_Std'].values
f1_means = df_cv['CV_Macro_F1_Mean'].values
f1_stds = df_cv['CV_Macro_F1_Std'].values

bars1 = ax.bar(x_cv - w_cv/2, acc_means, w_cv, yerr=acc_stds, capsize=4, label='Mean CV Accuracy (±1 SD)', color='#1f77b4', edgecolor='black', linewidth=0.7)
bars2 = ax.bar(x_cv + w_cv/2, f1_means, w_cv, yerr=f1_stds, capsize=4, label='Mean CV Macro F1 (±1 SD)', color='#ff7f0e', edgecolor='black', linewidth=0.7)

for bar in bars1:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
for bar in bars2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')

ax.set_title('Fig. 5. 5-Fold stratified cross-validation performance on training partition (N = 1,211).\nError bars represent standard deviation across cross-validation folds.', fontsize=10, fontweight='bold', pad=14)
ax.set_xlabel('Classification Algorithm', fontsize=10, fontweight='semibold')
ax.set_ylabel('Score (0.0 to 1.0)', fontsize=10, fontweight='semibold')
ax.set_xticks(x_cv)
ax.set_xticklabels(model_names_plot, fontsize=9.5, fontweight='bold')
ax.set_ylim(0, 0.85)
ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9.5, loc='upper right')
ax.yaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
save_fig(fig, os.path.join('ml', 'plots', 'figure5_cross_validation_comparison.png'))
# Also mirror to cross_validation_scores.png
fig_cv_clone, ax_cv_clone = plt.subplots(figsize=(9, 5), dpi=300)
bars1 = ax_cv_clone.bar(x_cv - w_cv/2, acc_means, w_cv, yerr=acc_stds, capsize=4, label='Mean CV Accuracy (±1 SD)', color='#1f77b4', edgecolor='black', linewidth=0.7)
bars2 = ax_cv_clone.bar(x_cv + w_cv/2, f1_means, w_cv, yerr=f1_stds, capsize=4, label='Mean CV Macro F1 (±1 SD)', color='#ff7f0e', edgecolor='black', linewidth=0.7)
for bar in bars1:
    h = bar.get_height()
    ax_cv_clone.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
for bar in bars2:
    h = bar.get_height()
    ax_cv_clone.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
ax_cv_clone.set_title('Fig. 5. 5-Fold stratified cross-validation performance on training partition (N = 1,211).\nError bars represent standard deviation across cross-validation folds.', fontsize=10, fontweight='bold', pad=14)
ax_cv_clone.set_xlabel('Classification Algorithm', fontsize=10, fontweight='semibold')
ax_cv_clone.set_ylabel('Score (0.0 to 1.0)', fontsize=10, fontweight='semibold')
ax_cv_clone.set_xticks(x_cv)
ax_cv_clone.set_xticklabels(model_names_plot, fontsize=9.5, fontweight='bold')
ax_cv_clone.set_ylim(0, 0.85)
ax_cv_clone.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9.5, loc='upper right')
ax_cv_clone.yaxis.grid(True, linestyle='--', alpha=0.5)
ax_cv_clone.set_axisbelow(True)
save_fig(fig_cv_clone, os.path.join('ml', 'plots', 'cross_validation_scores.png'))

# FIGURE 6: Confusion Matrix for Primary Random Forest
fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=300)
sns.heatmap(primary_cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax, cbar=False)
ax.set_title('Fig. 6. Confusion matrix for the Primary Leakage-Controlled Random Forest (Test Set N = 303).', fontsize=9.5, fontweight='bold', pad=12)
ax.set_xlabel('Predicted Impact Category', fontsize=10, fontweight='semibold')
ax.set_ylabel('True Survey Impact Category', fontsize=10, fontweight='semibold')
save_fig(fig, os.path.join('ml', 'plots', 'figure6_confusion_matrix.png'))
# Mirror to confusion_matrix_raw.png
fig_cm, ax_cm = plt.subplots(figsize=(6.5, 5.5), dpi=300)
sns.heatmap(primary_cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax_cm, cbar=False)
ax_cm.set_title('Fig. 6. Confusion matrix for the Primary Leakage-Controlled Random Forest (Test Set N = 303).', fontsize=9.5, fontweight='bold', pad=12)
ax_cm.set_xlabel('Predicted Impact Category', fontsize=10, fontweight='semibold')
ax_cm.set_ylabel('True Survey Impact Category', fontsize=10, fontweight='semibold')
save_fig(fig_cm, os.path.join('ml', 'plots', 'confusion_matrix_raw.png'))

# FIGURE 7: SHAP Global Feature Importance
print("Calculating Tree SHAP feature importances for Primary Random Forest...")
explainer = shap.TreeExplainer(rf_primary)
sample_bg = X_train_b.iloc[:200]
shap_values = explainer.shap_values(sample_bg)

# Handle multiclass list of arrays: mean absolute across all classes
if isinstance(shap_values, list):
    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
else:
    mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2)) if shap_values.ndim == 3 else np.abs(shap_values).mean(axis=0)

shap_df = pd.DataFrame({
    'Feature': feature_names_b,
    'Mean_Abs_SHAP': mean_abs_shap
}).sort_values(by='Mean_Abs_SHAP', ascending=False).reset_index(drop=True)

# Save SHAP CSV
for out_base in ['results', os.path.join('notebook', 'results')]:
    shap_df.to_csv(os.path.join(out_base, 'ml', 'shap_feature_importance.csv'), index=False)

top15_shap = shap_df.head(15)
fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
y_pos = np.arange(len(top15_shap))
ax.barh(y_pos, top15_shap['Mean_Abs_SHAP'][::-1], color='#2b5c8f', edgecolor='black', linewidth=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(top15_shap['Feature'][::-1], fontsize=9)
ax.set_xlabel('Mean |SHAP Value| (Average Impact on Model Output Magnitude across Classes)', fontsize=9.5, fontweight='semibold')
ax.set_title('Fig. 7. Tree SHAP global feature attributions for Primary Random Forest (Top 15 Predictors).\nValues reflect contribution to model output and do not imply clinical or causal relationships.', fontsize=9.5, fontweight='bold', pad=14)
ax.xaxis.grid(True, linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
save_fig(fig, os.path.join('ml', 'plots', 'figure7_shap_importance.png'))
# Mirror to shap_bar_plot.png
fig_s_clone, ax_s_clone = plt.subplots(figsize=(9, 6), dpi=300)
ax_s_clone.barh(y_pos, top15_shap['Mean_Abs_SHAP'][::-1], color='#2b5c8f', edgecolor='black', linewidth=0.7)
ax_s_clone.set_yticks(y_pos)
ax_s_clone.set_yticklabels(top15_shap['Feature'][::-1], fontsize=9)
ax_s_clone.set_xlabel('Mean |SHAP Value| (Average Impact on Model Output Magnitude across Classes)', fontsize=9.5, fontweight='semibold')
ax_s_clone.set_title('Fig. 7. Tree SHAP global feature attributions for Primary Random Forest (Top 15 Predictors).\nValues reflect contribution to model output and do not imply clinical or causal relationships.', fontsize=9.5, fontweight='bold', pad=14)
ax_s_clone.xaxis.grid(True, linestyle='--', alpha=0.5)
ax_s_clone.set_axisbelow(True)
save_fig(fig_s_clone, os.path.join('ml', 'plots', 'shap_bar_plot.png'))

print("\nAll figures, models, tables, and metadata successfully generated and saved!")
