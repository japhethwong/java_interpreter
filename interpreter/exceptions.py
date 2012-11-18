'''
exceptions.py
Stores the exceptions that are used in interpreter.
@author: Japheth Wong
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

