"""
buffer.py

Buffer data structure for the compiler module of the Java 
Interpreter. 

Authors: Albert Wu

This file is designed to run on python3
"""

DELIMS = ('{', '}',
          '(', ')',
          '[', ']',
          '=', ';', ',')
PS1 = 'Jp> '
PS2 = '    '
interrupt = '\nExiting compiler'

class Buffer:
    def __init__(self, line):
        self._tokens = Buffer.tokenize(line)
        self._tokens.reverse() # more efficient

    def pop(self):
        """Removes and returns the first token in the buffer. If there
        are no more tokens, raise an IndexError.
        """
        while len(self._tokens) == 0:
            try:
                self._tokens = Buffer.tokenize(input(PS2))
            except KeyboardInterrupt:
                print(interrupt)
                exit(0)
            else:
                self._tokens.reverse()
        return self._tokens.pop()

    def current(self):
        """Returns the first token in the current buffer. If the
        buffer is empty, prompt the user for more user input.

        >>> b = Buffer('int x = 3;')
        >>> b.current()
        'int'
        >>> repr(b)
        "Buffer(['int', 'x', '=', '3', ';'])"
        """
        while len(self._tokens) == 0:
            try:
                self._tokens = Buffer.tokenize(input(PS2))
            except KeyboardInterrupt:
                print(interrupt)
                exit(0)
            else:
                self._tokens.reverse()
        return self._tokens[-1]

    def prepend(self, token):
        """Adds the token to the front of the buffer.
        
        >>> b = Buffer('int x = 3')
        >>> b.prepend('static')
        >>> b.current()
        'static'
        """
        self._tokens.append(token)

    @staticmethod
    def tokenize(line):
        """Converts a string (presumably a line of user input) into
        a list of tokens.

        >>> Buffer.tokenize("class Ex { int x = 4; }")
        ['class', 'Ex', '{', 'int', 'x', '=', '4', ';', '}']
        >>> Buffer.tokenize("int x() {}")
        ['int', 'x', '(', ')', '{', '}']
        """
        for delim in DELIMS:
            line = line.replace(delim, ' ' + delim + ' ')
        return line.split()

    @property
    def empty(self):
        """Returns True if the Buffer is empty, False otherwise."""
        return len(self._tokens) == 0

    def __str__(self):
        """Returns a human-readable representation of this Buffer.

        >>> b = Buffer('x = 4')
        >>> str(b)
        "['x', '=', '4']"
        >>> b.pop()
        'x'
        >>> str(b)
        "['=', '4']"
        """
        return str(list(reversed(self._tokens)))

    def __repr__(self):
        """Returns the repr string of this Buffer.

        >>> b = Buffer("x = 4")
        >>> repr(b)
        "Buffer(['x', '=', '4'])"
        >>> b.pop()
        'x'
        >>> repr(b)
        "Buffer(['=', '4'])"
        """
        return "Buffer(" + repr(list(reversed(self._tokens))) + ")"
    
