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

# zaimplementowac selekccje -- aby zgadzal sie wiek i paczkolata! 50-74 i >20 paczkolat (wyciagnac te dane)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)