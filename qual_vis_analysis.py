import argparse
import pandas as pd

def load_to_df(kwalifikacyjne):
        try:
                df_kwalifikacyjne = pd.read_csv(kwalifikacyjne, index_col=0, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        return df_kwalifikacyjne


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-q', '--qualification', 
                required=True, 
                help="Path to the qualification results .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                required=True,
                help="Output file."
        )

        args = parser.parse_args()

        df_kwalifikacyjne = load_to_df(args.qualification)

        traits = df_kwalifikacyjne.iloc[:16]

        try:
                traits.to_csv(args.output,  sep='\t', index=False)
        except (OSError, IOError) as e:
                print("File couldn't be saved: ", e)

