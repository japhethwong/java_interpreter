#! /usr/bin/python3

import re

def tokenize(src):
    """Tokenizes an input string.

    >>> tokenize("class Ex { int x = 4; }")
    ['class', 'Ex', '{', 'int' x', '=', '4', ';', '}']
    """

    src.replace("{", " { ")
    src.replace("}", " } ")
    src.replace("(", " ) ")
    src.replace("=", " = ")
    src.replace(";", " ; ")
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
         'args': list of strings, 'body': TODO}

    >>> read_statement(tokenize('class Ex {}'))
    {'op': 'class', 'name': 'Ex', 'body': []}
    >>> read_statement(tokenize('int x;'))
    {'op': 'declare', 'name': 'x', 'type': 'int'} 
    >>> read_statement(tokenize('x = 4;'))
    {'op': 'assign', 'name': 'x', 'value': '4'} 
    >>> read_statement(tokenize('int foo() {}'))
    {'op': 'method', 'name': 'foo', 'type': 'int', 'args': [], 'body': None} 
    """
    val = tokens.pop(0)
    if val in modifiers:
        pass
    elif val == 'class':
        return read_class(tokens)
    elif tokens[0] == '=':
        # val is a field name
        return read_assign(val, tokens)
    elif tokens[0] == '(':
        # val is a method name
        return read_method(val, tokens)
    else:
        # val is a type
        return read_declare(val, tokens)

def read_class(tokens):
    name = tokens.pop(0)
    validate_name(name)
    if tokens[0] != '{':
        raise SyntaxError('expected {')
    tokens.pop(0)
    exp = cur = Pair('class', Pair(name, nil))
    while tokens and tokens[0] != '}':
        cur.second = Pair(read_statement(tokens), nil)
        cur = cur.second
    if not tokens:
        raise SyntaxError('expected }')
    else:
        return cur

def read_assign(name, tokens):
    validate_identifier(name)
    return Pair('assign var', read_exp(tokens))



def repl():
    while True:
        line = input("> ")
        print(read_statement(tokenize(line)))

if __name__ == '__main__':
    repl()
