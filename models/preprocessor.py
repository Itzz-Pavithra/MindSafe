import pandas as pd
import numpy as np

class SurveyFeaturePreprocessor:
    """
    Standardized Preprocessor for MindSafe Cyberbullying & Mental Health Survey Features.
    Supports Scenario A (Full Benchmark) and Scenario B (Leakage-Controlled Primary Model).
    Fitted strictly on training records to prevent information leakage.
    """
    def __init__(self, scenario='B'):
        self.scenario = scenario
        self.col_names = {}
        self.multiselect_tokens = {}
        self.nominal_categories = {}
        self.feature_names_ = []
        
        # Ordinal mapping dictionaries
        self.age_map = {'Below 18': 0, '18–22': 1, '23–30': 2, 'Above 30': 3, '31–40': 3, '41–50': 4}
        self.usage_map = {'Less than 1 hour': 0, '1–3 hours': 1, '3–5 hours': 2, 'More than 5 hours': 3}
        self.freq_map = {'Never': 0, 'Rarely': 1, 'Sometimes': 2, 'Often': 3, 'Very Often': 4}
        self.sev_map = {'1 (Very Low)': 1, '2': 2, '3': 3, '4': 4, '5 (Very High)': 5}
        
    def _locate_cols(self, df):
        cols = df.columns
        mapping = {
            'age': [c for c in cols if '1. What is your age?' in c][0],
            'gender': [c for c in cols if '2. What is your gender?' in c][0],
            'platforms': [c for c in cols if '3. Which social media' in c][0],
            'usage': [c for c in cols if c.startswith('4.')][0],
            'q5_exp': [c for c in cols if '5. Have you personally experienced' in c][0],
            'q6_wit': [c for c in cols if c.startswith('6.')][0],
            'q7_post': [c for c in cols if c.startswith('7.')][0],
            'q9_types': [c for c in cols if c.startswith('9.')][0],
            'q10_plat': [c for c in cols if c.startswith('10.')][0],
            'q11_freq': [c for c in cols if c.startswith('11.')][0],
            'q15_help': [c for c in cols if c.startswith('15.')][0],
            'q17_area': [c for c in cols if c.startswith('17.')][0],
            'q18_act': [c for c in cols if c.startswith('18.')][0]
        }
        if self.scenario == 'A':
            mapping['q13_sym'] = [c for c in cols if c.startswith('13.')][0]
            mapping['q14_sev'] = [c for c in cols if c.startswith('14.')][0]
        return mapping

    def fit(self, X_df, y=None):
        self.col_names = self._locate_cols(X_df)
        
        # Multiselect columns to parse
        multiselect_keys = ['platforms', 'q9_types', 'q15_help', 'q18_act']
        if self.scenario == 'A':
            multiselect_keys.append('q13_sym')
            
        for k in multiselect_keys:
            col_str = self.col_names[k]
            tokens = set()
            for val in X_df[col_str].dropna():
                for t in str(val).split(','):
                    ct = t.strip()
                    if ct:
                        tokens.add(ct)
            self.multiselect_tokens[k] = sorted(list(tokens))
            
        # Nominal categorical columns
        nominal_keys = ['gender', 'q7_post', 'q10_plat', 'q17_area']
        for k in nominal_keys:
            col_str = self.col_names[k]
            cats = sorted([str(x) for x in X_df[col_str].dropna().unique() if str(x) != 'nan'])
            self.nominal_categories[k] = cats
            
        # Construct feature names list
        fnames = [
            'Age_Ordinal',
            'Daily_Usage_Ordinal',
            'Experienced_Cyberbullying_Binary',
            'Witnessed_Cyberbullying_Binary',
            'Cyberbullying_Frequency_Ordinal'
        ]
        
        # Add nominal one-hot features
        for g in self.nominal_categories['gender']:
            fnames.append(f'Gender_{g}')
        for q in self.nominal_categories['q7_post']:
            fnames.append(f'Posted_Offensive_{q}')
        for p in self.nominal_categories['q10_plat']:
            fnames.append(f'Incident_Platform_{p}')
        for a in self.nominal_categories['q17_area']:
            fnames.append(f'Context_Area_{a}')
            
        # Add multiselect binary indicator features
        label_prefixes = {
            'platforms': 'Platform_Used',
            'q9_types': 'Bullying_Type',
            'q15_help': 'Sought_Help',
            'q18_act': 'Action_Taken',
            'q13_sym': 'Negative_Symptom'
        }
        for k in multiselect_keys:
            prefix = label_prefixes[k]
            for tok in self.multiselect_tokens[k]:
                fnames.append(f'{prefix}_{tok}')
                
        if self.scenario == 'A':
            fnames.append('Emotional_Impact_Severity_Scale')
            
        self.feature_names_ = fnames
        return self

    def transform(self, X_df):
        m = self.col_names
        rows = []
        multiselect_keys = ['platforms', 'q9_types', 'q15_help', 'q18_act']
        if self.scenario == 'A':
            multiselect_keys.append('q13_sym')
            
        for _, row in X_df.iterrows():
            feat = []
            # 1. Age Ordinal
            feat.append(self.age_map.get(str(row[m['age']]), 1))
            # 2. Daily Usage Ordinal
            feat.append(self.usage_map.get(str(row[m['usage']]), 1))
            # 3. Experienced Cyberbullying Binary
            feat.append(1 if row[m['q5_exp']] == 'Yes' else 0)
            # 4. Witnessed Cyberbullying Binary
            feat.append(1 if row[m['q6_wit']] == 'Yes' else 0)
            # 5. Cyberbullying Frequency Ordinal
            feat.append(self.freq_map.get(str(row[m['q11_freq']]), 0))
            
            # Nominal One-hot features
            for g in self.nominal_categories['gender']:
                feat.append(1 if row[m['gender']] == g else 0)
            for q in self.nominal_categories['q7_post']:
                feat.append(1 if row[m['q7_post']] == q else 0)
            for p in self.nominal_categories['q10_plat']:
                feat.append(1 if row[m['q10_plat']] == p else 0)
            for a in self.nominal_categories['q17_area']:
                feat.append(1 if row[m['q17_area']] == a else 0)
                
            # Multiselect binary indicators
            for k in multiselect_keys:
                raw_val = str(row[m[k]]) if pd.notna(row[m[k]]) else ''
                row_toks = set([t.strip() for t in raw_val.split(',') if t.strip()])
                for tok in self.multiselect_tokens[k]:
                    feat.append(1 if tok in row_toks else 0)
                    
            if self.scenario == 'A':
                feat.append(self.sev_map.get(str(row[m['q14_sev']]), 1))
                
            rows.append(feat)
            
        return pd.DataFrame(rows, columns=self.feature_names_, index=X_df.index)

    def fit_transform(self, X_df, y=None):
        return self.fit(X_df, y).transform(X_df)

    def get_feature_names_out(self, input_features=None):
        return np.array(self.feature_names_)
