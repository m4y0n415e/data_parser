import argparse
import pandas as pd
import numpy as np
import chardet
from columns_selection import *

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.detector.UniversalDetector()
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

        size = df_kwal_no_dupl['patient_globalentryid'].nunique()
        with open(R"../output_files/selection_steps.txt", "w") as f:
              f.write(f"Number of unique ids before any processing of data: {size} \n")

        return df_kwal_no_dupl, df_NDTK, df_wynikowe

def change_date_and_count(df_initial, df_ndtk, df_consultation, date_cols):
        
        df_list = [df_initial, df_ndtk, df_consultation]

        for df in df_list:
                for col in df.columns:
                        if 'date' in col.lower():
                                df[col] = pd.to_datetime(df[col], format='mixed')
                                date_cols.add(col)
                
        return df_initial, df_ndtk, df_consultation, date_cols


def add_age(df):
        df['age'] = np.round(((df['reportdate'] - df['patient_birthdate']).dt.days / 365.25),1)
        return df

def selection1_age_and_packyears(df):
        # df_temp = df[df["entryprocess_qualificationdecision"] == "qualified"]
        # print(df_temp.shape)

        df_clean_age = df[(df['age'] >= 50.0) & (df['age'] < 75.0)]
        size = df_clean_age['patient_globalentryid'].nunique()
        with open(R"../output_files/selection_steps.txt", "a") as f:
                f.write(f"Number of unique ids after selecting the patients by their age (50-74): {size} \n")

        df_clean_packyears = df_clean_age[(df_clean_age['patientcard_packyears_packyearsvalue'] >= "20.0") | (df_clean_age['entryprocess_qualificationdecision'] == "qualified")]
        size = df_clean_packyears['patient_globalentryid'].nunique()
        with open(R"../output_files/selection_steps.txt", "a") as f:
                f.write(f"Number of unique ids after selecting patients by the number of packyears >= 20 yrs: {size} \n")

        return df_clean_packyears

def selection2_three_visits(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_joined = pd.concat(
               (df_kwalifikacyjne[['patient_globalentryid','reportdate', 'report_title', 'order_id']],
               df_NDTK[['patient_globalentryid','reportdate', 'report_title', 'order_id']],
               df_wynikowe[['patient_globalentryid','reportdate', 'report_title', 'order_id']])
        )

        df_grouped = df_joined.groupby("patient_globalentryid").filter(lambda x: x['report_title'].nunique() == 3)

        df_grouped_no_dup = df_grouped.drop_duplicates('patient_globalentryid')

        size = df_grouped_no_dup['patient_globalentryid'].shape
        with open(R"../output_files/selection_steps.txt", "a") as f:
              f.write(f"Number of unique ids after checking if patient has the three first necessary visits (initial, one NDTK examination and one visit to discuss consultation): {size} \n")

        return df_grouped

def add_time_since_last_visit(df, df_ndtk, df_consultation):
       df.sort_values(by=['patient_globalentryid', 'reportdate'], inplace=True)
       df['days_since_last_visit'] = (df['reportdate'] - (df.groupby('patient_globalentryid')['reportdate'].shift())).dt.days
       
       ndtk = df[df['report_title'] == 'SR_NDTK']
       consultation = df[df['report_title'] == 'SR_WIZYTA_WYNIKOWA']

       df_ndtk = pd.merge(df_ndtk, ndtk[['order_id', 'patient_globalentryid', 'days_since_last_visit']],
        on=['order_id', 'patient_globalentryid'],
        how='inner')
       df_consultation = pd.merge(df_consultation, consultation[['order_id', 'patient_globalentryid', 'days_since_last_visit']],
        on=['order_id', 'patient_globalentryid'],
        how='inner')

       df_ndtk.fillna({'days_since_last_visit': 0}, inplace=True)
       df_consultation.fillna({'days_since_last_visit': 0}, inplace=True)

       return df_ndtk, df_consultation

def add_time_since_program_start(df, df_ndtk, df_consultation):
        df.sort_values(by=['patient_globalentryid', 'reportdate'], inplace=True)
        baseline_dates = df.groupby('patient_globalentryid')['reportdate'].transform('min')
        df['days_since_initial_visit'] = (df['reportdate'] - baseline_dates).dt.days
        ndtk = df[df['report_title'] == 'SR_NDTK']
        consultation = df[df['report_title'] == 'SR_WIZYTA_WYNIKOWA']

        df_ndtk = pd.merge(df_ndtk, ndtk[['order_id', 'patient_globalentryid', 'days_since_initial_visit']],
         on=['order_id', 'patient_globalentryid'],
         how='inner')
        df_consultation = pd.merge(df_consultation, consultation[['order_id', 'patient_globalentryid', 'days_since_initial_visit']],
         on=['order_id', 'patient_globalentryid'],
         how='inner')

        df_ndtk.fillna({'days_since_initial_visit': 0}, inplace=True)
        df_consultation.fillna({'days_since_initial_visit': 0}, inplace=True)

        return df_ndtk, df_consultation


def format_date(df_initial, df_ndtk, df_consultation, date_cols):
        df_list = [df_initial, df_ndtk, df_consultation]
        for df in df_list:
                for col in date_cols:
                        if(col in df.columns):
                                df.loc[:, col] = df.loc[:, col].dt.strftime("%Y-%m-%d")
        return df_initial, df_ndtk, df_consultation
               

def draft_merge(df_initial, df_ndtk, df_consultation, output):
        df_joined = pd.merge(
        df_initial, 
        df_ndtk, 
        on='patient_globalentryid',
        how='inner',
        suffixes=('_qual', '_ndtk')
        )
        
        df_joined = pd.merge(
        df_joined,
        df_consultation,
        on='patient_globalentryid',
        how='inner'
        )
        
        df_joined.to_csv(output, index=False)

        return df_initial, df_ndtk, df_consultation


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-i', '--initial', 
                required=True, 
                help="Path to the initial consultation .csv file"
        )

        parser.add_argument(
                '-n', '--ndtk',
                required=True,
                help="Path to the NDTK consultation .csv file"
        )

        parser.add_argument(
                '-c', '--consultation',
                required=True,
                help="Path to the total consultation of the medical tests .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                default=(R"../output_files/selected_data_merged_newcolumn.csv"),
                help="Output filename"
        )

        args = parser.parse_args()

        df_initial, df_ndtk, df_consultation = load_to_df(args.initial, args.ndtk, args.consultation)

        date_cols = set()
        df_initial, df_ndtk, df_consultation, date_cols = change_date_and_count(df_initial, df_ndtk, df_consultation, date_cols)

        df_initial_w_age = add_age(df_initial)

        df_initial_selected = selection1_age_and_packyears(df_initial_w_age)

        df_grouped = selection2_three_visits(df_initial_selected, df_ndtk, df_consultation)

        df_ndtk_w_time_s, df_consultation_w_time_s = add_time_since_last_visit(df_grouped, df_ndtk, df_consultation)

        df_ndtk_start_time, df_consultation_start_time = add_time_since_program_start(df_grouped, df_ndtk_w_time_s, df_consultation_w_time_s)
        
        df_initial_f, df_ndtk_f, df_consultation_f = format_date(df_initial_selected, df_ndtk_start_time, df_consultation_start_time, date_cols)

        initial_fin, ndtk_fin, consultation_fin = draft_merge(df_initial_f, df_ndtk_f, df_consultation_f, args.output)

        #print(ndtk_fin['patient_globalentryid'].unique().shape)

        initial_fin.to_csv(R"../output_files/initial.csv", index=False)
        ndtk_fin.to_csv(R"../output_files/NDTK.csv", index=False)
        consultation_fin.to_csv(R"../output_files/consultation.csv", index=False)