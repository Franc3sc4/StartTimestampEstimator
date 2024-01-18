import pm4py

def set_start_timestamp_from_alpha(log, alphas):

    resources = pm4py.get_event_attribute_values(log, 'org:resource')
    dict_res_av = {}
    for trace in log:
        for event in trace:
            res = event["org:resource"]
            if res not in dict_res_av.keys():
                dict_res_av[res] = event["time:timestamp"]
        if set(dict_res_av.keys()) == set(resources):
            break
             
    for trace in log:
        trace[0]['start:timestamp'] = trace[0]['time:timestamp'] 
        for i in range(1,len(trace)):
            r = trace[i]["org:resource"]
            av_time = trace[i]["time:timestamp"]
            delta_av = (max(trace[i-1]['time:timestamp'], dict_res_av[r]) - av_time)*alphas[trace[i]["concept:name"]]
            trace[i]["start:timestamp"] = av_time + delta_av
            dict_res_av[r] = trace[i]["time:timestamp"]

    return log