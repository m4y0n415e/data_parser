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


def change_date_and_count(df_joined, date_cols):
        
        for col in df_joined.columns:
                if 'date' in col.lower():
                        df_joined[col] = pd.to_datetime(df_joined[col], format='mixed')
                        date_cols.append(col)
                
        return df_joined, date_cols


def add_age(df_joined):
        df_joined['age'] = np.floor((df_joined['reportdate_qual'] - df_joined['patient_birthdate']).dt.days / 365.25)
        return df_joined

def add_time_since_last_visit(df_joined):
       df_joined['unified_reportdate'] = (df_joined['reportdate_qual'].combine_first(df_joined['reportdate_ndtk'])).combine_first(df_joined['reportdate'])
       df_joined.sort_values(by=['patient_globalentryid', 'unified_reportdate'], inplace=True)
       df_joined['time_since_last_visit'] = (df_joined['unified_reportdate'] - (df_joined.groupby('patient_globalentryid')['unified_reportdate'].shift())).dt.days
       
       # df_patient = df_patient_profiles[df_patient_profiles['patient_globalentryid'] == 'fc7c260a-e902-49ff-b2a1-58bf25471937']
       # df_patient.to_csv('output.csv', columns=['reportdate_qual','reportdate_ndtk', 'reportdate', 'unified_reportdate'])
       df_joined.drop(labels='unified_reportdate', axis=1, inplace=True)
       return df_joined

def format_date(df_joined, date_cols):
        for col in date_cols:
                df_joined[col] = df_joined[col].dt.strftime("%Y-%m-%d")
        return df_joined


def fusion(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_joined = pd.concat(
               (df_kwalifikacyjne[['patient_globalentryid','reportdate', 'report_title']],
               df_NDTK[['patient_globalentryid','reportdate', 'report_title']],
               df_wynikowe[['patient_globalentryid','reportdate', 'report_title']])
        ) # continue from here

        # df_joined = pd.merge(
        # df_kwalifikacyjne, 
        # df_NDTK, 
        # on='patient_globalentryid',
        # how='inner',
        # suffixes=('_qual', '_ndtk')
        # )
        
        # df_joined = pd.merge(
        # df_joined,
        # df_wynikowe,
        # on='patient_globalentryid',
        # how='inner'
        # )

        return df_joined


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-q', '--qualification', 
                required=True, 
                help="Path to the qualification results .csv file"
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
                default=(R"..\output_files\final_database_select_test.csv"),
                help="Output filename"
        )

        args = parser.parse_args()

        df_qualification, df_ndtk, df_results = load_to_df(args.qualification, args.ndtk, args.results)

        df_patient_profiles = fusion(df_qualification, df_ndtk, df_results)

        # date_cols = []
        # df_patient_profiles, date_cols = change_date_and_count(df_patient_profiles, date_cols)

        # df_patient_profiles_new_col1 = add_age(df_patient_profiles)

        # df_patient_profiles_new_col2 = add_time_since_last_visit(df_patient_profiles_new_col1)

        # df_patient_profiles_fin = format_date(df_patient_profiles_new_col2, date_cols)

        df_patient_profiles.to_csv(args.output, index=False)