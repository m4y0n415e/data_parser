import argparse
import pandas as pd
import numpy as np
import chardet
from columns_selection import *
import pickle
import string as s

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']

def load_to_df(kwalifikacyjne, NDTK, wynikowe):
        coding = detect_encoding(kwalifikacyjne)
        try:
                df_kwalifikacyjne = pd.read_csv(kwalifikacyjne, encoding=coding, usecols=COLS_QUAL, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        try:
                df_NDTK = pd.read_csv(NDTK, encoding=coding, usecols=COLS_NDTK, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        try:
                df_wynikowe = pd.read_csv(wynikowe, encoding=coding, usecols=COLS_RES, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        
        df_kwal_no_dupl = df_kwalifikacyjne.drop_duplicates('patient_globalentryid')

        return df_kwal_no_dupl, df_NDTK, df_wynikowe


def change_date_and_count(df, date_cols):
        
        for col in df.columns:
                if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], format='mixed')
                        date_cols.append(col)
        return df


def add_age(df_joined):
        df_joined['age'] = np.round(((df_joined['reportdate'] - df_joined['patient_birthdate']).dt.days / 365.25),1)
        return df_joined


def format_date(df_joined, date_cols):
        for col in date_cols:
                df_joined[col] = df_joined[col].dt.strftime("%Y-%m-%d")
        return df_joined


def fusion(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_joined = pd.merge(
        df_kwalifikacyjne, 
        df_NDTK, 
        on='patient_globalentryid',
        how='left',
        suffixes=('_init', '_ndtk')
        )
        
        df_joined = pd.merge(
        df_joined,
        df_wynikowe,
        on='patient_globalentryid',
        how='left'
        )

        return df_joined


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-i', '--initial', 
                required=True, 
                help="Path to the initial results .csv file"
        )

        parser.add_argument(
                '-n', '--ndtk',
                required=True,
                help="Path to the NDTK results .csv file"
        )

        parser.add_argument(
                '-r', '--results',
                required=True,
                help="Path to the total results of the medical tests .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                default=(R"../output_files/full_data_merged_left.csv"),
                help="Output filename"
        )

        args = parser.parse_args()

        df_initial, df_ndtk, df_results = load_to_df(args.initial, args.ndtk, args.results)

        df_patient_profiles = fusion(df_initial, df_ndtk, df_results)

        date_cols = []
        df_patient_profiles = change_date_and_count(df_initial, date_cols)

        df_patient_profiles_new_col = add_age(df_patient_profiles)

        df_patient_profiles_fin = format_date(df_patient_profiles_new_col, date_cols)

        df_patient_profiles.to_csv(args.output, index=False)