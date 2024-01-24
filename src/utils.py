import pm4py

def set_start_timestamp_from_alpha(log, alphas, is_res=True):

    if is_res:
        resources = pm4py.get_event_attribute_values(log, 'org:resource')
        dict_res_av = {res:[] for res in resources}
        for trace in log:
            trace[0]['start:timestamp'] = trace[0]['time:timestamp']
            for event in trace:
                res = event["org:resource"]
                dict_res_av[res].append(event["time:timestamp"])

    for trace in log:
        for i in range(1, len(trace)):
            r = trace[i]["org:resource"]
            av_time = trace[i]["time:timestamp"]
            #t_r = [t for t in dict_res_av[r] if t<av_time][-1]
            #t_r = [t else av_time if (t-av_time).total_seconds()<0 for t in dict_res_av[r]][-1]
            if is_res:
                t_r = [t for t in dict_res_av[r] if (t-av_time).total_seconds()<=0][-1]
                delta_av = (max(trace[i-1]['time:timestamp'], t_r) - av_time)*alphas[trace[i]["concept:name"]]
            else:
                delta_av = (trace[i-1]['time:timestamp'] - av_time)*alphas[trace[i]["concept:name"]]
            trace[i]["start:timestamp"] = av_time + delta_av
    
    return log       

  #  for trace in log:
  #      trace[0]['start:timestamp'] = trace[0]['time:timestamp'] 
  #      for i in range(1,len(trace)):
  #          r = trace[i]["org:resource"]
  #          av_time = trace[i]["time:timestamp"]
  #          delta_av = (max(trace[i-1]['time:timestamp'], dict_res_av[r]) - av_time)*alphas[trace[i]["concept:name"]]
  #          trace[i]["start:timestamp"] = av_time + delta_av
  #          dict_res_av[r] = trace[i]["time:timestamp"]
# il nostro problema è se la risorsa ha già iniziato una nuova attività in un'altra traccia nel mentre in cui
            # noi analiziamo questa
            # dovrei controllare, per quella risorsa, il time stamp più prossimo a av_time
