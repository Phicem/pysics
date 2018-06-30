#!/usr/bin/env python3

# (C) 2017 Phicem
# This software is released under MIT license (provided in LICENSE.txt)


import numpy as np
from units import *


class DataArray:
    """This class is a convenient way to store and handle a sampled 1D-function 
    (with physical units). It is implemented as a numpy array with two rows, each 
    one associated with a physical unit.

    DataArrays can handle basic arithmeric operations (+-*/), power, absolute 
    value, and equality test. Two DataArrays with different samplings can work 
    together (linear interpolations are done when necessary).

    EXAMPLES:

    Constructing a DataArray:
        >> from units import *
        >> from arrays import DataArray
        >> import numpy as np
        >> time = np.array([0,1,2,3]) * s
        >> output = np.array([1,2,3,4]) * kg
        >> output_vs_time = DataArray(time, output)
        >> output_vs_time

            DataArray with units : s | kg
            [[ 0.  1.]
             [ 1.  2.]
             [ 2.  3.]
             [ 3.  4.]]

    Operation on two DataArray with the same x sampling:
        >> output_vs_time + output_vs_time

            DataArray with units : s | kg
            [[ 0.  2.]
             [ 1.  4.]
             [ 2.  6.]
             [ 3.  8.]]

    Operation on two DataArray with different x samplings:
        >> time_2 = np.array(  [1.5, 2.5, 3.5]) * s
        >> output_2 = np.array([1,   1,   1  ]) * kg
        >> output_2_vs_time_2 = DataArray(time_2, output_2)
        >> output_2_vs_time_2

            DataArray with units : s | kg
            [[ 1.5  1. ]
             [ 2.5  1. ]
             [ 3.5  1. ]]

        >> output_2_vs_time_2 + output_vs_time # only the common interval can be defined
            DataArray with units : s | kg
            [[ 1.5  3.5]
             [ 2.5  4.5]
             [ 3.5  5. ]]

    """

    def __init__(self, X_with_units, Y_with_units):
        self.X_with_units = X_with_units
        self.Y_with_units = Y_with_units
        self.X_unit = Quantity(1,unit(X_with_units))
        self.Y_unit = Quantity(1,unit(Y_with_units))
        self.X_without_units = X_with_units/self.X_unit
        self.Y_without_units =  Y_with_units/self.Y_unit
        
        if len(np.shape(self.X_without_units)) != 1 or np.shape(self.X_without_units) != np.shape(self.Y_without_units):
            raise Exception("Vectors have invalid shapes (%s and %s), they must be 1-D arrays of the same size" % (np.shape(X),np.shape(Y)) )

    def without_units(self,unit_x=None,unit_y=None):
        if unit_x is None and unit_y is None:
            return np.transpose(np.vstack((self.X_without_units, self.Y_without_units)))
        else:
            X_without_units = self.X_with_units/unit_x
            Y_without_units = self.Y_with_units/unit_y
            try:
                X_without_units + Y_without_units +1 # unit check
                return np.transpose(np.vstack((X_without_units, Y_without_units)))
            except:
                raise Exception("Invalid unit given for graph display: data are (%s,%s), specified unit is (%s,%s)" % (unit(self.X_unit),unit(self.Y_unit),unit(unit_x),unit(unit_y)))

    def __repr__(self):
        string = "DataArray with units : %s | %s\n" % (unit(self.X_unit), unit(self.Y_unit))
        string += np.array_str( np.transpose(np.vstack((self.X_without_units, self.Y_without_units))) , precision = 3)
        return string

    def __compute_x_scale(self, other_array):
        """ Re-interpolate (linearly) both DataArrays in order to enable the mathematical operation"""
        if self.X_unit != other_array.X_unit:
            raise DimensionError( str(self.X_unit), str(other_array.X_unit) )
        
        X1 = self.X_without_units
        Y1 = self.Y_without_units
        
        X2 = other_array.X_without_units
        Y2 = other_array.Y_without_units

        # compute x scale
        x_min = max(min(X1),min(X2))
        x_max = min(max(X1),max(X2))
        x_step = min( min(np.diff(X1)), min(np.diff(X2)))
        new_x = np.arange(x_min, x_max + x_step, x_step)
        self.new_x_with_units = new_x * self.X_unit
        # interpolate
        self.new_self_Y_with_units = np.interp(new_x, X1, Y1)* self.Y_unit
        self.new_other_Y_with_units = np.interp(new_x, X2, Y2)* other_array.Y_unit

    def __create_result(self,result_with_units):
        """ Function called by the operators (code factorization)"""
        new_array = DataArray(self.new_x_with_units, result_with_units)
        # resetting buffer
        self.new_x = None
        self.new_self_Y = None
        self.new_other_Y = None
        return new_array

    def __add__(self, y):
        if isinstance(y,DataArray):
            self.__compute_x_scale(y)
            new_result_with_units = self.new_self_Y_with_units + self.new_other_Y_with_units
            return self.__create_result(new_result_with_units)
        else:
            raise TypeError("Incorrect type when adding, must be DataArray, not %s" % type(y))
         
    def __sub__(self, y):
        if isinstance(y,DataArray):
            self.__compute_x_scale(y)
            new_result_with_units = self.new_self_Y_with_units - self.new_other_Y_with_units
            return self.__create_result(new_result_with_units)
        else:
            raise TypeError("Incorrect type when adding, must be DataArray, not %s" % type(y))

    def __mul__(self, y):
        if isinstance(y,DataArray):
            self.__compute_x_scale(y)
            new_result_with_units = self.new_self_Y_with_units * self.new_other_Y_with_units
            return self.__create_result(new_result_with_units) 
        elif isinstance(y+0., float):
            return DataArray(self.X_with_units, self.Y_with_units*y)
        else:
            raise TypeError("Incorrect type when multiplying, must be scalar or DataArray, not %s" % type(y))
       
    def __div__(self, y):
        if isinstance(y,DataArray):
            self.__compute_x_scale(y)
            new_result_with_units = self.new_self_Y_with_units / self.new_other_Y_with_units
            return self.__create_result(new_result_with_units) 
        elif isinstance(y+0., float):
            return DataArray(self.X_with_units, self.Y_with_units/y)
        else:
            raise TypeError("Incorrect type when multiplying, must be scalar or DataArray, not %s" % type(y))

    def __truediv__(self,y):
        return self.__div__(y)

    def __pow__(self,y):
        try:
            power = float(y)
            return DataArray(self.X_with_units, self.Y_with_units**y)
        except:
            raise TypeError("The power must be a real number, not a %s" % type(y))

    def __neg__(self):
        return 0. - self

    def __invert__(self):
        return 1./self

    def __rmul__(self,y):
        return self * y

    def __eq__(self,y):
        return (self.X_with_units == y.X_with_units).all() and (self.Y_with_units == y.Y_with_units).all()

    def __abs__(self):
        return DataArray(self.X_with_units, abs(self.Y_without_units*self.Y_unit))

    def __call__(self, x):
        """ Enables the use of a a DataArray as if it were a continuous function. Interpolates linearly"""
        try:
            x_without_unit = float(x/self.X_unit)
        except TypeError:
            raise TypeError("Function argument must have unit '{unit}', not '{given}'".format(unit= unit(self.X_unit), given = unit(x)))

        X_min = min(self.X_without_units)* self.X_unit
        X_max = max(self.X_without_units)* self.X_unit
        if x >= X_min and x <= X_max:
            return np.interp(x_without_unit, self.X_without_units, self.Y_without_units)*self.Y_unit
        else:
            raise ValueError("Cannot interpolate DataArray: {x} is not in abscissa range [{min} ; {max}]".format(x = x, min =  str(X_min), max = str(X_max)))

    def integ(self, xmin, xmax):
        """ Return the integral of the array between xmin and xmax with the trapezoidal rule."""
        min_X = self.X_without_units.min()*self.X_unit
        max_X = self.X_without_units.max()*self.X_unit
        if not isInAscendingOrder(self.X_without_units):
            raise Exception("X array must be sorted by ascending order")
        if xmin > xmax:
            raise Exception("xmax must be greater than xmin to avoid ambiguity")
        if xmin < min_X or xmax > max_X:
            raise Exception("Integration interval ({xmin},{xmax} should be entirely in the definition interval [{min},{max}]".format(xmin = str(xmin), xmax = str(xmax), min = str(min_X), max = str(max_X)))
        i = 0
        while self.X_with_units[i] < xmin:
            i +=1
        # reaching first point of integration 
        X1 = xmin
        Y1 = self(X1)
        X2 = self.X_with_units[i]
        Y2 = self.Y_with_units[i]
        integral = (Y2+Y1)/2 * (X2-X1)
        #print("\nPoint {X1},{Y1},{X2},{Y2}, integ = {integral}".format(X1=X1,X2=X2,Y1=Y1,Y2=Y2,integral=integral))
        i += 1
        while self.X_with_units[i] < xmax:
            X1 = self.X_with_units[i-1]
            Y1 = self.Y_with_units[i-1]
            X2 = self.X_with_units[i]
            Y2 = self.Y_with_units[i]
            integral += (Y2+Y1)/2 * (X2-X1)
            i += 1
        # reaching last point of integration
        X1 = self.X_with_units[i-1]
        Y1 = self.Y_with_units[i-1]
        X2 = xmax
        Y2 = self(X2)
        integral += (Y2+Y1)/2 * (X2-X1)

        return integral

def sampleFunction(function, xmin, xmax, nb_points = 50):
    X_array = Quantity(np.linspace(SIValue(xmin), SIValue(xmax), num = nb_points), unit(xmin))
    Y_array_without_units = np.zeros(nb_points)
    Y1 = function(X_array[0])
    Y_unit = unit(Y1)
    Y_array_without_units[0] = Y1.value
    for i in range(1, nb_points):
        result = function(X_array[i])
        if unit(result) != Y_unit:
            raise Exception("Function should have the same unit for every value of the input array")
        Y_array_without_units[i] = SIValue(result)

    X = X_array
    Y = Quantity(Y_array_without_units, Y_unit)
    return DataArray(X,Y)


def isInAscendingOrder(np_array):
    """ Return whether a np_array is in ascending order. Useful for IsValid conditions."""
    dx = np.diff(np_array)
    return np.all(dx > 0) 


#EOF
