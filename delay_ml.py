#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import os


def main():
    # --- 1. Data Loading & Type Conversion ---
    print("--- 1. Loading Data ---")

    # Define file path
    file_path = "merged_arrivals_cleand.csv"

    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at {file_path}")
        return

    # Load the arrivals CSV, recognizing "NA" as missing values
    # low_memory=False helps with mixed type warnings
    df2 = pd.read_csv(file_path, sep=";", na_values="NA", low_memory=False)

    # Date format used in the file (DD.MM.YYYY HH:MM)
    date_format = '%d.%m.%Y %H:%M'

    # Convert time columns to datetime objects
    print("Converting timestamps...")
    time_cols = ['STA', 'ATA', 'SDT']
    for col in time_cols:
        df2[f'{col}_dt'] = pd.to_datetime(df2[col], format=date_format, errors='coerce')

    # Convert delay column to numeric
    df2['DLY_min'] = pd.to_numeric(df2['DLY_min'], errors='coerce')

    print("Data Info after conversion:")
    print(df2.info())

    # --- 2. Data Cleaning & Target Variable ---
    print("\n--- 2. Data Cleaning & Target Definition ---")

    # Remove rows where critical timestamps or delay info is missing
    df_model = df2.dropna(subset=['STA_dt', 'SDT_dt', 'DLY_min']).copy()

    # Define Target: "Delayed" defined as > 15 minutes
    DELAY_THRESHOLD = 15
    df_model['Ist_Verspaetet'] = (df_model['DLY_min'] > DELAY_THRESHOLD).astype(int)

    # Check distribution
    print("\nTarget Variable Distribution (0=On Time, 1=Delayed):")
    print(df_model['Ist_Verspaetet'].value_counts(normalize=True))

    # --- 3. Feature Engineering ---
    print("\n--- 3. Feature Engineering ---")

    # Time-based features from Scheduled Arrival (STA)
    df_model['Geplant_Ankunft_Stunde'] = df_model['STA_dt'].dt.hour
    df_model['Geplant_Ankunft_TagDerWoche'] = df_model['STA_dt'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_model['Geplant_Ankunft_Monat'] = df_model['STA_dt'].dt.month

    # Flight duration (Scheduled Arrival - Scheduled Departure) in minutes
    df_model['Geplante_Flugdauer_Min'] = (df_model['STA_dt'] - df_model['SDT_dt']).dt.total_seconds() / 60

    # Passenger count
    df_model['PAX'] = pd.to_numeric(df_model['PAX'], errors='coerce')

    # --- 4. Preprocessing for Model ---
    print("\n--- 4. Preprocessing for Model ---")

    # Select Features
    features_numeric = [
        'Geplant_Ankunft_Stunde',
        'Geplant_Ankunft_TagDerWoche',
        'Geplant_Ankunft_Monat',
        'Geplante_Flugdauer_Min',
        'PAX'
    ]

    features_categorical = [
        'FLC',  # Airline
        'ORG',  # Origin Airport
        'TYP',  # Aircraft Type
        'NAT',  # Flight Nature
        'TER'  # Terminal
    ]

    TARGET_VAR = 'Ist_Verspaetet'

    # Filter dataframe
    df_final = df_model[features_numeric + features_categorical + [TARGET_VAR]].copy()

    # Imputation (Filling missing values)
    # Numeric: Median
    for col in features_numeric:
        median_val = df_final[col].median()
        df_final[col] = df_final[col].fillna(median_val)

    # Categorical: 'Unbekannt' (Unknown)
    for col in features_categorical:
        df_final[col] = df_final[col].fillna('Unbekannt')

    # One-Hot Encoding for categorical variables
    print("Encoding categorical features...")
    X_categorical = pd.get_dummies(df_final[features_categorical], drop_first=True)

    # Combine features
    X = pd.concat([df_final[features_numeric], X_categorical], axis=1)
    y = df_final[TARGET_VAR]

    # Split Data (80% Train, 20% Test)
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Training Data Shape: {X_train.shape}")
    print(f"Test Data Shape: {X_test.shape}")

    # --- 5. Model Training ---
    print("\n--- 5. Training Random Forest ---")

    # Initialize Model
    # class_weight='balanced' handles the imbalance between on-time/delayed
    # n_jobs=-1 uses all CPU cores
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    print("Training finished!")

    # --- 6. Evaluation ---
    print("\n--- 6. Evaluation ---")

    y_pred = model.predict(X_test)

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")

    print("\n--- Classification Report ---")
    # Note: 0 = Pünktlich (On Time), 1 = Verspätet (Delayed)
    print(classification_report(y_test, y_pred, target_names=['On Time (0)', 'Delayed (1)']))

    # Confusion Matrix Plot
    print("\nGenerating Confusion Matrix Plot...")
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Pred: On Time', 'Pred: Delayed'],
                yticklabels=['True: On Time', 'True: Delayed'])
    plt.title("Confusion Matrix")
    plt.ylabel('Actual')
    plt.xlabel('Predicted')

    # Check if we are in a non-interactive environment (optional safety)
    try:
        plt.show()
    except Exception as e:
        print("Could not display plot directly (headless environment?).")
        print("Saving plot to 'confusion_matrix.png' instead.")
        plt.savefig('confusion_matrix.png')


if __name__ == "__main__":
    main()