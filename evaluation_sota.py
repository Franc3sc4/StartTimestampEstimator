import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.metric_utils import compute_start_difference
from run_sota import run_framework

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--log_path', type=str, default='data/purchasing_example.xes')
parser.add_argument('--bpmn_path', type=str, default='data/purchasing_example.bpmn')
parser.add_argument('--json_path', type=str, default='data/purchasing_example.json')
parser.add_argument('--output_path', type=str, default='results/single')
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

df_log_alpha, alphas_track, errors_track = run_framework(log_path, bpmn_path, json_path, output_path, delta, starting_at, perc_head_tail)
  
activities = list(df_log_alpha["concept:name"].unique())

#-------------------------------------------------
# df saving
data_df = pd.DataFrame(columns = ["Activity", "Alpha", "W.Distance"])

for a in activities:
    for i in range(len(alphas_track[a])):
        new_row = {"Activity":a, "Alpha":alphas_track[a][i], "W.Distance":errors_track[i]}
        data_df.loc[len(data_df)] = new_row


if shuffle_activities:
    data_df.to_csv(output_path + "/data_single_update_shuffle.csv")    
else:
    data_df.to_csv(output_path + "/data_single_update.csv")

#-------------------------------------------------
# start:timestamp comparison

if shuffle_activities:
    df_log_alpha_one_shuffle = pd.read_csv(output_path + '/log_alpha_one_shuffle.csv')
    time_difference_median, time_difference_mean, time_difference_weighted = compute_start_difference(df_log_alpha)
    print('\n\nTime-delta between real log and single update with shuffled activities (median):\n\n', time_difference_median)
    print('\n\nTime-delta between real log and single update with shuffled activities (mean):\n\n', time_difference_mean)
    print('\n\nTime-delta between real log and single update with shuffled activities (weighted):\n\n', time_difference_weighted)
else:
    df_log_alpha_one = pd.read_csv( output_path + '/log_alpha_one.csv')
    time_difference_median, time_difference_mean, time_difference_weighted = compute_start_difference(df_log_alpha)
    print('\n\nTime-delta between real log and single update (median):\n\n', time_difference_median)
    print('\n\nTime-delta between real log and single update (mean):\n\n', time_difference_mean)
    print('\n\nTime-delta between real log and single update (weighted):\n\n', time_difference_weighted)


#-------------------------------------------------
# plot creation
plot_ = True

if plot_:
    for a in activities:
        data_one_a = data_df.loc[data_df.Activity==a,:]
        g = sns.lineplot(data=data_one_a, x='Alpha', y='W.Distance', markers=True, style = "Activity")
        g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
        if shuffle_activities:
            plt.savefig(output_path + '/plots/run_one_alpha_shuffle_errors_{}.png'.format(a))
            plt.show()
        else:
            plt.savefig(output_path + '/plots/run_one_alpha_errors_{}.png'.format(a))
            plt.show()