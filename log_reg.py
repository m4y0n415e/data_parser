import numpy
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

    modified_cancer_diagosed = str_to_bool(df['is_diagnosed'])
    X = numpy.array(df['emphysema_present'].astype(int)).reshape(-1,1)
    y = numpy.array(modified_cancer_diagosed.astype(int)).ravel()

    logr = linear_model.LogisticRegression()
    logr.fit(X,y)

    predicted = logr.predict(X)
    print(predicted)

    log_odds = logr.coef_
    odds = numpy.exp(log_odds)
    print(odds) 

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-c', '--cancers_full',
        required=True
    )

    args = parser.parse_args()

    df = load(args.cancers_full)

    log_regr_analysis(df)
