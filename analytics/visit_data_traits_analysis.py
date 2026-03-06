import argparse
import pandas as pd
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as file:
        detector = chardet.universaldetector.UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result['encoding']

def load_to_df(argument):
        coding = detect_encoding(argument)
        try:
                df = pd.read_csv(argument, dtype=str, encoding=coding, on_bad_lines='warn')
        except FileNotFoundError:
                print("File not found.")
                return None
        return df

def traits_count(traits):
        report_data = {}
        total_rows = traits.shape[0]
        for col in traits.columns:
                count = traits[col].nunique()
                if (count/total_rows < 0.3):
                        to_show = ", ".join(str(x) for x in traits[col].unique())
                else:
                        to_show = "Wiele wartosci unikatowych."
                report_data[col] = [count, to_show]

        filtered_traits = pd.DataFrame(report_data, index=['Unique count', 'Unique values'])
        return filtered_traits
        
def load_to_csv(traits, output_file):
        try:
                traits.to_csv(output_file, index=False)
        except (OSError, IOError) as e:
                 print("File couldn't be saved: ", e)


if __name__ == "__main__":

        parser = argparse.ArgumentParser()

        parser.add_argument(
                '-q', '--qualification', 
                required=True, 
                help="Path to the qualification results .csv file"
        )

        parser.add_argument(
                '-n', '--ndtk', 
                required=False, 
                help="Path to the NDTK results .csv file"
        )

        parser.add_argument(
                '-r', '--results', 
                required=False, 
                help="Path to the examinations results .csv file"
        )

        parser.add_argument(
                '-o', '--output',
                required=True,
                help="Output file."
        )

        args = parser.parse_args()

        traits = load_to_df(args.qualification)

        traits_slice = traits.iloc[:40]

        filtered_traits = traits_count(traits)

        load_to_csv(filtered_traits, args.output)
       
