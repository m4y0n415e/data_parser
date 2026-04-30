import argparse
import pandas as pd
from encoding import detect_encoding
import pickle
from scipy import stats
import statistics
import numpy as np


def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df


def analyse(df):
    df_no_dup = df.drop_duplicates('patient_globalentryid')

    if 'patient_sex_shortdesc' in df_no_dup.columns:
        gender_count = df_no_dup['patient_sex_shortdesc'].value_counts()
        with open(R"output_files/gender.txt",'wb') as filehandler:
            pickle.dump(gender_count, filehandler)

    if 'patientcard_packyears_packyearsvalue' in df_no_dup.columns:
        packyears_count = df_no_dup['patientcard_packyears_packyearsvalue'].value_counts()
        with open(R"output_files/packyears.txt", 'wb') as filehandler:
            pickle.dump(packyears_count, filehandler) 

    # possible to add: extracting all patients' ids with certain packyears values (negative) -- code below
    # negative_packyears = df_no_dup[df_no_dup['patientcard_packyears_packyearsvalue'].astype(float) < 0]
    # negative_packyears.to_csv("output_files/negative_packyears.csv", columns=['patient_globalentryid', 'patientcard_packyears_packyearsvalue'])

    if 'patientcard_smokingstatus' in df_no_dup.columns:
        smokingstatus = df_no_dup['patientcard_smokingstatus'].value_counts()
        with open(R"output_files/smokingstatus.txt", 'wb') as filehandler:
            pickle.dump(smokingstatus,filehandler) # possible to add: extracting all patients' ids with certain status

    if 'patientcard_attemptstoquit' in df_no_dup.columns:
        attempts = df_no_dup['patientcard_attemptstoquit'].value_counts()
        with open(R"output_files/attempts_to_quit.txt", 'wb') as filehandler:
            pickle.dump(attempts, filehandler) # possible to add: extracting all patients' ids with certain attempts counts

    pulmonary_disease_history_fam = df_no_dup[['patientcard_pulmonarycancersinfamily_parents', 'patientcard_pulmonarycancersinfamily_siblings',
    'patientcard_pulmonarycancersinfamily_children']] == "TRUE"

    no_history = 0
    is_history = 0

    history = pulmonary_disease_history_fam.any(axis=1).value_counts()

    no_history = history.get(0, 0)
    is_history = history.get(1, 0)

    # print("No pulmonary cancer history in family: ", no_history, "\n", "Pulmonary cancer diagnosed in family: ", is_history)

    # choroby płuc stwierdzone u pacjenta: patientcard_pulmonarydiseases_chronicobstructive ? patientcard_pulmonarydiseases_none ? patientcard_pulmonarydiseases_idiopathicpulmonaryfibrosis ?
    pulmonary_disease_history_pat = ['patientcard_pulmonarydiseases_idiopathicpulmonaryfibrosis','patientcard_pulmonarydiseases_chronicobstructive']
    pulmonary_pat = df_no_dup[pulmonary_disease_history_pat].value_counts()
    with open(R"output_files/pulmonary_diseases.txt", 'wb') as filehandler:
        pickle.dump(pulmonary_pat, filehandler)

    environmental_risks = ["patientcard_environmentalrisks_miner",
    "patientcard_environmentalrisks_ironmillworker",
    "patientcard_environmentalrisks_constructionworker",
    "patientcard_environmentalrisks_welder",
    "patientcard_environmentalrisks_stonemason",
    "patientcard_environmentalrisks_railwayman",
    "patientcard_environmentalrisks_roadworker",
    "patientcard_environmentalrisks_other",
    "patientcard_environmentalrisks_professionaldriver",
    "patientcard_environmentalrisks_carpenter",
    "patientcard_environmentalrisks_firefighter",
    "patientcard_environmentalrisksother"]
    
    ennvironmental_risks_count = df_no_dup[environmental_risks].value_counts()
    df_environmental_risks = pd.DataFrame(ennvironmental_risks_count)
    values = df_environmental_risks.sum(axis=1, skipna=True)
    values.to_csv("output_files/env_risks.csv")
    with open(R"output_files/environmental_risks.txt", 'wb') as filehandler:
        pickle.dump(values, filehandler)



def loc_stats(df):
        df_working = df.drop_duplicates('patient_globalentryid')
        df_working['age'] = df_working['age'].astype(float)
        df_working['patientcard_packyears_packyearsvalue'] = df_working['patientcard_packyears_packyearsvalue'].astype(float)

        mean_age = round(df_working['age'].mean(), 1)
        print("SD of age: ", statistics.stdev(df_working['age'].dropna(), xbar=mean_age))
        mean_age_women = round(df_working[df_working['patient_sex_shortdesc'] == 'K']['age'].mean(), 1)
        mean_age_men = round(df_working[df_working['patient_sex_shortdesc'] == 'M']['age'].mean(), 1)
        median_age = df_working['age'].median()
        max_age = max(df_working['age'])
        min_age = min(df_working['age'])

        mean_pack = round(df_working['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        print("SD of pack-years: ", statistics.stdev(df_working['patientcard_packyears_packyearsvalue'].dropna(), xbar=mean_pack))
        mean_pack_women = round(df_working[df_working['patient_sex_shortdesc'] == 'K']['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        mean_pack_men = round(df_working[df_working['patient_sex_shortdesc'] == 'M']['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        median_pack = df_working['patientcard_packyears_packyearsvalue'].dropna().median()
        max_pack = max(df_working['patientcard_packyears_packyearsvalue'])
        min_pack = min(df_working['patientcard_packyears_packyearsvalue'])

        with open(R"output_files/loc_stat.txt", "w") as f:
              f.write(f"Mean age: {mean_age}\nMean age women: {mean_age_women} \nMean age men: {mean_age_men}\nMedian age: {median_age}\nMaximum age: {max_age}\nMinumum age: {min_age}\n")
        with open(R"output_files/loc_stat.txt", "a") as f:
              f.write(f"\nMean packyears: {mean_pack}\nMean packyears women: {mean_pack_women} \nMean packyears men: {mean_pack_men}\nMedian packyears: {median_pack}\nMaximum packyears: {max_pack}\nMinumum packyears: {min_pack}\n")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the first input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)

    loc_stats(df)

    analise(df)

