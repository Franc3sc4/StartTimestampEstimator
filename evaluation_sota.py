


     
        


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
    time_difference_median, time_difference_mean, time_difference_weighted = compute_start_difference(df_log_alpha_one_shuffle)
    print('\n\nTime-delta between real log and single update with shuffled activities (median):\n\n', time_difference_median)
    print('\n\nTime-delta between real log and single update with shuffled activities (mean):\n\n', time_difference_mean)
    print('\n\nTime-delta between real log and single update with shuffled activities (weighted):\n\n', time_difference_weighted)
else:
    df_log_alpha_one = pd.read_csv( output_path + '/log_alpha_one.csv')
    time_difference_median, time_difference_mean, time_difference_weighted = compute_start_difference(df_log_alpha_one)
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
            plt.savefig(output_path + '/plot_single_alpha_shuffle/run_one_alpha_shuffle_errors_{}.png'.format(a))
            plt.show()
        else:
            plt.savefig(output_path + '/plot_single_alpha/run_one_alpha_errors_{}.png'.format(a))
            plt.show()