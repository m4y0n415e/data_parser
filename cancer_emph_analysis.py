import argparse
import pandas as pd
from encoding import detect_encoding
from scipy import stats
import statistics
import numpy as np


def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df


def get_stats_with_ci(group):
    data = pd.to_numeric(group, errors='coerce').dropna()
    
    if len(data) < 2:
        return f"{data.mean():.2f} [N/A]"
    
    mean = data.mean()
    sem = stats.sem(data)
    ci_low, ci_high = stats.t.interval(0.95, len(data)-1, loc=mean, scale=sem)
    
    return f"{mean:.2f} [95% CI: {ci_low:.2f}, {ci_high:.2f}]"


def run_full_t_test(df, status_to_check, variable):
    group_target = df[df['comorbidity_status'] == status_to_check][variable].dropna()
    group_neither = df[df['comorbidity_status'] == 'Neither'][variable].dropna()
    
    if len(group_target) < 2 or len(group_neither) < 2:
        return np.nan, np.nan, np.nan
    
    t_stat, p_val = stats.ttest_ind(group_target.astype(float), group_neither.astype(float), equal_var=False)
    
    df_val = len(group_target) + len(group_neither) - 2
    
    return t_stat, p_val, df_val

def get_connection_stats(df, gender_filter=None):
    if gender_filter:
        data = df[df['patient_sex_desc'] == gender_filter]
    else:
        data = df

    counts = data['comorbidity_status'].value_counts()
    a = counts.get('Both', 0)
    b = counts.get('Emphysema only', 0)
    c = counts.get('Cancer only', 0)
    d = counts.get('Neither', 0)

    table = [[a, b], [c, d]]
    
    odds_ratio, p_val = stats.fisher_exact(table)
    print(counts)
    
    if a > 0 and b > 0 and c > 0 and d > 0:
        log_or = np.log(odds_ratio)
        se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d)
        ci_low = np.exp(log_or - 1.96 * se_log_or)
        ci_high = np.exp(log_or + 1.96 * se_log_or)
        ci_string = f"[{ci_low:.2f}, {ci_high:.2f}]"
    else:
        ci_string = "[N/A]"

    return {
        'Group': gender_filter if gender_filter else 'Total',
        'OR': f"{odds_ratio:.2f}",
        '95% CI': ci_string,
        'p-value': f"{p_val:.4f}",
        'Result': "Significant" if p_val < 0.05 else "Not Significant"
    }

def run_intergender_t_test(df, status_filter, variable):
    subset = df[df['comorbidity_status'] == status_filter]
    
    men = pd.to_numeric(subset[subset['patient_sex_shortdesc'] == 'M'][variable], errors='coerce').dropna()
    women = pd.to_numeric(subset[subset['patient_sex_shortdesc'] == 'K'][variable], errors='coerce').dropna()
    
    if len(men) < 2 or len(women) < 2:
        return np.nan, np.nan, np.nan
    
    t_stat, p_val = stats.ttest_ind(men, women, equal_var=False)
    df_val = len(men) + len(women) - 2
    
    return t_stat, p_val, df_val

from scipy.stats import chi2_contingency

def run_universal_chi(df, group_col, target_col):
    pct = ct.div(ct.sum(axis=1), axis=0) * 100
    
    with open("output_files/comorbidity_analysis.txt", "a") as f:
        f.write(f"""
        \nChi-Square: {group_col} vs {target_col}
        Counts Table:
        {ct.to_string()}
        Prevalence Rates (%):
        {pct.to_string()}
        Chi2: {chi2:.3f}, p-value: {p_val:.4e}
        \n""")
    
    return ct, p_val

def get_binary_report(df, diag_column, variable_column):
    temp_df = df.copy()
    temp_df[variable_column] = pd.to_numeric(temp_df[variable_column], errors='coerce')
    
    mask_present = temp_df[diag_column].astype(float) == 1
    
    group_present = temp_df[mask_present][variable_column].dropna()
    group_absent = temp_df[~mask_present][variable_column].dropna()
    
    stats_present = get_stats_with_ci(group_present)
    stats_absent = get_stats_with_ci(group_absent)
    
    t_stat, p_val = stats.ttest_ind(group_present, group_absent, equal_var=False)
    
    with open("output_files/comorbidity_analysis.txt", "a") as f:
        f.write(f"\nAnalysis for: {diag_column} vs {variable_column}")
        f.write(f"\nDiagnosed: {stats_present}")
        f.write(f"\nNo cancer:  {stats_absent}")
        f.write(f"\nT-statistic: {t_stat:.3f}, p-value: {p_val:.4f}")
    
    return stats_present, stats_absent, p_val


def analyse(df):

    dataOne = df_no_dup[df_no_dup['patient_sex_shortdesc'] == 'K']['age'].astype(float)
    dataTwo = df_no_dup[df_no_dup['patient_sex_shortdesc']== 'M']['age'].astype(float)

    result = stats.ttest_ind(dataOne.dropna(), dataTwo.dropna(), equal_var=True)
    print(result, result.confidence_interval(confidence_level=0.95))

    dataThree = df_no_dup[df_no_dup['patient_sex_shortdesc'] == 'K']['patientcard_packyears_packyearsvalue'].astype(float)
    dataFour = df_no_dup[df_no_dup['patient_sex_shortdesc']== 'M']['patientcard_packyears_packyearsvalue'].astype(float)

    result = stats.ttest_ind(dataThree.dropna(), dataFour.dropna(), equal_var=True)
    print(result, result.confidence_interval(confidence_level=0.95))

    data = pd.to_numeric(df_no_dup['patient_sex_shortdesc'], errors='coerce').dropna()

# statistics of the cancer group - age and packyears value, grouped by sex and cancer presence
    cancer_stats = df_no_dup.groupby(['is_diagnosed', 'patient_sex_desc']).agg({
        'age': get_stats_with_ci,
        'patientcard_packyears_packyearsvalue': get_stats_with_ci
    }).unstack()

# statistics of the emphysema group - age and packyears value, grouped by sex and emphysema presence
    emph_stats = df_no_dup.groupby(['emphysema_emphysema', 'patient_sex_desc']).agg({
        'age': get_stats_with_ci,
        'patientcard_packyears_packyearsvalue': get_stats_with_ci
    }).unstack()

    with open("output_files/cancer_stats_final.txt", "w") as f:
        f.write("Cancer statistics (Mean [95% CI]): \n")
        f.write(cancer_stats.to_string())
        f.write("\n\nEmphysema statistics (Mean [95% CI]): \n")
        f.write(emph_stats.to_string())


    df_complete = df_no_dup.dropna(subset=['emphysema_present']).copy()

    df_complete['emphysema_present'] = pd.to_numeric(df_complete['emphysema_present'], errors='coerce').astype(int)
    df_complete['is_diagnosed'] = df_complete['is_diagnosed'].astype(str).str.lower() == 'true'

    conditions = [
        (df_complete['is_diagnosed'] == False) & (df_complete['emphysema_present'] == 0), 
        (df_complete['is_diagnosed'] == False) & (df_complete['emphysema_present'] == 1), 
        (df_complete['is_diagnosed'] == True)  & (df_complete['emphysema_present'] == 0), 
        (df_complete['is_diagnosed'] == True)  & (df_complete['emphysema_present'] == 1) 
    ]

    choices = ['Neither', 'Emphysema only', 'Cancer only', 'Both']
    df_complete['comorbidity_status'] = np.select(conditions, choices, default='Unknown')   

    final_stats = df_complete.groupby(['comorbidity_status', 'patient_sex_desc']).agg({  
        'age': get_stats_with_ci,
        'patientcard_packyears_packyearsvalue': get_stats_with_ci
    }).unstack()

    t_test_results = []

    for gender_label, gender_short in [('Kobieta', 'K'), ('Mężczyzna', 'M')]:
        df_gender = df_complete[df_complete['patient_sex_shortdesc'] == gender_short]
        
        for var in ['age', 'patientcard_packyears_packyearsvalue']:
            var_name = 'Age' if var == 'age' else 'Packyears'
            
            for status in ['Emphysema only', 'Cancer only', 'Both']:
                t_stat, p_val, df_val = run_full_t_test(df_gender, status, var)
                
                t_test_results.append({
                    'Gender': gender_label,
                    'Variable': var_name,
                    'Comparison': f"{status} vs Neither",
                    't-stat': f"{t_stat:.3f}",
                    'df': df_val,
                    'p-value': f"{p_val:.4f}"
                })

    t_df = pd.DataFrame(t_test_results)

    results = [
        get_connection_stats(df_complete, 'Kobieta'),
        get_connection_stats(df_complete, 'Mężczyzna'),
        get_connection_stats(df_complete)
    ]
    or_table = pd.DataFrame(results)

    # print("Counts for OR calculation (Complete Data only):")
    # print(df_complete['comorbidity_status'].value_counts())

    # print("\nCounts by Gender:")
    # print(df_complete.groupby('patient_sex_shortdesc')['comorbidity_status'].value_counts())

    gender_comp_results = []

    target_statuses = ['Emphysema only', 'Cancer only', 'Both']
    variables = ['age', 'patientcard_packyears_packyearsvalue']

    for status in target_statuses:
        for var in variables:
            var_name = 'Age' if var == 'age' else 'Packyears'
            
            t_stat, p_val, df_val = run_intergender_t_test(df_complete, status, var)
            
            gender_comp_results.append({
                'Clinical Group': status,
                'Variable': var_name,
                'Comparison': 'Men vs Women',
                't-stat': f"{t_stat:.3f}" if not np.isnan(t_stat) else "N/A",
                'df': df_val if not np.isnan(df_val) else "N/A",
                'p-value': f"{p_val:.4f}" if not np.isnan(p_val) else "N/A"
            })

    gender_comp_df = pd.DataFrame(gender_comp_results)

    with open("output_files/intergender_comparison.txt", "w") as f:
        f.write("Inter-gender comparison: \n")
        f.write(gender_comp_df.to_string(index=False))
    
    with open("output_files/comorbidity_analysis.txt", "w") as f:
        f.write("Complete analysis\n\n")
        f.write("1. Descriptive statistics (Mean [95% CI])\n")
        f.write(final_stats.to_string())
        f.write("\n\n2. T-tests\n")
        f.write(t_df.to_string(index=False))
        f.write("\n\n3. OR\n")
        f.write(or_table.to_string(index=False))


    # Question: Are men more likely to get emphysema than women?
    run_universal_chi(df_complete, 'patient_sex_desc', 'emphysema_present')

    # Question: Are men more likely to get cancer than women?
    run_universal_chi(df_complete, 'patient_sex_desc', 'is_diagnosed')

    # Question: Is there a link between having emphysema and having cancer?
    run_universal_chi(df_complete, 'emphysema_present', 'is_diagnosed')


    get_binary_report(df_complete, 'emphysema_present', 'age')
    get_binary_report(df_complete, 'emphysema_present', 'patientcard_packyears_packyearsvalue')

    get_binary_report(df_complete, 'is_diagnosed', 'age')
    get_binary_report(df_complete, 'is_diagnosed', 'patientcard_packyears_packyearsvalue')


def loc_stats(df):
        df_working = df.drop_duplicates('patient_globalentryid')
        df_working['age'] = df_working['age'].astype(float)
        df_working['patientcard_packyears_packyearsvalue'] = df_working['patientcard_packyears_packyearsvalue'].astype(float)

        mean_age = round(df_working['age'].mean(), 1)
        print("SD of age: ", statistics.stdev(df_working['age'].dropna(), xbar=mean_age))
        mean_age_women = round(df_working[df_working['patient_sex_shortdesc'] == 'K']['age'].mean(), 1)
        mean_age_men = round(df_working[df_working['patient_sex_shortdesc'] == 'M']['age'].mean(), 1)
        median_age = df_working['age'].median()
        max_age = max(df_working['age'])
        min_age = min(df_working['age'])

        mean_pack = round(df_working['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        print("SD of pack-years: ", statistics.stdev(df_working['patientcard_packyears_packyearsvalue'].dropna(), xbar=mean_pack))
        mean_pack_women = round(df_working[df_working['patient_sex_shortdesc'] == 'K']['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        mean_pack_men = round(df_working[df_working['patient_sex_shortdesc'] == 'M']['patientcard_packyears_packyearsvalue'].dropna().mean(), 1)
        median_pack = df_working['patientcard_packyears_packyearsvalue'].dropna().median()
        max_pack = max(df_working['patientcard_packyears_packyearsvalue'])
        min_pack = min(df_working['patientcard_packyears_packyearsvalue'])

        with open(R"output_files/loc_stat.txt", "w") as f:
              f.write(f"Mean age: {mean_age}\nMean age women: {mean_age_women} \nMean age men: {mean_age_men}\nMedian age: {median_age}\nMaximum age: {max_age}\nMinumum age: {min_age}\n")
        with open(R"output_files/loc_stat.txt", "a") as f:
              f.write(f"\nMean packyears: {mean_pack}\nMean packyears women: {mean_pack_women} \nMean packyears men: {mean_pack_men}\nMedian packyears: {median_pack}\nMaximum packyears: {max_pack}\nMinumum packyears: {min_pack}\n")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-i', '--input', 
            required=True, 
            help="Path to the first input .csv file to analise"
    )

    args = parser.parse_args()

    df = load(args.input)

    loc_stats(df)

    analise(df)

