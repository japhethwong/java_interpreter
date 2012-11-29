This is the README for the interface module of the Java Interpreter.

Author: Albert Wu

*----- GENERAL -----*
All interface functions and classes can be imported from the file
primitives.py


*----- CONTENTS -----*
- Interface
    - Variable
    - Method
    - ClassObj
- Testing
    

*----- INTERFACE -----*
Variable
    TYPE:       class
    FUNCTION:   Wrapper class for variables and their values. Holds 
                info on 
                - name       (string)
                - datatype   (string)
                - value      (string)   
                - protection (boolean)
                - static     (boolean)
    PURPOSE:    Intended as an abstract data type
    METHODS:    self.__str__()
                    returns human-readable format as string
    NOTES:      None

Method
    TYPE:       class
    FUNCTION:   Wrapper class for methods. Holds info on
                - name      (string)
                - datatype  (string)
                - arguments (list of Variable objects)
                - body      (string)
    PURPOSE:    Intended as an abstract data type
    METHODS:    self.is_constructor()
                    returns True if self is a constructor, False
                            otherwise
                self. __str__()
                    returns human-readable format as string
    NOTES:      None

ClassObj
    TYPE:       class
    FUNCTION:   Wrapper class for Class objects. Holds info on
                - name                (string)
                - protection          (boolean)
                - superclass          (string)
                - instance attributes (dictionary of Variable objects)
                - methods             (dictionary of Method objects)
                - constructors        (dictionary of Method objects)
    PURPOSE:    Intended as an abstract data type
    METHODS:    self.private(state=None)
                    if state == None, return True if class is private.
                    if state != None, set the class's private attribute
                    to state (must be a boolean)
                self.superclass(sup=None)
                    if sup == None, return the superclass as a string.
                    if sup != None, set the superclass to sup
                self. __str__()
                    returns human-readable format as string
    NOTES:      None


*----- TESTING -----*

