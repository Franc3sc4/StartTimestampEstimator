import pm4py
import numpy as np
import pandas as pd
from scipy.stats import wasserstein_distance


def compute_wass_dist_execution(log_real, log_sim_df):

    activities = list(pm4py.get_event_attribute_values(log_real, "concept:name").keys())

    a_real = {a:[] for a in activities}
    for trace in log_real:
        for event in trace:
            a_real[event["concept:name"]].append((event["time:timestamp"]-event["start:timestamp"]).total_seconds())


    a_sim = {}
    for a in activities:
        log_sim_a = log_sim_df[log_sim_df['activity'] == a]
        a_sim[a] = list((pd.to_datetime(log_sim_a['end_time']) - pd.to_datetime(log_sim_a['start_time'])).apply(lambda x: x.total_seconds()))

    wass_distances = {a: wasserstein_distance(a_real[a], a_sim[a]) for a in activities}

    return np.mean(list(wass_distances.values()))