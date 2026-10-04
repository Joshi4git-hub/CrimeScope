import os
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_prep import get_processed_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_FILES = {
    "RandomForest": os.path.join(MODEL_DIR, "random_forest.joblib"),
    "LogisticRegression": os.path.join(MODEL_DIR, "logistic_regression.joblib"),
    "DecisionTree": os.path.join(MODEL_DIR, "decision_tree.joblib")
}

METRICS_FILE = os.path.join(MODEL_DIR, "model_metrics.joblib")

FEATURES_NUM = ["hour", "day_of_week_num", "month", "district", "community_area", "latitude", "longitude"]
FEATURES_BOOL = ["is_weekend"]
TARGET_COL = "primary_type_clean"

def train_and_eval_models(df=None, force_retrain=False):
    """
    Trains RandomForest, LogisticRegression, and DecisionTree models on crime features.
    Saves models and metrics to /models/.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Check if cached metrics and models exist
    if not force_retrain and os.path.exists(METRICS_FILE):
        all_exist = all(os.path.exists(path) for path in MODEL_FILES.values())
        if all_exist:
            try:
                metrics_data = joblib.load(METRICS_FILE)
                return metrics_data
            except Exception:
                pass
                
    if df is None:
        df = get_processed_data()
        
    # Sample up to 60,000 rows for training speed if larger
    if len(df) > 60000:
        df_sample = df.sample(n=60000, random_state=42)
    else:
        df_sample = df.copy()
        
    X = df_sample[FEATURES_NUM + FEATURES_BOOL]
    y = df_sample[TARGET_COL]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    classes = np.unique(y)
    
    # Preprocessor pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURES_NUM),
            ("bool", "passthrough", FEATURES_BOOL)
        ]
    )
    
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=16, random_state=42, class_weight="balanced", n_jobs=-1
        ),
        "LogisticRegression": LogisticRegression(
            max_iter=1000, random_state=42, class_weight="balanced"
        ),
        "DecisionTree": DecisionTreeClassifier(
            max_depth=14, random_state=42, class_weight="balanced"
        )
    }
    
    results = {}
    
    for model_name, clf in models.items():
        start_time = time.time()
        
        pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", clf)
        ])
        
        pipeline.fit(X_train, y_train)
        train_time = round(time.time() - start_time, 3)
        
        y_pred = pipeline.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
        
        cm = confusion_matrix(y_test, y_pred, labels=classes)
        
        # Feature importances if available
        feature_importances = None
        if hasattr(clf, "feature_importances_"):
            feature_importances = dict(zip(FEATURES_NUM + FEATURES_BOOL, clf.feature_importances_))
            
        results[model_name] = {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "train_time": train_time,
            "confusion_matrix": cm.tolist(),
            "classes": classes.tolist(),
            "feature_importances": feature_importances
        }
        
        # Save trained pipeline model
        joblib.dump(pipeline, MODEL_FILES[model_name])
        
    joblib.dump(results, METRICS_FILE)
    return results

def predict_crime_category(hour, day_of_week_num, month, district, community_area=0, latitude=41.8781, longitude=-87.6298, model_name="RandomForest"):
    """
    Predicts crime primary type given spatio-temporal inputs.
    """
    model_path = MODEL_FILES.get(model_name, MODEL_FILES["RandomForest"])
    if not os.path.exists(model_path):
        train_and_eval_models()
        
    pipeline = joblib.load(model_path)
    
    is_weekend = bool(day_of_week_num >= 5)
    
    input_df = pd.DataFrame([{
        "hour": int(hour),
        "day_of_week_num": int(day_of_week_num),
        "month": int(month),
        "district": int(district),
        "community_area": int(community_area),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "is_weekend": is_weekend
    }])
    
    probs = pipeline.predict_proba(input_df)[0]
    classes = pipeline.classes_
    
    top5_indices = np.argsort(probs)[::-1][:5]
    
    top5_probs = [
        {"category": classes[i], "probability": round(float(probs[i]), 4)}
        for i in top5_indices
    ]
    
    top_prediction = classes[top5_indices[0]]
    
    return {
        "predicted_category": top_prediction,
        "top_probabilities": top5_probs
    }

if __name__ == "__main__":
    print("Training models...")
    res = train_and_eval_models(force_retrain=True)
    print("Results summary:")
    for name, m in res.items():
        print(f"{name}: Accuracy={m['accuracy']}, F1={m['f1_score']}, TrainTime={m['train_time']}s")
