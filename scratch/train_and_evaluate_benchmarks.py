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

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath('.'))
from models.preprocessor import SurveyFeaturePreprocessor

def main():
    print("=== MindSafe Multi-Model Benchmark Evaluation ===")
    
    # 1. Load exact analytical dataset
    data_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')
    df = pd.read_csv(data_path, encoding='utf-8')
    
    target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
    valid_mask = df[target_col].notna() & (df[target_col] != '')
    usable_df = df[valid_mask].reset_index(drop=True)
    
    classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
    class_to_idx = {c: i for i, c in enumerate(classes)}
    idx_to_class = {i: c for i, c in enumerate(classes)}
    y = usable_df[target_col].map(class_to_idx).values
    
    # 2. Exact same 80/20 stratified train/test split
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
    
    # 3. Exact same Scenario B preprocessor (54 features, leakage-controlled)
    preprocessor_path = os.path.join('models', 'mindsafe_primary_preprocessor.joblib')
    prep_b = joblib.load(preprocessor_path)
    X_train_b = prep_b.transform(df_train)
    X_test_b = prep_b.transform(df_test)
    
    print(f"Dataset: N_train = {len(X_train_b)} (54 features), N_test = {len(X_test_b)} (54 features)")
    
    # 4. Instantiate models
    # Random Forest is the existing primary model loaded from disk to preserve exact existing results
    rf_primary = joblib.load(os.path.join('models', 'mindsafe_primary_model.joblib'))
    
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),
        'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),
        'Random Forest': rf_primary,
        'Dummy Classifier': DummyClassifier(strategy='most_frequent')
    }
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    comparison_rows = []
    detailed_rows = []
    confusion_matrices_dict = {}
    
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
        
        # 5-fold cross-validation on 411 training records
        if name == 'Random Forest':
            rf_for_cv = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
            cv_scores = cross_validate(rf_for_cv, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
        else:
            cv_scores = cross_validate(model, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted', 'f1_macro'])
            
        cm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3])
        confusion_matrices_dict[name] = cm
        
        # Required single comparison row format:
        # Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted Precision | Weighted Recall | Weighted F1
        comparison_rows.append({
            'Model': name,
            'Accuracy': round(acc, 4),
            'Macro Precision': round(mp, 4),
            'Macro Recall': round(mr, 4),
            'Macro F1': round(mf1, 4),
            'Weighted Precision': round(wp, 4),
            'Weighted Recall': round(wr, 4),
            'Weighted F1': round(wf1, 4)
        })
        
        detailed_rows.append({
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
        
        # Save individual confusion matrix CSV in results/ml/ matching existing project pattern
        cm_norm = confusion_matrix(y_test, y_pred, labels=[0, 1, 2, 3], normalize='true')
        cm_rows = []
        for i, act_cls in enumerate(classes):
            row = {'Actual_Class': act_cls}
            for j, pred_cls in enumerate(classes):
                row[f'Pred_{pred_cls}_Raw'] = int(cm[i, j])
                row[f'Pred_{pred_cls}_Norm'] = round(float(cm_norm[i, j]), 4)
            cm_rows.append(row)
            
        safe_name = name.lower().replace(' ', '_').replace('(', '').replace(')', '')
        cm_file_path = os.path.join('results', 'ml', f'confusion_matrix_{safe_name}.csv')
        pd.DataFrame(cm_rows).to_csv(cm_file_path, index=False, encoding='utf-8')
        print(f"Saved confusion matrix for {name} to: {cm_file_path}")

    # 5. Save the primary comparison CSV requested:
    # Model | Accuracy | Macro Precision | Macro Recall | Macro F1 | Weighted Precision | Weighted Recall | Weighted F1
    df_comp = pd.DataFrame(comparison_rows)
    comp_path = os.path.join('results', 'ml', 'model_comparison.csv')
    df_comp.to_csv(comp_path, index=False, encoding='utf-8')
    print(f"\n[OK] Saved model comparison results to: {comp_path}")
    
    # Save detailed comparison including CV metrics
    detailed_path = os.path.join('results', 'ml', 'model_comparison_detailed.csv')
    pd.DataFrame(detailed_rows).to_csv(detailed_path, index=False, encoding='utf-8')
    print(f"[OK] Saved detailed comparison with CV to: {detailed_path}")
    
    # Save combined confusion matrices overview
    all_cm_rows = []
    for model_name, cm in confusion_matrices_dict.items():
        cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        for i, act_cls in enumerate(classes):
            row = {
                'Model': model_name,
                'Actual_Class': act_cls,
                'Pred_Not_at_all_Raw': int(cm[i, 0]),
                'Pred_Slightly_Raw': int(cm[i, 1]),
                'Pred_Moderately_Raw': int(cm[i, 2]),
                'Pred_Severely_Raw': int(cm[i, 3]),
                'Pred_Not_at_all_Norm': round(float(cm_norm[i, 0]), 4),
                'Pred_Slightly_Norm': round(float(cm_norm[i, 1]), 4),
                'Pred_Moderately_Norm': round(float(cm_norm[i, 2]), 4),
                'Pred_Severely_Norm': round(float(cm_norm[i, 3]), 4)
            }
            all_cm_rows.append(row)
    combined_cm_path = os.path.join('results', 'ml', 'all_models_confusion_matrices.csv')
    pd.DataFrame(all_cm_rows).to_csv(combined_cm_path, index=False, encoding='utf-8')
    print(f"[OK] Saved combined confusion matrices to: {combined_cm_path}")
    
    print("\n================ FINAL COMPARISON RESULT TABLE ================")
    print(df_comp.to_string(index=False))

if __name__ == '__main__':
    main()
