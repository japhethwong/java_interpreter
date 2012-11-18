#! /usr/bin/python3

import re

def tokenize(src):
    """Tokenizes an input string.

    >>> tokenize("class Ex { int x = 4; }")
    ['class', 'Ex', '{', 'int', 'x', '=', '4', ';', '}']
    >>> tokenize("int x() {}")
    ['int', 'x', '(', ')', '{', '}']
    """

    src = src.replace("{", " { ")
    src = src.replace("}", " } ")
    src = src.replace("(", " ( ")
    src = src.replace(")", " ) ")
    src = src.replace("=", " = ")
    src = src.replace(";", " ; ")
    src = src.replace(",", " , ")
    return src.split()

modifiers = ('public', 'protected', 'private')

def validate_name(name):
    """Determines if NAME is a valid identifier. 
    
    A valid identifier is defined as a string whose first character is
    an upper or lower case letter. The rest of the name can be any 
    alphanumeric character: [a-zA-Z0-9_].

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
    if val in modifiers:
        pass
    elif val == 'class':
        return read_class(tokens)
    elif tokens[0] == '=':
        # val is a field name
        tokens.pop(0)
        return read_assign(val, tokens)
    else:
        # val is a type
        return read_declare(val, tokens)

def read_class(tokens):
    """Reads a complete class expression."""
    name = tokens.pop(0)
    validate_name(name)
    if tokens[0] != '{':
        raise SyntaxError('expected {')
    tokens.pop(0)
    exp = []
    while tokens and tokens[0] != '}':
        exp.append(read_statement(tokens))
        print(tokens)
    if not tokens:
        raise SyntaxError('expected }')
    else:
        tokens.pop(0)
        return {'op': 'class', 'name': name, 'body': exp}

def read_declare(datatype, tokens):
    name = tokens.pop(0)
    validate_name(name)
    if tokens[0] == ';':
        tokens.pop(0)
    elif tokens[0] == '=':
        tokens.insert(0, name)
    elif tokens[0] == '(':
        tokens.pop(0)
        return read_method(name, datatype, tokens)
    return {'op': 'declare', 'name': name, 'type': datatype}

def read_assign(name, tokens):
    value = ''
    while tokens[0] != ';':
        value += tokens.pop(0)
    tokens.pop(0)
    return {'op': 'assign', 'name': name, 'value': value}

def read_method(name, datatype, tokens):
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

    body, parens = '', 1
    while parens:
        val = tokens.pop(0)
        if val == '{':
            parens += 1
        elif val == '}':
            parens -= 1
        body += val
    body = body[:-1]
    return {'op': 'method', 'name': name, 'type': datatype,
            'args': args, 'body': body}

def repl():
    while True:
        line = input("> ")
        statements, line = [], tokenize(line)
        while line:
            statements.append(read_statement(line))
        print(statements)

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
    assert test3['value'] == '4', 'test3 failed'

    test4 = read_statement(tokenize('int foo() {}'))
    assert test4['op'] == 'method', 'test4 failed'
    assert test4['name'] == 'foo', 'test4 failed'
    assert test4['args'] == [], 'test4 failed'
    assert test4['body'] == '', 'test4 failed'

