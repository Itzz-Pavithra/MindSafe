import os
import json
import pandas as pd
import numpy as np

# Load raw and cleaned data
raw_path = os.path.join('Data', 'raw', 'Survey on Cyberbullying, Mental Health, and Cyber Law Awareness Among Social Media Users (Responses) - Form Responses 1.csv')
cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')

df_raw = pd.read_csv(raw_path, encoding='cp1252')
df_clean = pd.read_csv(cleaned_path, encoding='utf-8')

print("=== 1. DATASET CHECKS ===")
print(f"Raw shape: {df_raw.shape}")
print(f"Cleaned shape: {df_clean.shape}")

# Check blank rows in raw
blank_raw = df_raw.isna().all(axis=1).sum()
print(f"Completely blank rows in raw: {blank_raw}")

# Check target column
target_col = [c for c in df_clean.columns if '12. Do you think' in c][0]
print(f"Target column name: {target_col}")
print("Target values counts in cleaned:")
print(df_clean[target_col].value_counts(dropna=False))

# Valid target rows
df_ml = df_clean.dropna(subset=[target_col])
print(f"ML dataset size (non-null target): {len(df_ml)}")
print("Class counts:")
print(df_ml[target_col].value_counts())
print("Class percentages:")
print(df_ml[target_col].value_counts(normalize=True) * 100)

# Check duplicates in raw and cleaned
print(f"Raw duplicates (all cols): {df_raw.duplicated().sum()}")
print(f"Cleaned duplicates (excluding timestamp): {df_clean.drop(columns=[df_clean.columns[0]]).duplicated().sum()}")

# Check train and test files
x_train = pd.read_csv(os.path.join('Data', 'processed', 'X_train.csv'))
x_test = pd.read_csv(os.path.join('Data', 'processed', 'X_test.csv'))
y_train = pd.read_csv(os.path.join('Data', 'processed', 'y_train.csv'))
y_test = pd.read_csv(os.path.join('Data', 'processed', 'y_test.csv'))

print(f"X_train shape: {x_train.shape}, y_train shape: {y_train.shape}")
print(f"X_test shape: {x_test.shape}, y_test shape: {y_test.shape}")
print(f"Total train+test: {len(x_train) + len(x_test)}")

print("\n=== 2. FEATURE COLUMNS (X_train) ===")
print(f"Number of features in X_train: {x_train.shape[1]}")
print(list(x_train.columns))

# Check for any target leakage in X_train features
target_leakage_keywords = ['mental', 'health', 'symptom', 'severity', 'depress', 'anxiet', 'stress']
potential_leaks = [c for c in x_train.columns if any(k in c.lower() for k in target_leakage_keywords)]
print(f"Potential leakage column names in X_train: {potential_leaks}")

# Check test target class distribution
print("\ny_test class distribution:")
print(y_test.iloc[:, 0].value_counts().sort_index())
