import numpy as np
from scipy.stats import norm, expon, uniform, triang, lognorm, gamma, wasserstein_distance
from statistics import mode

possible_distributions = [
    'fix',
    'norm',
    'expon',
    'uniform',
    'triang',
    'lognorm',
    'gamma'
    ]


def find_best_fit_distribution(observed_values, N=None):        
    if not N:
        N = len(observed_values)

    generated_values = dict()
    distr_params = {d: dict() for d in possible_distributions}

    if np.min(observed_values) == np.max(observed_values):
        return 'fix', {'value': 0}, np.array([observed_values[0]] * N)

    for distr_name in possible_distributions:
        if distr_name == 'fix':
            distr_params[distr_name] = {'value' : np.mean(observed_values)}
            generated_values[distr_name] = np.array([distr_params[distr_name]['value']] * N)
        elif distr_name == 'norm':
            distr_params[distr_name] = {'loc': np.mean(observed_values), 'scale': np.std(observed_values)}
            generated_values[distr_name] = norm(loc=distr_params[distr_name]['loc'], scale=distr_params[distr_name]['scale']).rvs(size=N)
        elif distr_name == 'expon':
            distr_params[distr_name] = {'loc': np.mean(observed_values), 'scale': np.std(observed_values)}
            generated_values[distr_name] = expon(loc=distr_params[distr_name]['loc'], scale=distr_params[distr_name]['scale']).rvs(size=N)
        elif distr_name == 'uniform':
            distr_params[distr_name] = {'loc': np.min(observed_values), 'scale': np.max(observed_values)} 
            generated_values[distr_name] = uniform(loc=distr_params[distr_name]['loc'], scale = distr_params[distr_name]['scale'] - distr_params[distr_name]['loc']).rvs(size=N)
        elif distr_name == 'triang':
            distr_params[distr_name] = {'c': mode(observed_values), 'loc': np.min(observed_values), 'scale': np.max(observed_values)}
            generated_values[distr_name] = triang(c=(distr_params[distr_name]['c'] - distr_params[distr_name]['loc'])/(distr_params[distr_name]['scale'] - distr_params[distr_name]['loc']), loc=distr_params[distr_name]['loc'], scale = distr_params[distr_name]['scale'] - distr_params[distr_name]['loc']).rvs(size=N)
        elif distr_name == 'lognorm':
            distr_params[distr_name] = {'loc': np.mean(observed_values), 'scale': np.std(observed_values)}
            #generated_values[distr_name] = lognorm(s = distr_params[distr_name]['scale'], loc = distr_params[distr_name]['loc'], scale = np.exp(distr_params[distr_name]['loc'])).rvs(size=N)
            generated_values[distr_name] = lognorm(distr_params[distr_name]['scale'], scale=np.exp(np.log(distr_params[distr_name]['loc'])-0.5*distr_params[distr_name]['scale']**2)).rvs(size=N)
        elif distr_name == 'gamma':
            distr_params[distr_name] = {'loc': np.mean(observed_values), 'scale': np.std(observed_values)}
            generated_values[distr_name] = gamma(a=distr_params[distr_name]['loc'], loc = distr_params[distr_name]['loc'], scale=distr_params[distr_name]['scale']).rvs(size=N)

    wass_distances = {d_name: wasserstein_distance(observed_values, generated_values[d_name]) for d_name in possible_distributions}
    best_distr = min(wass_distances, key=wass_distances.get)

    return best_distr, distr_params[best_distr]
