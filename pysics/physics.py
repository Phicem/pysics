#!/usr/bin/env python3

# (C) 2018 Phicem
# This software is released under MIT license (provided in LICENSE.txt)


import scipy.constants
import numpy as np

from pysics.units import *

# Physical constants
# TODO: rely on other packages (like scipy) for physical constant values, this file should only add the units
M_T = 5.97219 * 10**24 * kg # mass of planet Earth
c = 299792458 * m/s # speed of light in vacuum
G = 6.67*10**(-11)*N*(m/kg)**2 # gravitational constant
R_T = 6371 * km # radius of the Earth
q = 1.602*10**(-19) * C # elementary charge


h_p = scipy.constants.h * J * s
k_B = scipy.constants.k * J / K

# Energy of one photon
def E_ph(lmbda):
    return h_p*c/lmbda
