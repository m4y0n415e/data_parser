import argparse
import pandas as pd
import numpy as np
import chardet
from columns_selection import *

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

        size = df_kwal_no_dupl['patient_globalentryid'].nunique()
        with open(R"..\output_files\selection_steps.txt", "w") as f:
              f.write(f"Before first selection: {size} \n")

        return df_kwal_no_dupl, df_NDTK, df_wynikowe

def change_date_and_count(df_qualification, df_ndtk, df_results, date_cols):
        
        df_list = [df_qualification, df_ndtk, df_results]

        for df in df_list:
                for col in df.columns:
                        if 'date' in col.lower():
                                df[col] = pd.to_datetime(df[col], format='mixed')
                                date_cols.add(col)
                
        return df_qualification, df_ndtk, df_results, date_cols

def grouping_and_selection1(df_kwalifikacyjne, df_NDTK, df_wynikowe):
        df_joined = pd.concat(
               (df_kwalifikacyjne[['patient_globalentryid','reportdate', 'report_title', 'order_id']],
               df_NDTK[['patient_globalentryid','reportdate', 'report_title', 'order_id']],
               df_wynikowe[['patient_globalentryid','reportdate', 'report_title', 'order_id']])
        )

        df_grouped = df_joined.groupby("patient_globalentryid").filter(lambda x: x['report_title'].nunique() == 3)

        return df_grouped

def add_age(df):
        df['age'] = np.round(((df['reportdate'] - df['patient_birthdate']).dt.days / 365.25),1)
        return df

def selection2(df):
       df_clean_age = df[(df['age'] >= 50.0) & (df['age'] <= 74.0)]
       size = df_clean_age['patient_globalentryid'].nunique()
       with open(R"..\output_files\selection_steps.txt", "a") as f:
              f.write(f"After age selection: {size} \n")

       df_clean_packyears = df_clean_age[(df_clean_age['patientcard_packyears_packyearsvalue'] >= "20.0") & (df_clean_age['entryprocess_qualificationdecision'] == "qualified")]
       size = df_clean_packyears['patient_globalentryid'].nunique()
       with open(R"..\output_files\selection_steps.txt", "a") as f:
              f.write(f"After packyears selection: {size} \n")

       return df_clean_packyears

def add_time_since_last_visit(df, df_ndtk, df_results):
       df.sort_values(by=['patient_globalentryid', 'reportdate'], inplace=True)
       df['days_since_last_visit'] = (df['reportdate'] - (df.groupby('patient_globalentryid')['reportdate'].shift())).dt.days
       
       ndtk = df[df['report_title'] == 'SR_NDTK']
       results = df[df['report_title'] == 'SR_WIZYTA_WYNIKOWA']

       df_ndtk = pd.merge(df_ndtk, ndtk[['order_id', 'patient_globalentryid', 'days_since_last_visit']],
        on=['order_id', 'patient_globalentryid'],
        how='inner')
       df_results = pd.merge(df_results, results[['order_id', 'patient_globalentryid', 'days_since_last_visit']],
        on=['order_id', 'patient_globalentryid'],
        how='inner')

       df_ndtk['days_since_last_visit'].fillna(0, inplace=True)
       df_results['days_since_last_visit'].fillna(0, inplace=True)

       return df_ndtk, df_results

def format_date(df_qualification, df_ndtk, df_results, date_cols):
        df_list = [df_qualification, df_ndtk, df_results]
        for df in df_list:
                for col in date_cols:
                        if(col in df.columns):
                                df.loc[:, col] = df.loc[:, col].dt.strftime("%Y-%m-%d")
        return df_qualification, df_ndtk, df_results

# def completed_full_programme(df_ndtk, df_results):
#         df_ndtk_selected = [df_ndtk['days_since_last_visit'] >= 300.0]

#       do dodania: finalnie, wybór tych, co dotrwali do końca programu 
#       (daty między wizytą kwal. lub ewentualnie ndtk (jak wyjdzie z timeline-u) a ostatnią zanotowaną wizytą to ok. 3 lata)

               

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

        size = df_joined['patient_globalentryid'].nunique()
        with open(R"..\output_files\selection_steps.txt", "a") as f:
              f.write(f"After checking if patient has the three necessary visits: {size} \n")

        df_joined.to_csv(output, index=False)


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

        date_cols = set()
        df_qualification, df_ndtk, df_results, date_cols = change_date_and_count(df_qualification, df_ndtk, df_results, date_cols)

        df_grouped = grouping_and_selection1(df_qualification, df_ndtk, df_results)

        df_qualification_w_age = add_age(df_qualification)

        df_qualification_selected = selection2(df_qualification_w_age)

        df_ndtk_w_time_s, df_results_w_time_s = add_time_since_last_visit(df_grouped, df_ndtk, df_results)

        # completed_full_programme(df_ndtk_w_time_s, df_results_w_time_s)

        df_qualification_f, df_ndtk_f, df_results_f = format_date(df_qualification_selected, df_ndtk_w_time_s, df_results_w_time_s, date_cols)

        draft_merge(df_qualification_f, df_ndtk_f, df_results_f, args.output)

        df_qualification_f.to_csv(R"..\output_files\qualification.csv", index=False)
        df_ndtk_f.to_csv(R"..\output_files\NDTK.csv", index=False)
        df_results_f.to_csv(R"..\output_files\results.csv", index=False)