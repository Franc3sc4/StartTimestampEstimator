from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

log_path = 'data/purchasing_example.xes'
log = xes_importer.apply(log_path)
log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)
activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())

data_df = pd.read_csv('data/data_multi_update.csv')
data_one_df = pd.read_csv('data/data_single_update.csv')
data_one_shuffle_df = pd.read_csv('data/data_single_update_shuffle.csv')

data_df.loc[:,'Method'] = 'Multi Alpha Update'
data_one_df.loc[:,'Method'] = 'Single Alpha Update'
data_one_shuffle_df.loc[:,'Method'] = 'Shuffle Single Alpha Update'

full_data = pd.concat([data_df, data_one_df, data_one_shuffle_df], ignore_index=True)

for a in activities:
        data_a = full_data.loc[full_data.Activity==a,:]
        g = sns.lineplot(data=data_a, x='Alpha', y='W.Distance', hue = 'Method')
        g.set_title('Wasserstein Distance wrt Alpha\nActivity: {}'.format(a))
        plt.savefig('data/plot_comparison_alpha/comparison_errors_{}.png'.format(a))
        plt.show()