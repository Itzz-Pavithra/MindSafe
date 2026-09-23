import os
import pandas as pd
import numpy as np

cleaned_path = os.path.join('Data', 'processed', 'cleaned_survey_data.csv')
df = pd.read_csv(cleaned_path, encoding='utf-8', keep_default_na=False)
for col in df.columns:
    df[col] = df[col].replace({'': np.nan})

print(f"Loaded Phase 1 cleaned data: {df.shape}")

# 1. Blank rows check
row_nulls = df.iloc[:, 1:].isna().sum(axis=1) # check all survey questions (cols 1..18)
blank_indices = row_nulls[row_nulls == 18].index.tolist()
print(f"Indices with all 18 questions blank: {blank_indices}")

# 2. Q8 skip logic check:
# Q7: "7. Have you ever posted, shared, or sent a message online that could have hurt or offended someone?"
# Q8: "8. If yes, what was the main reason for your action?"
col_q7 = [c for c in df.columns if c.startswith('7.')][0]
col_q8 = [c for c in df.columns if c.startswith('8.')][0]
print(f"\nQ7 breakdown:\n{df[col_q7].value_counts(dropna=False)}")
print(f"\nCross-tab Q7 vs Q8 missingness:")
print(pd.crosstab(df[col_q7].fillna('MISSING'), df[col_q8].isna(), rownames=['Q7'], colnames=['Q8 is NaN']))

# 3. Q16 skip logic check:
# Q16: "16. If you did not report the incident, what was the main reason?"
# Let's inspect who answered and who skipped Q16
col_q5 = [c for c in df.columns if '5. Have you personally experienced' in c][0]
col_q11 = [c for c in df.columns if c.startswith('11.')][0]
col_q16 = [c for c in df.columns if '16. If you did not report' in c][0]
col_q18 = [c for c in df.columns if c.startswith('18.')][0]

print(f"\nQ16 missingness count: {df[col_q16].isna().sum()} out of {len(df)}")
print(f"Q16 unique values:\n{df[col_q16].value_counts(dropna=False)}")

# Check Q16 missingness against Q5 (Experienced) and Q18 (Action taken - reported)
print("\nCross-tab Q5 (Experienced) vs Q16 is NaN:")
print(pd.crosstab(df[col_q5].fillna('MISSING'), df[col_q16].isna(), rownames=['Q5'], colnames=['Q16 is NaN']))

# Check Q18 actions containing 'Reported'
reported = df[col_q18].fillna('').str.contains('Reported')
print("\nCross-tab Q18 Reported vs Q16 is NaN:")
print(pd.crosstab(reported, df[col_q16].isna(), rownames=['Reported Account'], colnames=['Q16 is NaN']))

# 4. Check Emotional_Impact_Severity
col_q14 = [c for c in df.columns if c.startswith('14.')][0]
print(f"\nQ14 values breakdown:\n{df[col_q14].value_counts(dropna=False)}")

# 5. Check Target variable
col_target = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]
print(f"\nTarget values breakdown:\n{df[col_target].value_counts(dropna=False)}")
