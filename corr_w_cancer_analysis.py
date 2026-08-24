import argparse
import pandas as pd
from tabulate import tabulate
from encoding import detect_encoding

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def extract_diagnosed(df, cancers):
# function that extracts the data of the cancer-diagnosed patients into a separate table, using the full ndtk.csv data table and the 'Acession Number' key
# to match the patients
    diagnosed_w = df[df['externalbusinessid_client'].isin(cancers['Accession_Number'])]
    # diagnosed_w.to_csv("diagnosed_with_cancer_data")
    diagnosed_w = diagnosed_w.drop_duplicates("patient_globalentryid")
    
    return diagnosed_w


def modify(ndtk, ndtk_unmodified):
# function that serves to modify the ndtk.csv file, so it contains the 'age' and 'packyears value' columns (which only appear once in the initial visit data)
    ndtk_unmodified['age'] = ndtk['age']
    ndtk_unmodified['patientcard_packyears_packyearsvalue'] = ndtk['patientcard_packyears_packyearsvalue']

    modified_ndtk = ndtk_unmodified[ndtk_unmodified['patient_globalentryid'].isin(ndtk['patient_globalentryid'])].drop_duplicates('patient_globalentryid')
    modified_ndtk = modified_ndtk.drop_duplicates('patient_globalentryid')

    modified_ndtk.to_csv("ndtk_data_with_age_and_packyears.csv")

    return modified_ndtk


def emphysema_analysis(df, cancers):
# the patients who have been deleted in the process of clearing the ndtk.csv data table (too little data, etc.) are included in the dataframe for analysis
    exceptions = ['8d94c658-2da7-412e-b926-f53fa591d6ca', 'ebe50e50-1b59-4523-8b80-1e183ac1eded', 'b11ce3d3-4340-42f2-95ea-979643081852']
    temp = cancers[cancers['patient_globalentryid'].isin(exceptions)]
    df = pd.concat([df, temp], ignore_index=True)

# only patients with any data on emphysema are included (null data throws off the result)
    df = df[df['emphysema_emphysema'].notna()]

    # df_temp = df[~df['emphysema_emphysema'].isna()]
    print(df['patient_sex_desc'].value_counts())

# all emphysema descriptions that indicate "present" are combined into one group
    emphysema_desc = ["moderate", "mild", "severe"]
    emphysema_present_total = df['emphysema_emphysema'].value_counts()
    print(emphysema_present_total)
    sum_of_present_total = emphysema_present_total[emphysema_desc].sum()

# no emphysema described as "notVisible"
    no_emphysema = emphysema_present_total["notVisible"]

    with open(R"output_files/emphysema.txt", 'w') as filehandler:
            filehandler.write(f"Emphysema present: {sum_of_present_total}\nNo visible emphysema: {no_emphysema}\n")

    diagnosed_patients = df[df['patient_globalentryid'].isin(cancers['patient_globalentryid'])]

    is_diagnosed = df['patient_globalentryid'].isin(cancers['patient_globalentryid'])

# added a new column, with a True/False variable to indicate whether the patient has cancer or not
    df['is_diagnosed'] = is_diagnosed
    
    # diagnosed_patients_temp = diagnosed_patients[~diagnosed_patients['emphysema_emphysema'].isna()]
    print(diagnosed_patients['patient_sex_desc'].value_counts())

    emphysema_in_diag_pat_values = diagnosed_patients['emphysema_emphysema'].value_counts()

    # print(diagnosed_patients['patient_globalentryid'].shape)

    sum_in_diag = emphysema_in_diag_pat_values[emphysema_desc].sum()

    with open(R"output_files/emphysema.txt", 'a') as filehandler:
            filehandler.write(f"Emphysema present in patients diagnosed with cancer: {sum_in_diag}\n{emphysema_in_diag_pat_values}\n")

    emphysema_condition = (df['emphysema_emphysema'].dropna() != 'notVisible').map({True: 'Yes', False: 'No'})

    emphysema_column = df['emphysema_emphysema'].dropna() != 'notVisible'

    df['emphysema_present'] = emphysema_column.astype(int)
    
    
    emphysema_gender_cross = pd.crosstab(index=emphysema_condition, columns=df['patient_sex_desc'], rownames=['has_emphysema'])

    print(emphysema_gender_cross)

    with open(R"output_files/emphysema.txt", 'a') as filehandler:
            filehandler.write(f"Emphysema presence across genders:\n{emphysema_gender_cross.to_string()}\n")
            
    emphysema_condition_cancers = (diagnosed_patients['emphysema_emphysema'].dropna() != "notVisible").map({True: 'Yes', False: 'No'})

    emphysema_gender_cross_cancers = pd.crosstab(index=emphysema_condition_cancers, columns=diagnosed_patients['patient_sex_desc'], rownames=['has_emphysema'])

    print(emphysema_gender_cross_cancers)

    with open(R"output_files/emphysema.txt", 'a') as filehandler:
            filehandler.write(f"Emphysema presence across genders in patients diagnosed with cancer:\n{emphysema_gender_cross_cancers.to_string()}\n")

#     emphysema_ages_cross = pd.crosstab(columns=df['patient_sex_desc'], values=df['age'].astype(float), aggfunc='mean', index=emphysema_condition)
#     with open(R"output_files/emphysema.txt", 'a') as filehandler:
#             filehandler.write(f"Mean age across genders in cases of emphysema:\n{emphysema_ages_cross.to_string()}\n") 

#     packyears_good_values = df[df['patientcard_packyears_packyearsvalue'].astype(float) > 0]

#     emphysema_packyears_values_cross = pd.crosstab(columns=df['patient_sex_desc'], values=packyears_good_values['patientcard_packyears_packyearsvalue'].astype(float), aggfunc='mean', index=emphysema_condition)
#     with open(R"output_files/emphysema.txt", 'a') as filehandler:
#             filehandler.write(f"Mean packyears value across genders in case of emphysema:\n{emphysema_packyears_values_cross.to_string()}\n")

#     cancer_ages_cross = pd.crosstab(columns=diagnosed_patients['patient_sex_desc'], values=diagnosed_patients['age'].astype(float), aggfunc='mean', index='has_cancer')
#     with open(R"output_files/cancer.txt", 'w') as filehandler:
#             filehandler.write(f"Mean age across genders in cases of cancer:\n{cancer_ages_cross.to_string()}\n")
    
#     cancer_packyears_cross = pd.crosstab(columns=diagnosed_patients['patient_sex_desc'], values=diagnosed_patients['patientcard_packyears_packyearsvalue'].astype(float), aggfunc='mean', index='has_cancer')
#     with open(R"output_files/cancer.txt", 'a') as filehandler:
#             filehandler.write(f"Mean packyears value across genders in cases of cancer:\n{cancer_packyears_cross.to_string()}\n")

    df.to_csv("output_files/cancer_analysis_base.csv")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the first input .csv file to analise"
    )

    parser.add_argument(
            '-i2', '--input2',
            required=True,
            help="Path to the second input .csv file"
    )

    parser.add_argument(
            '-c', '--cancers',
            required=True
    )

    args = parser.parse_args()

    df = load(args.input)
    df_ndtk = load(args.input2)
    cancers = load(args.cancers)

    diagnosed_w_cancer = extract_diagnosed(df, cancers)

    modified_ndtk_data = modify(df_ndtk, df)

    emphysema_analysis(modified_ndtk_data, diagnosed_w_cancer)
