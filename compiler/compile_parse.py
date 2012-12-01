#! /usr/bin/python3

"""
compile_parse.py

Parser for the compiler module of the Java Interpreter.
Interface documentation can be found in README.txt in the compiler
directory.

Authors: Albert Wu

This file is designed to run on python3
"""

import sys
sys.path.append(sys.path[0] + '/../')

import re
from compiler.buffer import Buffer, PS1, interrupt
from interface.exceptions import CompileException

PS1 = "Parser> "

MODIFIERS = ('public', 'protected', 'private')
CLASS = 'class'
VARIABLE = 'variable'
METHOD = 'method'

###################
# DATA STRUCTURES #
###################

class Statement:
    """A wrapper class for Java statements.

    DESCRIPTION:
    Each Statement object has a 'type', which can be one of the
    following:
        - CLASS
        - VARIABLE
        - METHOD
    The 'type' can be referenced as an instance attribute (e.g. 
    'stmt.type').

    Statement objects can be indexed like dictionaries -- through keys
    and values.
    """
    def __init__(self, stmt_type, **kargs):
        """Constructor.

        ARGUMENTS:
        stmt_type -- the type of statement
        kargs     -- keyword arguments
        """
        self._type = stmt_type
        self.kargs = kargs

    @property
    def type(self):
        return self._type

    def __getitem__(self, key):
        return self.kargs[key]

    def __setitem__(self, key, value):
        self.kargs[key] = value

    def __eq__(self, other):
        return self.type == other.type and \
               self.kargs == other.kargs

    def __str__(self):
        s = self.type + " statement:\n\t"
        for key in self.kargs:
            s += key + ": " + str(self.kargs[key]) + "\n\t"
        return s 

    def __repr__(self):
        return "Statement({}, {})".format(repr(self.type), 
                                            repr(self.kargs))


##########
# PARSER #
##########

def validate_name(name):
    """Determines if NAME is a valid identifier. 
    
    DESCRIPTION:
    A valid identifier is defined as a string whose first character is
    an upper or lower case letter. The rest of the name can be any 
    alphanumeric character: [a-zA-Z0-9_].

    ARGUMENTS:
    name -- a single token

    >>> validate_name('hello')
    >>> validate_name('hello world')
    Traceback (most recent call last):
      ...
    SyntaxError: invalid identifier: 'hello world'
    >>> validate_name('h3110')
    >>> validate_name('9h3110')
    Traceback (most recent call last):
      ...
    SyntaxError: invalid identifier: '9h3110'
    """
    if not re.match("[a-zA-Z][\w]*$", name):
        raise CompileException("invalid identifier: '{}'".format(name))

def is_number(token):
    """Returns True if token can be converted to an int."""
    try:
        int(token)
    except ValueError:
        return False
    else:
        return True
    
def read_statement(tokens):
    """Reads a complete Java statement and pops it off TOKENS.

    DESCRIPTION:
    A complete Java statement is defined as one of the following:
    - a class declaration
        "class Ex { // body of class }"
    - a field declaration
        "int x;"
    - a field assignment
        "int x = 4 + 3"
    - a method declaration
        "int example(arg) { // body of method }"
    - a constructor declaration
        "Ex(String x) { // body of constructor }"

    RETURNS:
    A Statement object:
    - Class:
        type: CLASS, name: string, body: list of Statements
    - Field Declaration:
        type: VARIABLE, name: string, type: string, value: None
    - Field Assignement:
        type: VARIABLE, name: string, type: string, 
        value: Statement(EXPR)
    - Method Declaration:
        type: METHOD, name: string, datatype: string,
        args:  list of pairs, body: list of Statements
    - Constructor Declaration:
        type: METHOD, name: string, datatype: None,
        args:  list of pairs, body: list of Statements
    """
    val = tokens.pop()

    is_private = False
    if val.lower() in MODIFIERS:
        is_private = val == 'private'
        val = tokens.pop()

    is_static = False
    if val == 'static':
        is_static = True
        val = tokens.pop()
        
    if val == 'class':
        if is_static:
            raise CompileException('invalid modifier for class: static')
        return read_class(is_private, tokens)
    else:
        # val is expected to be a type declaration
        validate_name(val)
        return read_declare(is_private, is_static, val, tokens)

def read_class(is_private, tokens):
    """Reads a complete class declaration.
    
    DESCRIPTION:
    A valid class declaration has the following syntax:
        [modifier] class [name] [extends superclass] { [body] }

    ARGUMENTS:
    is_private -- True if class is private, False otherwise
    tokens     -- a Buffer of tokens

    RETURNS:
    A Statement object with the following attributes:
        type:   CLASS
        name:   string
        body:   list of Statements
        super:  string, 'Object' if none provided
        private: boolean
    """
    name = tokens.pop()
    validate_name(name)
    superclass = 'Object' # TODO don't hardcode this?
    if tokens.current() == 'extends':
        tokens.pop()
        superclass = tokens.pop()
        validate_name(superclass)
    if tokens.pop() != '{':
        raise SyntaxError('expected {')
    exp = []
    while tokens.current() != '}':
        exp.append(read_statement(tokens))
    tokens.pop()
    return Statement(CLASS, name=name, body=exp, super=superclass,
                    private=is_private)

def read_declare(is_private, is_static, datatype, tokens):
    """Reads a complete field declaration.
    
    DESCRIPTION:
    The following are valid declarations:
        Variable:
            [modifier] [static] [type] [name] ;
            [modifier] [static] [type] [name] = [value] ;
            [modifier] [static] [type] [name1], [name2], ...;
            [modifier] [static] [type] [name1] = [value1], ...;
        Method:
            [modifier] [static] [type] [name] ( [type1] [arg1], ...) {}
        Constructor:
            [modifier] [static] [class name] ( [type1] [arg1], ...) {}

    ARGUMENTS:
    is_private -- True if field is private, False otherwise
    is_static  -- True if the field is static, False otherwise
    datatype   -- a string, the type of variable
    tokens     -- Buffer of tokens

    RETURNS:
    The following dictionary:
    { 'op':      DECLARE
      'name':    name, string
      'type':    type, string
      'private': True if field is private, False otherwise
      'static':  True if field is static, False otherwise
      }
    """
    name = tokens.pop()
    if name == '(':
        # expect it to be a constructor
        return read_method(is_private, is_static, None, datatype, 
                tokens)
    validate_name(name)
    
    next_token = tokens.pop()
    if next_token == '(':
        return read_method(is_private, is_static, datatype, 
                           name, tokens)
    elif next_token == '=':
        result = read_assign(is_private, is_static, datatype, name, 
                            tokens)
        next_token = tokens.pop()
    else:
        result = Statement(VARIABLE, name=name, datatype=datatype, 
                private=is_private, static=is_static, value=None)

    if next_token == ',':
        tokens.prepend(datatype)
        if is_static:
            tokens.prepend('static')
        if is_private:
            tokens.prepend('private')
        return result
    elif next_token == ';':
        return result
    else:
        raise SyntaxError("Unexpected token: {}".format(next_token))

def read_assign(is_private, is_static, datatype, name, tokens):
    """Reads a complete assignment statement.
    
    DESCRIPTION:
    TOKENS is assumed to be begin with the expression on the right
    side of an '=' sign. READ_ASSIGN will parse the expression until
    it reaches a ',' or a ';', but will not pop off the delimiter.
    """
    validate_name(name)
    value = read_expr(tokens)
    return Statement(VARIABLE, datatype=datatype, name=name, 
            value=value, private=is_private, static=is_static)

def read_expr(tokens):
    """Reads an expression.

    3 + 4
    3 + 4 * 5
    (3 + 4) * 5
    3 + x
    x + x
    x.method()
    x.method(arg)
    x + y.method(arg)
    Ex(arg)
    """
    result = []
    while tokens.current() != ';' and tokens.current() != ',':
        next_token = tokens.pop()
        if result and is_number(result[-1]) and next_token == '.':
            decimal = tokens.current()
            if is_number(decimal):
                result[-1] = result[-1] + next_token + tokens.pop()
                continue
            elif decimal == ';' or decimal == ',':
                result[-1] = result[-1] + next_token
                break
            else:
                raise CompileException("Invalid decimal")
        result.append(next_token)
    return " ".join(result)



def read_method(is_private, is_static, datatype, name, tokens):
    """Reads a method declaration.
    
    DESCRIPTION:
    A valid method declaration has the following syntax:
        [modifier] [static] [type] [name] ( [type1] [arg1], ...) 
            { [body] }

    ARGUMENTS:
    is_private -- True if the method is private, False otherwise
    is_static  -- True if the method is static, False otherwise
    datatype   -- type, string
    name       -- name, string
    tokens     -- Buffer of tokens

    RETURNS:
    A Statement object with the following attributes:
        type:       CLASS
        name:       string, name of the method, or name of class if 
                    constructor
        datatype    string if method, None if constructor
        args        list of pairs
        body        a single string
        private     True if method is private
        static      True if method is static
    """
    validate_name(name)
    args = parse_args(tokens)
    body = parse_body(tokens)
    return Statement(METHOD, name=name, datatype=datatype, args=args,
                     body=body, private=is_private, static=is_static)
    
def parse_args(tokens):
    """Subroutine used to parse arguments.

    DESCRIPTION:
    A valid list of arguments has the following syntax:
        [type1] [param1], [type2] [param2], ...

    ARGUMENTS:
    tokens -- list of tokens. PARSE_ARGS assumes the opening paren '('
              has already been popped off, so tokens[0] != '('

    RETURNS:
    A list of type/name pairs (tuples)
    """
    args = []
    if tokens.current() != ')':
        validate_name(tokens.current())
        datatype = tokens.pop()
        validate_name(tokens.current())
        args.append((datatype, tokens.pop()))
    while tokens.current() == ',':
        tokens.pop()
        validate_name(tokens.current())
        datatype = tokens.pop()
        validate_name(tokens.current())
        args.append((datatype, tokens.pop()))
    if tokens.pop() != ')':
        raise SyntaxError("expected )")
    if tokens.pop() != '{':
        raise SyntaxError("expected {")
    return args

def parse_body(tokens):
    """Subroutine used to parse the body of a method or a constructor.

    DESCRIPTION:
    A valid body is any string that contains any characters.

    ARGUMENTS:
    tokens -- list of tokens. PARSE_BODY assumes the opening brace '{'
              has already been popped off, so tokens[0] != '{'

    RETURNS:
    A single string -- this is NOT guaranteed to contain well-formed
    Java expressions. This is left as a job for the main interpreter.
    """
    body, braces = [], 1
    while braces:
        val = tokens.pop()
        if val == '{':
            braces += 1
        elif val == '}':
            braces -= 1
        body.append(val)
    body = " ".join(body[:-1])
    return body


#############
# INTERFACE #
#############

def read_line(line):
    """Main method to call for the compiler's parser.

    READ_LINE parses a single line of java code.
    """
    statements, line = [], Buffer(line)
    while not line.empty:
        statements.append(read_statement(line))
    return statements


def repl():
    """For testing purposes."""
    while True:
        try:
            line = input(PS1)
        except KeyboardInterrupt:
            print(interrupt)
            exit(0)
        else:
            try:
                result = read_line(line)
            except BaseException as e:
                print(e)
            else:
                for stmt in result:
                    print(stmt)

def load(path):
    with open(path, 'r') as f:
        return read_line(f.read().replace('\n', ' '))
    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(load(sys.argv[1]))
    repl()

