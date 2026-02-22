import argparse
import pandas as pd
from encoding import detect_encoding
import matplotlib.pyplot as plt
import string as s
import numpy as np
from columns_selection import *

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
        
        df_kwalifikacyjne['patient_globalentryid'].drop_duplicates()

        return df_kwalifikacyjne, df_NDTK, df_wynikowe


def fusion(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_patient_profiles = pd.merge(
        df_kwalifikacyjne, 
        df_NDTK, 
        on='patient_globalentryid',
        how='inner',
        suffixes=('_qual', '_ndtk')
        )
        
        df_patient_profiles = pd.merge(
        df_patient_profiles,
        df_wynikowe,
        on='patient_globalentryid',
        how='inner'
        )

        return df_patient_profiles

def change_date_count_add_column(df_patient_profiles):
       
        date_cols = []
        gender_count = 0
        for col in df_patient_profiles.columns:
                if 'date' in col.lower():
                        df_patient_profiles[col] = pd.to_datetime(df_patient_profiles[col], format='mixed')
                        date_cols.append(col)
                elif col == 'patient_sex_shortdesc':
                        gender_count = df_patient_profiles[col].value_counts()

        df_patient_profiles['age'] = round((df_patient_profiles['reportdate_qual'] - df_patient_profiles['patient_birthdate']).dt.days / 365.25)

        for col in date_cols:
                df_patient_profiles[col] = df_patient_profiles[col].dt.strftime("%Y-%m-%d")

        return df_patient_profiles, gender_count

def graphs(patient_profiles, gender_count):
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
        # piramida wieku i płci?


def loc_stats(patient_profiles):
       mean_age = round(patient_profiles['age'].mean(), 1)
       mean_age_women = round(patient_profiles[patient_profiles['patient_sex_shortdesc'] == 'K']['age'].mean(), 1)
       mean_age_men = round(patient_profiles[patient_profiles['patient_sex_shortdesc'] == 'M']['age'].mean(), 1)
       median_age = patient_profiles['age'].median()
       max_age = max(patient_profiles['age'])
       min_age = min(patient_profiles['age'])

       with open("loc_stat.txt", "w") as f:
              f.write(f"Mean age: {mean_age} \nMean age women: {mean_age_women}\nMean age men: {mean_age_men}\nMedian age: {median_age}\nMaximum age: {max_age}\nMinumum age: {min_age}\n")


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
                default="final_database.csv",
                help="Output filename"
        )

        args = parser.parse_args()

        df_qualification, df_ndtk, df_results = load_to_df(args.qualification, args.ndtk, args.results)

        patient_profiles_no_age = fusion(df_qualification, df_ndtk, df_results)

        patient_profiles, gender_count = change_date_count_add_column(patient_profiles_no_age)

        graphs(patient_profiles, gender_count)

        loc_stats(patient_profiles)

        patient_profiles.to_csv(args.output, index=False, na_rep = 'Brak danych')