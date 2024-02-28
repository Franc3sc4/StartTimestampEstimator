import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.metric_utils import compute_start_difference
from run import run_framework

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

#args.log_path = 'data/Production_Case_Study/production.xes'
#args.bpmn_path = 'data/Production_Case_Study/production.bpmn'
#args.json_path = 'data/Production_Case_Study/production.json'
#output_path = 'results/Production_Case_Study/bisection'

bpmn_path = args.bpmn_path #'data/Production_Case_Study/production.bpmn' 
json_path = args.json_path #'data/Production_Case_Study/production.json'
perc_head_tail = args.perc_head_tail
log_path = args.log_path #'data/Production_Case_Study/production.xes'
starting_at = args.starting_at
N_iterations = args.N_max_iteration
output_path = args.output_path #'results/Production_Case_Study/bisection'


df_log_alpha, alphas_track, errors_track = run_framework(log_path, bpmn_path, json_path, output_path, starting_at, perc_head_tail, N_iterations)

activities = list(df_log_alpha["concept:name"].unique())


#------------------------------------------------------
# df saving
data = {a:[[],[]] for a in activities}
for a in activities:
    for i in range(len(alphas_track)):
        data[a][0].append(alphas_track[i][a])
        data[a][1].append(errors_track[i][a])

# remove duplicates
for a in activities:
    index=[]
    for i in range(1,len(data[a][0])):
        if data[a][0][i]==data[a][0][i-1]:
            index.append(i)
    data[a][0] = [j for i, j in enumerate(data[a][0]) if i not in index]
    data[a][1] = [j for i, j in enumerate(data[a][1]) if i not in index]
    

data_df = pd.DataFrame(columns = ["Activity", "Alpha", "W.Distance"])
for a in activities:
    for i in range(len(data[a][0])):
        new_row = {"Activity":a, "Alpha":data[a][0][i], "W.Distance":data[a][1][i]}
        data_df.loc[len(data_df)] = new_row

data_df.to_csv(output_path + "/data_multi_update.csv")


#-------------------------------------
# plot creation

plot_ = True

if plot_:
    for a in activities:
        data_a = data_df.loc[data_df.Activity==a,:]
        g = sns.lineplot(data=data_a, x='Alpha', y='W.Distance', markers=True, style="Activity")
        g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
        plt.savefig(output_path + '/plots/run_errors_{}.png'.format(a))
        plt.show()


# Production Case Study
# WD : 84641.10453089906

# Purchase Process Case Study
# WD : 49149.22296238147