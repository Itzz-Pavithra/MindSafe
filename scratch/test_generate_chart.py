import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load exact values from model_comparison.csv
csv_path = os.path.join('results', 'ml', 'model_comparison.csv')
df = pd.read_csv(csv_path)

# Label mapping to display "(Primary)" and "(Baseline)" if desired
model_display_names = {
    'Logistic Regression': 'Logistic\nRegression',
    'Decision Tree': 'Decision\nTree',
    'Support Vector Machine (SVM)': 'Support Vector\nMachine (SVM)',
    'Random Forest': 'Random Forest\n(Primary)',
    'Dummy Classifier': 'Dummy Classifier\n(Baseline)'
}

df['Display_Name'] = df['Model'].map(lambda x: model_display_names.get(x, x))

metrics = ['Accuracy', 'Macro Precision', 'Macro Recall', 'Macro F1']
x = np.arange(len(df))  # 5 models
bar_width = 0.18

# Academic grayscale / B&W tones with crisp borders
# Differentiated with shades and subtle hatching for IEEE publication standards
styles = [
    {'color': '#2b2b2b', 'hatch': '', 'label': 'Accuracy'},
    {'color': '#6e6e6e', 'hatch': '///', 'label': 'Macro Precision'},
    {'color': '#a8a8a8', 'hatch': '\\\\\\', 'label': 'Macro Recall'},
    {'color': '#e2e2e2', 'hatch': 'xx', 'label': 'Macro F1'}
]

fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

for i, (m_col, style) in enumerate(zip(metrics, styles)):
    offset = (i - 1.5) * bar_width
    bars = ax.bar(
        x + offset,
        df[m_col],
        width=bar_width,
        label=style['label'],
        color=style['color'],
        hatch=style['hatch'],
        edgecolor='black',
        linewidth=0.8,
        zorder=3
    )
    
    # Add numerical value on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.015,
            f'{height:.2f}',
            ha='center',
            va='bottom',
            fontsize=8,
            fontweight='medium',
            color='black'
        )

# Styling for academic standards
ax.set_title('Comparison of Test-Set Performance Across Machine-Learning Models', fontsize=12, fontweight='bold', pad=15)
ax.set_xlabel('Model', fontsize=11, fontweight='semibold', labelpad=10)
ax.set_ylabel('Score (0–1)', fontsize=11, fontweight='semibold')
ax.set_xticks(x)
ax.set_xticklabels(df['Display_Name'], fontsize=9.5)
ax.set_ylim(0, 1.05)
ax.set_yticks(np.arange(0.0, 1.1, 0.2))

# Horizontal grid behind bars
ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#aaaaaa', zorder=0)
ax.set_axisbelow(True)

# Clean legend
ax.legend(
    loc='upper left',
    bbox_to_anchor=(0.02, 0.98),
    frameon=True,
    framealpha=0.9,
    edgecolor='#888888',
    fontsize=9.5
)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#333333')
ax.spines['bottom'].set_color('#333333')

plt.tight_layout()

out_path = os.path.join('results', 'ml', 'model_comparison_bar_chart.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved successfully to {out_path}")
