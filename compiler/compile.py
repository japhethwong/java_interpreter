#! /usr/bin/python3


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
    return tokenize.split()

modifiers = ('public', 'protected', 'private')

def read(tokens):
    val = tokens.pop(0)
    if val in modifiers:
        pass
    elif val == 'class':
        name = tokens.pop(0)
        validate_identifier(name)
        if tokens[0] != '{':
            raise SyntaxError('expected {')
        tokens.pop(0)
        read(

def read_class(tokens):
    name = tokens.pop(0)
    validate_identifier(name)
    if tokens[0] != '{':
        raise SyntaxError('expected {')
    tokens.pop(0)
    exp = cur = Pair('class', Pair(name, nil))
    while tokens and tokens[0] != '}':
        cur.second = Pair(read(tokens), nil)
        cur = cur.second
    if not tokens:
        raise SyntaxError('expected }')
    else:
        return cur
