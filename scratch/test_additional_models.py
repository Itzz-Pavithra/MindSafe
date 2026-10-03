import os
import json
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_validate

X_train = pd.read_csv(os.path.join('Data', 'processed', 'X_train.csv'))
y_train = pd.read_csv(os.path.join('Data', 'processed', 'y_train.csv')).values.ravel()
X_test = pd.read_csv(os.path.join('Data', 'processed', 'X_test.csv'))
y_test = pd.read_csv(os.path.join('Data', 'processed', 'y_test.csv')).values.ravel()

print(f"X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"X_test : {X_test.shape}, y_test : {y_test.shape}")

models = {
    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
    'Random Forest (Primary Model)': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
    'Dummy Classifier (Baseline)': DummyClassifier(strategy='most_frequent')
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

results = []

for name, m in models.items():
    m.fit(X_train, y_train)
    y_pred = m.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    mp = precision_score(y_test, y_pred, average='macro', zero_division=0)
    mr = recall_score(y_test, y_pred, average='macro', zero_division=0)
    mf1 = f1_score(y_test, y_pred, average='macro', zero_division=0)
    wp = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    wr = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    wf1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    cv_scores = cross_validate(m, X_train, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
    
    results.append({
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
        'CV_Weighted_F1_Mean': round(cv_scores['test_f1_weighted'].mean(), 4)
    })
    
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
    print(f"\n=== {name} ===")
    print(f"Accuracy: {acc:.4f} | Macro F1: {mf1:.4f} | Weighted F1: {wf1:.4f}")
    print(f"Confusion Matrix:\n{cm}")

df_res = pd.DataFrame(results)
print("\n=== SUMMARY TABLE ===")
print(df_res[['Model', 'Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted Precision', 'Weighted Recall', 'Weighted F1']].to_string(index=False))
