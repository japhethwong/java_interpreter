'''
variable.py class
Stores value and datatype of variable.
@author: Japheth Wong, Joy Jeng
'''
from util import parse_value
from constants import *

class Variable(object):
    def __init__(self, value, datatype, name=UNDEFINED_PARAM):
        self.name = name
        self.datatype = datatype
        self.value = parse_value(value)
        
    def __repr__(self):
        return '[Variable] {0} {1} = {2} '.format(self.datatype, self.name, self.value)
        
    def __str__(self):
        return self.value if self.value != None else "Variable not initialized" 

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value
    
    def get_datatype(self):
        return self.datatype
    
    def set_value(self, value):
        self.value = value
        