import numpy as np
import pm4py
from datetime import timezone
from scipy.stats import wasserstein_distance
from src.distribution_utils import find_best_fit_distribution

possible_distributions = [
    'fix',
    'norm',
    'expon',
    'uniform',
    'triang',
    'lognorm',
    'gamma'
    ]


def compute_execution_times(log):

    activities = list(pm4py.get_event_attribute_values(log, 'concept:name').keys())
    activities_extimes = {a: [] for a in activities}
    for trace in log:
        for event in trace:
            act = event['concept:name']
            time_0 = event['start:timestamp']
            time_1 = event['time:timestamp']
            if not time_0.tzinfo:
                time_0 = time_0.replace(tzinfo=timezone.utc)
            if not time_1.tzinfo:
                time_1 = time_1.replace(tzinfo=timezone.utc)
            activities_extimes[act].append((time_1 - time_0).total_seconds())

    return activities_extimes


def find_execution_distributions(log):
    """
    output: {ACTIVITY_NAME: (DISTRNAME, {PARAMS: VALUE})}
    """
    activities_extimes = compute_execution_times(log)
    activities = list(activities_extimes.keys())
    exec_distr = {a: find_best_fit_distribution(activities_extimes[a]) for a in activities}

    return exec_distr