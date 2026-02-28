import argparse
import pandas as pd
from encoding import detect_encoding
import matplotlib.pyplot as plt
import numpy as np
from merging.columns_selection import *
from profiling import *
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

        plt.hist(df_no_dup['age'], bins=10, rwidth=1)
        plt.title('Age distribution of patients in the programme')
        plt.xlabel('Age')
        plt.ylabel('Total number of patients')
        plt.savefig(R"graphs\age_distribution.png")

        plt.clf()
        
        ages_w = df_no_dup[df_no_dup['patient_sex_shortdesc'] == 'K']['age']
        ages_m = df_no_dup[df_no_dup['patient_sex_shortdesc']== 'M']['age']

        bins = np.arange(30, 90, 5)
        counts_w, _ = np.histogram(ages_w, bins=bins)
        counts_m, _ = np.histogram(ages_m, bins=bins)

        counts_m_inverted = counts_m * -1

        plt.barh(bins[:-1], counts_w, height=4.5, label='Women', color='red')
        plt.barh(bins[:-1], counts_m_inverted, height=4.5, label='Men',color='teal')

        ticks = plt.xticks()[0]
        plt.xticks(ticks, [str(abs(int(tick))) for tick in ticks])
        plt.xlabel('Number of patients')
        plt.ylabel('Age')
        plt.title('Patient age-sex pyramind')
        plt.legend()

        plt.savefig(R"graphs\b2b_pyramid_select.png")


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
