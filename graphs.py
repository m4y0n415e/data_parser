import argparse
import pandas as pd
from encoding import detect_encoding
import matplotlib.pyplot as plt
import numpy as np
from columns_selection import *
from profiling import *
import pickle

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def graphs(patient_profiles, gender):
        gender_count = pickle.load(gender)
        gender_counts = [gender_count.get('K', 0), gender_count.get('M', 0)]
        plt.bar(['Kobieta', 'Mężczyzna'], gender_counts)
        plt.title('Rozkład płci pacjentów w programie')
        plt.xlabel('Płeć')
        plt.ylabel('Liczba pacjentów')
        plt.savefig("gender_distribution.png")

        plt.clf()

        plt.hist(patient_profiles['age'], bins=10, rwidth=1)
        plt.title('Rozkład wieku pacjentów w programie')
        plt.xlabel('Wiek')
        plt.ylabel('Liczba pacjentów')
        plt.savefig("age_distribution.png")

        plt.clf()
        # piramida wieku i płci : back-to-back histogram

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    parser.add_argument(
          '-g', '--gender',
          required=True
    )

    args = parser.parse_args()

    df = load(args.input)

    graphs(df, args.gender)
