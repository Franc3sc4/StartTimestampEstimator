#from pm4py.objects.log.importer.xes import importer as xes_importer
#import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

data_df = pd.read_csv('data/data_multi_update.csv')
data_one_df = pd.read_csv('data/data_single_update.csv')
data_one_shuffle_df = pd.read_csv('data/data_single_update_shuffle.csv')

activities = list(data_df.Activity.unique())

data_df.loc[:,'Method'] = 'Multi Alpha Update'
data_one_df.loc[:,'Method'] = 'Single Alpha Update'
data_one_shuffle_df.loc[:,'Method'] = 'Shuffle Single Alpha Update'

full_data = pd.concat([data_df, data_one_df, data_one_shuffle_df], ignore_index=True)
full_data.loc[:,'Iteration'] = 0

# add 'Iteration' column
for a in activities:
        for m in full_data.Method.unique():
                full_data.loc[(full_data.Activity==a) & (full_data.Method==m),'Iteration'] = range(len(full_data.loc[(full_data.Activity==a) & (full_data.Method==m),:]))
                
                

alpha_comparison = False
iteration_comparison = False

if alpha_comparison:
        for a in activities:
                data_a = full_data.loc[full_data.Activity==a,:]
                g = sns.lineplot(data=data_a, x='Alpha', y='W.Distance', hue = 'Method', markers=True, style = "Method")
                g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
                plt.savefig('data/plot_comparison_alpha/comparison_errors_{}.png'.format(a))
                plt.show()

# remove Wasserstein distance track for alpha=0,1 for the 'Multi Alpha Update'
full_data[full_data.Method == 'Multi Alpha Update'] = full_data[(full_data.Method == 'Multi Alpha Update') & (full_data.Alpha!=0) & (full_data.Alpha!=1)]
full_data.dropna(axis=0, inplace=True)

# adjust Iteration column
full_data.loc[full_data.Method == 'Multi Alpha Update','Iteration'] = full_data[full_data.Method == 'Multi Alpha Update']['Iteration'].apply(lambda x: x-2)

if iteration_comparison:
        for a in activities:
                data_a = full_data.loc[full_data.Activity==a,:]
                g = sns.lineplot(data=data_a, x='Iteration', y='W.Distance', hue = 'Method', markers=True, style = "Method")
                g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
                plt.savefig('data/plot_comparison_alpha/comparison_errors_iterations{}.png'.format(a))
                plt.show()

y_pos = np.arange(len(activities))
g = sns.boxplot(data=full_data[full_data.Method=='Multi Alpha Update'], x='Activity', y='W.Distance')
#g.set_xticklabels(g.get_xticklabels(), rotation=90)
g.set_title('Wasserstein Distance wrt the Activity\n Bisection method update (WT)')
plt.xticks(y_pos, activities, rotation=90)
plt.subplots_adjust(bottom=0.3)
plt.savefig('data/plot_comparison_alpha/box_plot_errors_multi_wt.png')
plt.show()

g = sns.boxplot(data=full_data[full_data.Method=='Single Alpha Update'], x='Activity', y='W.Distance')
#g.set_xticklabels(g.get_xticklabels(), rotation=90)
plt.xticks(y_pos, activities, rotation=90)
plt.subplots_adjust(bottom=0.3)
g.set_title('Wasserstein Distance wrt the Activity\n single update (WT)')
plt.savefig('data/plot_comparison_alpha/box_plot_errors_single_wt.png')
plt.show()

g = sns.boxplot(data=full_data[full_data.Method=='Shuffle Single Alpha Update'], x='Activity', y='W.Distance')
#g.set_xticklabels(g.get_xticklabels(), rotation=90)
plt.xticks(y_pos, activities, rotation=90)
plt.subplots_adjust(bottom=0.3)
g.set_title('Wasserstein Distance wrt the Activity\n Single update with shuffled activites (WT)')
plt.savefig('data/plot_comparison_alpha/box_plot_errors_shuffle_wt.png')
plt.show()