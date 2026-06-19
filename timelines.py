import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn import set_config
from sklearn.mixture import GaussianMixture
from statsmodels.tsa.ar_model import AutoReg
from encoding import detect_encoding
from scipy.stats import norm

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def draw_graphs(scaled_df, df_filtered):
    kmeans = KMeans(init='random', n_clusters=3, n_init=10, random_state=1)

    kmeans.fit(scaled_df)

    df_filtered['cluster_id'] = pd.Series(kmeans.labels_)

    point_in_time = (df_filtered['days_since_ldct_visit'].astype(float).groupby(df_filtered['cluster_id'])).mean()

    df_filtered['days_since_ldct_visit'] = pd.to_numeric(df_filtered['days_since_ldct_visit'], errors='coerce')

    frequencies = df_filtered['cluster_id'].value_counts(sort=False).sort_index(ascending=True)

    plt.vlines(x=point_in_time, ymin=0, ymax=frequencies.astype(float).mean())

    plt.title("Patient visits with k-means temporal nodes")
    plt.ylabel("Frequency")
    plt.xlabel("Point in time of the visits")
    
    plt.savefig(R"graphs/kmeans_interval_lines.png")

    plt.clf()

    x = df_ldct['days_since_initial_visit_in_ldct'].astype(float)
    df_ldct['days_since_initial_visit_in_ldct'].astype(float).plot.kde(bw_method=0.05)

    plt.xticks(np.arange(min(x), max(x)+1, 30.0), rotation=45)

    plt.savefig(R"graphs/kde_days.png")

    plt.clf()

def calculate_bic(df_ldct):
    x = df_ldct['days_since_initial_visit_in_ldct'].astype(float)
    threshold = x.quantile(0.95)
    x_clean = x[x <= threshold]
    X = x_clean.values.reshape(-1,1)
    bic_scores = []

    for k in range(1,12):
        model = GaussianMixture(n_components=k, random_state=0)
        model = model.fit(X)
        bic_scores.append(model.bic(X))

    plt.plot(range(1,12), bic_scores, marker='o')
    plt.title('BIC values')
    plt.xlabel('N-components')
    plt.ylabel('BIC')
    plt.show()

    plt.clf()
    return np.argmin(bic_scores) + 1
    
def create_GMM(df_ldct):
    X = df_ldct['days_since_initial_visit_in_ldct'].astype(float).values.reshape(-1,1)
    model_4 = GaussianMixture(n_components=4, random_state=0, n_init=10)
    model_4.fit(X)
    print(model_4.means_)

    # plt.hist(X, density=True)
    x_synthetic = np.linspace(0, 800, 1000)

    x_new = x_synthetic.reshape(-1, 1)

    probability_matrix = model_4.predict_proba(x_new) # predict_proba basically uses PDF to determine probability of an x belonging to a Gaussian function n
    print(probability_matrix[400])

    probability_matrix_slice0 = probability_matrix[:, 3]
    probability_matrix_slice1 = probability_matrix[:, 0]

    condition = probability_matrix_slice1 > probability_matrix_slice0    
    max_el = []
    max_el.append(np.argmax(condition))

    probability_matrix_slice2 = probability_matrix[:, 2]
    condition = probability_matrix_slice2 > probability_matrix_slice1
    max_el.append(np.argmax(condition))

    probability_matrix_slice3 = probability_matrix[:, 1]
    condition = (probability_matrix_slice2 > probability_matrix_slice3) & (x_synthetic > 383)
    max_el.append(np.argmax(condition))

    print(x_synthetic[max_el])

    st_dev = np.sqrt(model_4.covariances_.flatten())
    timeline = np.linspace(0, 729+3*st_dev[1], 1000)

    pdf_values_1 = norm. pdf(timeline, loc=model_4.means_.flatten()[2], scale=st_dev[2]) * model_4.weights_[2]
    pdf_values_2 = norm.pdf(timeline, loc=model_4.means_.flatten()[1], scale=st_dev[1]) * model_4.weights_[1]
    pdf_values_3 = norm.pdf(timeline, loc=model_4.means_.flatten()[0], scale=st_dev[0]) * model_4.weights_[0]
    plt.plot(timeline, pdf_values_1, label="Distribution", color="blue")
    plt.plot(timeline, pdf_values_2, color='red')
    plt.plot(timeline, pdf_values_3, color='yellow')
    plt.title("PDF of xyz Distribution")
    plt.xlabel("x")
    plt.ylabel("Probability Density")
    plt.show()

    # roots = optimize.fsolve(, 505) # <- calculate weighted height for x and put in the difference of these heights for 2 and 1 into the first parameter 


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-n', '--ldct',
            required=True
    )

    args = parser.parse_args()

    df_ldct = load(args.ldct)

    set_config(transform_output="pandas")

    # print((df_ldct['visit_sequence'].astype(int)).mean()) # something weird happens here
    no_in_seq = df_ldct['visit_sequence'].astype(int) == 2 # 2, 3 and 4 work correctly

    df_ldct['reportdate'] = pd.to_datetime(df_ldct['reportdate'], format='mixed')
    df_filtered = df_ldct[no_in_seq].copy()
    df_filtered.fillna({'days_since_ldct_visit': 0}, inplace=True)

    scaled_df = StandardScaler().fit_transform(df_filtered['days_since_ldct_visit'].to_frame())

    draw_graphs(scaled_df, df_filtered)
   
    opt_k = calculate_bic(df_ldct)

    create_GMM(df_ldct)
   

    # Conclude with one GMM for the second? group




