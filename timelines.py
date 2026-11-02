import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from encoding import detect_encoding
from sklearn.preprocessing import PowerTransformer
from sklearn import set_config
from sklearn.mixture import GaussianMixture
from statsmodels.tsa.ar_model import AutoReg
from scipy.stats import norm

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
    

def pdf_distribution_hist(timeline, sorted_means, st_dev, sorted_weights, optimal_k, transformed_df, transformer):
    # calculating the values of a PDF algirithm, and plotting the distribution
    for i in range(0, optimal_k):
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


def create_GMM(transformed_df, k):
    # creating the GMM for the chosen number of components
    X = transformed_df.astype(float)
    model = GaussianMixture(n_components=k, random_state=0, n_init=10, covariance_type='tied')
    model.fit(X)

    return model


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-n', '--ldct',
            required=True
    )

    args = parser.parse_args()

    df_ldct = load(args.ldct)

    set_config(transform_output="pandas")

    pre_x_data = df_ldct['days_since_ldct_visit'].astype(float)

    upper_threshold = 730
    lower_threshold = 45
    x_data = pre_x_data[(pre_x_data > 0) & (pre_x_data <= upper_threshold) & (pre_x_data >= lower_threshold)].to_frame()

    with open("number_of_dates.txt", "a") as f:
        f.write(x_data.value_counts().to_string())


    # initializing the GMM clustering
    clusters_number = 4
    model = create_GMM(x_data, clusters_number)

    # creating labels and sorting means from the data
    labels = model.predict(x_data)

    means = model.means_.flatten()

    sorted_means = np.argsort(means)

    mean_labels = ['3mos', '6mos', '12mos', 'late_visits']

    means_w_labels = dict(zip(sorted_means, mean_labels))

    labels_series = pd.Series(labels, x_data.index).map(means_w_labels)

    # adding labels as visit category for each patient's visit
    df_ldct['visit_category'] = labels_series

    df_ldct['days_since_ldct_visit'] = df_ldct['days_since_ldct_visit'].astype(float)

    # printing results to test accuracy
    print(df_ldct[['days_since_ldct_visit', 'visit_category']].dropna().head(15))

    df_grouped = df_ldct.groupby(['visit_category'])

    print(df_grouped['days_since_ldct_visit'].agg(['min','max','count']))





    # for row in transformed_x_data.intertuples():


    # draw_graphs(df_ldct)


