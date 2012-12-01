#! /usr/bin/python3

import re

MODIFIERS = ('public', 'protected', 'private')
DELIMS = ('{', '}',
          '(', ')',
          '[', ']',
          '=', ';', ',')


def tokenize(src):
    """Tokenizes an input string.

    >>> tokenize("class Ex { int x = 4; }")
    ['class', 'Ex', '{', 'int', 'x', '=', '4', ';', '}']
    >>> tokenize("int x() {}")
    ['int', 'x', '(', ')', '{', '}']
    """

    for delim in DELIMS:
        src = src.replace(delim, ' ' + delim + ' ')
    return src.split()


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
    val = tokens.pop(0)
    is_private = False
    if val in MODIFIERS:
        is_private = val == 'private'
        val = tokens.pop(0)

    is_static = False
    if val == 'static':
        is_static = True
        val = tokens.pop(0)
        
    if val == 'class':
        return read_class(is_private, tokens)
    elif tokens[0] == '=':
        # val is a field name
        tokens.pop(0)
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
    name = tokens.pop(0)
    validate_name(name)
    superclass = None
    if tokens[0] == 'extends':
        tokens.pop(0)
        superclass = tokens.pop(0)
        validate_name(superclass)
    if tokens[0] != '{':
        raise SyntaxError('expected {')
    tokens.pop(0)
    exp = []
    while tokens and tokens[0] != '}':
        exp.append(read_statement(tokens))
    if not tokens:
        raise SyntaxError('expected }')
    else:
        tokens.pop(0)
        return {'op':       'class', 
                'name':     name, 
                'body':     exp,
                'super':    superclass,
                'private':  is_private}

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
    name = tokens.pop(0)
    if name == '(':
        if is_static:
            raise SyntaxError("Constructor can't be static")
        return read_constructor(is_private, datatype, tokens)

    validate_name(name)
    if tokens[0] == ';':
        tokens.pop(0)
    elif tokens[0] == '=':
        tokens.insert(0, name)
    elif tokens[0] == '(':
        tokens.pop(0)
        return read_method(is_private, is_static, datatype, 
                           name, tokens)
    return {'op':      'declare', 
            'name':    name, 
            'type':    datatype,
            'private': is_private,
            'static':  is_static}

def read_assign(name, tokens):
    """Reads a complete assignment statement."""
    value = []
    while tokens[0] != ';':
        value.append(tokens.pop(0))
    value.append(tokens.pop(0))
    return {'op': 'assign', 'name': name, 'value': " ".join(value)}

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

    return {'op':       'method', 
            'name':     name, 
            'type':     datatype,
            'args':     args, 
            'body':     body,
            'private':  is_private,
            'static':   is_static }
    
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
    return {'op':       'constructor',
            'name':     datatype,
            'args':     args,
            'body':     body,
            'private':  is_private }

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
    if tokens[0] != ')':
        validate_name(tokens[0])
        validate_name(tokens[1])
        args.append((tokens.pop(0), tokens.pop(0)))
    while tokens[0] == ',':
        tokens.pop(0)
        validate_name(tokens[0])
        validate_name(tokens[1])
        args.append((tokens.pop(0), tokens.pop(0)))
    if tokens[0] != ')' or tokens[1] != '{':
        raise SyntaxError("method declaration is invalid")
    tokens.pop(0); tokens.pop(0)
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
        val = tokens.pop(0)
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
    statements, line = [], tokenize(line)
    while line:
        statements.append(read_statement(line))
    return statements


def repl():
    """For testing purposes."""
    while True:
        line = input("Parse> ")
        print(read_line(line))

if __name__ == '__main__':
    repl()

def test_read_statement():
    test1 = read_statement(tokenize('class Ex {}'))
    assert test1['op'] == 'class', 'test1 failed'
    assert test1['name'] == 'Ex', 'test1 failed'
    assert test1['body'] == [], 'test1 failed'

    test2 = read_statement(tokenize('int x;'))
    assert test2['op'] ==  'declare', 'test2 failed'
    assert test2['name'] == 'x', 'test2 failed'
    assert test2['type'] == 'int', 'test2 failed'

    test3 = read_statement(tokenize('x = 4;'))
    assert test3['op'] == 'assign', 'test3 failed'
    assert test3['name'] == 'x', 'test3 failed'
    assert test3['value'] == '4;', 'test3 failed'

    test4 = read_statement(tokenize('int foo() {}'))
    assert test4['op'] == 'method', 'test4 failed'
    assert test4['name'] == 'foo', 'test4 failed'
    assert test4['args'] == [], 'test4 failed'
    assert test4['body'] == '', 'test4 failed'

