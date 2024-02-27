# Execution time: 6 mins 19 secs, 10 mins 7 secs, 16 mins 23 secs

from prosimos.simulation_engine import *
import json
from src.simulation_utils import update_sim_params, run_simulation
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.utils import set_start_timestamp_from_alpha
from src.temporal_utils import find_execution_distributions
from src.metric_utils import compute_error_sota
import pm4py
import timeit
import random
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--log_path', type=str, default='data/purchasing_example.xes')
parser.add_argument('--bpmn_path', type=str, default='data/purchasing_example.bpmn')
parser.add_argument('--json_path', type=str, default='data/purchasing_example.json')
parser.add_argument('--output_path', type=str, default='results/bisection')
parser.add_argument('--starting_at', type=str, default='2011-01-01T00:00:00.000000+00:00')
parser.add_argument('--perc_head_tail', type=float, default=.1)
parser.add_argument('--delta', type=float, default=.1)
parser.add_argument('--shuffle_activities', type=bool, default=False)

args = parser.parse_args()

bpmn_path = args.bpmn_path
json_path = args.json_path
perc_head_tail = args.perc_head_tail
log_path = args.log_path
starting_at = args.starting_at
output_path = args.output_path
delta = args.delta
shuffle_activities = args.shuffle_activities


def compute_distance(alphas_best, log, json_data, output_path, diffsim_info, perc, gen_cases, starting_at):

    total_cases = gen_cases+int(gen_cases*perc)
    log = set_start_timestamp_from_alpha(log, alphas_best)

    if shuffle_activities:
        df_log_alpha = pm4py.convert_to_dataframe(log)
        df_log_alpha.to_csv(output_path + '/log_alpha_one_shuffle.csv', index=False)
    else:
        df_log_alpha = pm4py.convert_to_dataframe(log)
        df_log_alpha.to_csv(output_path + '/log_alpha_one.csv', index=False)

    best_distr_act_execution = find_execution_distributions(log)

    json_data, diffsim_info = update_sim_params(json_data, diffsim_info, best_distr_act_execution)

    run_simulation(
        diffsim_info,
        log_out_path = output_path + "/simulated_log.csv",
        starting_at = starting_at
    )

    log_sim_df = pd.read_csv(output_path + "/simulated_log.csv")
    min_case_id = int(total_cases*perc/2)
    max_case_id = min_case_id+gen_cases
    log_sim_df = log_sim_df[(log_sim_df["case_id"]>min_case_id) & (log_sim_df["case_id"]<=max_case_id)]
    err_cycle = compute_error_sota(log, log_sim_df)

    return err_cycle, df_log_alpha


def prev_succ(alpha, delta, trial=3):
    L=[]
    i=1
    while i<=trial:
        x = alpha - delta*i
        if x>0:      
            L.append(round(x,3))
        i+=1
    return L

def next_succ(alpha, delta, trial=3):
    L=[]
    i=1
    while i<=trial:
        x = alpha + delta*i
        if x<1:      
            L.append(round(x,3))
        i+=1
    return L


def run_framework(log_path, bpmn_path, json_path, output_path, delta, starting_at, perc_head_tail):
    log = xes_importer.apply(log_path)
    try:
        log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)
    except:
        pass

    gen_cases = len(log)
    total_cases = gen_cases+int(gen_cases*perc_head_tail)

    activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())

    if shuffle_activities:
        random.shuffle(activities)

    with open(json_path) as json_file:
        json_data = json.load(json_file)

    diffsim_info = SimDiffSetup(bpmn_path, json_path, is_event_added_to_log=False, total_cases=total_cases)


    start = timeit.default_timer()
    alphas_best = {a: round(random.random(),2) for a in activities}
    epsilon_best, df_log_alpha = compute_distance(alphas_best, log, json_data, output_path, diffsim_info, perc_head_tail, gen_cases, starting_at)
    alphas_track = {a: [v] for a,v in alphas_best.items()}
    errors_track = [epsilon_best]

    for a in activities:
        print('\nActivity:',a)
        Q_tried = [alphas_best[a]]
        Q_next = prev_succ(alphas_best[a], delta)+next_succ(alphas_best[a], delta)
        while Q_next!=[]:
            alpha = alphas_best.copy()
            alpha[a] = Q_next.pop(0)
            if alpha[a] not in Q_tried:
                Q_tried.append(alpha[a])
                alphas_track[a].append(alpha[a])
                epsilon, df_log_alpha = compute_distance(alphas_best, log, json_data, output_path, diffsim_info, perc_head_tail, gen_cases, starting_at)
                errors_track.append(epsilon)
                if epsilon < epsilon_best: # abs(epsilon[a]-epsilon_best[a]) < 60*60 : check per fermare le iterazioni
                    if alpha[a]<alphas_best[a]:
                        Q_next = [x for x in Q_next if x<alpha[a]]
                    else:
                        Q_next = [x for x in Q_next if x>alpha[a]]
                    alphas_best[a] = alpha[a]
                if epsilon >= epsilon_best: 
                    if alpha[a]<alphas_best[a]:
                        Q_next = [x for x in Q_next if x>alphas_best[a]]
                    if alpha[a]>alphas_best[a]:
                        Q_next = [x for x in Q_next if x<alphas_best[a]]

    stop = timeit.default_timer()
        
    print('\nExecution time: {} minutes and {} seconds'.format(divmod(stop-start, 60)[0],divmod(stop-start, 60)[1])) # ~ 12' 10"
    print("\nBest alphas", alphas_best)
    print("\nBest Wasserstein distances", epsilon_best)

    return df_log_alpha, alphas_track, errors_track


if __name__ == '__main__':
    run_framework(log_path, bpmn_path, json_path, output_path, delta, starting_at, perc_head_tail)