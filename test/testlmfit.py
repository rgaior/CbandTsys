from lmfit import minimize, Parameters
import numpy as np

def residual(params, x, data, eps_data):
    print 'in residual'
    amp = params['amp']
    pshift = params['phase']
    freq = params['frequency']
    decay = params['decay']
    x = x.flatten()
    model = amp * x  + pshift
    data = data.flatten()
    model = model.flatten()
    eps_data = eps_data.flatten()
    print np.shape((data-model)/eps_data)
    print (data-model)/eps_data
    return (data-model)/eps_data

params = Parameters()
params.add('amp', value=10)
params.add('decay', value=0.007)
params.add('phase', value=0.2)
params.add('frequency', value=3.0)
size = 100
x = np.linspace(0,10,size)
print x
data = 10 * x + 9 + np.random.normal(0,1,size)
print data
eps_data = 0.1*np.ones(size)
print params

out = minimize(residual, params, args=(x, data, eps_data))
