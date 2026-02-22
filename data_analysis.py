import argparse
import pandas as pd
from encoding import detect_encoding
from columns_selection import *

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def analise(df):
    unique = df['patient_globalentryid'].nunique()
    print(unique)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)

    analise(df)


