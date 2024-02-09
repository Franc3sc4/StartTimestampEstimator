#from pm4py.objects.log.importer.xes import importer as xes_importer
#import pm4py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#log_path = 'data/purchasing_example.xes'
#log = xes_importer.apply(log_path)
#log = pm4py.filter_event_attribute_values(log, 'lifecycle:transition', ['complete'], level="event", retain=True)
#activities = list(pm4py.get_event_attribute_values(log, "concept:name").keys())
activities = ['Create Purchase Requisition',
 'Create Request for Quotation',
 'Analyze Request for Quotation',
 'Send Request for Quotation to Supplier',
 'Create Quotation comparison Map',
 'Analyze Quotation Comparison Map',
 'Choose best option',
 'Settle Conditions With Supplier',
 'Create Purchase Order',
 'Confirm Purchase Order',
 'Deliver Goods Services',
 'Release Purchase Order',
 'Approve Purchase Order for payment',
 'Send Invoice',
 "Release Supplier's Invoice",
 "Authorize Supplier's Invoice payment",
 'Pay Invoice',
 'Amend Request for Quotation',
 'Settle Dispute With Supplier',
 'Analyze Purchase Requisition',
 'Amend Purchase Requisition']

data_df = pd.read_csv('data/data_multi_update.csv')
data_one_df = pd.read_csv('data/data_single_update.csv')
data_one_shuffle_df = pd.read_csv('data/data_single_update_shuffle.csv')

data_df.loc[:,'Method'] = 'Multi Alpha Update'
data_one_df.loc[:,'Method'] = 'Single Alpha Update'
data_one_shuffle_df.loc[:,'Method'] = 'Shuffle Single Alpha Update'

full_data = pd.concat([data_df, data_one_df, data_one_shuffle_df], ignore_index=True)
full_data.loc[:,'Iteration'] = 0

# add 'Iteration' column
for a in activities:
        for m in full_data.Method.unique():
                full_data.loc[(full_data.Activity==a) & (full_data.Method==m),'Iteration'] = range(len(full_data.loc[(full_data.Activity==a) & (full_data.Method==m),:]))
                
                

alpha_comparison = True
iteration_comparison = True

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