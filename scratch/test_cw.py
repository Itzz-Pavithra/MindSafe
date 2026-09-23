from scratch.test_ml_pipeline import X_train_b, y_train, X_test_b, y_test, classes
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score

for cw in [None, 'balanced', 'balanced_subsample']:
    rf = RandomForestClassifier(random_state=42, class_weight=cw)
    rf.fit(X_train_b, y_train)
    preds = rf.predict(X_test_b)
    acc = accuracy_score(y_test, preds)
    wf1 = f1_score(y_test, preds, average='weighted')
    mf1 = f1_score(y_test, preds, average='macro')
    print(f"class_weight={repr(cw)}: Acc={acc:.4f}, Weighted F1={wf1:.4f}, Macro F1={mf1:.4f}")
