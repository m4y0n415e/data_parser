import argparse
import pandas as pd
from encoding import detect_encoding
import string as s
from columns_selection import *

def load_to_df(db):
        coding = detect_encoding(db)
        try:
                df_joined = pd.read_csv(db, encoding=coding, usecols=COLS_QUAL, dtype=str)
        except FileNotFoundError:
                print("File not found.")

        return df_joined

def loc_stats(joined):
       mean_age = round(joined['age'].mean(), 1)
       mean_age_women = round(joined[joined['patient_sex_shortdesc'] == 'K']['age'].mean(), 1)
       mean_age_men = round(joined[joined['patient_sex_shortdesc'] == 'M']['age'].mean(), 1)
       median_age = joined['age'].median()
       max_age = max(joined['age'])
       min_age = min(joined['age'])

       with open("loc_stat.txt", "w") as f:
              f.write(f"Mean age: {mean_age} \nMean age women: {mean_age_women}\nMean age men: {mean_age_men}\nMedian age: {median_age}\nMaximum age: {max_age}\nMinumum age: {min_age}\n")


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-i', '--input', 
                required=True, 
                help="Path to the input database .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                required=False,
                help="Path to the output database .csv file"
        )

        args = parser.parse_args()

        df_joined = load_to_df(args.input)

        loc_stats(df_joined)

        df_joined.to_csv(args.output, index=False)