import argparse
import pandas as pd
from encoding import detect_encoding
from merging.columns_selection import *
import pickle

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

    df_no_dup= df.drop_duplicates('patient_globalentryid')
    if 'patient_sex_shortdesc' in df_no_dup.columns:
        gender_count = df_no_dup['patient_sex_shortdesc'].value_counts()
        with open(R"output_files\gender.txt",'wb') as filehandler:
                pickle.dump(gender_count, filehandler)


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

