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


def change_date_and_count(df_qualification, df_ndtk, df_results, date_cols):
        
        df_list = [df_qualification, df_ndtk, df_results]

        for df in df_list:
                for col in df.columns:
                        if 'date' in col.lower():
                                df[col] = pd.to_datetime(df[col], format='mixed')
                                date_cols.append(col)
                
        return df_qualification, df_ndtk, df_results, date_cols

def add_age(df):
        df['age'] = np.floor((df['reportdate_qual'] - df['patient_birthdate']).dt.days / 365.25)
        return df

def selection2(df):
       df_clean_age = df[(df['age'] >= 50) & (df['age'] <= 74)]
       df_clean_packyears = df_clean_age[()]
       print("Twoja mama")

def add_time_since_last_visit(df):
       df.sort_values(by=['patient_globalentryid', 'reportdate'], inplace=True)
       df['time_since_last_visit'] = (df['reportdate'] - (df.groupby('patient_globalentryid')['reportdate'].shift())).dt.days
       return df

def format_date(df_qualification, df_ndtk, df_results, date_cols):
        df_list = [df_qualification, df_ndtk, df_results]
        for df in df_list:
                for col in date_cols:
                        df[col] = df[col].dt.strftime("%Y-%m-%d")
                return df

def draft_merge(df_qualification, df_ndtk, df_results, output):
        df_joined = pd.merge(
        df_qualification, 
        df_ndtk, 
        on='patient_globalentryid',
        how='inner',
        suffixes=('_qual', '_ndtk')
        )
        
        df_joined = pd.merge(
        df_joined,
        df_results,
        on='patient_globalentryid',
        how='inner'
        )

        df_joined.to_csv(output, index=False)

def grouping_and_selection1(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_joined = pd.concat(
               (df_kwalifikacyjne[['patient_globalentryid','reportdate', 'report_title']],
               df_NDTK[['patient_globalentryid','reportdate', 'report_title']],
               df_wynikowe[['patient_globalentryid','reportdate', 'report_title']])
        )

        df_grouped = df_joined.groupby("patient_globalentryid").filter(lambda x: x['report_title'].nunique() == 3)

        # do dodania: wybór tylko tych w wieku 50-74 lat; > 20 paczkolat; oraz finalnie, tych, co dotrwali do końca programu 
        # (daty między wizytą kwal. lub ewentualnie ndtk (jak wyjdzie z timeline-u) a ostatnią zanotowaną wizytą to ok. 3 lata)
        # na każdym etapie selekcji, dodać zapis do pliku (append) rozmiaru tabeli danych (unique ids, które pozostają)

        # df_patient = df_grouped[df_grouped['patient_globalentryid'] == 'fc7c260a-e902-49ff-b2a1-58bf25471937']
        # df_patient.to_csv('output.csv', columns=['reportdate', 'report_title'])

        return df_grouped


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
                default=(R"..\output_files\database_select_draft.csv"),
                help="Output filename"
        )

        args = parser.parse_args()

        df_qualification, df_ndtk, df_results = load_to_df(args.qualification, args.ndtk, args.results)

        df_grouped = grouping_and_selection1(df_qualification, df_ndtk, df_results)

        date_cols = []
        df_qualification, df_ndtk, df_results = change_date_and_count(df_qualification, df_ndtk, df_results, date_cols)

        df_qualification_w_age = add_age(df_qualification)

        df_qualification_selected = selection2(df_qualification_w_age)

        df_ndtk_w_time_s, df_results_w_time_s = add_time_since_last_visit(df_ndtk, df_results)

        df_qualification_f, df_ndtk_f, df_results_f = format_date(df_ndtk_w_time_s, df_results_w_time_s, df_qualification_selected, date_cols)

        draft_merge(df_qualification_f, df_ndtk_f, df_results_f, args.output)