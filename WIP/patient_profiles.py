import argparse
import pandas as pd
from chardet import detect

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = detect.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']


def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

# tu wrzucić do złożenia w strukturę 'patient_profile' wyselekcjonowaną pod kątem spełniających wszystkie kryteria pacjentów tabelę/tabele danych

def group(df):
    df_grouped = df.groupby('patient_id').agg('first')
    return df_grouped


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)

    df.sort_values(['patient_globalentryid', 'reportdate'])

    df['patient_id'] = df['patient_globalentrid'].factorize()

    print(df['patient_id'])

    # df = group(df)

