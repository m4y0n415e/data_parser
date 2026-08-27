import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
    
set_config(transform_output="pandas")
# print((df_ldct['visit_sequence'].astype(int)).mean()) # something weird happens here
no_in_seq = df_ldct['visit_sequence'].astype(int) == 2 # 2, 3 and 4 work correctly

df_ldct['reportdate'] = pd.to_datetime(df_ldct['reportdate'], format='mixed')
df_filtered = df_ldct[no_in_seq].copy()
df_filtered.fillna({'days_since_ldct_visit': 0}, inplace=True) 

scaler = StandardScaler()

scaled_df = scaler.fit_transform(df_filtered)
 
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