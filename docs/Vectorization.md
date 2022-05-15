---
layout: default
title: Vectorization issues
#description: Module documentation
---
[BACK TO HOME PAGE](MainPage.html)

[BACK TO UNITS PAGE](Units.html)
# Vectorization 

### Numpy broadcasting and units 

When the argument of a function call is a numpy array, numpy generally computes an array of results, like in the following example.

```python
import numpy as np

def myfunc_1(x):
    return 2*x

a = np.array([1,2,3])
myfunc_1(a) # Outputs: array([2, 4, 6])
```

The behavior is exactly the same with units:

```python
b = np.array([1,2,3]) * km
myfunc_1(b) # Outputs: [2000. 4000. 6000.]  m [PHYS]
```

However, this works only if the function is vectorized. This is generaly the case when only basic operations (`+`, `*`, etc.) are applied.

### Vectorization issues 

When calling a function that is not natively vectorized, for instance with functions using an 'if' statement, the behavior is different.

```python
# Define a function using an 'if' statement
def myfunc_2(d):
    if d < 2*m:
        return d+5*km
    else:
        return 0*m

# Array for abscissa
d_array = np.arange(3)*m

# Compute output array
out_array = myfunc_2(d_array) # Outputs: ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

The error is due to the condition of the 'if' statement, which cannot be computed on a array, this is not specific to units:

```python
def myfunc_2_nounit(d):
    if d < 2:
        return d+5000
    else:
        return 0

out_array = myfunc_2_nounit(np.arange(10)) # Same error
```

### Vectorization techniques 

There are numerous ways to compute the desired result without this error. Here we explore four of them.

```python
# Solution 1: use list comprehension
out_array = np.array([ myfunc_2(d) for d in d_array ])

# Solution 2: use python built-in 'map' function
out_array = np.array(list(map(myfunc_2, d_array)))

# Solution 3: use numpy 'vectorize' function
myfunc_2_vect = np.vectorize(myfunc_2)
out_array = myfunc_2_vect(d_array)

# Solution 4 : use numpy 'where' mechanism (faster computation but requires re-writing the function)
def myfunc_2_improved(d):
    return np.where(d < 2*m, d + 5*km, 0*m)

out_array = myfunc_2_improved(d_array)

```

Unfortunately, in all those cases, the result is not a Quantity but a numpy array which items are Quantity. 
```python
# Outputs (in all cases):
array([5.000E+03  m [PHYS], 5.001E+03  m [PHYS], 0.000E+00  m [PHYS]],
      dtype=object)
```

This might be a problem for functions that expect a Quantity. 

### Converting to a Quantity 

Converting this numpy array to a Quantity is done with :
```python
from pysics import units
out_quantity = units.factorize_units(out_array)
```

This time the output is what we expect:
```python
from pysics import units
[5000. 5001.    0.]  m [PHYS]
```

This function is automatically called when performing basic operations on an array, so it is generally not necessary to call this function manually. For instance, the following code behaves as expected:
```python
out_array = np.array([ myfunc_2(d) for d in d_array ])
result = out_array + 1*km
print(result) # Outputs: [6000. 6001. 1000.]  m [PHYS]

```

[BACK TO UNITS PAGE](Units.html)

[BACK TO HOME PAGE](MainPage.html)
