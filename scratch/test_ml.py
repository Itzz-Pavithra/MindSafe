import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import shap

# Load phase2 analytical dataset
df = pd.read_csv('Data/processed/phase2_analysis_data.csv', encoding='utf-8')
print("Loaded analytical dataset:", df.shape)

# Step 2: Target column
target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
valid_df = df[df[target_col].notna()].reset_index(drop=True)
print(f"Total rows: {len(df)}, Missing target: {df[target_col].isna().sum()}, Usable ML rows: {len(valid_df)}")
assert len(valid_df) == 514

# Target distribution
print("\nTarget Distribution:")
print(valid_df[target_col].value_counts())

# Target encoding
classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']
class_to_idx = {c: i for i, c in enumerate(classes)}
y = valid_df[target_col].map(class_to_idx).values

# Let's map candidate features for Scenario B (Leakage-controlled)
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
col_q15 = [c for c in valid_df.columns if c.startswith('15.')][0]
col_q17 = [c for c in valid_df.columns if c.startswith('17.')][0]
col_q18 = [c for c in valid_df.columns if c.startswith('18.')][0]

# For Scenario A, also include Q13 and Q14
col_q13 = [c for c in valid_df.columns if c.startswith('13.')][0]
col_q14 = [c for c in valid_df.columns if c.startswith('14.')][0]

print("\nAll columns located successfully.")
