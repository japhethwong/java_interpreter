#! /usr/bin/python3

"""
compile_eval.py

Evaluator for the compiler module of the Java Interpreter.
Interface documentation can be found in README.txt in the compiler
directory.

Authors: Brian Yin
         Albert Wu

This file is designed to run on python3
"""

import sys
sys.path.append(sys.path[0] + '/../')

from compiler.buffer import Buffer, PS1, interrupt
from compiler.compile_parse import read_line, read_statement, CLASS, \
                                   VARIABLE, METHOD

from interface.structures import Variable, Method, ClassObj

PS1 = 'Evaler> '

#####################
# INTERFACE METHODS #
#####################

def load_file(src):
    """Loads a .java file into the Java interpreter. This method will
    compile the Java code into a format that is understandable by
    the interpreter.

    ARGUMENTS:
    src -- a file containing Java code
    
    RAISES:
    IOError        -- if the file at SRC is not found
    AssertionError -- if parsed input does not contain classes
    """
    try:
        f = open(src, 'r')
    except IOError as e:
        raise IOError('cannot find file {}'.format(src))
    return load_str(f.read())

def load_str(src):
    """Loads a string of Java code and compiles it into a format that
    the interpreter will understand.

    ARGUMENTS:
    src -- a string of Java code

    RAISES:
    AssertionError -- if parsed input does not contain classes
    """
    parsed = read_line(src.replace('\n', ' '))
    classes = {}
    for cls in parsed:
        assert cls.type == CLASS, 'not a class'
        classes[cls['name']] = eval_class(cls)
    return classes


########################
# EVALUATION FUNCTIONS #
########################


def eval_class(stmt):
    """Subroutine that processes the contents of the class.

    ARGUMENTS:
    cls -- a Statement object, guaranteed to be of type 'class'
    """
    assert stmt.type == CLASS, 'Not a valid class: {}'.format(stmt)
    cls = ClassObj(stmt['name'])
    cls.private(stmt['private'])
    cls.superclass(stmt['super'])
    for expr in stmt['body']:
        op = expr.type
        if op == VARIABLE:
            eval_variable(cls, expr)
        elif op == METHOD:
            eval_method(cls, expr)
    return cls

def eval_variable(cls, expr):
    """Subroutine for declaring instance variables.

    ARGUMENTS:
    expr -- a Statement object, guaranteed to be of type 'declare'

    RAISES:
    SyntaxError -- if the identifier has already been defined
    """
    assert expr.type == VARIABLE, 'Not a valid var: {}'.format(expr)
    var = Variable(expr['datatype'], expr['name'], expr['value'], 
            expr['static'], expr['private'])
    cls.declare_var(var)


def eval_method(cls, expr):
    """Subroutine for defining methods.

    DESCRIPTION:
    Method overloading is handled by making the key to the
    METHODS dictionary tuples of (name, num_arguments). A method
    with a certain number of arguments can only be defined twice.

    RAISES:
    SyntaxError -- if method with that many args has already been
                   defined
    """
    assert expr.type == METHOD, 'Not a valid method: {}'.format(expr)
    is_constructor = expr['name'] == cls.name;
    cls.declare_method(Method(None if is_constructor else expr['name'],
        expr['datatype'], expr['args'], expr['body']))


################
# COMMAND LINE #
################

def repl():
    """For interactive testing purposes"""
    while True:
        try:
            line = input(PS1)
        except KeyboardInterrupt:
            print(interrupt)
            exit(0)
        else:
            try:
                classes = read_line(line)
            except BaseException as e:
                print(e)
            else:
                for cls in classes:
                    print(eval_class(cls))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '-t':
            test1()
        else:
            result = load_file(sys.argv[1])
            for key, value in result.items():
                print(key, value, sep='\n')
    repl()

