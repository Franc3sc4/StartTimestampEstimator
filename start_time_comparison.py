from prosimos.simulation_engine import *
from src.simulation_utils import update_sim_params, run_simulation
from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py
import pandas as pd

import warnings
warnings.filterwarnings("ignore")


log_path_real = 'data/purchasing_example.xes'
log_path_1 = 'data2/alpha_log_WT_FIXED_greedy.xes'
log_path_2 = 'data2/alpha_log_WT_FIXED_MOGAII_001.xes'
log_path_3 = 'data2/alpha_log_WT_FIXED_MOGAII_005.xes'
log_path_4 = 'data2/alpha_log_WT_FIXED_NSGAII_001.xes'
log_path_5 = 'data2/alpha_log_WT_FIXED_NSGAII_005.xes'

#----------------------------------------------------------------------------
# preparation

activities = ['Create Purchase Requisition','Create Request for Quotation','Analyze Request for Quotation',
              'Send Request for Quotation to Supplier','Create Quotation comparison Map','Analyze Quotation Comparison Map',
              'Choose best option','Settle Conditions With Supplier','Create Purchase Order','Confirm Purchase Order',
              'Deliver Goods Services','Release Purchase Order','Approve Purchase Order for payment','Send Invoice',
              "Release Supplier's Invoice","Authorize Supplier's Invoice payment",'Pay Invoice','Amend Request for Quotation',
              'Settle Dispute With Supplier','Analyze Purchase Requisition','Amend Purchase Requisition']


def compute_start_difference_log(log_path_sim):
    
    log_path = 'data/purchasing_example.xes'
    log_real = xes_importer.apply(log_path)
    log_real = pm4py.filter_event_attribute_values(log_real, 'lifecycle:transition', ['complete'], level="event", retain=True)
    log_real_df = pm4py.convert_to_dataframe(log_real)
    log_real_df = log_real_df.sort_values(by='time:timestamp')
    #log_real_df = log_real_df.loc[log_real_df['lifecycle:transition']!='complete',['org:resource','time:timestamp','lifecycle:transition', 'concept:name']]
    log_real_df['time:timestamp'] = pd.to_datetime(log_real_df['time:timestamp'])
    
    log_sim = xes_importer.apply(log_path_sim)
    log_sim_df = pm4py.convert_to_dataframe(log_sim)
    log_sim_df = log_sim_df.sort_values(by='time:timestamp')
    log_sim_df = log_sim_df.loc[:,['org:resource','time:timestamp','start:timestamp','concept:name']].sort_values(by='time:timestamp')
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

def set_df(delta, delta_name):
    d = pd.DataFrame(delta, index=range(len(activities)))
    d = d.T
    d.reset_index(inplace=True)
    d = d[['index',0]]
    d.rename(columns={'index':'Activity',0:'Timestamp'}, inplace=True)
    d.loc[:,'log'] = delta_name
    return d

# compute deltas

delta_1 = compute_start_difference_log(log_path_1)
print('\nTime-delta between real log and alpha_log_WT_FIXED_greedy:\n')
print('\nmedian \n\n{} \n mean \n\n{}\n weighted mean value: {}\n'.format(delta_1[0], delta_1[1], delta_1[2]))

delta_2 = compute_start_difference_log(log_path_2)
print('Time-delta between real log and alpha_log_WT_FIXED_MOGAII_001:\n')
print('\nmedian \n\n{} \n mean \n\n{}\n weighted mean value: {}\n'.format(delta_2[0], delta_2[1], delta_2[2]))

delta_3 = compute_start_difference_log(log_path_3)
print('Time-delta between real log and alpha_log_WT_FIXED_MOGAII_005:\n')
print('\nmedian \n\n{} \n mean \n\n{}\n weighted mean value: {}\n'.format(delta_3[0], delta_3[1], delta_3[2]))

delta_4 = compute_start_difference_log(log_path_4)
print('Time-delta between real log and alpha_log_WT_FIXED_NSGAII_001:\n')
print('\nmedian \n\n{} \n mean \n\n{}\n weighted mean value: {}\n'.format(delta_4[0], delta_4[1], delta_4[2]))

delta_5 = compute_start_difference_log(log_path_5)
print('Time-delta between real log and alpha_log_WT_FIXED_NSGAII_005:\n')
print('\nmedian \n\n{} \n mean \n\n{}\n weighted mean value: {}\n'.format(delta_5[0], delta_5[1], delta_5[2]))


#-----------------------------------------------------------------------
# sum up values

delta_1_df = set_df(delta_1[0],'delta_1')
delta_2_df = set_df(delta_2[0],'delta_2')
delta_3_df = set_df(delta_3[0],'delta_3')
delta_4_df = set_df(delta_4[0],'delta_4')
delta_5_df = set_df(delta_5[0],'delta_5')

full_data = pd.concat([delta_1_df, delta_2_df, delta_3_df, delta_4_df, delta_5_df], ignore_index=True)
print(full_data)

