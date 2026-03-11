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

# tu wrzucić do złożenia w strukturę 'patient_profile' wyselekcjonowaną pod kątem spełniających wszystkie kryteria pacjentów tabelę/tabele danych

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

#     parser.add_argument(
#             '-i1', '--input1', 
#             required=True, 
#             help="Path to the input .csv file to analise"
#     )

#     parser.add_argument(
#             '-i2', '--input2', 
#             required=True, 
#             help="Path to the input .csv file to analise"
#     )

    args = parser.parse_args()

    df = load(args.input)