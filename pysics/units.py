#!/usr/bin/env python3

# (C) 2018 Phicem
# This software is released under MIT license (provided in LICENSE.txt)

# TODO: do rad and sr really belong here?
# TODO: implement in-place operators (__iadd__, etc.) for better performance with numpy?
# TODO: numpy dependency should be made optional... (with a "try: import ...")
# TODO: prepare a wrapper (as a decorator) to manage third-party functions that are not units compatible
# TODO: unit testing...
# TODO: clean up units namespace of find an other way to import all units in current namespace
# TODO: a_quantity.symbol returns surprising results when it's not a basic unit
# TODO: add a 'favorite' unit for a quantity?

""" This module implements a basic physical units system.
SI units [ 'm', 's', 'kg', 'A', 'K', 'cd','mol'] as well as 'rad' and all 
their multiples (km, cm, etc.) are defined in the module's namespace.

Some other common units (Hz, N, Pa, J, W, C, V, F, Ohm, S, hr (hour), 
mn (minute), sr) are also defined, but not their multiples.

Basic usage example :
    >> from units import *
    >> mass = 10*kg
    >> v = 36*km/hr
    >> Ec= 1./2 * mass * v**2
    >> Ec
        500.000  kg*m**2/s**2 [PHYS]
    >> Ec / J
        500.0

Dimension checkings:
    >> Ec + 3*kg
        units.DimensionError: Error with physical units: cannot add, 
        substract or compare kg*m**2/s**2 with kg
    >> Ec + 3*J
        503.000  kg*m**2/s**2 [PHYS]


Getting units and value:
    >> Ec.unit
        <unit: kg*m**2/s**2>
    >> Ec.value
       500.0
    >> float(Ec) # Ec is not unitless
        TypeError: can't convert physical quantity (unit = kg*m**2/s**2) to float
    >> type(Ec/J) # when a quantity is dimensionless, it is automatically converted to a float
        <class 'float'>

Defining new units:
    >> kJ = 1000*J
    >> Ec / kJ
        0.5

Playing with numpy arrays:
    >> import numpy as np
    >> a = np.array([1,2,3]) * km
    >> 2*a
        [ 2000.  4000.  6000.]  m [PHYS]




DISPLAY_DIGITS and EXP_THRESHOLD can be edited to adjust how quantities are defined.
"""

from __future__ import division
import pdb
import numpy as np
import sympy 


# Constants used to change how physical quantities are turned to strings
DISPLAY_DIGITS = 3 # To change default display precision, change DISPLAY_DIGITS value
EXP_THRESHOLD = DISPLAY_DIGITS
UNIT_SUFFIX = " [PHYS]"
UNIT_PREFIX= "  "

list_of_basic_SI_units = [ 'm', 's', 'kg', 'A', 'K', 'cd','mol'] + ['rad']

def displayNumber(number):
    """Format 'number' (real of complex) to a readable string with a limited number of digits"""
    scientific = '%.' + str(DISPLAY_DIGITS) + 'E'
    classic =  '%.' + str(DISPLAY_DIGITS) + 'f'
    if np.isreal(number):
        if abs(number) >= 10**EXP_THRESHOLD or abs(number) < 10**(-EXP_THRESHOLD):
            return scientific % number
        else:
            return classic % number
    elif np.iscomplex(number):
            return "(%s + %sj)" % (displayNumber(number.real), displayNumber(number.imag))
    else:
        raise TypeError("displayNumber argument must be a number (real of complex).")

def displayUnit(*args):
    """ Each argument must be a tuple ('unit_name', power)"""
    output = 1
    for (unit_name, power) in args:
        output *= sympy.Symbol(unit_name)**power
    return str(output)

class Dimension(object):
    """ This class defines a Dimension object, which is the 'physical unit' 
    of a physical quantity. There is no value associated with a Dimension 
    object, just a unit. For instance 'kg' can be a Dimension object, but not '2 kg'. 

    This is an internal object and should not be handled by the final user. The final user
    should handle units through quantities (with a value of 1 and a Dimension object as unit).

    There are two ways to build a Dimension object :
    1/ with the constructor (which takes a basic SI unit as argument (ie 'm', 's', 'kg', etc)
    2/ by combining several dimensions (for instance 'a = Dimension('m') * Dimension('kg')' 
    will return a Dimension object corresponding to 'm*kg'
    """
    def __init__(self, definition):
        self.units = {}
        for base_unit in list_of_basic_SI_units:
            self.units[base_unit] = 0
        if definition == None:
            pass
        elif definition in list(self.units.keys()):
            self.units[definition] = 1
        elif isinstance(definition,dict): # it must be a dict:
                self.units = definition
        else:
                raise TypeError("Dimension constructor takes a string among %s, or None, or a dict, but not '%s'" % (str(self.units.keys()),type(definition)))
   
    def __str__(self):
        string = ""        
        list_of_units = self.units.items()
        string = displayUnit(*list_of_units)
        return string

    def __repr__(self):
        string = str(self)
        if string == '':
            return '<unit: dimensionless>'
        else:
            return '<unit: %s>' % string

    def __mul__(self,y):
        if isinstance(y,Dimension):
            new_unit = {}
            for key in self.units.keys():
                new_unit[key] = self.units[key] + y.units[key]
            return Dimension(new_unit)
        else:
            raise TypeError("%s is not a valid unit, cannot multiply" % str(y) )

    def __div__(self,y):
        if isinstance(y,Dimension):
            new_unit = {}
            for key in self.units.keys():
                new_unit[key] = self.units[key] - y.units[key]
            return Dimension(new_unit)
        else:
            raise TypeError("%s is not a valid unit, cannot divide" % str(y) )

    def __truediv__(self,y): # called if __future__.division is active
        return self.__div__(y)

    def __eq__(self,y):
        return isinstance(y,Dimension) and self.units == y.units

    def __neq__(self,y):
        return not self.__eq__(y)

    def __pow__(self,y):
        if np.isreal(y):
            new_unit = {}
            for key in self.units.keys():
                new_unit[key] = self.units[key] * y
            return Dimension(new_unit)
        else:
            raise TypeError("The power of a physical quantity must be a real number (not a %s)." % type(y))

def turn_to_Quantity(x):
    """ Turn a number to a (unitless) quantity. If the argument is a quantity, returns it unchanged."""
    if isinstance(x,Quantity):
        return x
    elif isinstance(x, np.ndarray) or np.isreal(x) or np.iscomplex(x):
            return Quantity(x,Dimension(None), symbol = '<number>')
    else:
        raise TypeError("Invalid number, cannot turn it to a quantity. A %s is not a real, complex number or numpy array." % type(x))

def unit(quantity_or_float): # it's a function, not a method (to work with usual numbers, and not just Quantities)
    try:
        return quantity_or_float.unit
    except:
        return unitless.unit

def SIValue(quantity_or_float):
    """Return the value of a given quantity expressed in its SI unit. If given a float, return the same float
    Example:
    --------
        SIValue(2) --> 2
        SIValue(3*cm) --> 0.03
    """
    if isinstance(quantity_or_float,Quantity):
        return quantity_or_float.value
    else:
        return quantity_or_float
    

class DimensionError(Exception):
    """ This exception is raised when trying to add, substract, compare or do any invalid operation on two different units."""
    def __init__(self, unit_1, unit_2):
        self.message = "Error with physical units: cannot add, substract or compare %s with %s." % (str(unit_1), str(unit_2))
    def __str__(self):
        return self.message

def isSympyExpression(test_object): # TODO: very ugly...
    try:
        a = test_object + sympy.Symbol('1')
        return True
    except:
        return False


class Quantity(object):
    """ A quantity is a number (real or complex) associated with a Dimension."""
    def __init__(self, value, unit, symbol = '<custom>'):
        self.value = value
        self.unit = unit
        if symbol == '<number>':
            self.symbol = 1
        elif isinstance(symbol,str):
            self.symbol = sympy.Symbol(symbol)
       # elif isinstance(symbol,syp_expr.Expr):
        elif isSympyExpression(symbol):
            self.symbol = symbol
        else:
            raise TypeError("The symbol of a new quantity must be either a string or a sympy symbol ; %s is of type  %s" % (str(symbol),type(symbol)))
        self.__array_priority__ = 100 # without this line, ndarray * quantity is an ndarray of dtype=object, instead of a quantity

    def __repr__(self):
        if isinstance(self.value, np.ndarray):
            return "Array with units:\n" + str(self.value) +  UNIT_PREFIX + str(self.unit) + UNIT_SUFFIX
        else:
            string = displayNumber(self.value) + UNIT_PREFIX + str(self.unit) + UNIT_SUFFIX
            return string

    def isDimensionless(self):
        return self.unit == Dimension(None)

    def removeUnitIfPossible(self):
        if self.isDimensionless():
            return self.value
        else:
            return self

    def __add__(self, y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit: # adding is allowed
            return Quantity( self.value + Y.value, self.unit, symbol = self.symbol)
        else:
            raise DimensionError( str(self.unit), str(Y.unit) )
         
    def __sub__(self, y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit: # substracting is allowed
            return Quantity( self.value - Y.value, self.unit, symbol = self.symbol) 
        else:
            raise DimensionError( str(self.unit), str(y.unit) )

    def __mul__(self, y):
        Y = turn_to_Quantity(y)
        new_val = self.value * Y.value
        new_unit = self.unit * Y.unit
        new_symbol = self.symbol * Y.symbol

        return Quantity(new_val, new_unit, symbol = new_symbol).removeUnitIfPossible()
                        
    def __div__(self, y):
        Y = turn_to_Quantity(y)
        new_val = self.value / Y.value 
        new_unit = self.unit / Y.unit
        new_symbol = self.symbol / Y.symbol
        return Quantity(new_val, new_unit, new_symbol).removeUnitIfPossible()

    def __truediv__(self,y):
        return self.__div__(y)

    def __pow__(self,y):
        if (isinstance(y, np.ndarray) and y.isreal(y).all() ) or  np.isreal(y):
            return Quantity(self.value ** y, self.unit ** y, symbol = self.symbol**y).removeUnitIfPossible()
        else:
            raise TypeError("The power must be a real number (or numpy array with only real numbers), not a %s" % type(y))

    def __neg__(self):
        return self*(-1)

    def __invert__(self):
        return 1./self

    def __mod__(self, y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit: # adding is allowed
            return Quantity(self.value % Y.value, self.unit, symbol = self.symbol) 
        else:
            raise DimensionError(self.unit, Y.unit)

    # Right version of operators are mandatory to handle operations like "1*m"

    def __radd__(self,y):
        return self + y # commutative operation, no problem

    def __rsub__(self,y):
        Y = turn_to_Quantity(y) # not commutative, we have to convert y
        return Y - self

    def __rmul__(self,y):
        return self * y # commutative operation, no problem

    def __rdiv__(self,y): 
        Y = turn_to_Quantity(y) # not commutative, we have to convert y
        return Y / self

    def __rtruediv__(self,y):
        return self.__rdiv__(y)

    def __eq__(self,y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit:
            return self.value == Y.value
        else:
            return False

    def __ne__(self,y):
        # a simple "return not self == y" # won't work with numpy arrays
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit:
            return self.value != Y.value
        else:
            raise DimensionError(self.unit, Y.unit)
        
    def __gt__(self,y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit:
            return self.value > Y.value
        else:
            raise DimensionError(self.unit, Y.unit)

    def __ge__(self,y):
        return (self > y or self == y)

    def __lt__(self,y):
        Y = turn_to_Quantity(y)
        if self.unit == Y.unit:
            return self.value < Y.value
        else:
            raise DimensionError(self.unit, Y.unit)

    def __le__(self,y):
        return (self < y or self == y)

    def __abs__(self):
        return Quantity( abs(self.value), self.unit, symbol = self.symbol)

    def __complex__(self):
        if self.isDimensionless():
            return complex(self.value)
        else:
            raise TypeError("can't convert physical quantity (unit = %s) to complex" % self.unit)

    def __int__(self):
        if self.isDimensionless():
            return int(self.value)
        else:
            raise TypeError("can't convert physical quantity (unit = %s) to int" % self.unit)
    
    def __long__(self):
        if self.isDimensionless():
            return long(self.value)
        else:
            raise TypeError("can't convert physical quantity (unit = %s) to long" % self.unit)
    
    def __float__(self):
        if self.isDimensionless():
            return float(self.value)
        else:
            raise TypeError("can't convert physical quantity (unit = %s) to float" % self.unit)
    
    def get_SI_unit(self):
            return Quantity(1,self.unit)

    def __getitem__(self, key):
        return Quantity(self.value[key],self.unit, symbol = self.symbol)

    def disp(self, unit_str=None):
        """ Another display function that allows unit customization"""
        if unit_str is None:
            return self.__repr__()
        else:
            unit = eval(unit_str)
            if not isinstance(unit, Quantity):
                raise Exception("{unit_str} is not a valid unit string".format(unit_str = unit_str))
            value = self/unit
            if isinstance(value, Quantity): # there is a residual unit
                raise Exception("{unit_str} is not the right unit for {self}".format(unit_str = unit_str, self = self))
            else:
                if isinstance(value, np.ndarray):
                    return str(value) +  " " + unit_str
                else:
                    return displayNumber(value) + " " + unit_str



# Sub-multiples
sub_multiple_list = [ {'symbol': 'T', 'value': 1e12},
                      {'symbol': 'G', 'value': 1e9},
                      {'symbol': 'M', 'value': 1e6},
                      {'symbol': 'k', 'value': 1e3},
                      {'symbol': 'h', 'value': 1e2},
                      {'symbol': 'da', 'value': 1e1},
                      {'symbol': 'd', 'value': 1e-1},
                      {'symbol': 'c', 'value': 1e-2},
                      {'symbol': 'm', 'value': 1e-3},
                      {'symbol': 'mu', 'value': 1e-6},
                      {'symbol': 'micro', 'value': 1e-6},
                      {'symbol': 'n', 'value': 1e-9},
                      {'symbol': 'p', 'value': 1e-12},
                      {'symbol': 'f', 'value': 1e-15},
                      ]


# Basic units:
unitless = Quantity(1,Dimension(None),'1')
__mydict__ = globals()
for basic_unit in list_of_basic_SI_units:
    __mydict__[basic_unit] =  Quantity(1,Dimension(basic_unit), symbol = basic_unit)    

g = Quantity(1e-3,Dimension('kg')) # SI unit is kg, but it's easier to define the gram, for sub-multiples management

def defineUnit(symbol, quantity):
    __mydict__[ symbol ] = Quantity(SIValue(quantity),unit(quantity), symbol = symbol)


defineUnit('Hz', 1/s)
defineUnit('N', kg*m/s**2)
defineUnit('Pa', N/m**2)
defineUnit('J', kg * (m / s)**2)
defineUnit('W', J/s)
defineUnit('C', A*s)
defineUnit('V', W/A)
defineUnit('F', C/V)
defineUnit('Ohm', V/A)
defineUnit('S', A/V)
defineUnit('hr', 3600*s)
defineUnit('mn', 60*s)
defineUnit('sr',  rad**2)



def defineSubmultiples(namespace_dict, main_unit):
    for sub_multiple in sub_multiple_list:
        main_unit_object = namespace_dict[main_unit]
        sub_unit_name = sub_multiple['symbol'] + main_unit
        namespace_dict[ sub_unit_name ] = sub_multiple['value'] * main_unit_object
        namespace_dict[ sub_unit_name ].symbol =  sympy.Symbol(sub_multiple['symbol'] + str(main_unit_object.symbol))


for main_unit in list_of_basic_SI_units: # I'm hoping there is no name conflict!
    defineSubmultiples(__mydict__, main_unit)

# A few not-SI but convenient units
ft = 0.3048*m
NM = 1.852*km
yard = 0.9144*m
inch = 2.54*cm # not 'in' because it is a reserved word in python
kft = 1000*ft
