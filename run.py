# Execution time Purchase Process Case Study: 2 mins 30 secs, 4 mins 48 secs
# Execution time Prduction Case Study: 2 mins 4 secs

from prosimos.simulation_engine import *
import json
from src.simulation_utils import update_sim_params, run_simulation
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.utils import set_start_timestamp_from_alpha
from src.temporal_utils import find_execution_distributions
from src.metric_utils import compute_wass_err
import pm4py
import pandas as pd
import timeit

import warnings
warnings.filterwarnings("ignore")

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--log_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.xes')
parser.add_argument('--bpmn_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.bpmn')
parser.add_argument('--json_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.json')
parser.add_argument('--output_path', type=str, default='results/Purchase_Process_Case_Study/bisection')
parser.add_argument('--starting_at', type=str, default='2011-01-01T00:00:00.000000+00:00')
parser.add_argument('--perc_head_tail', type=float, default=.1)
parser.add_argument('--N_max_iteration', type=int, default=20)


args = parser.parse_args()

args.log_path = 'data/Production_Case_Study/production.xes'
args.bpmn_path = 'data/Production_Case_Study/production.bpmn'
args.json_path = 'data/Production_Case_Study/production.json'
output_path = 'results/Production_Case_Study/bisection'

bpmn_path = args.bpmn_path
json_path = args.json_path
perc_head_tail = args.perc_head_tail
log_path = args.log_path
starting_at = args.starting_at
N_iterations = args.N_max_iteration
output_path = args.output_path


def run_framework(log_path, bpmn_path, json_path, output_path, starting_at, perc_head_tail, N_iterations):

    log = xes_importer.apply(log_path)
    try:
        log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)
    except:
        pass

    gen_cases = len(log)
    total_cases = gen_cases+int(gen_cases*perc_head_tail)

    activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())

    with open(json_path) as json_file:
        json_data = json.load(json_file)

    diffsim_info = SimDiffSetup(bpmn_path, json_path, is_event_added_to_log=False, total_cases=total_cases)  
    
    #activities_sim = [diffsim_info.bpmn_graph.element_info[e].name for e in diffsim_info.bpmn_graph.element_info.keys() if diffsim_info.bpmn_graph.element_info[e].type == BPMN.TASK]
    #activities_not_included = [a for a in activities if a not in activities_sim]
    
    alphas_tot = [{a: 0 for a in activities}, {a: 1 for a in activities}]
    errors = []

    alphas_track = [{a: 0 for a in activities}, {a: 1 for a in activities}]
    errors_track = []

    start = timeit.default_timer()
    for i in range(N_iterations):
        print(i)
        if i == 0:
            alphas = alphas_tot[0]
        if i == 1:
            alphas = alphas_tot[1]
        if i>1:
            alphas = {a: (alphas_tot[0][a]+alphas_tot[1][a])/2 for a in activities}
            alphas_tot.append(alphas)
            alphas_track.append(alphas)
            
        log = set_start_timestamp_from_alpha(log, alphas)

        df_log_alpha = pm4py.convert_to_dataframe(log)
        df_log_alpha.to_csv(output_path + '/log_alpha.csv', index=False)

        best_distr_act_execution = find_execution_distributions(log)

        json_data, diffsim_info = update_sim_params(json_data, diffsim_info, best_distr_act_execution)


        run_simulation(
            diffsim_info,
            log_out_path = output_path + "/simulated_log.csv",
            starting_at = starting_at
        )

        log_sim_df = pd.read_csv(output_path + "/simulated_log.csv")
        min_case_id = int(total_cases*perc_head_tail/2)
        max_case_id = min_case_id+gen_cases
        log_sim_df = log_sim_df[(log_sim_df["case_id"]>min_case_id) & (log_sim_df["case_id"]<=max_case_id)]
        
        err_cycle = compute_wass_err(log, log_sim_df)
        errors.append(err_cycle.copy())
        errors_track.append(err_cycle.copy())

        if i>=2:    
            for a in activities:
                if errors[i][a]<errors[1][a] and errors[1][a]<errors[0][a]: # err_i < err_1 < err_0
                    alphas_tot[0][a] = alphas_tot[i][a] # 0: alpha_i, 1: alpha_1 --> err_0 = err_i < err_1
                    errors[0][a] = errors[i][a]
                if errors[i][a]<errors[0][a] and errors[0][a]<errors[1][a]: # err_i < err_0 < err_1
                    alphas_tot[1][a] = alphas_tot[i][a] # 0: alpha_0, 1: alpha_i --> err_1 = err_i < err_0
                    errors[1][a] = errors[i][a]
                if errors[1][a]<errors[i][a] and errors[i][a]<errors[0][a]: # err_1 < err_i < err_0
                    alphas_tot[0][a] = alphas_tot[i][a] # 0: alpha_i, 1: alpha_1 --> err_1 < err_0 = err_i
                    errors[0][a] = errors[i][a]
                if errors[0][a]<errors[i][a] and errors[i][a]<errors[1][a]: # err_0 < err_i < err_1
                    alphas_tot[1][a] = alphas_tot[i][a] # 0: alpha_0, 1: alpha_i --> err_0 < err_i = err_1
                    errors[1][a] = errors[i][a]
                if (errors[i][a]==errors[0][a]) and (errors[i][a]==errors[1][a]):
                    continue
                    
        # early stopping criterion
        # se non vi è un cambiamento nel valore di alpha nelle ultime 2 iterazioni, per ogni attività, ci si ferma
        x = 0
        epsilon = 0.001 # tollerance
        if i>2:
            for a in activities:
                A=[]
                for i in range(len(alphas_tot)):
                    A.append(alphas_tot[i][a])
                if abs(A[-1]-A[-2])<epsilon: 
                    x+=1
            if x==len(activities):
                print('no more minimum')
                break

    # extract the best values of alpha for minimizing the wasserstein distance
    stop = timeit.default_timer()

    best_alphas = {a:0 for a in activities}
    best_errors = {a:0 for a in activities}
    for a in activities:
        L = []
        for i in range(len(errors)):
            L.append(errors[i][a]) # L è una lista di lungh. pari al nr di iteraz. e contiene 3 valori distinti per gli errori
                                    # gli unici valori che vengono sostituiti sono quelli in posizione 0 e 1, che migliorano il
                                    # loro valore a seguito del confronto
        best_errors[a] = min(L)
        index_min = min(range(len(L)), key=L.__getitem__)
        best_alphas[a] = alphas_tot[index_min][a]


    print('\nExecution time: {} minutes and {} seconds'.format(divmod(stop-start, 60)[0],divmod(stop-start, 60)[1])) # 2'48"
    print('\nBest alphas:', best_alphas)
    print('\nBest Wasserstein distances:', best_errors)
    print('\nBest Wasserstein distance mean: ',np.mean(list(best_errors.values())))

    return df_log_alpha, alphas_track, errors_track


if __name__ == '__main__':
    run_framework(log_path, bpmn_path, json_path, output_path, starting_at, perc_head_tail, N_iterations)