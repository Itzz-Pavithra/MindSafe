import json
import os
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor

nb_path = os.path.join('notebook', '03_ml_training_evaluation.ipynb')

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# The last cell (index 36) is currently empty
# Replace cell 36 with a markdown cell explaining multi-model benchmark comparison
nb['cells'][36] = {
    'cell_type': 'markdown',
    'metadata': {},
    'source': [
        "## 17. Research Paper Analysis \u2014 Multi-Model Benchmark Comparison\n",
        "To satisfy standard peer-review expectations for empirical machine-learning research, this section benchmarks multiple standard baseline classifiers against the **Primary Random Forest** model:\n",
        "1. **Logistic Regression** (L2 regularized, balanced class weights, max_iter=1000)\n",
        "2. **Decision Tree** (CART, balanced class weights, random_state=42)\n",
        "3. **Support Vector Machine (SVM)** (RBF kernel, balanced class weights, probability=True)\n",
        "4. **Random Forest** (*Existing Primary Model*, 100 trees, balanced weights, random_state=42)\n",
        "5. **Dummy Classifier** (*Existing Baseline*, majority class 'most_frequent')\n\n",
        "> **Strict Academic Isolation:** All benchmark models are evaluated on the exact same 54 Scenario B leakage-controlled features and tested on the exact same held-out test partition ($N = 103$). The Random Forest remains the designated primary operational model."
    ]
}

# Add code cell to run comparison and display the exact requested table
code_source = [
    "# ==============================================================================\n",
    "# MULTI-MODEL BENCHMARK COMPARISON (TABLE FOR RESEARCH PAPER)\n",
    "# Evaluates Logistic Regression, Decision Tree, SVM, Random Forest, & Dummy Classifier\n",
    "# ==============================================================================\n",
    "\n",
    "from sklearn.linear_model import LogisticRegression\n",
    "from sklearn.tree import DecisionTreeClassifier\n",
    "from sklearn.svm import SVC\n",
    "\n",
    "benchmark_models = {\n",
    "    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),\n",
    "    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced'),\n",
    "    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),\n",
    "    'Random Forest': rf_b,\n",
    "    'Dummy Classifier': dummy\n",
    "}\n",
    "\n",
    "benchmark_rows = []\n",
    "for name, m in benchmark_models.items():\n",
    "    if name not in ['Random Forest', 'Dummy Classifier']:\n",
    "        m.fit(X_train_b, y_train)\n",
    "    \n",
    "    y_p = m.predict(X_test_b)\n",
    "    \n",
    "    benchmark_rows.append({\n",
    "        'Model': name,\n",
    "        'Accuracy': round(accuracy_score(y_test, y_p), 4),\n",
    "        'Macro Precision': round(precision_score(y_test, y_p, average='macro', zero_division=0), 4),\n",
    "        'Macro Recall': round(recall_score(y_test, y_p, average='macro', zero_division=0), 4),\n",
    "        'Macro F1': round(f1_score(y_test, y_p, average='macro', zero_division=0), 4),\n",
    "        'Weighted Precision': round(precision_score(y_test, y_p, average='weighted', zero_division=0), 4),\n",
    "        'Weighted Recall': round(recall_score(y_test, y_p, average='weighted', zero_division=0), 4),\n",
    "        'Weighted F1': round(f1_score(y_test, y_p, average='weighted', zero_division=0), 4)\n",
    "    })\n",
    "\n",
    "df_benchmark_comp = pd.DataFrame(benchmark_rows)\n",
    "display(df_benchmark_comp)\n",
    "\n",
    "# Export comparison CSV to results/ml/model_comparison.csv\n",
    "comp_csv_out = os.path.join('..', 'results', 'ml', 'model_comparison.csv')\n",
    "if not os.path.exists(os.path.dirname(comp_csv_out)):\n",
    "    comp_csv_out = os.path.join('results', 'ml', 'model_comparison.csv')\n",
    "df_benchmark_comp.to_csv(comp_csv_out, index=False, encoding='utf-8')\n",
    "print(f\"Exported multi-model benchmark comparison to: {comp_csv_out}\")\n"
]

nb['cells'].append({
    'cell_type': 'code',
    'execution_count': None,
    'metadata': {},
    'outputs': [],
    'source': code_source
})

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Updated {nb_path} successfully. Total cells now: {len(nb['cells'])}")
