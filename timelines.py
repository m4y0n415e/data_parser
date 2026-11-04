import argparse
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from encoding import detect_encoding
from sklearn import set_config
from sklearn.mixture import GaussianMixture

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

    subset = ['patient_globalentryid', 'reportdate']
    df_ldct = df_ldct.drop_duplicates(subset, keep='first')

    df_ldct.sort_values(subset, inplace=True)

    df_ldct['reportdate'] = pd.to_datetime(df_ldct['reportdate'])

    df_ldct['days_since_ldct_visit'] = df_ldct.groupby('patient_globalentryid')['reportdate'].diff().dt.days

    df_ldct['visit_sequence'] = df_ldct.groupby('patient_globalentryid')['reportdate'].cumcount() + 1

    patient_id = '001ba35b-281c-432c-9187-3a58b7d928a9'

    print(df_ldct[df_ldct['patient_globalentryid'] == patient_id][['patient_globalentryid', 'visit_sequence']])

    set_config(transform_output="pandas")

    pre_x_data = df_ldct['days_since_ldct_visit'].astype(float)

    upper_threshold = 730
    lower_threshold = 45
    x_data = pre_x_data[(pre_x_data > 0) & (pre_x_data <= upper_threshold) & (pre_x_data >= lower_threshold)].to_frame()

    with open("output_files/number_of_dates.txt", "a") as f:
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
    # print(df_ldct[['days_since_ldct_visit', 'visit_category']].dropna().head(15))

    df_grouped = df_ldct.groupby(['visit_category'])

    print(df_grouped['days_since_ldct_visit'].agg(['min','max','count']))


    # preparing the df_ldct table for Sankey creation

    conditions = [
        df_ldct['visit_category'].isna() & (df_ldct['days_since_ldct_visit'] < lower_threshold),
        df_ldct['visit_category'].isna() & (df_ldct['days_since_ldct_visit'] > upper_threshold)
    ]
    choices = ['Quick examination', 'Comeback after > 2 yrs']

    df_ldct['visit_category'] = df_ldct['visit_category'].fillna(
        pd.Series(np.select(conditions, choices, default='Inne'), index=df_ldct.index)
    )

    df_ldct.loc[df_ldct['visit_sequence'] == 1, 'visit_category'] = 'Start'

    # building source nodes for Sankey
    df_ldct['sankey_node'] = 'Visit no. ' + df_ldct['visit_sequence'].astype(str) + ' (' + df_ldct['visit_category'] + ')'

    df_ldct['target_node'] = df_ldct.groupby('patient_globalentryid')['sankey_node'].shift(-1)

    # print(df_ldct[df_ldct['patient_globalentryid'] == patient_id][['patient_globalentryid', 'visit_sequence', 'sankey_node', 'target_node']])


    # agregation of data for Sankey plot

    df_pre_sankey = df_ldct.dropna(subset=['target_node'])
    data_for_sankey = df_pre_sankey.groupby(['sankey_node', 'target_node']).size().reset_index(name='value')
    #print(data_for_sankey)
    
    unique_nodes = pd.concat([data_for_sankey['sankey_node'], data_for_sankey['target_node']]).unique().tolist()

    node_map = {node_name: idx for idx, node_name in enumerate(unique_nodes)}

    data_for_sankey['source_id'] = data_for_sankey['sankey_node'].map(node_map)
    data_for_sankey['target_id'] = data_for_sankey['target_node'].map(node_map)


    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=unique_nodes
        ),
        link=dict(
            source=data_for_sankey['source_id'],
            target=data_for_sankey['target_id'],
            value=data_for_sankey['value']
        )
    )])

    fig.update_layout(
        title_text="Patient timeline trajectories based on the LDCT visits data",
        font_size=10
    )

    fig.show()

    # print(df_ldct['days_since_initial_visit'].astype(float).min())

    # draw_graphs(df_ldct)


