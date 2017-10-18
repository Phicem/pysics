#!/usr/bin/env python3

# (C) 2017 Phicem
# This software is released under MIT license (provided in LICENSE.txt)

# TODO: add a smart scale that enables functions like x|--> 1/x to display properly

""" This module is an additional layer over matplotlib to ease data plotting. The main features are:
    - a Curve (containing a set of data, a label for the legend, and a color/marker) can be re-used in several graphs with the same formatting
    - a function can be plotted without having to define an array for abscissa
    - labels are automatically added to any plotted data
    - graphs and curves can be edited through a simple object-oriented API

    Usage example:
        >> def f(x): return 3*x**3+2
        >> curve_1 = Curve(f)

        >> curve_2 = Curve(lambda x: x**2)

        >> X = np.array([1,2,3,4,5])
        >> Y = X**3
        >> curve_3 = Curve((X,Y), marker = '-*', color='r')

        >> graph_1 = Graph([curve_1, curve_2], xlabel = "Abscissa")
        >> graph_1.show()

        >> graph_2 = Graph([curve_1, curve_2, curve_3])
        >> graph_2.show()
        >> graph_2.xmax = 5

    For people in a hurry:
        >> GG = quickGraph(f,2,10) # show plot of f between xmin = 2 and xmax = 10


"""

import matplotlib
#matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
#plt.ioff() # to disable interactive mode
import numpy as np
import types
from arrays import DataArray



def loop_generator(mylist):
    i = 0
    while 1:
        nmax = len(mylist)
        yield mylist[i % nmax]
        i+=1

list_of_colors = ['g', 'r', 'c', 'm','k', 'b']
list_of_markers = ['x', 's', '*', '+', '^', 'v', 'd', 'o' ]

colors = loop_generator(list_of_colors)

markers = loop_generator(list_of_markers)


class Curve:
    """ A Curve object is a set of data, color, marker and label. It's purpose is to be added to a graph"""
    def __init__(self, data, color = 'auto', marker='auto', label='auto'):
        # TODO: can 'data' be a DataArray?
        """ data can be a couple of vectors (X,Y), or a 2-column (or 2-rows) array, or a function
        Possible optional arguments:
            color : one of the following: ['g', 'r', 'c', 'm','k', 'b']
            marker : one of the following: ['x', 's', '*', '+', '^', 'v', 'd', 'o' ]
            label (for the legend) : any string """
        if isinstance(data, tuple) and len(data) == 2:
            [X, Y] = data
            if isinstance(Y, np.ndarray) and isinstance(X, np.ndarray):
                self.type = 'array'
                if len(Y.shape) == 1 and X.shape == Y.shape:
                    self.X = X
                    self.Y = Y
                else:
                    raise Exception("X and Y must be vectors and have the same number of elements")
        elif isinstance(data, types.FunctionType):
            self.type = 'function'
            self.function = data
            if label == 'auto':
                label = data.__name__
        elif isinstance(data, np.ndarray):
            self.type = 'array'
            if len(data.shape) == 1: # 1-D array
                self.X = np.arange(0,data.shape[0])
                self.Y = data
            elif len(data.shape) == 2 and data.shape[0] == 1: # badly formatted 1-D array
                self.X = np.arange(0,data.shape[1])
                self.Y = data[0,:]
            elif len(data.shape) == 2 and data.shape[1] == 1: # badly formatted 1-D array
                self.X = np.arange(0,data.shape[0])
                self.Y = data[:,0]
            elif len(data.shape) == 2 and data.shape[0] == 2: # 2 rows? or columns?
                self.X = data[0,:]
                self.Y = data[1,:]
            elif len(data.shape) == 2 and data.shape[1] == 2: # 2 columns? or rows?
                self.X = data[:,0]
                self.Y = data[:,1]
            else:
                raise Exception("Invalid shape for array, cannot create Curve instance: shape is %s but should be (2,N) or (N,)" % str(data.shape) )
        else:
            raise Exception("Invalid type of arguments, cannot create Curve instance. Data is of type %s instead of array or function" % str(type(data)))



        self.__set_color(color)
        self.__set_marker(marker)
        self.label = label

    def __set_color(self, color):
        if color in list_of_colors +['auto']:
            self.color = color
        else:
            print("Invalid color: %s" % color)
            self.color = "auto"

    
    def __set_marker(self, marker):
        if marker.replace('-','')  in list_of_markers+['auto']+['']:
            self.marker = marker
        else:
            print("Invalid marker: %s. Setting to auto" % marker)
            self.marker = "auto"

class Graph:
    def __init__(self,list_of_curves, xmin = 'auto', xmax = 'auto', ymin = 'auto', ymax= 'auto', xlabel = '', ylabel = '', title = '', nb_pts = 1000):
        if isinstance(list_of_curves, list):
            self.list_of_curves = list_of_curves
        elif isinstance(list_of_curves, Curve):
            self.list_of_curves = [list_of_curves]
        else:
            print("Invalid data type, must be a curve or list of curves")
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.title = title
        self.nb_pts = nb_pts

    def __compute_x_scale(self):       
        if self.xmin == 'auto':
            list_of_x_min = [ min(curve.X) for curve in self.list_of_curves if curve.type == 'array' ]
            if len(list_of_x_min) > 0:
                self.real_xmin = min(list_of_x_min)
            else:
                self.real_xmin = -10
        else:
            self.real_xmin = self.xmin
        if self.xmax == 'auto':
            list_of_x_max = [ max(curve.X) for curve in self.list_of_curves if curve.type == 'array' ]
            if len(list_of_x_max) > 0:
                self.real_xmax = max(list_of_x_max)
            else:
                self.real_xmax = 10
        else:
             self.real_xmax = self.xmax
            
    def __compute_data(self):
        
        self.list_of_curve_data = []
        
        self.list_of_y_min = []
        self.list_of_y_max = []    
      
        for curve in self.list_of_curves:
            if curve.type == 'function': # TODO: mins and maxs should be computed before drawing any function curve...
                X_step = (self.real_xmax-self.real_xmin+0.) / self.nb_pts
                X =  np.arange(self.real_xmin, self.real_xmax + X_step, X_step)
                Y = curve.function(X)
            else:
                X = curve.X
                Y = curve.Y  
            
            self.list_of_curve_data.append((X,Y))
               
            self.list_of_y_min.append(np.nanmin(Y))
            self.list_of_y_max.append(np.nanmax(Y))
    
    def __compute_y_scale(self):
        if self.ymin == 'auto':
            self.real_ymin = min(self.list_of_y_min)
        else:
           self.real_ymin = self.ymin
        if self.ymax == 'auto':
            self.real_ymax = max(self.list_of_y_max)
        else:
            self.real_ymax = self.ymax

  
    def draw(self):
        self.__compute_x_scale()
        self.__compute_data()
        self.__compute_y_scale()
        # Compute auto scale

        plt.clf()
        for index in range(0,len(self.list_of_curves)):
            curve = self.list_of_curves[index]
            (X, Y) = self.list_of_curve_data[index]
            
            # Auto-formatting
            if curve.color == 'auto':
                #color = colors.next()
                color = next(colors)
            else:
                color = curve.color
            if curve.marker == 'auto':
                if curve.type == 'function':
                    marker = '-'
                else:
                    #marker = markers.next()
                    marker = next(markers)
            else:
                marker = curve.marker
            if curve.label == 'auto':
                label = "Dataset n#%i" % index
            elif curve.label == '<lambda>':
                label = "Function n#%i" % index
            else:
                label = curve.label

            plt.plot(X, Y, color + marker, label = label)


        # Actual figure building
        plt.axis([self.real_xmin, self.real_xmax, self.real_ymin, self.real_ymax])
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.title(self.title)
        #plt.legend(loc="center right")
        plt.legend(loc="best")
    
        return plt

    def show(self):
        self.draw().show()


def quickGraph(data_or_function, xmin = 'auto', xmax = 'auto'):
    """Quickly plot data_or_function in one step. Labels and scales cannot be changed."""
    if isinstance(data_or_function, DataArray):
        x_unit = data_or_function.X_unit.unit
        y_unit = data_or_function.Y_unit.unit
        data_or_function = (data_or_function.X_without_units, data_or_function.Y_without_units)
        curve = Curve(data_or_function, label='auto', color='r', marker = '*-')
        G = Graph(curve, xmin = xmin, xmax = xmax)
        G.xlabel = 'X ({unit})'.format(unit = x_unit)
        G.ylabel = 'Y ({unit})'.format(unit = y_unit)
    else:
        curve = Curve(data_or_function, label='auto', color='r')
        G = Graph(curve, xmin = xmin, xmax = xmax)
    G.show()
    return G



## TESTS
def test():
    X = np.array([1,2,3,4,5])
    Y = X**3
    curve = Curve((X,Y), marker = '-*', color='r')
    other_curve = Curve(lambda x: x**2)
    G = Graph([curve,other_curve])
    G = Graph([other_curve])
    #G.show()
    
    
    
    def f(x): return 3*x**3+2
        
    GG = quickGraph(f,2,10)
    GG = quickGraph((X,Y))

#test()
