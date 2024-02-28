import pm4py
import numpy as np
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
from scipy.stats import wasserstein_distance



def compute_wass_err(log_real, log_sim_df):
    
    activities = pm4py.get_event_attribute_values(log_real, "concept:name")
    cycle_time_real = {a:[] for a in list(activities.keys())}
    
    for trace in log_real:
        cycle_time_real[trace[0]['concept:name']].append(0)
        for i in range(1, len(trace)):
            cycle_time_real[trace[i]['concept:name']].append((trace[i]['time:timestamp']-trace[i-1]['time:timestamp']).total_seconds())

    log_sim_df['start_time'] = pd.to_datetime(log_sim_df['start_time'])
    log_sim_df['end_time'] = pd.to_datetime(log_sim_df['end_time'])
    cycle_time_sim = {a:[] for a in list(activities.keys())}

    case_ids = list(log_sim_df['case_id'].unique())
    for i in case_ids:
        trace_end_times = list(pd.to_datetime(log_sim_df[(log_sim_df['case_id'] == i)]['end_time']))
        trace_activities = list(log_sim_df[(log_sim_df['case_id'] == i)]['activity'])
        for j in range(len(trace_end_times)):
            if j > 0:
                act = trace_activities[j]
                t = trace_end_times[j]
                t_prev = trace_end_times[j-1]
                cycle_time_sim[act].append((t - t_prev).total_seconds())
            else:
                act = trace_activities[j]
                cycle_time_sim[act].append(0)
    
    for a in list(activities.keys()):
        if cycle_time_sim[a]==[]:
            cycle_time_sim[a]=[0]*len(cycle_time_real[a])
        else:
            continue

    return {a: wasserstein_distance(cycle_time_real[a], cycle_time_sim[a]) for a in list(activities.keys())}


def compute_error_sota(log_real, log_sim_df):

    activities = pm4py.get_event_attribute_values(log_real, "concept:name")
    cycle_time_real = []
    wt_time_real = {a:[] for a in list(activities.keys())}
    
    for trace in log_real:
        wt_time_real[trace[0]['concept:name']].append(0)
        for i in range(1, len(trace)):
            wt_time_real[trace[i]['concept:name']].append((trace[i]['start:timestamp']-trace[i-1]['time:timestamp']).total_seconds())
        cycle_time_real.append((trace[-1]['time:timestamp']-trace[0]['start:timestamp']).total_seconds())


    log_sim_df['start_time'] = pd.to_datetime(log_sim_df['start_time'])
    log_sim_df['end_time'] = pd.to_datetime(log_sim_df['end_time'])
    cycle_time_sim = []
    wt_time_sim = {a:[] for a in list(activities.keys())}

    case_ids = list(log_sim_df['case_id'].unique())
    for i in case_ids:
        trace_start_times = list(pd.to_datetime(log_sim_df[(log_sim_df['case_id'] == i)]['start_time']))
        trace_end_times = list(pd.to_datetime(log_sim_df[(log_sim_df['case_id'] == i)]['end_time']))
        trace_activities = list(log_sim_df[(log_sim_df['case_id'] == i)]['activity'])
        for j in range(len(trace_end_times)):
            if j > 0:
                act = trace_activities[j]
                t = trace_start_times[j]
                t_prev = trace_end_times[j-1]
                wt_time_sim[act].append((t - t_prev).total_seconds())
            else:
                act = trace_activities[j]
                wt_time_sim[act].append(0)
        cycle_time_sim.append((trace_end_times[-1] - trace_start_times[0]).total_seconds())

    for a in list(activities.keys()):
        if wt_time_sim[a]==[]:
            wt_time_sim[a]=[0]*len(wt_time_real[a])
        else:
            continue

    wt_time_errors = {a: wasserstein_distance(wt_time_real[a], wt_time_sim[a]) for a in list(activities.keys())}
    
    return wasserstein_distance(cycle_time_real, cycle_time_sim) + np.mean(list(wt_time_errors.values()))


def compute_start_difference(log_sim_df):
    
    log_path = 'data/purchasing_example.xes'
    log_real = xes_importer.apply(log_path)
    log_real_df = pm4py.convert_to_dataframe(log_real)
    log_real_df = log_real_df.sort_values(by='time:timestamp')
    log_real_df = log_real_df.loc[log_real_df['lifecycle:transition']!='complete',['org:resource','time:timestamp','lifecycle:transition', 'concept:name']]
    log_real_df['time:timestamp'] = pd.to_datetime(log_real_df['time:timestamp'])
    
    log_sim_df = log_sim_df.loc[:,['org:resource','time:timestamp','start:timestamp','lifecycle:transition', 'concept:name']].sort_values(by='time:timestamp')
    log_sim_df = log_sim_df.sort_values(by='time:timestamp')
    log_sim_df['start:timestamp'] = pd.to_datetime(log_sim_df['start:timestamp'])

    activities = list(log_real_df['concept:name'].unique())

    delta_starts_median = {a:[] for a in activities}
    delta_starts_mean = {a:[] for a in activities}
    delta_starts_weighted = {a:[] for a in activities}
    for a in activities:
        delta_starts_median[a] = np.median([abs(a_i-b_i) for a_i,b_i in zip(log_real_df.loc[log_real_df['concept:name']==a,'time:timestamp'], log_sim_df.loc[log_sim_df['concept:name']==a,'start:timestamp'])])
        delta_starts_mean[a] = np.mean([abs(a_i-b_i) for a_i,b_i in zip(log_real_df.loc[log_real_df['concept:name']==a,'time:timestamp'], log_sim_df.loc[log_sim_df['concept:name']==a,'start:timestamp'])])
        delta_starts_weighted[a] = np.mean([abs(a_i-b_i) for a_i,b_i in zip(log_real_df.loc[log_real_df['concept:name']==a,'time:timestamp'], log_sim_df.loc[log_sim_df['concept:name']==a,'start:timestamp'])])/len(log_real_df.loc[log_real_df['concept:name']==a,'time:timestamp'])

    return delta_starts_median, delta_starts_mean, np.mean(list(delta_starts_weighted.values()))