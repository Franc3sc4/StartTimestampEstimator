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
    
    activities = pm4py.get_event_attribute_values(log_real, "concept:name")
    cycle_time_real = {a:[] for a in list(activities.keys())}
    
    for trace in log_real:
        t_0 = trace[0]['start:timestamp'] # 'Create Purchase Requisition' è la prima activity di ogni traccia
        for i in range(len(trace)):
            cycle_time_real[trace[i]['concept:name']].append((trace[i]['time:timestamp']-t_0).total_seconds())

    log_sim_df['start_time'] = pd.to_datetime(log_sim_df['start_time'])
    log_sim_df['end_time'] = pd.to_datetime(log_sim_df['end_time'])
    cycle_time_sim = {a:[] for a in list(activities.keys())}

    case_ids = list(log_sim_df['case_id'].unique())
    for i in case_ids:
        t_0 = pd.to_datetime(list(log_sim_df[log_sim_df['case_id'] == i]['start_time'])[0])
        for a in list(log_sim_df[log_sim_df['case_id'] == i]['activity'].unique()):
            t = list(log_sim_df[(log_sim_df['case_id'] == i) & (log_sim_df['activity'] == a)]['end_time'])
            for t_1 in t:
                cycle_time_sim[a].append((t_1 - t_0).total_seconds())
    

    #print('mean cycle_time_real[Create Request for Quotation]', np.mean(cycle_time_real['Create Request for Quotation']))
    #print('mean cycle_time_sim[Create Request for Quotation]',np.mean(cycle_time_sim['Create Request for Quotation']))
    return {a: round(wasserstein_distance(cycle_time_real[a], cycle_time_sim[a]),2) for a in list(activities.keys())}
    

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