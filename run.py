from prosimos.simulation_engine import *
import json
from src.simulation_utils import update_sim_params, run_simulation
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.utils import set_start_timestamp_from_alpha
from src.temporal_utils import find_execution_distributions
from src.metric_utils import compute_wass_dist_execution, compute_wass_dist_cycle_time, compute_wass_dist_waiting_time
import pm4py
import pandas as pd

bpmn_path = 'data/purchasing_example.bpmn'
json_path = 'data/purchasing_example.json'
perc = .1
gen_cases = 608
total_cases = gen_cases+int(gen_cases*perc)
log_path = 'data/purchasing_example.xes'
starting_at = '2011-01-01T00:00:00.000000+00:00'
N_iterations = 1
save_log_alpha= True

log = xes_importer.apply(log_path)
log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)

#log_df = pm4py.convert_to_dataframe(log)
#log_df = log_df.loc[log['lifecycle:transition']=="complete",["Resource", "Activity", "time:timestamp", "case:concept:name"]]
#log_df.rename(columns ={"Resource":"org:resource","Activity":"concept:name"}, inplace=True)

activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())

with open(json_path) as json_file:
    json_data = json.load(json_file)

diffsim_info = SimDiffSetup(bpmn_path, json_path, is_event_added_to_log=False, total_cases=total_cases)

errors = []

for i in range(N_iterations):
    # TODO crea alpha
    if i == 0:
        alphas = {a: 0.25 for a in activities}
    #else:
    #    alphas = update_alphas()
        
    log = set_start_timestamp_from_alpha(log, alphas)

    if save_log_alpha:
        df_log_alpha = pm4py.convert_to_dataframe(log)
        df_log_alpha.to_csv('data/log_alpha.csv', index=False)

    best_distr_act_execution = find_execution_distributions(log)

    json_data, diffsim_info = update_sim_params(json_data, diffsim_info, best_distr_act_execution)

    run_simulation(
        diffsim_info,
        log_out_path = "data/simulated_log.csv",
        starting_at = starting_at
    )

    log_sim_df = pd.read_csv("data/simulated_log.csv")
    min_case_id = int(total_cases*perc/2)
    max_case_id = min_case_id+gen_cases
    log_sim_df = log_sim_df[(log_sim_df["case_id"]>min_case_id) & (log_sim_df["case_id"]<=max_case_id)]
    # err_ex = compute_wass_dist_execution(log, log_sim_df)
    # print('Execution Activities Avg Wasserstein distance: ', round(err_ex, 2))
    err_cycle = compute_wass_dist_cycle_time(log, log_sim_df)
    print('Cycle time Avg Wasserstein distance: ', err_cycle)
    #err_wt = compute_wass_dist_waiting_time(log, log_sim_df)
    #print('Waiting time Activities Avg Wasserstein distance: ', round(err_wt, 2))

    err = err_cycle #+ err_wt
    print('Error: ', err)
    errors.append(err)