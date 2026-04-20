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
            '-i', '--input', 
            required=True, 
            help="Path to the first input .csv file to modify"
    )

    parser.add_argument(
            '-in', '--init', 
            required=True
    )

    args = parser.parse_args()

    ndtk = load(args.input)
    init = load(args.init)

    ndtk['age'] = init['age']
    ndtk['patientcard_packyears_packyearsvalue'] = init['patientcard_packyears_packyearsvalue']
    ndtk['patient_sex_shortdesc'] = init['patient_sex_shortdesc']

    ndtk.to_csv("output_files/NDTK_version_2_w_age.csv")