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

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the first input .csv file to analise"
    )

    parser.add_argument(
            '-in', '--init', 
            required=True
    )

    parser.add_argument(
            '-c', '--consult', 
            required=True
    )

    args = parser.parse_args()

    df = load(args.input)
    ndtk = load(args.init)
    consult = load(args.consult)

    joined = pd.merge(
        df, 
        ndtk, 
        on='patient_globalentryid',
        how='left',
        suffixes=['_ndtk', '_init']
    )
        
    joined = pd.merge(
        joined,
        consult,
        on='patient_globalentryid',
        how='left'
    )
    
    joined.to_csv("full_data_problem_cases.csv", index=False)
