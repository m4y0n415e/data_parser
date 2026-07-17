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
    # plt.show()

    plt.clf()
    return np.argmin(bic_scores) + 1
    
def create_GMM(df_ldct):
    X = df_ldct['days_since_initial_visit_in_ldct'].astype(float).values.reshape(-1,1)
    model_4 = GaussianMixture(n_components=4, random_state=0, n_init=10)
    model_4.fit(X)
    print(model_4.means_)

    order = model_4.means_

    flat_means = order.flatten()

    sorted_indexes = np.argsort(flat_means)

    sorted_means = model_4.means_.flatten()[sorted_indexes]
    sorted_covs = model_4.covariances_.flatten()[sorted_indexes]
    sorted_weights = model_4.weights_.flatten()[sorted_indexes]

    st_dev = np.sqrt(sorted_covs)
    timeline = np.linspace(0, sorted_means[3] + 3 * st_dev[3], 1000)
    timeline_2d = timeline.reshape(-1, 1)

    probability_matrix_np = model_4.predict_proba(timeline_2d)[:, sorted_indexes] # predict_proba basically uses PDF to determine probability of an x belonging to a Gaussian function n

    max_el = []

    delta_01 = probability_matrix_np[:, 1] - probability_matrix_np[:, 0]
    indices_01 = np.where(np.diff(np.sign(delta_01)) != 0)[0]
    coords_01 = timeline[indices_01]
    mask_01 = (coords_01 >= sorted_means[0]) & (coords_01 <= sorted_means[1])
    valid_index_01 = indices_01[mask_01][0]
    max_el.append(valid_index_01)

    delta_12 = probability_matrix_np[:, 2] - probability_matrix_np[:, 1]
    indices_12 = np.where(np.diff(np.sign(delta_12)) != 0)[0]
    coords_12 = timeline[indices_12]
    mask_12 = (coords_12 >= sorted_means[1]) & (coords_12 <= sorted_means[2])
    valid_index_12 = indices_12[mask_12][0]
    max_el.append(valid_index_12)

    delta_23 = probability_matrix_np[:, 3] - probability_matrix_np[:, 2]
    indices_23 = np.where(np.diff(np.sign(delta_23)) != 0)[0]
    coords_23 = timeline[indices_23]
    mask_23 = (coords_23 >= sorted_means[2]) & (coords_23 <= sorted_means[3])
    valid_index_23 = indices_23[mask_23][0]
    max_el.append(valid_index_23)

    print(timeline[max_el])

    boundary_coordinates = timeline[max_el]

    pdf_values_1 = norm.pdf(timeline, loc=sorted_means[1], scale=st_dev[1]) * sorted_weights[1]
    pdf_values_2 = norm.pdf(timeline, loc=sorted_means[2], scale=st_dev[2]) * sorted_weights[2]
    pdf_values_3 = norm.pdf(timeline, loc=sorted_means[3], scale=st_dev[3]) * sorted_weights[3]

    plt.plot(timeline, pdf_values_1, label="Component 1", color="blue")
    plt.plot(timeline, pdf_values_2, label="Component 2", color="red")
    plt.plot(timeline, pdf_values_3, label="Component 3", color="yellow")
    plt.title("PDF of xyz Distribution")
    plt.xlabel("x")
    plt.ylabel("Probability Density")
    plt.legend()
    plt.show()

    # potem GMM od kazdego punktu do punktu (-11-1, 1-2, 2-0)

    # histogram porównać z pdf-em

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




