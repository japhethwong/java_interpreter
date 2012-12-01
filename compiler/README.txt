This is the README for the compiler module of the Java Interpreter.

Author: Albert Wu

*----- GENERAL -----*
All interface functions and classes used by other modules can be 
imported from the file compile_eval.py:

    from compiler.compile_eval import load


*----- CONTENTS -----*
- Interface
    - load_str
    - load_file
- Testing
    - Parser
        - parse_test
        - Interactive
    - Evaluator
        - Interactive
        - .java files
    

*----- INTERFACE -----*
load_str(src)
    TYPE:       function
    FUNCTION:   Compiles a string of Java source code
    INPUT:      The input is string of Java source code
    OUTPUT:     The output is a dictionary of ClassObj objects.
    PURPOSE:    Intended to process command line arguments in the Java
                interpreter, specifically to load Java code
    ERRORS:     AssertionError -- if parsed input does not contain
                                  classes
    NOTES:      None


load_file(src)
    TYPE:       function
    FUNCTION:   Compiles a file of Java source code (not limited to 
                .java files).
    INPUT:      The input is the path of a file of Java code
    OUTPUT:     The output is a dictionary of ClassObj objects.
    PURPOSE:    Intended to process command line arguments in the Java
                interpreter, specifically to load a Java source file.
    ERRORS:     IOError        -- if the file at SRC is not found
                AssertionError -- if parsed input does not contain
                                  classes
    NOTES:      None


*----- TESTING -----*
Parser:
    parse_test:
                Contains several test suites for compile_parse. Run
                with
                    python3 parse_test.py
    Interactive:
                Test cases interactively with parser repl. Run with
                    python3 compile_parse.py

Evaluator
    Interactive:
                Test cases interactively with evaluator repl. Run with
                    python3 compile_eval.py
    .java files:
                Compiles a specified .java file. Run with
                    python3 compile_eval.py <file>.java

