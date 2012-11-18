'''
util.py
Contains utility functions that are useful across the program
@author: Japheth Wong
'''
from constants import *

"""
parse_value() takes the string versions of the datatype and the associated value and returns the value in the correct datatype.

Arguments:
datatype -- STRING representation of the datatype of the item to be parsed
value -- STRING representation of the value of to be parsed

Returns:
The value in the appropriate datatype

>>> parse_value("4")
4
>>> parse_value("4.0")
4.0
>>> parse_value("string")
"string"
"""
def parse_value(value):    
    if value == None:
        return value
    try:
        to_return = int(value)
    except ValueError as e:
        try:
            float(value)
        except ValueError as f:
            to_return = value
    
    return to_return
            
def flatten_list(lst):
    """
    >>> flatten_list([1, 2, [3, 4], [[[3], 4]]])
    [1, 2, 3, 4, 3, 4]
    """
    if not lst:
        return []
    if type(lst[0]) == list:
        return flatten_list(lst[0]) + flatten_list(lst[1:])
    return [lst[0]] + flatten_list(lst[1:])
    