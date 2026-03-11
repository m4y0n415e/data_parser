import argparse
import pandas as pd
from encoding import detect_encoding
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from merging.columns_selection import *
from data_analysis import *
import pickle

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def graphs(patient_profiles, gender):

        with open(gender, 'rb') as f:
                gender_count = pickle.load(f)
        gender_counts = [gender_count.get('K', 0), gender_count.get('M', 0)]

        bars = plt.bar(['Female', 'Male'], gender_counts)
        plt.title('Sex distribution of patients in the programme')
        plt.xlabel('Sex')
        plt.ylabel('Total number of patients')
        plt.bar_label(bars)
        plt.savefig(R"graphs\gender_distribution.png")

        plt.clf()
        
        patient_profiles['age'] = patient_profiles['age'].astype(float)
        df_no_dup= patient_profiles.drop_duplicates('patient_globalentryid')

        plt.hist(df_no_dup['age'], bins='fd', rwidth=1)
        plt.title('Age distribution of patients in the programme')
        plt.xlabel('Age')
        plt.ylabel('The number of patients')
        plt.savefig(R"graphs\age_distribution.png")

        plt.clf()

        dataOne = df_no_dup[df_no_dup['patient_sex_shortdesc'] == 'K']['age']
        dataTwo = df_no_dup[df_no_dup['patient_sex_shortdesc']== 'M']['age']

        ages_w = plt.hist(dataTwo, bins='fd', orientation='horizontal', label='Women', color='red')
        ages_m = plt.hist(dataOne, bins='fd', orientation='horizontal', label='Men',color='teal')

        for p in ages_m[2]:
                p.set_width( - p.get_width())

        xmin = min([ min(w.get_width() for w in ages_m[2]), 
                        min([w.get_width() for w in ages_w[2]]) ])
        xmin = np.floor(xmin)
        xmax = max([ max(w.get_width() for w in ages_m[2]), 
                        max([w.get_width() for w in ages_w[2]]) ])
        xmax = np.ceil(xmax)
        range = xmax - xmin
        delta = 0.0 * range
        plt.xlim([xmin - delta, xmax + delta])
        total = len(dataOne) + len(dataTwo)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.legend(loc='best')
        plt.axvline(0.0)
        plt.xlabel('Percent of patients')
        plt.ylabel('Age')
        plt.title('Patient age-sex pyramind')
        plt.legend()
        plt.savefig(R"graphs\b2b_pyramid_select.png")

        plt.clf()

        df_no_dup['patientcard_packyears_packyearsvalue'] = df_no_dup['patientcard_packyears_packyearsvalue'].astype(float)

        plt.hist(df_no_dup['patientcard_packyears_packyearsvalue'], bins='fd', rwidth=1)
        plt.title('Packyears smoked distribution in the programme')
        plt.xlabel('Packyears')
        plt.ylabel('The number of patients')
        plt.savefig(R"graphs\packyears_value_distribution.png")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    parser.add_argument(
          '-g', '--gender',
          required=True
    )

    args = parser.parse_args()

    df = load(args.input)

    graphs(df, args.gender)
