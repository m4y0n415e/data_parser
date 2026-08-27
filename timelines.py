import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import PowerTransformer
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

def draw_graphs(df_ldct):
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
    # plt.show()
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

    return knee_point


def pdf_distribution_hist(timeline, sorted_means, st_dev, sorted_weights, optimal_k, transformed_df, transformer):
    # calculating the values of a PDF algirithm, and plotting the distribution
    for i in range(1, optimal_k):
        pdf_values = norm.pdf(timeline, loc=sorted_means[i], scale=st_dev[i]) * sorted_weights[i]
        label = "Component " + str(i)
        plt.plot(timeline, pdf_values, label=label)

    plt.title("PDF of the visit dates distribution")
    plt.xlabel("x")
    plt.ylabel("Probability Density")
    plt.legend()

# code for creating a histogram of the same data

    plt.hist(transformed_df, bins='fd', density=True)
    x_values = plt.xticks()[0]
    plt.xticks(ticks=x_values, labels=np.round(transformer.inverse_transform(x_values.reshape(-1,1)).flatten()))
    plt.show()
    plt.clf()


def create_GMM(transformed_df, optimal_k, transformer): # continue changes from here - making the code universal for the gmm model, with the indexes below
    # creating the GMM for the optimal number of components (based on the BIC score)
    X = transformed_df.astype(float).values.reshape(-1,1)
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
    timeline = np.linspace(0, sorted_means[-1] + 3 * st_dev[-1], 1000)
    timeline_2d = timeline.reshape(-1, 1)

    # creating the probability matrix for each components
    probability_matrix_np = model.predict_proba(timeline_2d)[:, sorted_indexes] 
    # predict_proba basically uses PDF to determine probability of an x belonging to a Gaussian function n

    max_el = []
    
    for i in range(0, optimal_k - 1):
        delta = probability_matrix_np[:, i+1] - probability_matrix_np[:, i]
        indices = np.where(np.diff(np.sign(delta)) != 0)[0]
        # coords = timeline[indices]
        # mask = (coords >= sorted_means[i]) & (coords <= sorted_means[i+1])
        # valid_index = indices[mask][0]
        # max_el.append(valid_index)
        if indices.size > 0:
            max_el.append(indices[0])
        else: max_el.append(np.argmin(np.abs(timeline - (sorted_means[i]+sorted_means[i+1]) / 2)))

    # printing the maximum elements of each of these functions, which indicate that it is an intersection point
    # print(timeline[max_el])
    boundary_coordinates = timeline[max_el]

    # drawing a pdf distribution of the timeline Gaussian functions
    pdf_distribution_hist(timeline, sorted_means, st_dev, sorted_weights, optimal_k, transformed_df, transformer)
    # histogram porównać z pdf-em



    # initializaing the GMM algorithm for the values in-between each intersection point (0-1, 1-2, 2-0)    

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
   
    create_GMM(transformed_X_data, optimal_k, transformer)

    # draw_graphs(df_ldct)




