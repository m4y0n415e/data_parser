import numpy as np
from sklearn import linear_model
import argparse
import pandas as pd
from encoding import detect_encoding

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def str_to_bool(s):
   s.replace(["True", "False"],[1,0], inplace=True)
   return s

def log_regr_analysis(df):

    df['y_target'] = str_to_bool(df['is_diagnosed']).astype(int)

    df['sex_binary'] = pd.get_dummies(df['patient_sex_code'], drop_first=True, dtype=int)

    feature_columns = ['emphysema_present', 'age', 'patientcard_packyears_packyearsvalue', 'sex_binary']

    with open('output_files/regression_results.txt', 'w', encoding='utf-8') as f:
        f.write("Report: SISO regression\n")
        for col in feature_columns:
            f.write(f"\nAnalysis for {col} trait\n")
            subset = df[[col, 'y_target']].copy()

            subset_clean = subset.dropna()

            X = np.array(subset_clean[col].astype(float)).reshape(-1,1)
            y = np.array(subset_clean['y_target'].astype(int)).ravel()

            logr = linear_model.LogisticRegression()
            logr.fit(X,y)

            predicted = logr.predict_proba(X)

            beta = logr.coef_[0][0]
            odds_ratio = np.exp(beta)

            odds = np.exp(beta)

            f.write(f"Prediction [probability]: {predicted[:10]} ... (first 10 shown)\n")
            f.write(f"Beta (log-odds): {beta:.4f}\n")
            f.write(f"Odds Ratio (OR): {odds:.4f}\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--cancers_full',
        required=True
    )

    args = parser.parse_args()

    df = load(args.cancers_full)

    log_regr_analysis(df)
