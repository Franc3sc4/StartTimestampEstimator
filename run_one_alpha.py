from prosimos.simulation_engine import *
import json
from src.simulation_utils import update_sim_params, run_simulation
from pm4py.objects.log.importer.xes import importer as xes_importer
from src.utils import set_start_timestamp_from_alpha
from src.temporal_utils import find_execution_distributions
from src.metric_utils import compute_wass_dist_execution, compute_wass_dist_cycle_time, compute_wass_dist_waiting_time
import pm4py
import random
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

bpmn_path = 'data/purchasing_example.bpmn'
json_path = 'data/purchasing_example.json'
perc = .1
gen_cases = 608
total_cases = gen_cases+int(gen_cases*perc)
log_path = 'data/purchasing_example.xes'
starting_at = '2011-01-01T00:00:00.000000+00:00'
N_iterations = 1
save_log_alpha= True
delta = 0.05

log = xes_importer.apply(log_path)
log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)

activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())

with open(json_path) as json_file:
    json_data = json.load(json_file)

diffsim_info = SimDiffSetup(bpmn_path, json_path, is_event_added_to_log=False, total_cases=total_cases)

def compute_distance(alphas_best, log=log, json_data=json_data, diffsim_info=diffsim_info):
    perc = .1
    gen_cases = 608
    total_cases = gen_cases+int(gen_cases*perc)
    starting_at = '2011-01-01T00:00:00.000000+00:00'
    save_log_alpha= True

    log = set_start_timestamp_from_alpha(log, alphas_best)

    if save_log_alpha:
        df_log_alpha = pm4py.convert_to_dataframe(log)
        if shuffle_activities:
            df_log_alpha.to_csv('data/log_alpha_one_shuffle.csv', index=False)
        df_log_alpha.to_csv('data/log_alpha_one.csv', index=False)

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
    err_cycle = compute_wass_dist_cycle_time(log, log_sim_df)
   # print('Cycle time Avg Wasserstein distance: {}'.format(err_cycle))

    return err_cycle

def prev_succ(alpha, delta, trial=2):
    L=[]
    i=1
    while i<=trial:
        x = alpha - delta*i
        if x>0:      
            L.append(round(x,2))
        i+=1
    return L

def next_succ(alpha, delta, trial=2):
    L=[]
    i=1
    while i<=trial:
        x = alpha + delta*i
        if x<1:      
            L.append(round(x,2))
        i+=1
    return L


# -----------------------------------------------------------------

alphas_best = {a: round(random.random(),2) for a in activities}
epsilon_best = compute_distance(alphas_best)

alphas_track = [alphas_best]
errors_track = [epsilon_best]

shuffle_activities = False

if shuffle_activities:
    activities = random.shuffle(activities)

for a in activities:
    print('\nActivity:',a)
    for i in range(N_iterations):
        Q_tried = [alphas_best[a]]
        Q_next = prev_succ(alphas_best[a], delta)+next_succ(alphas_best[a], delta)
        while Q_next!=[]:
            alpha = alphas_best.copy()
            alpha[a] = Q_next.pop(0)
            if alpha[a] not in Q_tried:
                Q_tried.append(alpha[a])
                print("Q_tried", Q_tried)
                alphas_track.append(alpha)
                epsilon = compute_distance(alpha)
                errors_track.append(epsilon)
                if epsilon[a] < epsilon_best[a]: # abs(epsilon[a]-epsilon_best[a]) < 60*60 : check per fermare le iterazioni
                    print("epsilon < best")
                    if alpha[a]<alphas_best[a]:
                        Q_next = [x for x in Q_next if x<alpha[a]]
                    else:
                        Q_next = [x for x in Q_next if x>alpha[a]]
                    alphas_best[a] = alpha[a]
                    
                if epsilon[a] >= epsilon_best[a]: 
                    print("epsilon >= best")
                    if alpha[a]<alphas_best[a]:
                        Q_next = [x for x in Q_next if x>alphas_best[a]]
                    if alpha[a]>alphas_best[a]:
                        Q_next = [x for x in Q_next if x<alphas_best[a]]
    
print("Best alphas", alphas_track[-1])
print("Best distances", errors_track[-1])

#-------------------------------------------------
# graph creation

data = {a:[[],[]] for a in activities}
for a in activities:
    for i in range(len(alphas_track)):
        data[a][0].append(alphas_track[i][a])
        data[a][1].append(errors_track[i][a])

data_df = pd.DataFrame(columns = ["Activity", "Alpha", "W.Distance"])
for a in activities:
    for i in range(len(data[a][0])):
        new_row = {"Activity":a, "Alpha":data[a][0][i], "W.Distance":data[a][1][i]}
        data_df.loc[len(data_df)] = new_row

for a in activities:
    data_a = data_df.loc[data_df.Activity==a,:]
    #data_a = data_a[:len(set(data_a['Alpha']))] # per evitare doppioni negli alpha, prendo le righe con alpha tutti diversi
    g = sns.lineplot(data=data_a, x='Alpha', y='W.Distance')
    g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
    plt.savefig('data/plot_multi_alpha/run_one_alpha_errors_{}.png'.format(a))
    plt.show()