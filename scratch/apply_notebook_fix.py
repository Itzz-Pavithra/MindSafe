import json
import os
import nbformat as nbf
from nbclient import NotebookClient

nb_path = os.path.join('notebook', '03_ml_training_evaluation.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 1. Update Cell 2 (index 2) so that SurveyFeaturePreprocessor is imported immediately after basic imports
cell2_source = [
    "import os\n",
    "import sys\n",
    "import json\n",
    "import joblib\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "from datetime import datetime\n",
    "\n",
    "# Ensure project root and models directory are accessible for custom preprocessor\n",
    "sys.path.insert(0, os.path.abspath('..'))\n",
    "sys.path.insert(0, os.path.abspath('.'))\n",
    "from models.preprocessor import SurveyFeaturePreprocessor\n",
    "\n",
    "# Matplotlib compatibility setup\n",
    "import matplotlib\n",
    "if not hasattr(matplotlib.rcParams, '_get'):\n",
    "    matplotlib.rcParams._get = matplotlib.rcParams.get\n",
    "import matplotlib.pyplot as plt\n",
    "\n",
    "from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate\n",
    "from sklearn.ensemble import RandomForestClassifier\n",
    "from sklearn.dummy import DummyClassifier\n",
    "from sklearn.metrics import (\n",
    "    accuracy_score, precision_score, recall_score, f1_score,\n",
    "    classification_report, confusion_matrix\n",
    ")\n",
    "import shap\n",
    "\n",
    "pd.set_option('display.max_columns', None)\n",
    "pd.set_option('display.float_format', lambda x: f'{x:.3f}')\n",
    "plt.style.use('default')\n",
    "\n",
    "print(\"Phase 3 ML environment initialized successfully.\")\n"
]
nb['cells'][2]['source'] = cell2_source

# 2. Update Cell 10 (index 10) to include defensive import verification
cell10_source = [
    "# 5.1 Preprocess Scenario B (Primary Model)\n",
    "try:\n",
    "    SurveyFeaturePreprocessor\n",
    "except NameError:\n",
    "    import os, sys\n",
    "    sys.path.insert(0, os.path.abspath('..'))\n",
    "    sys.path.insert(0, os.path.abspath('.'))\n",
    "    from models.preprocessor import SurveyFeaturePreprocessor\n",
    "\n",
    "prep_b = SurveyFeaturePreprocessor(scenario='B')\n",
    "prep_b.fit(df_train)\n",
    "X_train_b = prep_b.transform(df_train)\n",
    "X_test_b = prep_b.transform(df_test)\n",
    "\n",
    "# 5.2 Preprocess Scenario A (Full Benchmark)\n",
    "prep_a = SurveyFeaturePreprocessor(scenario='A')\n",
    "prep_a.fit(df_train)\n",
    "X_train_a = prep_a.transform(df_train)\n",
    "X_test_a = prep_a.transform(df_test)\n",
    "\n",
    "print(f\"Scenario B (Leakage-Controlled) Dimensions : Train {X_train_b.shape}, Test {X_test_b.shape}\")\n",
    "print(f\"Scenario A (Full Benchmark) Dimensions      : Train {X_train_a.shape}, Test {X_test_a.shape}\")\n"
]
nb['cells'][10]['source'] = cell10_source

# 3. Clean up any trailing empty cells
if len(nb['cells']) > 38 and len(nb['cells'][38]['source']) == 0:
    nb['cells'] = nb['cells'][:38]

# Save updated notebook
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"Notebook source updated. Total cells: {len(nb['cells'])}. Now executing from beginning...")
