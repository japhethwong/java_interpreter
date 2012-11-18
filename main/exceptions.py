'''
exceptions.py
Stores the exceptions that are used in interpreter.
@author: Japheth Wong, Joy Jeng
'''

class JavaException(Exception):
    pass

class InvalidAssignmentException(JavaException):
    pass
        
class InvalidDeclarationException(JavaException):
    pass

class InvalidDatatypeException(JavaException):
    pass
        
class JavaNameError(JavaException):
    pass
    
class InvalidSystemCallException(JavaException):
    pass

class InvalidIfElseBlockException(JavaException):
    pass

class WhatTheHeckHappenedException(JavaException):
    pass
