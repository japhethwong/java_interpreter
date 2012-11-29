import sys
sys.path.append(sys.path[0] + '/../')

from compiler.compile_eval import eval_class
from compiler.compile_parse import read_line 
from interface.structures import *


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

def variable_test():
    print("*---- Variable Test ----*")

    print("  --- __init__ ---")
    var = Variable('x', 'int', False, True)
    assert_equal(var.name, 'x')
    assert_equal(var.type, 'int')
    assert_equal(var.static, False)
    assert_equal(var.private, True)
    assert_equal(var.value, None)

    var = Variable('foo', 'String')
    assert_equal(var.name, 'foo')
    assert_equal(var.type, 'String')
    assert_equal(var.static, False)
    assert_equal(var.private, False)
    assert_equal(var.value, None)

    print("  --- clone ---")
    var = Variable('x', 'int', False, True)
    clone = var.clone()
    assert_equal(var == clone, False)
    assert_equal(clone.name, 'x')
    assert_equal(clone.type, 'int')
    assert_equal(clone.static, False)
    assert_equal(clone.private, True)
    assert_equal(clone.value, None)

    print('All tests passed!\n')

def method_test():
    print("*---- Method Test ----*")

    print("  --- __init__ ---")
    method = Method('foo', 'int', [], '')
    assert_equal(method.name, 'foo')
    assert_equal(method.type, 'int')
    assert_equal(method.args, [])
    assert_equal(method.body, '')
    
    method = Method('bar', 'String', [('String', 'x')], '')
    assert_equal(method.name, 'bar')
    assert_equal(method.type, 'String')
    assert_equal(method.args[0].type, 'String')
    assert_equal(method.args[0].name, 'x')
    assert_equal(method.body, '')

    print("  --- is_constructor ---")
    method = Method('main', 'void', [], '')
    assert_equal(method.is_constructor(), False)

    method = Method(None, None, [], '')
    assert_equal(method.is_constructor(), True)

    method = Method('main', None, [], '')
    assert_equal(method.is_constructor(), False)

    method = Method(None, 'int', [], '')
    assert_equal(method.is_constructor(), False)

    print('All tests passed!\n')

def class_test():
    print("*---- ClassObj Test ----*")

    print("  --- __init__ ---")
    cls = eval_class(read_line("class Ex { }")[0])
    assert_equal(cls.name, 'Ex')
    assert_equal(cls.instance_attr, {})
    assert_equal(cls.methods, {})
    assert_equal(cls.constructors, {})

    cls = eval_class(read_line("class Ex { int x;}")[0])
    assert_equal(cls.instance_attr['x'].value, None)
    
    cls = eval_class(read_line("class Ex { int x = 3;}")[0])
    assert_equal(cls.instance_attr['x'].value, '3 ;')

    cls = eval_class(read_line("class Ex { int foo() {}}")[0])
    assert_equal(cls.methods[('foo', 0)].type, 'int')

    print("  --- private ---")
    cls = eval_class(read_line("private class Ex {}")[0])
    assert_equal(cls.private(), True)
    cls.private(False)
    assert_equal(cls.private(), False)
    assert_error("cls.private('hello')")

    print("  --- superclass ---")
    cls = eval_class(read_line("class Ex extends B {}")[0])
    assert_equal(cls.superclass(), 'B')
    cls.superclass('Foo')
    assert_equal(cls.superclass(), 'Foo')

    print('All tests passed!\n')

def instance_test():
    print("*---- Instance Test ----*")

    cls = eval_class(read_line(""" class Ex { int x; Ex (String x) { } 
        int foo(String x) { }  } """)[0])
    i = Instance(cls)
    assert_equal(i.getattr('x').value, None)
    assert_equal(i.get_method('foo', 1).type, 'int')
    assert_equal(i['x'].value, None)
    assert_equal(i[('foo', 1)].type, 'int')

    i.setattr('x', 4)
    assert_equal(i['x'].value, 4)
    i['x'] = 5
    assert_equal(i['x'].value, 5)
    assert_error("i[('foo', 1)] = 5")

    print('All tests passed!\n')

if __name__ == '__main__':
    variable_test()
    method_test()
    class_test()
    instance_test()

