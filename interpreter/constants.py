"""constants"""
DELIMITERS = {'(': ')', '{': '}'}
JAVA_TO_PYTHON = {'||': 'or', '&&': 'and', 'true': 'True', 'false': 'False'}
PYTHON_TO_JAVA = {val: key for key, val in JAVA_TO_PYTHON.items()}
THING_TO_REPLACE = 'SIEHRIESHRESIHRESIRHES'
INITIALIZE_VALS = {'int': 0, }
CONTINUE_KEYWORDS = ['for', 'while', 'if']

INT = 'int'
FLOAT = 'float'
DOUBLE = 'double'
STRING = 'String'
BOOLEAN = 'boolean'
CHAR = 'char'
SHORT = 'short'
LONG = 'long'

TYPES = [INT, FLOAT, DOUBLE, STRING, BOOLEAN, CHAR, SHORT, LONG]
INT_TYPES = [INT, SHORT, LONG]
FLOAT_TYPES = [FLOAT, DOUBLE]
STRING_TYPES = [CHAR, STRING]
KEYWORDS = TYPES + ['return', 'while', 'for'] + [key for key in JAVA_TO_PYTHON]+ [val for val in JAVA_TO_PYTHON.values()]

    
UNDEFINED_PARAM = None

