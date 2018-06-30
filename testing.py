#!/usr/bin/env python3

# (C) 2017 Phicem
# This software is released under MIT license (provided in LICENSE.txt)


import math
import logging
import unittest


from units import *
from arrays import DataArray, sampleFunction

# TODO: use coverage !! ('coverage run ./battery.py' then 'coverage report' then 'coverage html' (open htmlcov/index.html))

class TestDataArrays(unittest.TestCase):
    """ Behaviors to check
    Item 1
    Item 2
    """
    def setUp(self):
        time = np.array([0,1,2,3]) * s
        output = np.array([1,2,3,4]) * kg
        self.output_vs_time = DataArray(time, output)

        x_no_unit = np.array([0,1,2,3])
        y_no_unit = np.array([1,2,3,4])
        self.xy_no_unit = DataArray(x_no_unit, y_no_unit)

    def tearDown(self):
        pass


    def test_010_integ_only_one_point_in_interval(self):
        result = self.output_vs_time.integ(0.5*s,1.5*s)
        truth = 2*s*kg
        error_message = "Incorrect result for integ"
        self.assertEqual(result, truth, error_message)

    def test_011_integ_interval_exactly_on_data(self):
        result = self.output_vs_time.integ(1*s,2*s)
        truth = 2.5*s*kg
        error_message = "Incorrect result for integ"
        #pdb.set_trace()
        self.assertEqual(result, truth, error_message)

    def test_012_integ_limits_are_checked(self):
        with self.assertRaises(Exception):
            result = self.output_vs_time.integ(0*s,4*s)

        with self.assertRaises(Exception):
            result = self.output_vs_time.integ(2*s,1*s)

    def test_013_integ_array_without_units(self):
        result = self.xy_no_unit.integ(0.5,1.5)
        truth = 2
        error_message = "Incorrect result for integ"
        self.assertEqual(result, truth, error_message)

    def test_020_sampleFunction(self):
        def func(x):
            return x/s*kg+1*kg
        XY = sampleFunction(func, 0*s, 3*s, 4)
        self.assertEqual(XY, self.output_vs_time)


full_suite_DataArray= unittest.TestLoader().loadTestsFromTestCase(TestDataArrays)

TOTAL = unittest.TestSuite()
TOTAL.addTests(full_suite_DataArray)



#list_of_tests = ['test_013_integ_array_without_units'] 
#partial_suite = unittest.TestSuite(map(TestDataArrays, list_of_tests))

#suite = partial_suite
suite = TOTAL 

unittest.TextTestRunner(verbosity=2).run(suite)

#pdb.set_trace()
#print("End of tests")
