import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import shap

df = pd.read_csv('Data/processed/phase2_analysis_data.csv', encoding='utf-8')
target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_df = df[df[target_col].notna()].reset_index(drop=True)

classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
y = valid_df[target_col].map(class_to_idx).values

# Let's write a robust transformer class or function for survey features
def extract_multiselect_tokens(series):
    tokens = set()
    for item in series.dropna():
        for t in str(item).split(','):
            cleaned_t = t.strip()
            if cleaned_t:
                tokens.add(cleaned_t)
    return sorted(list(tokens))

# Column pointers
col_age = [c for c in valid_df.columns if '1. What is your age?' in c][0]
col_gender = [c for c in valid_df.columns if '2. What is your gender?' in c][0]
col_plat = [c for c in valid_df.columns if '3. Which social media' in c][0]
col_usage = [c for c in valid_df.columns if c.startswith('4.')][0]
col_q5 = [c for c in valid_df.columns if '5. Have you personally experienced' in c][0]
col_q6 = [c for c in valid_df.columns if c.startswith('6.')][0]
col_q7 = [c for c in valid_df.columns if c.startswith('7.')][0]
col_q9 = [c for c in valid_df.columns if c.startswith('9.')][0]
col_q10 = [c for c in valid_df.columns if c.startswith('10.')][0]
col_q11 = [c for c in valid_df.columns if c.startswith('11.')][0]
col_q13 = [c for c in valid_df.columns if c.startswith('13.')][0]
col_q14 = [c for c in valid_df.columns if c.startswith('14.')][0]
col_q15 = [c for c in valid_df.columns if c.startswith('15.')][0]
col_q17 = [c for c in valid_df.columns if c.startswith('17.')][0]
col_q18 = [c for c in valid_df.columns if c.startswith('18.')][0]

# Split train/test
train_idx, test_idx = train_test_split(np.arange(len(valid_df)), test_size=0.20, random_state=42, stratify=y)
print(f"Train size: {len(train_idx)}, Test size: {len(test_idx)}")

# Let's inspect class distribution in train and test
print("\nTrain class distribution:")
print(pd.Series(y[train_idx]).value_counts().sort_index())
print("\nTest class distribution:")
print(pd.Series(y[test_idx]).value_counts().sort_index())

# Feature engineering class
class SurveyFeaturePreprocessor:
    def __init__(self, scenario='B'):
        self.scenario = scenario
        self.multiselect_cols = [
            ('Platforms_Used', col_plat),
            ('Cyberbullying_Types', col_q9),
            ('Sought_Help', col_q15),
            ('Action_Taken', col_q18)
        ]
        if scenario == 'A':
            self.multiselect_cols.append(('Negative_Symptoms', col_q13))
            
        self.tokens_dict = {}
        self.gender_categories = []
        self.q7_categories = []
        self.platform_categories = []
        self.context_categories = []
        self.feature_names_ = []
        
    def fit(self, X_df):
        # Learn vocabulary for multiselect columns
        for name, col in self.multiselect_cols:
            self.tokens_dict[name] = extract_multiselect_tokens(X_df[col])
            
        self.gender_categories = sorted(X_df[col_gender].dropna().unique())
        self.q7_categories = sorted(X_df[col_q7].dropna().unique())
        self.platform_categories = sorted(X_df[col_q10].dropna().unique())
        self.context_categories = sorted(X_df[col_q17].dropna().unique())
        
        # Build feature names
        fnames = []
        fnames.append('Age_Ordinal')
        fnames.append('Daily_Usage_Ordinal')
        fnames.append('Experienced_Cyberbullying_Binary')
        fnames.append('Witnessed_Cyberbullying_Binary')
        fnames.append('Cyberbullying_Frequency_Ordinal')
        
        for g in self.gender_categories:
            fnames.append(f'Gender_{g}')
        for q in self.q7_categories:
            fnames.append(f'Posted_Offensive_{q}')
        for p in self.platform_categories:
            fnames.append(f'Incident_Platform_{p}')
        for c in self.context_categories:
            fnames.append(f'Context_Area_{c}')
            
        for name, col in self.multiselect_cols:
            for tok in self.tokens_dict[name]:
                fnames.append(f'{name}_{tok}')
                
        if self.scenario == 'A':
            fnames.append('Emotional_Impact_Severity_Scale')
            
        self.feature_names_ = fnames
        return self
        
    def transform(self, X_df):
        rows = []
        age_map = {'Below 18': 0, '18–22': 1, '23–30': 2, 'Above 30': 3, '31–40': 3, '41–50': 4}
        usage_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
        freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}
        sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
        
        for _, row in X_df.iterrows():
            feat = []
            feat.append(age_map.get(str(row[col_age]), 1))
            feat.append(usage_map.get(str(row[col_usage]), 1))
            feat.append(1 if row[col_q5] == 'Yes' else 0)
            feat.append(1 if row[col_q6] == 'Yes' else 0)
            feat.append(freq_map.get(str(row[col_q11]), 0))
            
            # Gender one-hot
            for g in self.gender_categories:
                feat.append(1 if row[col_gender] == g else 0)
            # Q7 one-hot
            for q in self.q7_categories:
                feat.append(1 if row[col_q7] == q else 0)
            # Platform one-hot
            for p in self.platform_categories:
                feat.append(1 if row[col_q10] == p else 0)
            # Context one-hot
            for c in self.context_categories:
                feat.append(1 if row[col_q17] == c else 0)
                
            # Multiselect
            for name, col in self.multiselect_cols:
                val = str(row[col]) if pd.notna(row[col]) else ''
                row_toks = set([t.strip() for t in val.split(',') if t.strip()])
                for tok in self.tokens_dict[name]:
                    feat.append(1 if tok in row_toks else 0)
                    
            if self.scenario == 'A':
                feat.append(sev_map.get(str(row[col_q14]), 1))
                
            rows.append(feat)
            
        return pd.DataFrame(rows, columns=self.feature_names_, index=X_df.index)

# Train and test split dataframes
df_train = valid_df.iloc[train_idx].copy()
df_test = valid_df.iloc[test_idx].copy()
y_train = y[train_idx]
y_test = y[test_idx]

# Fit prep B
prep_b = SurveyFeaturePreprocessor(scenario='B').fit(df_train)
X_train_b = prep_b.transform(df_train)
X_test_b = prep_b.transform(df_test)
print(f"Scenario B feature count: {X_train_b.shape[1]}")

# Fit prep A
prep_a = SurveyFeaturePreprocessor(scenario='A').fit(df_train)
X_train_a = prep_a.transform(df_train)
X_test_a = prep_a.transform(df_test)
print(f"Scenario A feature count: {X_train_a.shape[1]}")

# Baseline Dummy
dummy = DummyClassifier(strategy="most_frequent")
dummy.fit(X_train_b, y_train)
y_pred_dummy = dummy.predict(X_test_b)
print("\n--- BASELINE DUMMY RESULTS ---")
print(f"Accuracy: {accuracy_score(y_test, y_pred_dummy):.4f}")
print(f"Weighted F1: {f1_score(y_test, y_pred_dummy, average='weighted'):.4f}")

# Train Random Forest B (Primary)
rf_b = RandomForestClassifier(random_state=42, n_estimators=100, class_weight='balanced')
rf_b.fit(X_train_b, y_train)
y_pred_b = rf_b.predict(X_test_b)

# Cross validation on Train B
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_b = cross_validate(rf_b, X_train_b, y_train, cv=cv, scoring=['accuracy', 'f1_weighted'])
print(f"\n--- MODEL B (PRIMARY) CROSS-VALIDATION ---")
print(f"CV Accuracy: {cv_b['test_accuracy'].mean():.4f} +/- {cv_b['test_accuracy'].std():.4f}")
print(f"CV Weighted F1: {cv_b['test_f1_weighted'].mean():.4f} +/- {cv_b['test_f1_weighted'].std():.4f}")

print("\n--- MODEL B (PRIMARY) TEST EVALUATION ---")
print(f"Test Accuracy: {accuracy_score(y_test, y_pred_b):.4f}")
print(f"Test Macro F1: {f1_score(y_test, y_pred_b, average='macro'):.4f}")
print(f"Test Weighted F1: {f1_score(y_test, y_pred_b, average='weighted'):.4f}")
print("\nClassification Report B:")
print(classification_report(y_test, y_pred_b, target_names=classes))

# Train Random Forest A (Full Benchmark)
rf_a = RandomForestClassifier(random_state=42, n_estimators=100, class_weight='balanced')
rf_a.fit(X_train_a, y_train)
y_pred_a = rf_a.predict(X_test_a)

cv_a = cross_validate(rf_a, X_train_a, y_train, cv=cv, scoring=['accuracy', 'f1_weighted'])
print(f"\n--- MODEL A (FULL BENCHMARK) CROSS-VALIDATION ---")
print(f"CV Accuracy: {cv_a['test_accuracy'].mean():.4f} +/- {cv_a['test_accuracy'].std():.4f}")
print(f"CV Weighted F1: {cv_a['test_f1_weighted'].mean():.4f} +/- {cv_a['test_f1_weighted'].std():.4f}")

print("\n--- MODEL A (FULL BENCHMARK) TEST EVALUATION ---")
print(f"Test Accuracy: {accuracy_score(y_test, y_pred_a):.4f}")
print(f"Test Macro F1: {f1_score(y_test, y_pred_a, average='macro'):.4f}")
print(f"Test Weighted F1: {f1_score(y_test, y_pred_a, average='weighted'):.4f}")
print("\nClassification Report A:")
print(classification_report(y_test, y_pred_a, target_names=classes))

# Test SHAP TreeExplainer
explainer = shap.TreeExplainer(rf_b)
shap_values = explainer.shap_values(X_test_b)
print(f"\nSHAP TreeExplainer completed successfully. Type: {type(shap_values)}, length/shape: {len(shap_values) if isinstance(shap_values, list) else shap_values.shape}")
