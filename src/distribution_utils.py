import numpy as np
from scipy import stats

possible_distributions = [
    'fix',
    'norm',
    'expon',
    'uniform',
    'triang',
    'lognorm',
    'gamma'
    ]


# TODO Sistemare i parametri delle distrubuzioni con quelli in "pix_framework\statistics\distribution.py" linea 250 
# https://github.com/AutomatedProcessImprovement/pix-framework/tree/main/src/pix_framework
def find_best_fit_distribution(observed_values, N=None):
    
    if not N:
        N = len(observed_values)

    generated_values = dict()
    distr_params = {d: dict() for d in possible_distributions}

    if np.min(observed_values) == np.max(observed_values):
        return 'fix', {'value': np.min(observed_values)}

    for distr_name in possible_distributions:
        if distr_name == 'fix':
            distr_params[distr_name] = {'value' : np.mean(observed_values)}
            generated_values[distr_name] = np.array([distr_params[distr_name]['value']] * N)
        elif distr_name == 'norm':
            dist = stats.norm
            try:
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'mean': np.mean(observed_values), 'std': np.std(observed_values), 'min': 0, 'max': np.max(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            except:
                None
        elif distr_name == 'expon':
            dist = stats.expon
            try:
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'mean': np.mean(observed_values), 'min': 0, 'max': np.max(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            except:
                None
        elif distr_name == 'uniform':
            dist = stats.uniform
            try:
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'min': np.min(observed_values), 'max': np.max(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            except:
                None
        # # TODO check triang
        # elif distr_name == 'triang':
        #     dist = stats.triang
        #     try:
        #         c, loc, scale = dist.fit(observed_values)
        #         distr_params[distr_name] = {'c': c, 'loc': loc, 'scale': scale}
        #         generated_values[distr_name] = dist.rvs(c=c, loc=loc, scale=scale, size=N)
        #     except:
        #         None
        elif distr_name == 'lognorm':
            dist = stats.lognorm
            try:
                s, loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'mean': np.mean(observed_values), 'var': np.std(observed_values)**2, 'min': np.min(observed_values), 'max': np.max(observed_values)}
                generated_values[distr_name] = dist.rvs(s=s, loc=loc, scale=scale, size=N)
            except:
                None
        elif distr_name == 'gamma':
            dist = stats.gamma
            try:
                a, loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'mean': np.mean(observed_values), 'var': np.std(observed_values)**2, 'min': np.min(observed_values), 'max': np.max(observed_values)}
                generated_values[distr_name] = dist.rvs(a=a, loc=loc, scale=scale, size=N)
            except:
                None

    wass_distances = {d_name: stats.wasserstein_distance(observed_values, generated_values[d_name]) for d_name in generated_values.keys()}
    best_distr = min(wass_distances, key=wass_distances.get)

    return best_distr, distr_params[best_distr], wass_distances