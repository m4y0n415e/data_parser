import argparse
import pandas as pd
from encoding import detect_encoding

def load(input1, input2):
    coding = detect_encoding(input1)
    try:
            df1 = pd.read_csv(input1, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    try:
            df2 = pd.read_csv(input2, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df1, df2

def compare(df1, df2):
    df1['has_required_visits'] = df1['patient_globalentryid'].isin(df2['patient_globalentryid'])
    return df1

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input1', 
            required=True, 
            help="Path to the non-selective input .csv file to modify"
    )

    parser.add_argument(
            '-j', '--input2', 
            required=True, 
            help="Path to the selective input .csv file"
    )

    args = parser.parse_args()

    df1, df2 = load(args.input1, args.input2)

    df_final = compare(df1, df2)

    df_final.to_csv(R"output_files\database_final_cols.csv")

