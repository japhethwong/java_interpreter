#! /usr/bin/python3

import re
import sys
from buffer import Buffer

MODIFIERS = ('public', 'protected', 'private')

class Statement:
    def __init__(self, stmt_type, **kargs):
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
        raise SyntaxError("invalid identifier: '{}'".format(name))
    
def read_statement(tokens):
    """Reads a complete Java statement and pops it off TOKENS.

    DESCRIPTION:
    A complete Java statement is defined as one of the following:
    - a class declaration
        "class Ex { // body of class }"
    - a field declaration
        "int x;"
    - a field assignment
        "x = 4 + 3"
    - a method declaration
        "int example(arg) { // body of method }"

    RETURNS:
    A dictionary with key-value pairs specific to each type of
    statement.
    - Class:
        {'op': 'class', 'name': string, 'body': list of dicts}
    - Field Declaration:
        {'op': 'declare', 'name': string, 'type': string}
    - Field Assignement:
        {'op': 'assign', 'name': string, 'value': TODO}
    - Method Declaration:
        {'op': 'method', 'name': string, 'type': string, 
         'args': list of pairs, 'body': TODO}

    >>> test_read_statement()
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
        return read_class(is_private, tokens)

    elif tokens.current() == '=':
        # val is a field name
        tokens.pop()
        return read_assign(val, tokens)
    else:
        # val is a type
        return read_declare(is_private, is_static, val, tokens)

def read_class(is_private, tokens):
    """Reads a complete class declaration.
    
    DESCRIPTION:
    A valid class declaration has the following syntax:
        [modifier] class [name] [extends superclass] { [body] }

    ARGUMENTS:
    is_private -- True if class is private, False otherwise
    tokens     -- a list of tokens

    RETURNS:
    A dictionary with the following key-value pairs:
    { 'op':      'class'
      'name':    name, string
      'body':    body, string
      'super':   superclass, string if exists, None otherwise
      'private': True if modifier is private, False otherwise
    }
    """
    name = tokens.pop()
    validate_name(name)
    superclass = None
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
    return Statement('class',
                    name=name,
                    body=exp,
                    super=superclass,
                    private=is_private)

def read_declare(is_private, is_static, datatype, tokens):
    """Reads a complete field declaration.
    
    DESCRIPTION:
    A valid field declaration has the following syntax:
        [modifier] [static] [type] [name] ;

    ARGUMENTS:
    is_private -- True if field is private, False otherwise
    datatype   -- a string, the type of variable
    tokens     -- list of tokens

    RETURNS:
    The following dictionary:
    { 'op':      'declare'
      'name':    name, string
      'type':    type, string
      'private': True if field is private, False otherwise
      'static':  True if field is static, False otherwise
      }
    """
    name = tokens.pop()
    if name == '(':
        if is_static:
            raise SyntaxError("Constructor can't be static")
        return read_constructor(is_private, datatype, tokens)

    validate_name(name)
    if tokens.current() == ';':
        tokens.pop()
    elif tokens.current() == '=':
        tokens.prepend(name)
    elif tokens.current() == '(':
        tokens.pop()
        return read_method(is_private, is_static, datatype, 
                           name, tokens)
    return Statement('declare',
                     name=name,
                     type=datatype,
                     private=is_private,
                     static=is_static)

def read_assign(name, tokens):
    """Reads a complete assignment statement."""
    value = []
    while tokens.current() != ';':
        value.append(tokens.pop())
    value.append(tokens.pop())
    return Statement('assign',
                     name=name,
                     value=" ".join(value))

def read_method(is_private, is_static, datatype, name, tokens):
    """Reads a method declaration.
    
    DESCRIPTION:
    A valid method declaration has the following syntax:
        [modifier] [static] [type] [name] ( [type1] [arg1], ...) { [body] }

    ARGUMENTS:
    is_private -- True if the method is private, False otherwise
    is_static  -- True if the method is static, False otherwise
    datatype   -- type, string
    name       -- name, string
    tokens     -- list of tokens

    RETURNS:
    The following dictionary:
    { 'op':      'method'
      'name':    name, string
      'type':    type, string
      'args':    parameters, list of pairs (tuples)
      'body':    body of method, string
      'private': True if method is private
      'static':  True if method is static
      }
    """
    args = parse_args(tokens)
    body = parse_body(tokens)
    return Statement('method',
                     name=name,
                     type=datatype,
                     args=args,
                     body=body,
                     private=is_private,
                     static=is_static)
    
def read_constructor(is_private, datatype, tokens):
    """Reads a constructor declaration.

    DESCRIPTION:
    A valid constructor declaration has the following syntax:
        [modifier] [type] ([type1] [arg1], ...) { [body] }

    ARGUMENTS:
    is_private -- True if the constructor is private, False otherwise
    datatype   -- name of the constructor
    tokens     -- list of tokens

    RETURNS:
    The following dictionary:
    { 'op':      'constructor'
      'name':    name, string (eval should check this matches class)
      'args':    args, list of pairs (tuples)
      'body':    body, string
      'private': True if constructor is private, False otherwise }
    """
    args = parse_args(tokens)
    body = parse_body(tokens)
    return Statement('constructor',
                     name=datatype,
                     args=args,
                     body=body,
                     private=is_private)

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
        validate_name(tokens.current())
        datatype = tokens.pop()
        validate_name(tokens.current())
        args.append((datatype, tokens.pop()))
    if tokens.current() != ')' and tokens.current() != '{':
        raise SyntaxError("method declaration is invalid")
    tokens.pop(); tokens.pop()
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
            line = input("Java> ")
        except KeyboardInterrupt:
            print('\nExiting parser')
            exit(0)
        else:
            print(read_line(line))

def load(path):
    with open(path, 'r') as f:
        return read_line(f.read().replace('\n', ' '))
    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(load(sys.argv[1]))
    repl()

def test_read_statement():
    test1 = read_statement(Buffer('class Ex {}'))
    assert test1.type == 'class', 'test1 failed'
    assert test1['name'] == 'Ex', 'test1 failed'
    assert test1['body'] == [], 'test1 failed'

    test2 = read_statement(Buffer('int x;'))
    assert test2.type ==  'declare', 'test2 failed'
    assert test2['name'] == 'x', 'test2 failed'
    assert test2['type'] == 'int', 'test2 failed'

    test3 = read_statement(Buffer('x = 4;'))
    assert test3.type == 'assign', 'test3 failed'
    assert test3['name'] == 'x', 'test3 failed'
    assert test3['value'] == '4 ;', 'test3 failed'

    test4 = read_statement(Buffer('int foo() {}'))
    assert test4.type == 'method', 'test4 failed'
    assert test4['name'] == 'foo', 'test4 failed'
    assert test4['args'] == [], 'test4 failed'
    assert test4['body'] == '', 'test4 failed'

