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


def compute_wass_dist_cycle_time(log_real, log_sim_df):
    
    cycle_time_real = []
    for trace in log_real:
        cycle_time_real.append((trace[-1]['time:timestamp'] - trace[0]['start:timestamp']).total_seconds()/len(trace))

    log_sim_df['start_time'] = pd.to_datetime(log_sim_df['start_time'])
    log_sim_df['end_time'] = pd.to_datetime(log_sim_df['end_time'])

    case_ids = list(log_sim_df['case_id'].unique())
    cycle_time_sim = []
    for i in case_ids:
        cycle_time_sim.append((list(log_sim_df[log_sim_df['case_id'] == i]['end_time'])[-1] - list(log_sim_df[log_sim_df['case_id'] == i]['start_time'])[0]).total_seconds()/len(log_sim_df[log_sim_df['case_id'] == i]))

    return wasserstein_distance(cycle_time_real, cycle_time_sim)
    

def compute_wass_dist_waiting_time(log_real, log_sim_df):

    activities = pm4py.get_event_attribute_values(log_real, "concept:name")

    a_real = {a:[] for a in list(activities.keys())}
    for trace in log_real:
        for i in range(1,len(trace)):
            a_real[trace[i]["concept:name"]].append((trace[i]["start:timestamp"]-trace[i-1]["time:timestamp"]).total_seconds())

    a_sim = {}
    for a in list(activities.keys()):
        log_sim_a = log_sim_df[log_sim_df['activity'] == a]
        a_sim[a] = list((pd.to_datetime(log_sim_a['start_time']) - pd.to_datetime(log_sim_a['enable_time'])).apply(lambda x: x.total_seconds()))

    wass_distances = dict()
    for a in list(activities.keys()):
        try:
            wass_distances[a] = wasserstein_distance(a_real[a], a_sim[a])*activities[a]/sum(activities.values())
        except:
            continue

    return np.mean(list(wass_distances.values()))