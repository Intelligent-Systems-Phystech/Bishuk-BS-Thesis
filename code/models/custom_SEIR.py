# https://github.com/UTCovid/SEIR_Example/blob/master/src/seir.py

import numpy as np
import scipy
from scipy import integrate
import json
import argparse
import matplotlib.pyplot as plt
import os


def acquire_params(filename):
    """
    Загрузка параметров из файла
    """

    with open(filename, 'r') as param_file:
        params = json.loads(param_file.read())

    return params

# Validate Inputs

def validate_params(param_dict, float_keys, int_keys, str_keys):
    """
    Проверка параметров на адекватность
    """

    all_keys = float_keys + int_keys + str_keys
    for key in all_keys:
        if key not in param_dict.keys():
            raise ValueError('Parameter {} missing from input file.'.format(key))

    for key in float_keys:
        if type(param_dict[key]) != float:
            raise ValueError('Parameter {} is not specified as a float.'.format(key))

    for key in int_keys:
        if type(param_dict[key]) != int:
            raise ValueError('Parameter {} is not specified as an integer.'.format(key))

    for key in str_keys:
        if type(param_dict[key]) != str:
            raise ValueError('Parameter {} is not specified as a string.'.format(key))


# define the system of differential equations

class SEIR:

    def __init__(self, beta, mu, sigma, gamma, omega, start_S, start_E, start_I, start_R, duration, outdir):

        # Параметры модели SEIR

        self.beta = beta       # transmission rate
        self.mu = mu           # death rate from infection
        self.sigma = sigma     # rate E -> I
        self.gamma = gamma     # recovery rate
        self.omega = omega     # waning immunity
        self.start_S = start_S
        self.start_E = start_E
        self.start_I = start_I
        self.start_R = start_R
        self.duration = duration
        self.outdir = outdir
        self.R = [self.start_S, self.start_E, self.start_I, self.start_R]

    def seir(self, x, t):

        # Диф.уравнение SEIR для одного шага

        S = x[0]
        E = x[1]
        I = x[2]
        R = x[3]

        y = np.zeros(4)

        y[0] = self.mu - ((self.beta * I) + self.mu) * S + (self.omega * R)
        y[1] = (self.beta * S * I) - (self.mu + self.sigma) * E
        y[2] = (self.sigma * E) - (self.mu + self.gamma) * I
        y[3] = (self.gamma * I) - (self.mu * R) - (self.omega * R)

        return y

    def integrate(self):
        """
        Функция интегрирования диф.уравнения
        """

        time = np.arange(0, self.duration, 0.01)
        results = scipy.integrate.odeint(self.seir, self.R, time)

        return results

    def plot_timeseries(self, results):

        time = np.arange(0, len(results[:, 1]))

        plt.figure(figsize=(5,8), dpi=300)

        plt.plot(
            time, results[:, 0], "k",
            time, results[:, 1], "g",
            time, results[:, 2], "r",
            time, results[:, 3], "b",)
        plt.legend(("S", "E", "I", "R"), loc=0)
        plt.ylabel("Population Size")
        plt.xlabel("Time")
        plt.xticks(rotation=45)
        plt.title("SEIR Model")
        plt.savefig(os.path.join(self.outdir, 'SEIR_Model.png'))
        plt.show()

def main(opts):

    # Запуск проверки модели

    pars = acquire_params(opts.paramfile)

    float_keys = ['beta', 'mu', 'sigma', 'gamma', 'omega']
    int_keys = ['start_S', 'start_E', 'start_I', 'start_R', 'duration']
    str_keys = ['outdir']
    validate_params(pars, float_keys, int_keys, str_keys)

    seir_model = SEIR(**pars)
    r = seir_model.integrate()
    seir_model.plot_timeseries(r)