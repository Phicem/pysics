#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import sys
import os

path = os.path.realpath(__file__) 
sys.path.append(path)

from pysics.units import *
from pysics.graph import *

qg = quickGraph

deg = np.pi / 180
pi = np.pi

print("Environment loaded")
