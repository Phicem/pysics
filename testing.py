#!/usr/bin/env python3

# (C) 2018 Phicem
# This software is released under MIT license (provided in LICENSE.txt)

import math
import logging
import unittest


from pysics.units import *
from pysics.arrays import DataArray, sampleFunction

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

    def test_001_not_ascending_order(self):
        revert = np.array([1,2,3,0])

        with self.assertRaises(Exception):
            DataArray(revert, revert)
        with self.assertRaises(Exception):
            DataArray(revert, revert*m)
        with self.assertRaises(Exception):
            DataArray(revert*m, revert)


class TestUnits(unittest.TestCase):
    """ Behaviors to check
    Item 1
    Item 2
    """
    def setUp(self):
        pass
 
    def tearDown(self):
        pass

    def test_010_disp_for_scalar(self):
        # Regular value, simple unit
        a = 20*kft
        mystr1 = a.disp()
        #print(mystr1)
        self.assertEqual(mystr1, '6.096E+03  m [PHYS]', "Incorrect disp value")
        mystr2 = a.disp('km')
        self.assertEqual(mystr2, "6.096 km", "Incorrect disp value")

        #  Regular value, complex unit
        b = 2*J/s
        mystr3 = b.disp()
        self.assertEqual(mystr3, '2.000  kg*m**2/s**3 [PHYS]', "Incorrect disp value")
        mystr4 = b.disp('W')
        self.assertEqual(mystr4, '2.000 W', "Incorrect disp value")

        # Incorrect unit
        c = 2*J
        with self.assertRaises(Exception):
            mystr5 = c.disp('W')

    def test_020_automatic_factorize_units(self):
        A = np.array([1*m, 2*m])
        B = np.array([2, 3])*m
        self.assertIsNone(np.testing.assert_array_equal(A+1*m, B))
        

full_suite_DataArray= unittest.TestLoader().loadTestsFromTestCase(TestDataArrays)
full_suite_Units = unittest.TestLoader().loadTestsFromTestCase(TestUnits)

TOTAL = unittest.TestSuite()
TOTAL.addTests(full_suite_DataArray)
TOTAL.addTests(full_suite_Units)



#list_of_tests = ['test_013_integ_array_without_units'] 
#partial_suite = unittest.TestSuite(map(TestDataArrays, list_of_tests))

#suite = partial_suite
suite = TOTAL 

unittest.TextTestRunner(verbosity=2).run(suite)

#pdb.set_trace()
#print("End of tests")
