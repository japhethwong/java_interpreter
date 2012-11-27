This is the README for the compiler module of the Java Interpreter.

Author: Albert Wu

*----- GENERAL -----*
All interface functions and classes can be imported from the file
compile_eval.py


*----- CONTENTS -----*
- Interface
    - load
    - Variable
    - Method
    - ClassObj
- Testing
    - Suite 1
    - Interactive
    

*----- INTERFACE -----*
load(src)
    TYPE:       function
    FUNCTION:   Compiles a file of Java source code (not limited to 
                .java
                files).
    OUTPUT:     The output is a dictionary of ClassObj objects.
    PURPOSE:    Intended to process command line arguments in the Java
                interpreter, specifically to load a Java source file.
    ERRORS:     IOError        -- if the file at SRC is not found
                AssertionError -- if parsed input does not contain
                                  classes
    NOTES:      None

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
    METHODS:    self. __str__()
                    returns human-readable format as string
    NOTES:      None


*----- TESTING -----*
Suite 1
    TO CALL:    from command line:
                    python3 compile_eval.py -t

Interactive
    TO CALL:    from command line:
                    python3 compile_eval.py
