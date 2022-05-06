#!/usr/bin/env python3

# (C) 2022 Phicem
# This software is released under MIT license (provided in LICENSE.txt)


from scipy.integrate import quad
import numpy as np
import pdb

from pysics import units


def integ(func, a, b):
    """ Call scipy.integrate.quad after having removed units from function 'func'
    Raise an exception is the integral is not convergent
    'func' is a function of only ONE variable
    """
    a = units.turn_to_Quantity(a)
    b = units.turn_to_Quantity(b)
    if a.unit != b.unit:
        raise Exception("When integrating, both integration limits must have the same unit")
    x_unit = units.Quantity(1, a.unit)
    y = units.turn_to_Quantity(func(a))
    y_unit = units.Quantity(1, y.unit) 
    func_nounit = lambda x_no_unit: func(x_no_unit*x_unit)/y_unit
    res = quad(func_nounit, a/x_unit, b/x_unit, full_output = True)
    # Quad function returns a tuple of usually 3 items (result, tolerance, explanations), but a 4th item (error message) is appended in cas of an error
    if len(res) == 3:
        return res[0]*x_unit*y_unit
    else:
        msg = res[3]
        raise Exception(msg)


