import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
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
            '-i', '--initial', 
            required=True
    )

    parser.add_argument(
            '-n', '--ndtk',
            required=True
    )

    parser.add_argument(
            '-c', '--consultation',
            required=True
    )

    args = parser.parse_args()

    df_init = load(args.initial)
    df_ndtk = load(args.ndtk)
    df_consult = load(args.consultation)

    df_joined = pd.concat(
               (df_ndtk[['patient_globalentryid', 'days_since_initial_visit']],
               df_consult[['patient_globalentryid', 'days_since_initial_visit']]) # zmienic logike na krokami-data od ostatniej wizyty-tylko wynikowe!
        )

    df_joined['days_since_initial_visit'].astype(float)
    df_joined = df_joined.fillna({'days_since_initial_visit': 0}, inplace=True)

    df_data = df_joined['days_since_initial_visit'].dropna().to_frame()
    scaled_df = StandardScaler().fit_transform(df_data)
#
#    X = df_joined['days_since_initial_visit'].values.reshape(-1, 1)
#
#    inertia = []
#    silhouette_scores = []
#    K_range = range(2, 15)
#
#    for k in K_range:
#        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#        kmeans.fit(X)
#        
#        inertia.append(kmeans.inertia_)
#        silhouette_scores.append(silhouette_score(X, kmeans.labels_))
#
#    # Plotting the Elbow Method
#    plt.figure(figsize=(12, 5))
#    plt.subplot(1, 2, 1)
#    plt.plot(K_range, inertia, marker='o')
#    plt.title('Elbow Method For Optimal k')
#    plt.xlabel('Number of Clusters (k)')
#    plt.ylabel('Inertia')
#
#    # Plotting the Silhouette Scores
#    plt.subplot(1, 2, 2)
#    plt.plot(K_range, silhouette_scores, marker='o')
#    plt.title('Silhouette Score For Optimal k')
#    plt.xlabel('Number of Clusters (k)')
#    plt.ylabel('Silhouette Score')
#    plt.tight_layout()
#    plt.savefig("output_files/clusters_calcultaion.png")

    kmeans = KMeans(init='random', n_clusters=5, n_init=10, random_state=1)

    kmeans.fit(scaled_df)

    df_joined['cluster_id'] = kmeans.labels_

    point_in_time = kmeans.cluster_centers_.flatten()

    df_joined['days_since_initial_visit'] = pd.to_numeric(df_joined['days_since_initial_visit'], errors='coerce')

    frequencies = scaled_df['cluster_id'].value_counts(sort=False)

    standard_dev = scaled_df['days_since_initial_visit'].groupby(scaled_df['cluster_id']).std().fillna(5)

    plt.figure(figsize=(12,6))

    plt.bar(x=point_in_time,
    height=frequencies,
    width=standard_dev,
    color='steelblue',
    edgecolor='black',
    alpha=0.8
    )
    
    plt.title("'Patient visits with k-means temporal nodes")
    plt.xlabel("Days since initial visit")
    plt.ylabel("Algorithm assigned cluster id")

    plt.show()









