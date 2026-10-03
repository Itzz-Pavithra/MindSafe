import os
import sys
import json
import joblib
import pandas as pd
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

# Load data exactly as in execute_phase3.py
data_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
df = pd.read_csv(data_path, encoding='utf-8')

target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_mask = df[target_col].notna() & (df[target_col] != '')
usable_df = df[valid_mask].reset_index(drop=True)

classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
idx_to_class = {i: c for i, c in enumerate(classes)}
y = usable_df[target_col].map(class_to_idx).values

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

# Preprocess Scenario B using the fitted preprocessor
preprocessor_path = os.path.join('models', 'mindsafe_primary_preprocessor.joblib')
prep_b = joblib.load(preprocessor_path)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)

print(f"X_train_b shape: {X_train_b.shape}, X_test_b shape: {X_test_b.shape}")

# Define models
models = {
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest': joblib.load(os.path.join('models', 'mindsafe_primary_model.joblib')),
    'Dummy Classifier': DummyClassifier(strategy='most_frequent')
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

results_table = []
all_cms = {}

for name, model in models.items():
    if name != 'Random Forest':
        model.fit(X_train_b, y_train)
    
    y_pred = model.predict(X_test_b)
    
    acc = accuracy_score(y_test, y_pred)
    mp = precision_score(y_test, y_pred, average='macro', zero_division=0)
    mr = recall_score(y_test, y_pred, average='macro', zero_division=0)
    mf1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    wp = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    wr = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    wf1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # 5-fold CV on training set
    if name == 'Random Forest':
        # Train fresh RF with same params for CV
        rf_cv = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        cv_scores = cross_validate(rf_cv, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
    else:
        cv_scores = cross_validate(model, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
    
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
    all_cms[name] = cm
    
    results_table.append({
        'Model': name,
        'Accuracy': round(acc, 4),
        'Macro Precision': round(mp, 4),
        'Macro Recall': round(mr, 4),
        'Macro F1': round(mf1, 4),
        'Weighted Precision': round(wp, 4),
        'Weighted Recall': round(wr, 4),
        'Weighted F1': round(wf1, 4),
        'CV_Accuracy_Mean': round(cv_scores['test_accuracy'].mean(), 4),
        'CV_Accuracy_Std': round(cv_scores['test_accuracy'].std(), 4),
        'CV_Macro_F1_Mean': round(cv_scores['test_f1_macro'].mean(), 4),
        'CV_Macro_F1_Std': round(cv_scores['test_f1_macro'].std(), 4),
        'CV_Weighted_F1_Mean': round(cv_scores['test_f1_weighted'].mean(), 4),
        'CV_Weighted_F1_Std': round(cv_scores['test_f1_weighted'].std(), 4)
    })
    
    print(f"\n==================== {name} ====================")
    print(f"Accuracy           : {acc:.4f}")
    print(f"Macro Precision    : {mp:.4f}")
    print(f"Macro Recall       : {mr:.4f}")
    print(f"Macro F1           : {mf1:.4f}")
    print(f"Weighted Precision : {wp:.4f}")
    print(f"Weighted Recall    : {wr:.4f}")
    print(f"Weighted F1        : {wf1:.4f}")
    print(f"5-Fold CV Accuracy : {cv_scores['test_accuracy'].mean():.4f} +/- {cv_scores['test_accuracy'].std():.4f}")
    print(f"5-Fold CV Macro F1 : {cv_scores['test_f1_macro'].mean():.4f} +/- {cv_scores['test_f1_macro'].std():.4f}")
    print(f"Confusion Matrix:\n{cm}")

df_results = pd.DataFrame(results_table)
print("\n==================== COMPARISON TABLE ====================")
display_cols = ['Model', 'Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted Precision', 'Weighted Recall', 'Weighted F1']
print(df_results[display_cols].to_string(index=False))
