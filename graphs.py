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

        # Bar plot for gender distribution
        bars = plt.bar(['Woman', 'Man'], gender_counts, color=['red', 'teal'])
        plt.ylim(top=1700)
        plt.title('Sex distribution of patients in the programme')
        plt.xlabel('Sex')
        plt.ylabel('Total number of patients')
        plt.bar_label(bars)
        plt.savefig(R"graphs/gender_distribution.png")

        plt.clf()

        # Bar plot for cancer diagnosis distribution
        bars = plt.bar(['No cancer', 'Cancer diagnosed'], patient_profiles['is_diagnosed'].value_counts(), color=['lawngreen', 'blue'])
        plt.ylim(top=3050)
        plt.title('Cancer diagnosis distribution among patients in the programme')
        plt.xlabel('Diagnosis')
        plt.ylabel('Total number of patients')
        plt.bar_label(bars)
        plt.savefig(R"graphs/cancer_distribution.png")

        plt.clf()

        # Bar plot for emphysema distribution
        bars = plt.bar(['No emphysema', 'Emphysema present'], patient_profiles['emphysema_present'].value_counts(dropna=True), color=['yellow', 'orange'])
        plt.ylim(top=3000)
        plt.title('Emphysema presence among participants')
        plt.xlabel('Presence')
        plt.ylabel('Total number of patients')
        plt.bar_label(bars)
        plt.savefig(R"graphs/emphysema_distribution.png")

        plt.clf()
        
        # Histogram of age distribution of patients in the program
        patient_profiles['age'] = patient_profiles['age'].astype(float)
        df_no_dup= patient_profiles.drop_duplicates('patient_globalentryid')

        ages = plt.hist(df_no_dup['age'], bins='fd', rwidth=1)
        plt.xlim(left=30, right=80)
        plt.title('Age distribution of patients in the programme')
        plt.xlabel('Age')
        plt.ylabel('The number of patients')
        plt.savefig(R"graphs/age_distribution.png")

        plt.clf()

        # Back 2 back histogram: age-sex pyramid
        dataAgeWomen = df_no_dup[df_no_dup['patient_sex_shortdesc'] == 'K']['age']
        dataAgeMen = df_no_dup[df_no_dup['patient_sex_shortdesc']== 'M']['age']

        ages_w = plt.hist(dataAgeWomen, bins='fd', orientation='horizontal', label='Women', color='red')
        ages_m = plt.hist(dataAgeMen, bins='fd', orientation='horizontal', label='Men',color='teal')

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
        total = len(dataAgeWomen) + len(dataAgeMen)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.legend(loc='best')
        plt.axvline(0.0)
        plt.xlabel('Percent of patients')
        plt.ylabel('Age')
        plt.title('Patient age-sex pyramind')
        plt.legend()
        plt.savefig(R"graphs/b2b_age_sex.png")

        plt.clf()

        # Packyears boxplot
        df_no_dup['patientcard_packyears_packyearsvalue'] = df_no_dup['patientcard_packyears_packyearsvalue'].astype(float)

        ax = df_no_dup.boxplot(column='patientcard_packyears_packyearsvalue', whis=3.0)
        plt.title('Packyears smoked distribution in the programme')
        ax.set_xticklabels([])
        plt.ylabel('Packyears')
        plt.savefig(R"graphs/packyears_value_distribution.png")

        plt.clf()

        # Packyears distribution among sexes
        dataPackyearsWomen = df_no_dup[(df_no_dup['patient_sex_shortdesc'] == 'K') & (df_no_dup['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']
        dataPackyearsMen = df_no_dup[(df_no_dup['patient_sex_shortdesc']== 'M') & (df_no_dup['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']

        all_data = pd.concat([dataPackyearsWomen, dataPackyearsMen])
        _, bin_edges = np.histogram(all_data, bins=8)

        packyears_w = plt.hist(dataPackyearsWomen, bins=bin_edges, orientation='horizontal', label='Women', color='purple', edgecolor='black')
        packyears_m = plt.hist(dataPackyearsMen, bins=bin_edges, orientation='horizontal', label='Men',color='palegreen', edgecolor='black')

        for p in packyears_m[2]:
                p.set_width( - p.get_width())

        xmin = min([ min(w.get_width() for w in packyears_m[2]), 
                        min([w.get_width() for w in packyears_w[2]]) ])
        xmin = np.floor(xmin)
        xmax = max([ max(w.get_width() for w in packyears_m[2]), 
                        max([w.get_width() for w in packyears_w[2]]) ])
        xmax = np.ceil(xmax)
        range = xmax - xmin
        delta = 0.0 * range
        plt.xlim([xmin - delta, xmax + delta])
        plt.ylim((20, 60))
        total = len(dataPackyearsWomen) + len(dataPackyearsMen)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)
        plt.legend(loc='best')
        plt.axvline(0.0)
        plt.xlabel('Percent of patients')
        plt.ylabel('Packyears')
        plt.title('Patient packyears-to-sex pyramid')
        plt.legend()
        plt.savefig(R"graphs/b2b_packyears.png")

        plt.clf()
        # Back 2 back histogram of age in context of emphysema

        dataAgeEmph = df[df['emphysema_present'].astype(float) == 0]['age'].dropna()
        dataAgeNoEmph = df[df['emphysema_present'].astype(float) == 1]['age'].dropna()

        _, bin_edges = np.histogram(df['age'].dropna(), bins=8)

        emphysema = plt.hist(dataAgeEmph, bins=bin_edges, orientation='horizontal', label='No emphysema', color='orange')
        no_emphysema = plt.hist(dataAgeNoEmph, bins=bin_edges, orientation='horizontal', label='Emphysema', color='yellow')

        for p in no_emphysema[2]:
                p.set_width(-p.get_width())

        xmin = min([min(w.get_width() for w in no_emphysema[2]), 
                        min([w.get_width() for w in emphysema[2]])])
        xmin = np.floor(xmin)
        xmax = max([max(w.get_width() for w in no_emphysema[2]), 
                        max([w.get_width() for w in emphysema[2]])])
        xmax = np.ceil(xmax)

        limit = max(abs(xmin), abs(xmax))
        plt.xlim([-limit, limit])

        total = len(dataAgeEmph) + len(dataAgeNoEmph)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.axvline(0.0)
        plt.xlabel('Percent of patients')
        plt.ylabel('Age')
        plt.title('Emphysema-to-age pyramid')
        plt.legend()
        plt.savefig(R"graphs/b2b_age_emphysema.png")

        plt.clf()

        # Back to back histogram of cancer cases and age

        dataNoCancer = df[df['is_diagnosed'] == 'False']['age'].dropna()
        dataCancer = df[df['is_diagnosed'] == 'True']['age'].dropna()

        _, bin_edges = np.histogram(df['age'].dropna(), bins=8)

        no_cancer = plt.hist(dataNoCancer, bins=bin_edges, orientation='horizontal', label='No cancer', color='lawngreen')
        cancer = plt.hist(dataCancer, bins=bin_edges, orientation='horizontal', label='Cancer diagnosed', color='blue')

        for p in cancer[2]:
                p.set_width(-p.get_width())

        xmin = min([min(w.get_width() for w in cancer[2]), 
                        min([w.get_width() for w in no_cancer[2]])])
        xmin = np.floor(xmin)
        xmax = max([max(w.get_width() for w in cancer[2]), 
                        max([w.get_width() for w in no_cancer[2]])])
        xmax = np.ceil(xmax)

        limit = max(abs(xmin), abs(xmax))
        plt.xlim([-limit, limit])

        total = len(dataNoCancer) + len(dataCancer)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.axvline(0.0)
        plt.xlabel('Percent of patients')
        plt.ylabel('Age')
        plt.title('Cancer-to-age pyramid')
        plt.legend()
        plt.savefig(R"graphs/b2b_age_cancer.png")

        plt.clf()

        # Back 2 back for packyears in context of emphysema
        plt.figure(figsize=(10, 6))

        dataPackNoEmph = pd.to_numeric(df[(df['emphysema_present'].astype(float) == 0) & (df['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']).dropna()
        dataPackEmph = pd.to_numeric(df[(df['emphysema_present'].astype(float) == 1) & (df['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']).dropna()

        all_vals = pd.concat([dataPackNoEmph, dataPackEmph])
        _, bin_edges = np.histogram(all_vals, bins=15)

        no_emphysema = plt.hist(dataPackNoEmph, bins=bin_edges, orientation='horizontal', label='No emphysema', color='yellow')
        emphysema = plt.hist(dataPackEmph, bins=bin_edges, orientation='horizontal', label='Emphysema', color='orange')

        for p in emphysema[2]:
                p.set_width(-p.get_width())

        xmin = min([min(w.get_width() for w in emphysema[2]), 
                min([w.get_width() for w in no_emphysema[2]])])
        xmin = np.floor(xmin)
        xmax = max([max(w.get_width() for w in emphysema[2]), 
                max([w.get_width() for w in no_emphysema[2]])])
        xmax = np.ceil(xmax)

        limit = max(abs(xmin), abs(xmax))
        plt.xlim([-limit, limit])
        plt.ylim(20,60)

        total = len(dataPackNoEmph) + len(dataPackEmph)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.xlabel('Percent of patients')
        plt.ylabel('Packyears')
        plt.title('Distribution of packyears by emphysema')
        plt.legend()
        plt.savefig(R"graphs/b2b_pack_emph.png")


        plt.clf()
        # Back 2 back for packyears in context of cancer

        plt.figure(figsize=(10, 6))

        dataPackNoCancer = pd.to_numeric(df[(df['is_diagnosed'] == 'False') & (df['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']).dropna()
        dataPackCancer = pd.to_numeric(df[(df['is_diagnosed'] == 'True') & (df['patientcard_packyears_packyearsvalue'].astype(float) > 0)]['patientcard_packyears_packyearsvalue']).dropna()

        all_vals = pd.concat([dataPackNoCancer, dataPackCancer])
        _, bin_edges = np.histogram(all_vals, bins=15)

        no_cancers = plt.hist(dataPackNoCancer, bins=bin_edges, orientation='horizontal', label='No cancer', color='lawngreen')
        cancers = plt.hist(dataPackCancer, bins=bin_edges, orientation='horizontal', label='Diagnosed with lung cancer', color='blue')

        for p in cancers[2]:
                p.set_width(-p.get_width())

        xmin = min([min(w.get_width() for w in cancers[2]), 
                min([w.get_width() for w in no_cancers[2]])])
        xmin = np.floor(xmin)
        xmax = max([max(w.get_width() for w in cancers[2]), 
                max([w.get_width() for w in no_cancers[2]])])
        xmax = np.ceil(xmax)

        limit = max(abs(xmin), abs(xmax))
        plt.xlim([-limit, limit])
        plt.ylim(20,60)

        total = len(dataPackNoCancer) + len(dataPackCancer)
        formatter = mtick.FuncFormatter(lambda x, pos: f"{abs(x) / total * 100:.1f}%")
        plt.gca().xaxis.set_major_formatter(formatter)

        plt.xlabel('Percent of patients')
        plt.ylabel('Packyears')
        plt.title('Distribution of packyears by cancer diagnosis')
        plt.legend()
        plt.savefig(R"graphs/b2b_pack_cancer.png")

        plt.clf()
        # Stacked bar plot of emphysema cases among people diagnosed and not diagnosed

        figsize=(8, 6)
        cont_tab = pd.crosstab(df['emphysema_present'], df['is_diagnosed'], normalize='index')

        fig, ax = plt.subplots()
        cont_tab.plot(x=['Emphysema present', 'No visible emphysema'], kind='bar', stacked=True, rot=0, color=['lawngreen', 'blue'], ax=ax)
        ax.legend(['No cancer', 'Cancer diagnosed'])
        ax.set_xlabel('')
        ax.set_ylabel('Fraction of the whole group')

        plt.savefig(R"graphs/stacked_bar_cancer_emph.png")

        plt.clf()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the input .csv file to analise"
    )

    parser.add_argument(
          '-g', '--gender',
          required=False
    )

    args = parser.parse_args()

    df = load(args.input)

    graphs(df, args.gender)
