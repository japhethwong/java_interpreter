"""
parse_test.py

Testing harness for compile_parse.py

Authors: Albert Wu

This file is designed to run on python3
"""

from compile_parse import *
from buffer import Buffer

#############
# Statement #
#############

def assert_error(src, error_type=BaseException):
    """Subroutine that asserts that SRC, when evaluated, produces the
    specified ERROR_TYPE.

    ARGUMENTS:
    src        -- string, passed into eval
    error_type -- Python exception
    """
    try:
        result = eval(src)
    except error_type:
        pass
    else:
        raise AssertionError(str(error_type) + \
                " expected, got {}".format(result))

def assert_equal(actual, expected):
    """Subroutine that asserts that the ACTUAL value is equal to the
    EXPECTED value.
    """
    if expected != actual:
        raise AssertionError('should be {}, not {}'.format(expected,
            actual))


def statement_test():
    print("*---- Statement Test ----*")

    print("  --- __init__ ---")
    s = Statement(CLASS)
    assert_equal(s.type, CLASS)
    s = Statement(METHOD, name='foo', type='type')
    assert_equal(s.type, METHOD)

    print("  --- __getitem__ ---")
    assert_equal(s['name'], 'foo')
    assert_equal(s['type'], 'type')

    print("  --- __setitem__ ---")
    s['name'] = 'garply'
    assert_equal(s['name'], 'garply')
    s['super'] = 'Example'
    assert_equal(s['super'], 'Example')

    print("All tests passed!\n")


def validate_name_test():
    print("*---- validate_name Test ----*")

    print("  --- valid identifiers ---")
    validate_name('hello')
    validate_name('x')
    validate_name('foo')
    validate_name('hello_world93')

    print("  --- invalid identifiers ---")
    assert_error("validate_name('__init__')")
    assert_error("validate_name('hyphen-here')")
    assert_error("validate_name('space here')")
    assert_error("validate_name('9gag')")
    assert_error("validate_name('$jquery')")

    print("All tests passed!\n")

def read_class_test():
    print("*---- read_class Test ----*")

    print("  --- valid classes ---")
    s = read_class(False, Buffer("Ex {}"))
    assert_equal(s.type, CLASS)
    assert_equal(s['name'], 'Ex')
    assert_equal(s['super'], 'Object')
    assert_equal(s['body'], [])
    assert_equal(s['private'], False)

    s = read_class(False, Buffer("Ex extends B{}"))
    assert_equal(s.type, CLASS)
    assert_equal(s['name'], 'Ex')
    assert_equal(s['super'], 'B')
    assert_equal(s['body'], [])
    assert_equal(s['private'], False)

    s = read_class(True, Buffer("Ex extends B{}"))
    assert_equal(s.type, CLASS)
    assert_equal(s['name'], 'Ex')
    assert_equal(s['super'], 'B')
    assert_equal(s['body'], [])
    assert_equal(s['private'], True)

    s = read_class(False, Buffer("Ex{ int x;}"))
    assert_equal(s.type, CLASS)
    assert_equal(s['name'], 'Ex')
    assert_equal(s['super'], 'Object')
    assert_equal(len(s['body']), 1)
    assert_equal(s['private'], False)

    print("  --- invalid classes ---")
    assert_error("""read_class(False, Buffer("Ex }"))""")
    assert_error("""read_class(False, Buffer("private Ex {}"))""")
    assert_error("""read_class(False, Buffer("Ex hello {}"))""")
    assert_error("""read_class(False, Buffer("Ex extends {}"))""")
    assert_error("""read_class(False, Buffer("9gag {}"))""")
    assert_error("""read_class(False, Buffer("Ex() {}"))""")

    print('All tests passed!\n')


def read_declare_test():
    print("*---- read_declare Test ----*")

    print("  --- valid statements ---")
    s = read_declare(False, False, 'int', Buffer("x;"))
    assert_equal(s.type, VARIABLE)
    assert_equal(s['name'], 'x')
    assert_equal(s['datatype'], 'int')
    assert_equal(s['private'], False)
    assert_equal(s['static'], False)

    s = read_declare(True, False, 'String', Buffer("helllo;"))
    assert_equal(s.type, VARIABLE)
    assert_equal(s['name'], 'helllo')
    assert_equal(s['datatype'], 'String')
    assert_equal(s['private'], True)
    assert_equal(s['static'], False)

    s = read_declare(False, True, 'double', Buffer("CamelCase;"))
    assert_equal(s.type, VARIABLE)
    assert_equal(s['name'], 'CamelCase')
    assert_equal(s['datatype'], 'double')
    assert_equal(s['private'], False)
    assert_equal(s['static'], True)

    s = read_declare(False, False, 'Bob', Buffer("under_score;"))
    assert_equal(s.type, VARIABLE)
    assert_equal(s['name'], 'under_score')
    assert_equal(s['datatype'], 'Bob')
    assert_equal(s['private'], False)
    assert_equal(s['static'], False)

    s = read_declare(False, False, 'Bob', Buffer("x, y, z;"))
    assert_equal(s.type, VARIABLE)
    assert_equal(s['name'], 'x')
    assert_equal(s['datatype'], 'Bob')
    assert_equal(s['private'], False)
    assert_equal(s['static'], False)

    print("  --- invalid statements ---")
    assert_error("""read_declare(False, False, 'int', Buffer("hello world;"))""")
    assert_error("""read_declare(False, False, 'int', Buffer("9gag;"))""")
    assert_error("""read_declare(False, False, 'int', Buffer("3;"))""")
    assert_error("""read_declare(False, False, 'int', Buffer("'bam';"))""")
    assert_error("""read_declare(False, False, 'int', Buffer("hy-phen;"))""")

    print('All tests passed!\n')


def read_assign_test():
    print("*---- read_assign Test ----*")

    print("  --- valid statements ---")
    s = read_assign('x', Buffer("3;"))
    assert_equal(s.type, ASSIGN)
    assert_equal(s['name'], 'x')
    assert_equal(s['value'], '3 ;')

    s = read_assign('foo', Buffer("3 + 4;"))
    assert_equal(s.type, ASSIGN)
    assert_equal(s['name'], 'foo')
    assert_equal(s['value'], '3 + 4 ;')

    print("  --- invalid statements ---")
    assert_error("""read_assign('9gag', Buffer("3;"))""")
    assert_error("""read_assign('hy-phen', Buffer("3;"))""")
    assert_error("""read_assign('x', Buffer(";"))""")

    print('All tests passed!\n')

def read_method_test():
    print("*---- read_method Test ----*")

    print("  --- valid statements ---")
    s = read_method(False, False, 'int', 'x', Buffer(") {}"))
    assert_equal(s.type, METHOD)
    assert_equal(s['name'], 'x')
    assert_equal(s['datatype'], 'int')
    assert_equal(s['args'], [])
    assert_equal(s['body'], '')
    assert_equal(s['private'], False)
    assert_equal(s['static'], False)

    s = read_method(True, True, 'double', 'hello', Buffer("int x) { int y = 3;}"))
    assert_equal(s.type, METHOD)
    assert_equal(s['name'], 'hello')
    assert_equal(s['datatype'], 'double')
    assert_equal(s['args'], [('int', 'x')])
    assert_equal(s['body'], 'int y = 3 ;')
    assert_equal(s['private'], True)
    assert_equal(s['static'], True)

    s = read_method(True, True, 'Bob', 'y', Buffer("int x, String y) {}"))
    assert_equal(s.type, METHOD)
    assert_equal(s['name'], 'y')
    assert_equal(s['datatype'], 'Bob')
    assert_equal(s['args'], [('int', 'x'), ('String', 'y')])
    assert_equal(s['body'], '')
    assert_equal(s['private'], True)
    assert_equal(s['static'], True)

    print("  --- invalid statements ---")
    assert_error("""read_method(False, False, 'int', '9gag', Buffer("){}"))""")
    assert_error("""read_method(False, False, 'int', 'hy-phen', Buffer("){}"))""")
    assert_error("""read_method(False, False, 'int', 'x', Buffer("x, y){}"))""")
    assert_error("""read_method(False, False, 'int', 'x', Buffer("int x double, y){}"))""")
    assert_error("""read_method(False, False, 'int', 'x', Buffer(")(){}"))""")
    assert_error("""read_method(False, False, 'int', 'x', Buffer("}()"))""")

    print('All tests passed!\n')

def general_test():
    print("*---- General Tests ----*")

    assert_error("""read_statement(Buffer("class Ex { ; }))""")
    assert_error("""read_statement(Buffer("class Ex { int; }"))""")
    assert_error("""read_statement(Buffer("class Ex { int x,; }"))""")
    assert_error("""read_statement(Buffer("class Ex { int -x,; }"))""")
    assert_error("""read_statement(Buffer("class Ex { static private int -x,; }"))""")

    print('All tests passed!\n')
    
if __name__ == '__main__':
    statement_test()
    validate_name_test()
    read_class_test()
    read_declare_test()
    #read_assign_test()
    read_method_test()
    general_test()

