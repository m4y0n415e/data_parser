import argparse
import pandas as pd
from encoding import detect_encoding

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-in', '--init', 
            required=True
    )

    parser.add_argument(
            '-c', '--consult', 
            required=True
    )

    args = parser.parse_args()

    init = load(args.init)
    consult = load(args.consult)

    max_sequence = consult.groupby('patient_globalentryid')['visit_sequence'].max()

    consult['max_sequence'] = consult['patient_globalentryid'].map(max_sequence)

    consult['reportdate'] = pd.to_datetime(consult['reportdate'], format='mixed')
    no_dropouts = consult[consult['reportdate'].dt.year == 2023]

    finished_program_ids = no_dropouts['patient_globalentryid'].unique()

    suspected_dropout_or_diagnosis = consult[~consult['patient_globalentryid'].isin(finished_program_ids)]

    suspected_dropout_or_diagnosis.to_csv("output_files/sus_dropout_or_diagnosis.csv")

    suspected_dropout_or_diagnosis_ids = suspected_dropout_or_diagnosis['patient_globalentryid'].unique()

