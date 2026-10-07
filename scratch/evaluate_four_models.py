import os, sys
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

sys.path.insert(0, '.')
from models.preprocessor import SurveyFeaturePreprocessor

# Load analytical dataset
df = pd.read_csv('Data/processed/phase2_analysis_data.csv')
target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df[target_col].notna() & (df[target_col] != '')
usable_df = df[valid_mask].reset_index(drop=True)

classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
y = usable_df[target_col].map(class_to_idx).values

train_idx, test_idx = train_test_split(range(len(usable_df)), test_size=0.2, random_state=42, stratify=y)
df_train = usable_df.iloc[train_idx].reset_index(drop=True)
df_test = usable_df.iloc[test_idx].reset_index(drop=True)
y_train = y[train_idx]
y_test = y[test_idx]

# 54 features strictly fitted on training data
prep_b = SurveyFeaturePreprocessor(scenario='B')
prep_b.fit(df_train)
X_train = prep_b.transform(df_train)
X_test = prep_b.transform(df_test)

# Analysis 1: Exactly 4 Models
models = {
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', max_depth=15, min_samples_split=5),
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced')
}

cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

print('=== ANALYSIS 1: 5-FOLD STRATIFIED CV ON TRAINING SET (N=1,211) ===')
cv_rows = []
for name, m in models.items():
    cv_res = cross_validate(m, X_train, y_train, cv=cv5, scoring=['accuracy', 'f1_macro', 'f1_weighted'])
    row = {
        'Model': name,
        'CV_Accuracy_Mean': round(float(cv_res['test_accuracy'].mean()), 4),
        'CV_Accuracy_Std': round(float(cv_res['test_accuracy'].std()), 4),
        'CV_Macro_F1_Mean': round(float(cv_res['test_f1_macro'].mean()), 4),
        'CV_Macro_F1_Std': round(float(cv_res['test_f1_macro'].std()), 4),
        'CV_Weighted_F1_Mean': round(float(cv_res['test_f1_weighted'].mean()), 4),
        'CV_Weighted_F1_Std': round(float(cv_res['test_f1_weighted'].std()), 4),
    }
    cv_rows.append(row)
    print(f"{name:30s} | CV Acc: {row['CV_Accuracy_Mean']:.4f} +/- {row['CV_Accuracy_Std']:.4f} | CV Macro F1: {row['CV_Macro_F1_Mean']:.4f} +/- {row['CV_Macro_F1_Std']:.4f}")

df_cv = pd.DataFrame(cv_rows)

print('\n=== ANALYSIS 1: HELD-OUT TEST SET EVALUATION (N=303) ===')
test_rows = []
for name, m in models.items():
    m.fit(X_train, y_train)
    y_pred = m.predict(X_test)
    row = {
        'Model': name,
        'Accuracy': round(float(accuracy_score(y_test, y_pred)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
    }
    test_rows.append(row)
    print(f"{name:30s} | Acc: {row['Accuracy']:.4f} | Macro P: {row['Macro Precision']:.4f} | Macro R: {row['Macro Recall']:.4f} | Macro F1: {row['Macro F1']:.4f} | Weighted F1: {row['Weighted F1']:.4f}")

df_test_metrics = pd.DataFrame(test_rows)

# Analysis 2: Leakage-Controlled RF (54 feat) vs Full Benchmark RF (61 feat)
prep_a = SurveyFeaturePreprocessor(scenario='A')
prep_a.fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)

rf_b = models['Random Forest'] # fitted on X_train
rf_a = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf_a.fit(X_train_a, y_train)

y_pred_b = rf_b.predict(X_test)
y_pred_a = rf_a.predict(X_test_a)

cv_res_a = cross_validate(rf_a, X_train_a, y_train, cv=cv5, scoring=['accuracy', 'f1_macro', 'f1_weighted'])

print('\n=== ANALYSIS 2: LEAKAGE-CONTROLLED VS BENCHMARK FULL FEATURES ===')
leakage_rows = [
    {
        'Model': 'Primary Random Forest — Leakage Controlled',
        'Features': 54,
        'CV_Accuracy_Mean': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Accuracy_Mean'].values[0],
        'CV_Macro_F1_Mean': df_cv.loc[df_cv['Model'] == 'Random Forest', 'CV_Macro_F1_Mean'].values[0],
        'Accuracy': round(float(accuracy_score(y_test, y_pred_b)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred_b, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred_b, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred_b, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred_b, average='weighted', zero_division=0)), 4),
    },
    {
        'Model': 'Benchmark Random Forest — Full Features / Leakage',
        'Features': 61,
        'CV_Accuracy_Mean': round(float(cv_res_a['test_accuracy'].mean()), 4),
        'CV_Macro_F1_Mean': round(float(cv_res_a['test_f1_macro'].mean()), 4),
        'Accuracy': round(float(accuracy_score(y_test, y_pred_a)), 4),
        'Macro Precision': round(float(precision_score(y_test, y_pred_a, average='macro', zero_division=0)), 4),
        'Macro Recall': round(float(recall_score(y_test, y_pred_a, average='macro', zero_division=0)), 4),
        'Macro F1': round(float(f1_score(y_test, y_pred_a, average='macro', zero_division=0)), 4),
        'Weighted F1': round(float(f1_score(y_test, y_pred_a, average='weighted', zero_division=0)), 4),
    }
]
df_leakage = pd.DataFrame(leakage_rows)
print(df_leakage[['Model', 'Features', 'Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']].to_string(index=False))
