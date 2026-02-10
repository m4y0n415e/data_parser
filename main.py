import argparse
import pandas as pd


def load_to_df_and_fuse(kwalifikacyjne, NDTK, wynikowe):
        # df_komplet = pd.read_csv(args.all_tests)
        try:
                df_kwalifikacyjne = pd.read_csv(kwalifikacyjne, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        try:
                df_NDTK = pd.read_csv(NDTK, dtype=str)
        except FileNotFoundError:
                print("File not found.")
        try:
                df_wynikowe = pd.read_csv(wynikowe, dtype=str)
        except FileNotFoundError:
                print("File not found.")

        df_patient_profile = pd.merge(
        df_kwalifikacyjne, 
        df_NDTK, 
        on='order_id', # ep_examdata_patient_id,
        how='left'
        )
        
        df_patient_profile = pd.merge(
        df_patient_profile,
        df_wynikowe,
        on='order_id', # ep_examdata_patient_id,
        how='left'
        )
        
        return df_patient_profile


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        # parser.add_argument(
        #       '-a', '--all_tests', 
        #       required=True, 
        #       help="Path to the summary test .csv file"
        #)

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
                default="output_database.csv",
                help="Output filename"
        )

        args = parser.parse_args()

        final_df = load_to_df_and_fuse(args.qualification, args.ndtk, args.results)

        final_df.to_csv(args.output, index=False, na_rep = 'Brak danych', sep=';')