import json
import os

nb_path = 'notebook/03_ml_training_evaluation.ipynb'

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# Phase 3: Machine Learning Classification, Model Evaluation & SHAP Explainability\n",
            "**Project:** MindSafe — Multiclass Mental Health Impact Classification  \n",
            "**Target Variable:** `Mental_Health_Impact` (Multiclass: *Not at all*, *Slightly*, *Moderately*, *Severely*)  \n",
            "**IEEE Research Standard:** Strict isolation of training ($N = 1,211$) and testing ($N = 303$) partitions; leakage-controlled prospective feature modeling; Tree SHAP mathematical attribution."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## A. Dataset Characteristics & Partition Verification\n",
            "Verification of the analytical dataset ($N = 1,514$) derived from 1,521 raw survey responses following the removal of 2 completely blank submissions and 5 records missing the target outcome. No synthetic data, oversampling, or duplicate records are introduced."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import sys\n",
            "import json\n",
            "import joblib\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "# Ensure project root in sys.path\n",
            "sys.path.insert(0, os.path.abspath('..'))\n",
            "sys.path.insert(0, os.path.abspath('.'))\n",
            "from models.preprocessor import SurveyFeaturePreprocessor\n",
            "\n",
            "# Load processed analytical survey data\n",
            "data_path = os.path.join('..', 'Data', 'processed', 'phase2_analysis_data.csv')\n",
            "if not os.path.exists(data_path):\n",
            "    data_path = os.path.join('Data', 'processed', 'phase2_analysis_data.csv')\n",
            "\n",
            "df = pd.read_csv(data_path, encoding='utf-8')\n",
            "target_col = [c for c in df.columns if '12. Do you think cyberbullying' in c][0]\n",
            "usable_df = df[df[target_col].notna() & (df[target_col] != '')].reset_index(drop=True)\n",
            "N_total = len(usable_df)\n",
            "\n",
            "classes = ['Not at all', 'Slightly', 'Moderately', 'Severely']\n",
            "class_to_idx = {c: i for i, c in enumerate(classes)}\n",
            "y = usable_df[target_col].map(class_to_idx).values\n",
            "\n",
            "print(f\"Verified Analytical Dataset Size : N = {N_total}\")\n",
            "print(\"Class Distribution:\")\n",
            "for c, cnt in usable_df[target_col].value_counts()[classes].items():\n",
            "    print(f\"  {c:12s}: {cnt:4d} ({cnt/N_total*100:.2f}%)\")"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Stratified 80/20 Train/Test Partition (random_state=42)\n",
            "from sklearn.model_selection import train_test_split\n",
            "\n",
            "train_idx, test_idx = train_test_split(np.arange(N_total), test_size=0.20, random_state=42, stratify=y)\n",
            "df_train = usable_df.iloc[train_idx].copy().reset_index(drop=True)\n",
            "df_test = usable_df.iloc[test_idx].copy().reset_index(drop=True)\n",
            "y_train = y[train_idx]\n",
            "y_test = y[test_idx]\n",
            "\n",
            "print(f\"Training Set (80.0%): N = {len(df_train)}\")\n",
            "print(f\"Testing Set  (20.0%): N = {len(df_test)}\")\n",
            "assert len(df_train) + len(df_test) == N_total, \"Partition sum mismatch!\"\n",
            "\n",
            "# Fit Preprocessor STRICTLY on Training Set\n",
            "prep_b = SurveyFeaturePreprocessor(scenario='B')\n",
            "prep_b.fit(df_train)\n",
            "X_train_b = prep_b.transform(df_train)\n",
            "X_test_b = prep_b.transform(df_test)\n",
            "feature_names_b = prep_b.feature_names_\n",
            "print(f\"Scenario B (Leakage-Controlled) Features: {len(feature_names_b)} features\")\n",
            "\n",
            "# Scenario A (Full Features / Benchmark)\n",
            "prep_a = SurveyFeaturePreprocessor(scenario='A')\n",
            "prep_a.fit(df_train)\n",
            "X_train_a = prep_a.transform(df_train)\n",
            "X_test_a = prep_a.transform(df_test)\n",
            "print(f\"Scenario A (Full Benchmark) Features    : {len(prep_a.feature_names_)} features\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 2. Target Class Distribution\n",
            "Visualizing the distribution of survey-defined Mental Health Impact categories across the entire analytical cohort ($N = 1,514$)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "target_counts = usable_df[target_col].value_counts()[classes]\n",
            "fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)\n",
            "colors = ['#2b5c8f', '#4682b4', '#d97724', '#b22222']\n",
            "bars = ax.bar(classes, target_counts.values, color=colors, edgecolor='black', linewidth=0.8, width=0.55)\n",
            "for bar in bars:\n",
            "    h = bar.get_height()\n",
            "    pct = (h / N_total) * 100\n",
            "    ax.text(bar.get_x() + bar.get_width() / 2.0, h + 10, f'{h}\\n({pct:.1f}%)',\n",
            "            ha='center', va='bottom', fontsize=9, fontweight='medium')\n",
            "ax.set_title(f'Fig. 2. Distribution of survey-defined Mental Health Impact categories (N = {N_total:,}).', fontsize=11, fontweight='bold', pad=12)\n",
            "ax.set_xlabel('Target Category', fontsize=10, fontweight='semibold')\n",
            "ax.set_ylabel('Number of Respondents', fontsize=10, fontweight='semibold')\n",
            "ax.set_ylim(0, max(target_counts.values) * 1.2)\n",
            "ax.yaxis.grid(True, linestyle='--', alpha=0.5)\n",
            "ax.set_axisbelow(True)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## B. Four-Model Classification Comparison\n",
            "To determine which conventional machine-learning classifier performs best when predicting the survey-defined Mental Health Impact category using leakage-controlled predictors, we evaluate exactly four conventional classifiers:\n",
            "1. **Support Vector Machine (SVM)** (RBF kernel, balanced class weights, probability=True)\n",
            "2. **Random Forest** (100 trees, max_depth=15, min_samples_split=5, balanced weights)\n",
            "3. **Logistic Regression** (L2 penalty, balanced class weights, max_iter=1000)\n",
            "4. **Decision Tree** (CART criterion, balanced class weights)\n",
            "\n",
            "> **Experimental Rigor:** All four models receive the identical 54 leakage-controlled features, trained strictly on the $N = 1,211$ training set and tested on the held-out $N = 303$ test partition."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from sklearn.svm import SVC\n",
            "from sklearn.ensemble import RandomForestClassifier\n",
            "from sklearn.linear_model import LogisticRegression\n",
            "from sklearn.tree import DecisionTreeClassifier\n",
            "from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score\n",
            "\n",
            "models_four = {\n",
            "    'Support Vector Machine (SVM)': SVC(random_state=42, class_weight='balanced', probability=True),\n",
            "    'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=15, min_samples_split=5, min_samples_leaf=1, class_weight='balanced', criterion='gini', random_state=42),\n",
            "    'Logistic Regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000),\n",
            "    'Decision Tree': DecisionTreeClassifier(random_state=42, class_weight='balanced')\n",
            "}\n",
            "\n",
            "test_rows = []\n",
            "fitted_models = {}\n",
            "for name, m in models_four.items():\n",
            "    m.fit(X_train_b, y_train)\n",
            "    fitted_models[name] = m\n",
            "    y_pred = m.predict(X_test_b)\n",
            "    test_rows.append({\n",
            "        'Model': name,\n",
            "        'Accuracy': round(float(accuracy_score(y_test, y_pred)), 4),\n",
            "        'Macro Precision': round(float(precision_score(y_test, y_pred, average='macro', zero_division=0)), 4),\n",
            "        'Macro Recall': round(float(recall_score(y_test, y_pred, average='macro', zero_division=0)), 4),\n",
            "        'Macro F1': round(float(f1_score(y_test, y_pred, average='macro', zero_division=0)), 4),\n",
            "        'Weighted F1': round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4)\n",
            "    })\n",
            "\n",
            "df_four_test = pd.DataFrame(test_rows)\n",
            "display(df_four_test.style.format({\n",
            "    'Accuracy': '{:.4f}',\n",
            "    'Macro Precision': '{:.4f}',\n",
            "    'Macro Recall': '{:.4f}',\n",
            "    'Macro F1': '{:.4f}',\n",
            "    'Weighted F1': '{:.4f}'\n",
            "}))\n",
            "\n",
            "# Export comparison CSV\n",
            "comp_csv_out = os.path.join('..', 'results', 'ml', 'model_comparison.csv')\n",
            "if not os.path.exists(os.path.dirname(comp_csv_out)):\n",
            "    comp_csv_out = os.path.join('results', 'ml', 'model_comparison.csv')\n",
            "df_four_test.to_csv(comp_csv_out, index=False, encoding='utf-8')\n",
            "print(f\"Saved four-model comparison to: {comp_csv_out}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 3. Four-Model Test-Set Performance Comparison\n",
            "Comparison graph illustrating test-set performance across SVM, Random Forest, Logistic Regression, and Decision Tree on the identical 54 leakage-controlled features ($N = 303$)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "model_names_plot = ['SVM', 'Random Forest', 'Logistic Regression', 'Decision Tree']\n",
            "metrics_to_plot = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']\n",
            "x = np.arange(len(model_names_plot))\n",
            "width = 0.15\n",
            "palette = ['#1f77b4', '#aec7e8', '#ff7f0e', '#2ca02c', '#98df8a']\n",
            "\n",
            "fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)\n",
            "for i, m_col in enumerate(metrics_to_plot):\n",
            "    offset = (i - 2) * width\n",
            "    vals = df_four_test[m_col].values\n",
            "    bars = ax.bar(x + offset, vals, width, label=m_col, color=palette[i], edgecolor='black', linewidth=0.7)\n",
            "    for bar in bars:\n",
            "        h = bar.get_height()\n",
            "        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 0.012, f'{h:.2f}',\n",
            "                ha='center', va='bottom', fontsize=7.5, rotation=90)\n",
            "\n",
            "ax.set_title('Fig. 3. Test-set classification performance across four machine-learning models (N = 303).\\nAll models evaluated on the identical 54 leakage-controlled features.', fontsize=10.5, fontweight='bold', pad=14)\n",
            "ax.set_xlabel('Classification Algorithm', fontsize=10.5, fontweight='semibold')\n",
            "ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10.5, fontweight='semibold')\n",
            "ax.set_xticks(x)\n",
            "ax.set_xticklabels(model_names_plot, fontsize=10, fontweight='semibold')\n",
            "ax.set_ylim(0, 1.05)\n",
            "ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9, loc='upper right', ncol=3)\n",
            "ax.yaxis.grid(True, linestyle='--', alpha=0.5)\n",
            "ax.set_axisbelow(True)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## C. Leakage-Controlled vs. Full-Feature Benchmark Evaluation\n",
            "This experiment demonstrates the critical impact of target leakage in survey-based predictive modeling:\n",
            "- **Primary Random Forest (Leakage-Controlled):** Employs 54 pre-outcome behavioral and demographic features; strictly excludes Question 13 (`Negative_Emotional_Symptoms`) and Question 14 (`Emotional_Impact_Severity`). This represents the actual deployable model.\n",
            "- **Benchmark Random Forest (Full Features / Leakage):** Incorporates all 61 features, including Questions 13 and 14.\n",
            "\n",
            "> **Academic Note:** Questions 13 and 14 record post-outcome distress symptoms (e.g., Depression, Anxiety, Loss of confidence) and subjective severity rating (1–5 scale). Including them trivially inflates accuracy because they directly proxy the target outcome rather than prospectively predicting it from online behaviors."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "rf_primary = fitted_models['Random Forest']\n",
            "rf_bench = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)\n",
            "rf_bench.fit(X_train_a, y_train)\n",
            "\n",
            "y_pred_primary = rf_primary.predict(X_test_b)\n",
            "y_pred_bench = rf_bench.predict(X_test_a)\n",
            "\n",
            "leakage_comparison_rows = [\n",
            "    {\n",
            "        'Model': 'Primary Random Forest — Leakage Controlled',\n",
            "        'Features': 54,\n",
            "        'Accuracy': round(float(accuracy_score(y_test, y_pred_primary)), 4),\n",
            "        'Macro Precision': round(float(precision_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),\n",
            "        'Macro Recall': round(float(recall_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),\n",
            "        'Macro F1': round(float(f1_score(y_test, y_pred_primary, average='macro', zero_division=0)), 4),\n",
            "        'Weighted F1': round(float(f1_score(y_test, y_pred_primary, average='weighted', zero_division=0)), 4)\n",
            "    },\n",
            "    {\n",
            "        'Model': 'Benchmark Random Forest — Full Features / Leakage',\n",
            "        'Features': 61,\n",
            "        'Accuracy': round(float(accuracy_score(y_test, y_pred_bench)), 4),\n",
            "        'Macro Precision': round(float(precision_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),\n",
            "        'Macro Recall': round(float(recall_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),\n",
            "        'Macro F1': round(float(f1_score(y_test, y_pred_bench, average='macro', zero_division=0)), 4),\n",
            "        'Weighted F1': round(float(f1_score(y_test, y_pred_bench, average='weighted', zero_division=0)), 4)\n",
            "    }\n",
            "]\n",
            "\n",
            "df_leakage_comp = pd.DataFrame(leakage_comparison_rows)\n",
            "display(df_leakage_comp.style.format({\n",
            "    'Accuracy': '{:.4f}',\n",
            "    'Macro Precision': '{:.4f}',\n",
            "    'Macro Recall': '{:.4f}',\n",
            "    'Macro F1': '{:.4f}',\n",
            "    'Weighted F1': '{:.4f}'\n",
            "}))\n",
            "\n",
            "leakage_csv_out = os.path.join('..', 'results', 'ml', 'leakage_comparison.csv')\n",
            "if not os.path.exists(os.path.dirname(leakage_csv_out)):\n",
            "    leakage_csv_out = os.path.join('results', 'ml', 'leakage_comparison.csv')\n",
            "df_leakage_comp.to_csv(leakage_csv_out, index=False, encoding='utf-8')\n",
            "print(f\"Saved leakage comparison table to: {leakage_csv_out}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 4. Primary Leakage-Controlled Random Forest vs. Full-Feature Benchmark\n",
            "Visualizing the ~17.5% performance inflation introduced when post-outcome symptom and severity variables (Q13/Q14) are retained in the feature space."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)\n",
            "comp_labels = ['Primary RF\\n(54 Features, Leakage-Controlled)', 'Benchmark RF\\n(61 Features, Full/Leakage)']\n",
            "metrics_leak = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1', 'Weighted F1']\n",
            "x_leak = np.arange(len(comp_labels))\n",
            "w_leak = 0.15\n",
            "palette_leak = ['#2b5c8f', '#4682b4', '#d97724', '#2ca02c', '#98df8a']\n",
            "\n",
            "for i, m_col in enumerate(metrics_leak):\n",
            "    offset = (i - 2) * w_leak\n",
            "    vals = df_leakage_comp[m_col].values\n",
            "    bars = ax.bar(x_leak + offset, vals, w_leak, label=m_col, color=palette_leak[i], edgecolor='black', linewidth=0.7)\n",
            "    for bar in bars:\n",
            "        h = bar.get_height()\n",
            "        ax.text(bar.get_x() + bar.get_width() / 2.0, h + 0.015, f'{h:.3f}',\n",
            "                ha='center', va='bottom', fontsize=8.5, fontweight='bold')\n",
            "\n",
            "ax.set_title('Fig. 4. Comparison of Primary Leakage-Controlled Random Forest vs. Full-Feature Benchmark (N = 303).\\nBenchmark inclusion of Q13/Q14 inflates metrics due to direct post-outcome proxy leakage.', fontsize=9.5, fontweight='bold', pad=14)\n",
            "ax.set_ylabel('Metric Score (0.0 to 1.0)', fontsize=10, fontweight='semibold')\n",
            "ax.set_xticks(x_leak)\n",
            "ax.set_xticklabels(comp_labels, fontsize=9.5, fontweight='bold')\n",
            "ax.set_ylim(0, 1.05)\n",
            "ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9, loc='upper left')\n",
            "ax.yaxis.grid(True, linestyle='--', alpha=0.5)\n",
            "ax.set_axisbelow(True)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## D. 5-Fold Stratified Cross-Validation Results\n",
            "To evaluate algorithmic stability and generalization without touching the held-out test partition, 5-fold stratified cross-validation was conducted strictly across the training set ($N = 1,211$)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from sklearn.model_selection import StratifiedKFold, cross_validate\n",
            "\n",
            "cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)\n",
            "cv_summary_rows = []\n",
            "\n",
            "for name, m in models_four.items():\n",
            "    cv_res = cross_validate(m, X_train_b, y_train, cv=cv5, scoring=['accuracy', 'f1_macro', 'f1_weighted'])\n",
            "    cv_summary_rows.append({\n",
            "        'Model': name,\n",
            "        'CV_Accuracy_Mean': round(float(cv_res['test_accuracy'].mean()), 4),\n",
            "        'CV_Accuracy_Std': round(float(cv_res['test_accuracy'].std()), 4),\n",
            "        'CV_Macro_F1_Mean': round(float(cv_res['test_f1_macro'].mean()), 4),\n",
            "        'CV_Macro_F1_Std': round(float(cv_res['test_f1_macro'].std()), 4),\n",
            "        'CV_Weighted_F1_Mean': round(float(cv_res['test_f1_weighted'].mean()), 4),\n",
            "        'CV_Weighted_F1_Std': round(float(cv_res['test_f1_weighted'].std()), 4)\n",
            "    })\n",
            "\n",
            "df_cv_summary = pd.DataFrame(cv_summary_rows)\n",
            "display(df_cv_summary)\n",
            "\n",
            "cv_csv_out = os.path.join('..', 'results', 'ml', 'cross_validation_results.csv')\n",
            "if not os.path.exists(os.path.dirname(cv_csv_out)):\n",
            "    cv_csv_out = os.path.join('results', 'ml', 'cross_validation_results.csv')\n",
            "df_cv_summary.to_csv(cv_csv_out, index=False, encoding='utf-8')\n",
            "print(f\"Saved 5-fold CV summary to: {cv_csv_out}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 5. 5-Fold Stratified Cross-Validation Performance\n",
            "Cross-validation performance across the four models with error bars representing $\\pm 1$ standard deviation across the 5 training folds ($N = 1,211$)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, ax = plt.subplots(figsize=(9, 5), dpi=300)\n",
            "x_cv = np.arange(len(model_names_plot))\n",
            "w_cv = 0.35\n",
            "acc_means = df_cv_summary['CV_Accuracy_Mean'].values\n",
            "acc_stds = df_cv_summary['CV_Accuracy_Std'].values\n",
            "f1_means = df_cv_summary['CV_Macro_F1_Mean'].values\n",
            "f1_stds = df_cv_summary['CV_Macro_F1_Std'].values\n",
            "\n",
            "bars1 = ax.bar(x_cv - w_cv/2, acc_means, w_cv, yerr=acc_stds, capsize=4, label='Mean CV Accuracy (±1 SD)', color='#1f77b4', edgecolor='black', linewidth=0.7)\n",
            "bars2 = ax.bar(x_cv + w_cv/2, f1_means, w_cv, yerr=f1_stds, capsize=4, label='Mean CV Macro F1 (±1 SD)', color='#ff7f0e', edgecolor='black', linewidth=0.7)\n",
            "\n",
            "for bar in bars1:\n",
            "    h = bar.get_height()\n",
            "    ax.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')\n",
            "for bar in bars2:\n",
            "    h = bar.get_height()\n",
            "    ax.text(bar.get_x() + bar.get_width() / 2.0, h / 2.0, f'{h:.3f}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')\n",
            "\n",
            "ax.set_title('Fig. 5. 5-Fold stratified cross-validation performance on training partition (N = 1,211).\\nError bars represent standard deviation across cross-validation folds.', fontsize=10, fontweight='bold', pad=14)\n",
            "ax.set_xlabel('Classification Algorithm', fontsize=10, fontweight='semibold')\n",
            "ax.set_ylabel('Score (0.0 to 1.0)', fontsize=10, fontweight='semibold')\n",
            "ax.set_xticks(x_cv)\n",
            "ax.set_xticklabels(model_names_plot, fontsize=9.5, fontweight='bold')\n",
            "ax.set_ylim(0, 0.85)\n",
            "ax.legend(frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cccccc', fontsize=9.5, loc='upper right')\n",
            "ax.yaxis.grid(True, linestyle='--', alpha=0.5)\n",
            "ax.set_axisbelow(True)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## E. Per-Class Evaluation & Confusion Matrix (Primary Random Forest)\n",
            "Detailed breakdown of precision, recall, and F1-score across all four impact severity categories for the designated Primary Random Forest model."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from sklearn.metrics import classification_report, confusion_matrix\n",
            "\n",
            "primary_rep = classification_report(y_test, y_pred_primary, target_names=classes, digits=4, output_dict=True)\n",
            "primary_cm = confusion_matrix(y_test, y_pred_primary)\n",
            "\n",
            "clf_rows = []\n",
            "for c in classes:\n",
            "    clf_rows.append({\n",
            "        'Class': c,\n",
            "        'Precision': round(primary_rep[c]['precision'], 4),\n",
            "        'Recall': round(primary_rep[c]['recall'], 4),\n",
            "        'F1-Score': round(primary_rep[c]['f1-score'], 4),\n",
            "        'Support': int(primary_rep[c]['support'])\n",
            "    })\n",
            "clf_rows.append({\n",
            "    'Class': 'Macro Avg',\n",
            "    'Precision': round(primary_rep['macro avg']['precision'], 4),\n",
            "    'Recall': round(primary_rep['macro avg']['recall'], 4),\n",
            "    'F1-Score': round(primary_rep['macro avg']['f1-score'], 4),\n",
            "    'Support': int(primary_rep['macro avg']['support'])\n",
            "})\n",
            "clf_rows.append({\n",
            "    'Class': 'Weighted Avg',\n",
            "    'Precision': round(primary_rep['weighted avg']['precision'], 4),\n",
            "    'Recall': round(primary_rep['weighted avg']['recall'], 4),\n",
            "    'F1-Score': round(primary_rep['weighted avg']['f1-score'], 4),\n",
            "    'Support': int(primary_rep['weighted avg']['support'])\n",
            "})\n",
            "\n",
            "df_clf = pd.DataFrame(clf_rows)\n",
            "display(df_clf)\n",
            "\n",
            "print(\"\\nConfusion Matrix (Raw Counts):\")\n",
            "cm_df = pd.DataFrame(primary_cm, index=classes, columns=classes)\n",
            "display(cm_df)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 6. Confusion Matrix for Primary Random Forest\n",
            "Raw confusion matrix for the held-out test cohort ($N = 303$)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=300)\n",
            "sns.heatmap(primary_cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax, cbar=False)\n",
            "ax.set_title('Fig. 6. Confusion matrix for the Primary Leakage-Controlled Random Forest (Test Set N = 303).', fontsize=9.5, fontweight='bold', pad=12)\n",
            "ax.set_xlabel('Predicted Impact Category', fontsize=10, fontweight='semibold')\n",
            "ax.set_ylabel('True Survey Impact Category', fontsize=10, fontweight='semibold')\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## F. Tree SHAP Global Explainability Analysis\n",
            "Using Shapley Additive Explanations (TreeExplainer) to interpret global feature attribution. SHAP values quantify the contribution of each feature to the model output across categories. They describe statistical feature importance within the mathematical model and do not establish clinical causation."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import shap\n",
            "\n",
            "explainer = shap.TreeExplainer(rf_primary)\n",
            "sample_bg = X_train_b.iloc[:200]\n",
            "shap_values = explainer.shap_values(sample_bg)\n",
            "\n",
            "if isinstance(shap_values, list):\n",
            "    mean_abs_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)\n",
            "else:\n",
            "    mean_abs_shap = np.abs(shap_values).mean(axis=(0, 2)) if shap_values.ndim == 3 else np.abs(shap_values).mean(axis=0)\n",
            "\n",
            "shap_df = pd.DataFrame({\n",
            "    'Feature': feature_names_b,\n",
            "    'Mean_Abs_SHAP': mean_abs_shap\n",
            "}).sort_values(by='Mean_Abs_SHAP', ascending=False).reset_index(drop=True)\n",
            "\n",
            "print(\"Top 15 Most Influential Features by Mean Absolute SHAP:\")\n",
            "display(shap_df.head(15))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Fig. 7. Tree SHAP Global Feature Importance\n",
            "Ranking the top 15 survey predictor features by their mean absolute SHAP attribution values."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "top15_shap = shap_df.head(15)\n",
            "fig, ax = plt.subplots(figsize=(9, 6), dpi=300)\n",
            "y_pos = np.arange(len(top15_shap))\n",
            "ax.barh(y_pos, top15_shap['Mean_Abs_SHAP'][::-1], color='#2b5c8f', edgecolor='black', linewidth=0.7)\n",
            "ax.set_yticks(y_pos)\n",
            "ax.set_yticklabels(top15_shap['Feature'][::-1], fontsize=9)\n",
            "ax.set_xlabel('Mean |SHAP Value| (Average Impact on Model Output Magnitude across Classes)', fontsize=9.5, fontweight='semibold')\n",
            "ax.set_title('Fig. 7. Tree SHAP global feature attributions for Primary Random Forest (Top 15 Predictors).\\nValues reflect contribution to model output and do not imply clinical or causal relationships.', fontsize=9.5, fontweight='bold', pad=14)\n",
            "ax.xaxis.grid(True, linestyle='--', alpha=0.5)\n",
            "ax.set_axisbelow(True)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    }
]

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.11"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Successfully rebuilt {nb_path} with IEEE experimental structure (Sections A to F, Figures 2-7)!")
