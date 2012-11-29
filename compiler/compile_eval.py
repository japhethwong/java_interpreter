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
                                   DECLARE, ASSIGN, METHOD, CONSTRUCTOR

from interface.primitives import Variable, Method, ClassObj

#####################
# INTERFACE METHODS #
#####################

def load(src):
    """Loads a .java file into the Java interpreter. This method will
    compile the Java code into a format that is understandable by
    the interpreter.
    
    RAISES:
    IOError        -- if the file at SRC is not found
    AssertionError -- if parsed input does not contain classes
    """
    try:
        f = open(src, 'r')
    except IOError as e:
        raise IOError('cannot find file {}'.format(src))
    parsed = read_line(f.read().replace("\n", " "))
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
        if op == DECLARE:
            eval_declare(cls, expr)
        elif op == ASSIGN:
            eval_assign(cls, expr)
        elif op == METHOD:
            eval_method(cls, expr)
        elif op == CONSTRUCTOR:
            eval_constructor(cls, expr)
    return cls

def eval_declare(cls, expr):
    """Subroutine for declaring instance variables.

    ARGUMENTS:
    expr -- a Statement object, guaranteed to be of type 'declare'

    RAISES:
    SyntaxError -- if the identifier has already been defined
    """
    assert expr.type == DECLARE, 'Not a valid declare: {}'.format(expr)
    var = Variable(expr['name'], expr['type'], expr['static'], expr['private'])
    cls.declare_var(var)


def eval_assign(cls, expr):
    """Subroutine for assigning values to variables.

    ARGUMENTS:
    expr -- a Statement object, guaranteed to be of type 'assign'

    RAISES:
    SyntaxError -- if the identifier has not been defined
    """
    assert expr.type == ASSIGN, 'Not a valid assign: {}'.format(expr)
    cls.assign_var(expr['name'], expr['value'])

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
    cls.declare_method(Method(expr['name'], expr['type'], expr['args'],
                              expr['body']))

def eval_constructor(cls, expr):
    """Subroutine for defining constructors.

    DESCRIPTION:
    Constructors are represented as Method objects whose name
    and type attributes are None.

    RAISES:
    TypeError -- a constructor name that doesn't match the class
                 name
    """
    assert expr.type == CONSTRUCTOR, 'Not a valid constructor: {}'.format(expr)
    cls.declare_constructor(Method(None, None, expr['args'],
                                   expr['body']))

###########
# TESTING #
###########

def test1():
    """Test suite 1"""
    print("----- Test Suite 1 -----")
    print("-- 1.1 --")
    b1 = Buffer("class Ex { int x = 3; }")
    s1 = read_statement(b1)
    c1 = ClassObj(s1)
    print(c1)

    print("-- 1.2 --")
    b2 = Buffer("class Ex { int x = 3; int x; }")
    s2 = read_statement(b2)
    try:
        c2 = ClassObj(s2)
    except SyntaxError:
        print("Raised SyntaxError -- passed\n")
    else:
        print("Did not raise SyntaxError: " + str(e)) + "\n"

    print("-- 1.3 --")
    b3 = Buffer("""class Ex { int foo(String x) {}
                double foo(String x, int y) {}  }""")
    s3 = read_statement(b3)
    c3 = ClassObj(s3)
    print(c3)


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
            classes = read_line(line)
            for cls in classes:
                print(eval_class(cls))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == '-t':
            test1()
        else:
            result = load(sys.argv[1])
            for key, value in result.items():
                print(key, value, sep='\n')
    repl()

