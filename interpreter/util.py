'''
util.py
Contains utility functions that are useful across the program
@author: Japheth Wong, Joy Jeng
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
            
"""
clean_up_list_elems() takes a list and removes all empty list elements.  It also strips each element.

Arguments:
lst -- the list that we want to remove empty elements from

Returns:
A list with the length-0 elements removed
"""
def clean_up_list_elems(lst):
    return list(filter(lambda x: len(x) > 0, list(map(lambda x: x.strip(), lst))))

"""
flatten_list() takes a list and flattens it by combining sub-lists into a single list.

Arguments:
lst -- the list to be flattened

Returns:
A list that has been flattened (none of the elements are lists)
"""
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
