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
from compiler.compile_parse import read_line, read_statement



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
        assert cls.type == 'class', 'not a class'
        classes[cls['name']] = ClassObj(cls)
    return classes


###################
# DATA STRUCTURES #
###################

class Variable:
    """Wrapper class for variable definitions."""
    def __init__(self, name, datatype, static=False, private=False):
        self.name = name
        self.type = datatype
        self.static = static
        self.private = private
        self.value = None

    def __str__(self):
        return "{private} {type} {name}: {value}".format(
                private='private' if self.private else '',
                type=self.type,
                name=self.name,
                value=self.value)

class Method:
    """Wrapper class for method definitions. By definition, a 
    constructor is a Method whose name and datatype are None."""
    def __init__(self, name, datatype, args, body):
        self.name = name
        self.type = datatype
        self.args = []
        for arg in args:
            self.args.append(Variable(arg[1], arg[0]))
        self.body = body

    def is_constructor(self):
        """Returns True if self is a constructor, False otherwise."""
        return not self.name and not self.type

    def __str__(self):
        if self.is_constructor():
            s = "("
        else:
            s = "{type} {name}(".format(type=self.type, name=self.name)
        for arg in self.args:
            s += "{}, ".format(arg.type)
        return s[:-2] + ")"


class ClassObj:
    """Representation of a Java class.

    DESCRIPTION:
    All information of the Java class will be processed upon
    initialization. The body of the class will be sorted by statement
    type, and then placed into correct dictionaries.
    """
    def __init__(self, cls):
        """Constructor. CLS should be a Statement object of type
        'class'.
        """
        assert cls.type == 'class', 'not a class'
        self.name = cls['name'] 
        self.private = cls['private']
        self.superclass = cls['super'] if cls['super'] else 'Object'
        self.instance_attr = {} 
        self.methods = {}      
        self.constructors = {} 
        self.eval_class(cls)

    def eval_class(self, cls):
        """Subroutine that processes the contents of the class.

        ARGUMENTS:
        cls -- a Statement object, guaranteed to be of type 'class'
        """
        cls_name = self.name
        for expr in cls['body']:
            op = expr.type
            if op == 'declare':
                self.eval_declare(expr)
            elif op == 'assign':
                self.eval_assign(expr)
            elif op == 'method':
                self.eval_method(expr)
            elif op == 'constructor':
                self.eval_constructor(expr)

    ###############
    # SUBROUTINES #
    ###############
    
    def eval_declare(self, expr):
        """Subroutine for declaring instance variables.

        ARGUMENTS:
        expr -- a Statement object, guaranteed to be of type 'declare'

        RAISES:
        SyntaxError -- if the identifier has already been defined
        """
        if expr['name'] in self.instance_attr:
            raise SyntaxError(expr['name'] + ' already defined')
        self.instance_attr[expr['name']] = Variable(expr['name'], 
                                                    expr['type'], 
                                                    expr['static'],
                                                    expr['private'])

    def eval_assign(self, expr):
        """Subroutine for assigning values to variables.

        ARGUMENTS:
        expr -- a Statement object, guaranteed to be of type 'assign'

        RAISES:
        SyntaxError -- if the identifier has not been defined
        """
        if expr['name'] not in self.instance_attr:
            raise SyntaxError(expr['name'] + ' not defined')
        self.instance_attr[expr['name']].value = expr['value']

    def eval_method(self,expr):
        """Subroutine for defining methods.

        DESCRIPTION:
        Method overloading is handled by making the key to the
        METHODS dictionary tuples of (name, num_arguments). A method
        with a certain number of arguments can only be defined twice.

        RAISES:
        SyntaxError -- if method with that many args has already been
                       defined
        """
        key = (expr['name'], len(expr['args']))
        if key in self.methods:
            raise SyntaxError(expr['name'] + ' has already been ' + \
                              'defined with {} arguments'.format(
                                  len(expr['args'])))
        self.methods[(expr['name'], len(expr['args']))] = \
                Method(expr['name'],
                       expr['type'],
                       expr['args'],
                       expr['body'])

    def eval_constructor(self, expr):
        """Subroutine for defining constructors.

        DESCRIPTION:
        Constructors are represented as Method objects whose name
        and type attributes are None.

        RAISES:
        TypeError -- a constructor name that doesn't match the class
                     name
        """
        if self.name != expr['name']:
            raise TypeError("Constructor does not match class")
        self.constructors[len(expr['args'])] = Method(None,
                                                      None,
                                                      expr['args'],
                                                      expr['body'])

    def __str__(self):
        s = "class {}:\n".format(self.name)
        s += "\tprivate: {}\n".format(self.private)
        s += "\tsuper: {}\n".format(self.superclass)
        s += "\tInstance Attrs:\n"
        for var in self.instance_attr.values():
            s += "\t\t{}\n".format(var)
        s += "\tConstructors:\n"
        for var in self.constructors.values():
            s += "\t\t{}\n".format(var)
        s += "\tMethods:\n"
        for var in self.methods.values():
            s += "\t\t{}\n".format(var)
        return s


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
                print(ClassObj(cls))

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-t':
        test1()
    repl()

