import os
import glob
import json
import time
import numpy as np
import pandas as pd
import polars as pl
from catboost import CatBoostClassifier, Pool
import optuna

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, f1_score

# ==========================================================
# AegisNet Phase 1
# Intrusion Detection Engine (CatBoost Final Experiment)
# ==========================================================

DATASET_PATH = "/kaggle/input/datasets/dhoogla/csecicids2018/*.parquet"
OUTPUT_DIR = "aegisnet_phase1_outputs"

MAX_ROWS = 2_000_000
N_TRIALS = 20  

print("=" * 60)
print("Initializing AegisNet CatBoost Training Pipeline")
print("=" * 60)

# Create the dedicated output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Created/Verified output directory: ./{OUTPUT_DIR}/")

# ==========================================================
# Load and Merge Data
# ==========================================================

def load_data():

    print("=" * 60)
    print("Loading Dataset...")
    print("=" * 60)

    files = sorted(glob.glob(DATASET_PATH))

    if len(files) == 0:
        raise Exception(f"No parquet files found at {DATASET_PATH}")

    dfs = []

    for file in files:
        try:
            print(f"Loading {os.path.basename(file)}")
            df = pl.read_parquet(file)
            dfs.append(df)
        except Exception as e:
            print(f"Skipped {file}\n{e}")

    df = pl.concat(dfs, how="diagonal_relaxed")
    del dfs

    print(f"\nOriginal Shape: {df.shape}")

    # Clean column names
    df = df.rename({c: c.strip() for c in df.columns})

    if df.height > MAX_ROWS:
        print(f"Sampling {MAX_ROWS:,} rows from {df.height:,}")
        df = df.sample(n=MAX_ROWS, seed=42)

    cols_to_drop = [
        col for col in df.columns 
        if "source ip" in col.lower() 
        or "destination ip" in col.lower() 
        or "timestamp" in col.lower()
    ]

    print(f"\nDropping columns: {cols_to_drop}")
    if len(cols_to_drop) > 0:
        df = df.drop(cols_to_drop)

    df = df.fill_null(0)

    print("\nConverting to Pandas... This may take a few minutes...")
    pdf = df.to_pandas()

    numeric_cols = pdf.select_dtypes(include=[np.number]).columns
    pdf[numeric_cols] = pdf[numeric_cols].replace([np.inf, -np.inf], np.nan)
    pdf[numeric_cols] = pdf[numeric_cols].fillna(0)
    pdf = pdf.loc[:, ~pdf.columns.duplicated()]

    label_col = next((c for c in pdf.columns if c.lower() == "label"), None)
    if label_col is None:
        raise Exception(f"Label column not found.\n{pdf.columns}")

    # ------------------------------------------------------
    # MACRO-CLASS MERGING STRATEGY
    # ------------------------------------------------------
    print("\nApplying Macro-Class Merging Strategy...")
    
    mapping_dict = {
        "Benign": "Benign",
        "DDoS attacks-LOIC-HTTP": "DDoS",
        "DDOS attack-HOIC": "DDoS",
        "DDOS attack-LOIC-UDP": "DDoS",
        "DoS attacks-Hulk": "DoS",
        "DoS attacks-GoldenEye": "DoS",
        "DoS attacks-Slowloris": "DoS",
        "DoS attacks-SlowHTTPTest": "DoS",
        "Bot": "Bot",
        "Infilteration": "Infiltration",
        "SSH-Bruteforce": "Bruteforce",
        "FTP-BruteForce": "Bruteforce",
        "Brute Force -Web": "Web Attack",
        "Brute Force -XSS": "Web Attack",
        "SQL Injection": "Web Attack"
    }

    pdf[label_col] = pdf[label_col].map(mapping_dict)
    
    # Drop any unmapped rows just in case
    pdf = pdf.dropna(subset=[label_col])

    y = pdf[label_col]
    X = pdf.drop(columns=[label_col])

    feature_names = list(X.columns)
    feature_path = os.path.join(OUTPUT_DIR, "phase1_feature_names.json")
    with open(feature_path, "w") as f:
        json.dump(list(map(str, feature_names)), f, indent=4)

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    print("\nNew Macro-Class Distribution:")
    print(y.value_counts())
    print(f"\nFinal Shape: {X.shape}")

    return X, y_encoded, le


# ==========================================================
# Optuna Objective
# ==========================================================

def objective(trial, X_train, y_train, X_val, y_val):

    params = {
        "iterations": 1000,
        "loss_function": "MultiClass",
        "eval_metric": "TotalF1:average=Macro",
        "task_type": "GPU" if CatBoostClassifier().get_param('task_type') != 'CPU' else "CPU",
        "verbose": False,
        "auto_class_weights": "SqrtBalanced", 
        "od_type": "Iter",
        "od_wait": 50,
        
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "depth": trial.suggest_int("depth", 4, 10),
        "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 10),
        "random_strength": trial.suggest_float("random_strength", 0.1, 10.0, log=True),
        "bagging_temperature": trial.suggest_float("bagging_temperature", 0.0, 1.0)
    }

    train_pool = Pool(X_train, y_train)
    val_pool = Pool(X_val, y_val)

    model = CatBoostClassifier(**params)
    
    model.fit(
        train_pool,
        eval_set=val_pool
    )

    preds = model.predict(val_pool)
    score = f1_score(y_val, preds, average="macro")

    return score


# ==========================================================
# Main
# ==========================================================

def main():

    start = time.time()
    X, y, le = load_data()

    print("\nSplitting dataset...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    print("\nStarting Optuna Hyperparameter Tuning for CatBoost...")
    optuna.logging.set_verbosity(optuna.logging.INFO)
    study = optuna.create_study(direction="maximize")

    study.optimize(
        lambda trial: objective(trial, X_train, y_train, X_val, y_val),
        n_trials=N_TRIALS
    )

    print("\n" + "="*40)
    print("Best Macro F1 Score:", study.best_value)
    print("Best Params:", study.best_params)
    print("="*40)

    best_params = study.best_params
    best_params.update({
        "iterations": 1000, 
        "loss_function": "MultiClass",
        "task_type": "GPU" if CatBoostClassifier().get_param('task_type') != 'CPU' else "CPU",
        "verbose": 50,
        "auto_class_weights": "SqrtBalanced",
        "od_type": "Iter",
        "od_wait": 50
    })

    print("\nTraining Final AegisNet Model...")
    final_model = CatBoostClassifier(**best_params)
    
    final_model.fit(
        X_train, 
        y_train,
        eval_set=(X_val, y_val)
    )

    print("\nEvaluating Final Model on Test Set...")
    preds = final_model.predict(X_test)

    print("\n" + classification_report(y_test, preds, target_names=le.classes_, zero_division=0))

    # Save outputs to the dedicated folder
    model_path = os.path.join(OUTPUT_DIR, "phase1_catboost_model.cbm")
    final_model.save_model(model_path)
    print(f"\nSaved: {model_path}")

    mapping = {int(i): str(c) for i, c in enumerate(le.classes_)}
    mapping_path = os.path.join(OUTPUT_DIR, "phase1_label_mapping.json")
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=4)
    print(f"Saved: {mapping_path}")

    print(f"\nTotal Time: {(time.time()-start)/60:.2f} mins")

if __name__ == "__main__":
    main()