import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.metric_utils import compute_start_difference
from run_sota import run_framework

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--log_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.xes')
parser.add_argument('--bpmn_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.bpmn')
parser.add_argument('--json_path', type=str, default='data/Purchase_Process_Case_Study/purchasing_example.json')
parser.add_argument('--output_path', type=str, default='results/Purchase_Process_Case_Study/single')
parser.add_argument('--starting_at', type=str, default='2011-01-01T00:00:00.000000+00:00')
parser.add_argument('--perc_head_tail', type=float, default=.1)
parser.add_argument('--delta', type=float, default=.1)
parser.add_argument('--shuffle_activities', type=bool, default=False)

args = parser.parse_args()

bpmn_path = args.bpmn_path
json_path = args.json_path
log_path = args.log_path
output_path = args.output_path

#bpmn_path = 'data/Production_Case_Study/production.bpmn'
#json_path = 'data/Production_Case_Study/production.json'
#log_path = 'data/Production_Case_Study/production.xes'
#output_path = 'results/Production_Case_Study/single' 

perc_head_tail = args.perc_head_tail
starting_at = args.starting_at
delta = args.delta
shuffle_activities = args.shuffle_activities

df_log_alpha, alphas_track, errors_track = run_framework(log_path, bpmn_path, json_path, output_path, delta, starting_at, perc_head_tail)
  
activities = list(df_log_alpha["concept:name"].unique())

#-------------------------------------------------
# df saving
data_df = pd.DataFrame(columns = ["Activity", "Alpha", "W.Distance"])

for a in activities:
    for i in range(len(alphas_track[a])):
        new_row = {"Activity":a, "Alpha":alphas_track[a][i], "W.Distance":errors_track[a][i]}
        data_df.loc[len(data_df)] = new_row


if shuffle_activities:
    data_df.to_csv(output_path + "/data_single_update_shuffle.csv")    
else:
    data_df.to_csv(output_path + "/data_single_update.csv")


#-------------------------------------------------
# plot creation
plot_ = True

if plot_:
    for a in activities:
        data_one_a = data_df.loc[data_df.Activity==a,:]
        g = sns.lineplot(data=data_one_a, x='Alpha', y='W.Distance', markers=True)
        #g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
        if shuffle_activities:
            plt.savefig(output_path + '/plots/run_one_alpha_shuffle_errors_{}.png'.format(a))
            plt.show()
        else:
            plt.savefig(output_path + '/plots/run_one_alpha_errors_{}.png'.format(a))
            plt.show()


# Purchase Process Case Study
# WD :
# WD shuffle: 937811.228871315

# Production Case Study
# WD : 1506595.6116978354
# WD shuffle: 17354048.409436677