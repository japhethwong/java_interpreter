This is the README for the compiler module of the Java Interpreter.

Author: Albert Wu

*----- GENERAL -----*
All interface functions and classes can be imported from the file
compile_eval.py


*----- CONTENTS -----*
- Interface
    - load
- Testing
    - Parser
        - parse_test
        - Interactive
    - Evaluator
        - Interactive
        - .java files
    

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

