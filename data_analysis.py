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

def analise(df):
    unique = df['patient_globalentryid'].nunique()

    df_no_dup= df.drop_duplicates('patient_globalentryid')
    if 'patient_sex_shortdesc' in df_no_dup.columns:
        gender_count = df_no_dup['patient_sex_shortdesc'].value_counts()
        with open(R"output_files\gender.txt",'wb') as filehandler:
            pickle.dump(gender_count, filehandler)

    if 'patientcard_packyears_packyearsvalue' in df_no_dup.columns:
        packyears_count = df_no_dup['patientcard_packyears_packyearsvalue'].value_counts()
        with open(R"output_files\packyears.txt", 'wb') as filehandler:
            pickle.dump(packyears_count, filehandler)

    # analiza paczkolat i innych wybranych cech -- przejrzec, wybrac

def loc_stats(df):
       df_working = df.drop_duplicates('patient_globalentryid')
       df_working['age'] = df_working['age'].astype(float)

       mean_age = round(df_working['age'].mean(), 1)
       mean_age_women = round(df_working[df_working['patient_sex_shortdesc'] == 'K']['age'].mean(), 1)
       mean_age_men = round(df_working[df_working['patient_sex_shortdesc'] == 'M']['age'].mean(), 1)
       median_age = df_working['age'].median()
       max_age = max(df_working['age'])
       min_age = min(df_working['age'])

       with open(R"output_files\loc_stat.txt", "w") as f:
              f.write(f"Mean age: {mean_age} \nMean age women: {mean_age_women}\nMean age men: {mean_age_men}\nMedian age: {median_age}\nMaximum age: {max_age}\nMinumum age: {min_age}\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)

    loc_stats(df)

    analise(df)

