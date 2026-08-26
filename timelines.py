import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, PowerTransformer
from sklearn import set_config
from sklearn.mixture import GaussianMixture
from statsmodels.tsa.ar_model import AutoReg
from encoding import detect_encoding
from scipy.stats import norm
from kneed import KneeLocator, DataGenerator

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df

def draw_graphs(df_ldct, df_filtered):
    # initializing the KMeans model to assign clusters for every group - draft version
    # kmeans = KMeans(init='random', n_clusters=3, n_init=10, random_state=1)
    # kmeans.fit(scaled_df)

    # df_filtered['cluster_id'] = pd.Series(kmeans.labels_)
    # point_in_time = (df_filtered['days_since_ldct_visit'].astype(float).groupby(df_filtered['cluster_id'])).mean()
    # df_filtered['days_since_ldct_visit'] = pd.to_numeric(df_filtered['days_since_ldct_visit'], errors='coerce')
    # frequencies = df_filtered['cluster_id'].value_counts(sort=False).sort_index(ascending=True)

    # v-line plot of the cluster centers
    # plt.vlines(x=point_in_time, ymin=0, ymax=frequencies.astype(float).mean())

    # plt.title("Patient visits with k-means temporal nodes")
    # plt.ylabel("Frequency")
    # plt.xlabel("Time cluster of the visits")
    
    # plt.savefig(R"graphs/kmeans_interval_lines.png")
    # plt.clf()

    # kde plot of the days clusters (concentrated around 0, 6 mo, and 12 mo timestamps)
    x = df_ldct['days_since_initial_visit_in_ldct'].astype(float)
    df_ldct['days_since_initial_visit_in_ldct'].astype(float).plot.kde(bw_method=0.05)
    plt.xticks(np.arange(min(x), max(x)+1, 30.0), rotation=45)

    plt.savefig(R"graphs/kde_days.png")
    plt.clf()
    

def calculate_bic_for_gmm(X, max_clusters):
    bic_values = []
    for n in range(1, max_clusters + 1):
        gmm = GaussianMixture(n_components=n, random_state=0).fit(X)
        bic_values.append(gmm.bic(X))

    # creating a BIC plot to visualize the "knee" point
    plt.plot(range(1,12), bic_values, marker='o')
    plt.title('BIC values')
    plt.xlabel('N-components')
    plt.ylabel('BIC')
    plt.show()
    plt.clf() 

    return bic_values


def knee_point_calculation(max_clusters, bic_values):
    # kneedle = KneeLocator(range(1, max_clusters + 1), bic_values, S=20, curve='convex', direction='decreasing')        
    # knees.append(kneedle.knee)
    # norm_knees.append(kneedle.norm_knee)
    
    diff_table = np.diff(bic_values, n=1)
    minimum = np.amin(diff_table)

    threshold = 0.01 * minimum
    knee_point = 0
    for index in range(1, max_clusters - 1):
        if (diff_table[index] > threshold):
            knee_point = index + 1
            break
    # print(knee_point)
    return knee_point


def create_GMM(df_ldct, optimal_k): # continue changes from here - making the code universal for the gmm model, with the indexes below
    # creating the GMM for 4 components (based on the BIC score)
    X = df_ldct['days_since_initial_visit_in_ldct'].astype(float).values.reshape(-1,1)
    model = GaussianMixture(n_components=optimal_k, random_state=0, n_init=10)
    model.fit(X)

    # sorting the indexes into a proper sequence
    order = model.means_
    flat_means = order.flatten()
    sorted_indexes = np.argsort(flat_means)

    # sorting the means, covariances and weights
    sorted_means = model.means_.flatten()[sorted_indexes]
    sorted_covs = model.covariances_.flatten()[sorted_indexes]
    sorted_weights = model.weights_.flatten()[sorted_indexes]

    # calculating the standard deviation and the "timeline"
    st_dev = np.sqrt(sorted_covs)
    timeline = np.linspace(0, sorted_means[3] + 3 * st_dev[3], 1000)
    timeline_2d = timeline.reshape(-1, 1) # needs evaluation; why 3 ?

    probability_matrix_np = model.predict_proba(timeline_2d)[:, sorted_indexes] 
    # predict_proba basically uses PDF to determine probability of an x belonging to a Gaussian function n

    max_el = []
    
    # code below needs rewriting to be universal for different data sets

    # creating the probability matrix for each components - which values fit best into a component Gaussian
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

    # printing the maximum elements of each of these functions, which indicate that it is an intersection point
    print(timeline[max_el])

    boundary_coordinates = timeline[max_el]

    # calculating the values of a PDF algirithm, and plotting the distribution
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
    # plt.show()

    # initializaing the GMM algorithm for the values in-between each intersection point (0-1, 1-2, 2-0)    


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

    draw_graphs(df_ldct, df_filtered)

    x_data = df_ldct['days_since_initial_visit_in_ldct'].astype(float)

    # setting the threshold for BIC score
    threshold = x_data.quantile(0.95)

    clean_data = x_data[x_data <= threshold]

    X_data = clean_data.values.reshape(-1,1)

    transformer = PowerTransformer(method='yeo-johnson')

    transformed_X_data = transformer.fit_transform(X_data)

    max_clusters = 11

    bic_values = calculate_bic_for_gmm(transformed_X_data, max_clusters)

    optimal_k = knee_point_calculation(max_clusters, bic_values)
   
    create_GMM(df_ldct, optimal_k)

    # Conclude with one GMM for the second? group




