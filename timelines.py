import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn import set_config
from encoding import detect_encoding

def load(input):
    coding = detect_encoding(input)
    try:
            df = pd.read_csv(input, encoding=coding, dtype=str)
    except FileNotFoundError:
            print("File not found.")
    return df


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

    # X = df_filtered['days_since_ldct_visit'].values.reshape(-1, 1)

    # inertia = []
    # silhouette_scores = []
    # K_range = range(2, 15)

    # for k in K_range:
    #     kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    #     kmeans.fit(X)
    #     
    #     inertia.append(kmeans.inertia_)
    #     silhouette_scores.append(silhouette_score(X, kmeans.labels_))
 
    # # Plotting the Elbow Method
    # plt.figure(figsize=(12, 5))
    # plt.subplot(1, 2, 1)
    # plt.plot(K_range, inertia, marker='o')
    # plt.title('Elbow Method For Optimal k')
    # plt.xlabel('Number of Clusters (k)')
    # plt.ylabel('Inertia')

    # # Plotting the Silhouette Scores
    # plt.subplot(1, 2, 2)
    # plt.plot(K_range, silhouette_scores, marker='o')
    # plt.title('Silhouette Score For Optimal k')
    # plt.xlabel('Number of Clusters (k)')
    # plt.ylabel('Silhouette Score')
    # plt.tight_layout()
    # plt.savefig("graphs/clusters_calcultaion.png")

    kmeans = KMeans(init='random', n_clusters=9, n_init=10, random_state=1)

    kmeans.fit(scaled_df)

    df_filtered['cluster_id'] = pd.Series(kmeans.labels_)

    point_in_time = (df_filtered['days_since_ldct_visit'].astype(float).groupby(df_filtered['cluster_id'])).mean()

    df_filtered['days_since_ldct_visit'] = pd.to_numeric(df_filtered['days_since_ldct_visit'], errors='coerce')

    # standard_dev = df_filtered['days_since_ldct_visit'].groupby(df_filtered['cluster_id']).std().sort_index(ascending=True)

    frequencies = df_filtered['cluster_id'].value_counts(sort=False).sort_index(ascending=True)

    # colors = plt.cm.viridis(np.linspace(0, 1, len(point_in_time)))
    # plt.figure(figsize=(12,6))
    #
    # plt.bar(x=point_in_time,
    # height=frequencies,
    # width=6,
    # xerr=standard_dev,
    # capsize=3,
    # color=colors,
    # edgecolor='black',
    # alpha=0.8
    # )
    # 
    # plt.title("Patient visits with k-means temporal nodes")
    # plt.ylabel("Frequency")
    # plt.xlabel("Point in time of the visits")
    #
    # plt.savefig(R"graphs/kmeans_interval.png")
    # plt.clf()

    plt.vlines(x=point_in_time, ymin=0, ymax=frequencies.astype(float).mean())

    plt.title("Patient visits with k-means temporal nodes")
    plt.ylabel("Frequency")
    plt.xlabel("Point in time of the visits")
    
    plt.savefig(R"graphs/kmeans_interval_lines.png")

    plt.clf()

    x = df_ldct['days_since_initial_visit_in_ldct'].astype(float)
    df_ldct['days_since_initial_visit_in_ldct'].astype(float).plot.kde(bw_method=0.05)

    plt.xticks(np.arange(min(x), max(x)+1, 30.0), rotation=45)

    plt.show()