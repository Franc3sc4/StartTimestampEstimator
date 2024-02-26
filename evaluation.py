import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from run import run_framework

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--log_path', type=str, default='data/purchasing_example.xes')
parser.add_argument('--bpmn_path', type=str, default='data/purchasing_example.bpmn')
parser.add_argument('--json_path', type=str, default='data/purchasing_example.json')
parser.add_argument('--output_path', type=str, default='results/bisection')
parser.add_argument('--starting_at', type=str, default='2011-01-01T00:00:00.000000+00:00')
parser.add_argument('--perc_head_tail', type=float, default=.1)
parser.add_argument('--N_max_iteration', type=int, default=20)


args = parser.parse_args()

bpmn_path = args.bpmn_path
json_path = args.json_path
perc_head_tail = args.perc_head_tail
log_path = args.log_path
starting_at = args.starting_at
N_iterations = args.N_max_iteration
output_path = args.output_path


df_log_alpha, alphas_track, errors_track, activities = run_framework(log_path, bpmn_path, json_path, output_path, starting_at, perc_head_tail, N_iterations)


#------------------------------------------------------
# start:timestamp comparison
time_difference_median, time_difference_mean, time_difference_weighted = compute_start_difference(df_log_alpha)
print('\n\nTime-delta between real log and update with bisection method (median):\n\n', time_difference_median)
print('\n\nTime-delta between real log and update with bisection method (mean):\n\n', time_difference_mean)
print('\n\nTime-delta between real log and update with bisection method (weighted):\n\n', time_difference_weighted)

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
        plt.savefig(output_path + '/plot_multi_alpha/run_errors_{}.png'.format(a))
        plt.show()

##############################





