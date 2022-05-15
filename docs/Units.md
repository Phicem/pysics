---
layout: default
title: pysics.units 
description: Module documentation
---
[BACK TO HOME PAGE](MainPage.html)

#  Units module 


## Description 

This package defines new python objects called Quantities, which represent a physical quantity, that is to say a number and a physical unit. Quantities are handled exaclty like float or int objects: they can be added, multiplied, etc.

Such a module enables your code to be units-aware. The main benefits of having units-aware code is to detect dimension mistakes (for instance when you try to add meters with kilograms) and conversion mistakes (when you want to add '10 cm' with '2 mm', you need to convert one of the two numbers first).

Handling units with python is theoretically a very simple problem, so I wanted this module to be very simple. Features that increase complexity a lot (like Kelvin to Celcius conversion) should be discared. At the moment the module is less than 400 lines of code, and should ideally remain that way.


## Why not use existing packages? 

There are MANY units packages out there. You can find a [comparison table here](https://socialcompare.com/en/comparison/python-units-quantities-packages-383avix4). I'll just compare PYSICS.units with packages I uncountered before writing this module.

 * **python-quantities**:
   * a bit too complex (far longer than 400 LOC)
   * some behaviors weren't exactly what I expected (for instance `(1*ft)(1*m)` returns `1 ft / 1 m` while I would expect `0.3048`
 * **pint**:
   * code is too long to read (far longer than 400 LOC)
   * the example in the readme suggests that units can't be imported in current namespace
 * **numericalunits**: dimension analysis is based on detecting whether the result if random
 * **unum**: looks good, but not-invented-here...

After writting this module, I realized **unum** was very similar to what I needed: short and simple code. You may want to try it. It is released under the LGPL, while pysics is under MIT license.

Depending on what you need, pysics.units may not be for you and you might prefer other packages. Possible reasons why pysics.units would not be for you:
 * you don't like its dependency on sympy (and numpy)
 * you use custom units (ie not SI unit) and want physical quantities to remember their custom unit instead of being expressed in SI units all the time
 * you need some missing features like uncertainty management

[UPDATE] There is another package called **physipy** which is originally based on **pysics** but provides far better support for working with numpy, matplotlib and ipython: see [https://github.com/mocquin/physipy](https://github.com/mocquin/physipy)

## Features and examples 

### Defined units 
SI units [ 'm', 's', 'kg', 'A', 'K', 'cd','mol'] as well as 'rad' and all their multiples (km, cm, etc.) are defined in the module's namespace.

Some other common units (Hz, N, Pa, J, W, C, V, F, Ohm, S, hr (hour), mn (minute), sr, ft, NM, inch, yard) are also defined, but not their multiples.



### Usual operations 
```python
from units import *
mass = 10*kg
v = 36*km/hr
Ec= 1./2 * mass * v**2
Ec       # outputs: 500.000  kg*m**2/s**2 [PHYS]
Ec / J   # outputs: 500.0

# Defining new units:
kJ = 1000*J
Ec / kJ  # outputs : 0.5
```

### Conversions 

```python
1*cm/m # outputs: 0.01
# By default quantities are displayed in their SI unit:
speed = 90*km/hr 
speed # outputs: 25.000  m/s [PHYS]
# To display it in another unit, the easiest way is to divide by that unit:
speed / (km/hr) # outputs: 90.0
```

### Custom units 

```python
# Defining custom units is as simple as:
MPH = 1.609344*km/hr
70*MPH #outputs: 31.293  m/s [PHYS]
# Any result can be expressed in that custom unit:
speed = 90*km/hr 
speed / MPH  # outputs: 55.92340730136006
```

### Dimension checks 

```python
# Trying to do an invalid operation results in an exception
1*km + 3*kg # raises: units.DimensionError: Error with physical units: cannot add, substract or compare m with kg.
```

### Function calls

Units work transparently with functions:
```python
def myfunc_1(d):
    return d+5*km

myfunc_1(2*m) # Outputs:   5.002E+03  m [PHYS]
myfunc_1(2*s) # Raise DimensionError
```

Functions behave with units the same way than with types, ie with a 'duck typing' philosophy. For instance, the following function can be called with any dimension (or even with a number):

```python
def myfunc_2(d):
    return 2*d

myfunc_2(10*km) # Outputs:   2.000E+04  m [PHYS]
myfunc_2(3*s)   # Outputs:   6.000  s [PHYS]
myfunc_2(5)     # Outputs:  10
```


### Numpy arrays 

```python
import numpy as np
a = np.array([1,2,3]) * km
2*a # outputs: [ 2000.  4000.  6000.]  m [PHYS]
```

It is also possible to create this array directly from a list:
```python
a = [1, 2, 3]*km
```

Accessing an item is easy:
```python
a[1] # Outputs: 2.000E+03  m [PHYS]
```



### Removing units 
```python
# One can access the unit and the value separately
Ec = 500*J
Ec.unit  # outputs: <unit: kg*m**2/s**2>
Ec.value # outputs:  500.0

float(Ec) # Ec is not unitless ==> raises:
          # TypeError: can't convert physical quantity (unit = kg*m**2/s**2) to float

# when a quantity is dimensionless, it is automatically converted to a float
type(Ec/J) # outputs: <class 'float'>
```

### Integrals 

Scipy integration functions (like scipy.integrate.quad) are not units-aware. The solution is to use pysics.integrate.integ function.


```python
from pysics.integrate import integ
def f(x):
    return x + 1*m

integ(f, 1*m,3*m) # output: 6.000  m**2 [PHYS]

```


### Numpy broadcasting and vectorizing issues 

In some situations (see [Vectorization](Vectorization.html) page for more details), the output of a function call is not a Quantity (with a numpy array as a value), but a numpy array of Quantities:


```python
def myfunc_2(d):
    if d < 2*m:
        return d+5*km
    else:
        return 0*m

d_array = np.arange(3)*m
out_array = np.array([ myfunc_2(d) for d in d_array ])

print(out_array) 
# Outputs:    [5.000E+03  m [PHYS] 5.001E+03  m [PHYS] 0.000E+00  m [PHYS]]
# instead of  [5.000E+03           5.001E+03           0.000E+00          ]  m [PHYS]
```

Each item of the output array has a unit, instead of having a unitless array associated with a unique unit. This might cause problems when using this array with functions that expect a Quantity. To convert this kind of array to a proper quantity, use the 'factorize_units' function:

```python
factorized_array = units.factorize_units(out_array)  # Outputs: [5000. 5001.    0.]  m [PHYS]
```

This function is automatically called when performing basic operations on an array, so it is generally not necessary to call this function manually. See [Vectorization](Vectorization.html) page for more details.

## How does it work (internally)? 

PYSICS.units defines two classes:
 * a Dimension class, which represents the unit itself
 * a Quantity class, which represents a physical quantity (that's to say a number associated with a unit)

Dimensions are basically a python dictionary which keys are SI units. The value corresponding to each key is the exponent of the unit. For instance, the Dimension object corresponding to meters per second ('m/s') would look like:
```python
{ 'm': 1, 's':-1, 'A': 0, 'K': 0, 'cd': 0, 'kg': 0, 'mol': 0, 'rad': 0}
```

Operations on units (like adding and multiplying) is just a matter of doing operations on those exponents. For instance adding two units returns the same unit (if they are both equal, otherwise it raises an exception), while multiplying two units requires adding the exponents.

The Dimension class code is mainly about redefining usual operators (`__mul__`,`__div__`, etc.) to describe what the exponents should become.

The Quantity class is basically a number and a Dimension. Applying an operation (adding, multiplying...) on a Quantity is done by applying this operation on both the number and the Dimension. Like Dimension's code, Quantity's code mainly contains operator redefinitions.

[BACK TO HOME PAGE](MainPage.html)
