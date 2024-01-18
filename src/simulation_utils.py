from prosimos.simulation_engine import *
from prosimos.simulation_properties_parser import parse_resource_profiles, parse_task_resource_distributions


def update_sim_params(json_data, diffsim_info, best_distr_act_execution):
    for i in range(len(json_data["task_resource_distribution"])):
        task_id = json_data["task_resource_distribution"][i]['task_id']
        act = diffsim_info.bpmn_graph.element_info[task_id].name
        distr_act = best_distr_act_execution[act]
        for j in range(len(json_data["task_resource_distribution"][i]['resources'])):
            json_data["task_resource_distribution"][i]['resources'][j]['distribution_name'] = distr_act[0]
            json_data["task_resource_distribution"][i]['resources'][j]['distribution_params'] = [{'value': p} for p in distr_act[1]]


    _, res_pool = parse_resource_profiles(json_data["resource_profiles"])
    diffsim_info.task_resource = parse_task_resource_distributions(json_data["task_resource_distribution"], res_pool)
    diffsim_info.bpmn_graph.set_additional_fields_from_json(diffsim_info.element_probability,
                                                            diffsim_info.task_resource, diffsim_info.event_distibution,
                                                            diffsim_info.batch_processing, diffsim_info.gateway_conditions,
                                                            diffsim_info.gateway_execution_limit)
    return json_data, diffsim_info

def run_simulation(
    diffsim_info,
    log_out_path=None,
    starting_at=None
):

    if not diffsim_info:
        return None

    starting_at_datetime = (
        parse_datetime(starting_at, True) if starting_at else pytz.utc.localize(datetime.datetime.now())
    )
    diffsim_info.set_starting_datetime(starting_at_datetime)

    csv_writer_config = {
        'delimiter': ',',
        'quotechar': '"',
        'quoting': csv.QUOTE_MINIMAL
    }

    log_csv_file = open(log_out_path, mode="w", newline="", encoding="utf-8") if log_out_path else None

    try:
        log_writer = csv.writer(log_csv_file, **csv_writer_config) if log_csv_file else None
        result = run_simpy_simulation(diffsim_info, None, log_writer, None)
    finally:
        if log_csv_file:
            log_csv_file.close()

    return result