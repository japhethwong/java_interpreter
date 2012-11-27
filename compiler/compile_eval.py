#! /usr/bin/python3

import sys
sys.path.append(sys.path[0] + '/../')

from compiler.buffer import Buffer
from compiler.compile_parse import read_line, read_statement

### INTERFACE METHODS ####

def compile(parsed_input):
    """
    Function called by the Online interface Parser
    to create a list of External classes to send
    to the interpreter.
    """
    for cls in parsed_input:
        CLASSES[cls['name']] = InternalClass(cls)
    output = []
    for cls in CLASSES:
        output.append(ExternalClass(CLASSES[cls]))
    return output

def initialize(cls_name, num_args):
    """
    Interface method to interpreter
    After receiving constructor in interpreter, return a instance 
    of the ExternalClass object to send to the interpreter.
    """
    constructor = CLASSES[cls_name].constructors[num_args]
    
    instance_obj = ExternalClass(CLASSES[cls_name])
    body = get_const_body(constructor)
    str_paren = process_params(constructor)
    return {'obj': instance_obj, 'constructor':body, 'args': str_paren}

def get_method(instance_obj, method_name, num_args):
    """
    Returns the body of a specific method
    """
    typ = instance_obj.name
    return CLASSES[typ].methods[[method_name, num_args]]

def process_params(const):
    """
    Helper function: changes constructor params from form
    [('type', 'var1'), ('type', 'var2') ...] -> 
    """
    lst = []
    for tup in const[0]:
        lst.append(tup[0]+' '+ tup[1])
    return lst 

def get_const_body(const):
    """
    Helper function that returns the body of a constructor
    """
    return const[1]


CLASSES = {} # {class_name : class}


def reset_classes():
    """
    Function helps reset the dictionary of classes
    """
    global CLASSES
    CLASSES = {}

class Variable:
    def __init__(self, name, datatype, static=False, private=False):
        self.name = name
        self.type = datatype
        self.static = static
        self.private = private
        self.value = None

    def __str__(self):
        return "{private} {type} {name}: {value}".format(
                private='private' if self.private else '',
                type=self.type,
                name=self.name,
                value=self.value)

class Method:
    def __init__(self, name, datatype, args, body):
        self.name = name
        self.type = datatype
        self.args = args
        self.body = body

    def __str__(self):
        if not self.name or not self.type:
            s = "("
        else:
            s = "{type} {name}(".format(type=self.type, name=self.name)
        for arg in self.args:
            s += "{}, ".format(arg[0])
        return s[:-2] + ")"


class ClassObj:
    """Representation of a Java class.

    DESCRIPTION:
    All information of the Java class will be processed upon
    initialization. The body of the class will be sorted by statement
    type, and then placed into correct dictionaries.
    """
    def __init__(self, cls):
        """Constructor. CLS should be a Statement object of type
        'class'.
        """
        assert cls.type == 'class', 'not a class'
        self.name = cls['name'] 
        self.private = cls['private']
        self.instance_attr = {} #{name : [typ, value]}  
        self.methods = {}       #{[name,num_args] : [type, args, body]}
        self.constructors = {}  #{num_args : body}
        self.eval_class(cls)

    def eval_class(self, cls):
        """Subroutine that processes the contents of the class.

        ARGUMENTS:
        cls -- a Statement object, guaranteed to be of type 'class'
        """
        CLASSES[self.name] = self
        cls_name = self.name
        for expr in cls['body']:
            op = expr.type
            if op == 'declare':
                self.eval_declare(expr)
            elif op == 'assign':
                self.eval_assign(expr)
            elif op == 'method':
                self.eval_method(expr)
            elif op == 'constructor':
                self.eval_constructor(expr)

    def eval_declare(self, expr):
        """Subroutine for declaring instance variables.

        ARGUMENTS:
        expr -- a Statement object, guaranteed to be of type 'declare'

        RAISES:
        SyntaxError -- if the identifier has already been defined
        """
        if expr['name'] in self.instance_attr:
            raise SyntaxError(expr['name'] + ' already defined')
        self.instance_attr[expr['name']] = Variable(expr['name'], 
                                                    expr['type'], 
                                                    expr['static'],
                                                    expr['private'])

    def eval_assign(self, expr):
        """Subroutine for assigning values to variables.

        ARGUMENTS:
        expr -- a Statement object, guaranteed to be of type 'assign'

        RAISES:
        SyntaxError -- if the identifier has not been defined
        """
        if expr['name'] not in self.instance_attr:
            raise SyntaxError(expr['name'] + ' not defined')
        self.instance_attr[expr['name']].value = expr['value']

    def eval_method(self,expr):
        """Subroutine for defining methods.

        DESCRIPTION:
        Method overloading is handled by making the key to the
        METHODS dictionary tuples of (name, num_arguments). A method
        with a certain number of arguments can only be defined twice.

        RAISES:
        SyntaxError -- if method with that many args has already been
                       defined
        """
        key = (expr['name'], len(expr['args']))
        if key in self.methods:
            raise SyntaxError(expr['name'] + ' has already been ' + \
                              'defined with {} arguments'.format(
                                  len(expr['args'])))
        self.methods[(expr['name'], len(expr['args']))] = \
                Method(expr['name'],
                       expr['type'],
                       expr['args'],
                       expr['body'])

    def eval_constructor(self, expr):
        """Subroutine for defining constructors.

        DESCRIPTION:
        Constructors are represented as Method objects whose name
        and type attributes are None.

        RAISES:
        TypeError -- a constructor name that doesn't match the class
                     name
        """
        if self.name != expr['name']:
            raise TypeError("Constructor does not match class")
        self.constructors[len(expr['args'])] = Method(None,
                                                      None,
                                                      expr['args'],
                                                      expr['body'])

    def __str__(self):
        s = "class {}:\n".format(self.name)
        s += "\tprivate: {}\n".format(self.private)
        s += "\tInstance Attrs:\n"
        for var in self.instance_attr.values():
            s += "\t\t{}\n".format(var)
        s += "\tConstructors:\n"
        for var in self.constructors.values():
            s += "\t\t{}\n".format(var)
        s += "\tMethods:\n"
        for var in self.methods.values():
            s += "\t\t{}\n".format(var)
        return s


class ExternalClass(object):
    
    def __init__(self, cls):
        """
        Constructor for external representation of a class.
        Used to send class information to the Interpreter
        args:  cls = InternalClass object
        """
        self.name = cls.name
        self.methods = {}
        self.instance_attr = {}
        self.static_attr = {}
        self._populate(cls) 

    # Getter & Setter Methods
    def set_instance_attr(self, name, val):
        self.instance_attributes[name] = val

    def get_instance_attr(self, name):
        return self.instance_attr[name]

    def get_static_attr(self, name):
        return self.static_attr[name]

    def get_instance_attributes(self):
        return self.instance_attr

    def get_static_attributes(self):
        return self.static_attr


    # Setter Methods
    def _populate(self,cls):
        """
        Populates the ExternalClass object by processing
        fields in the InternalClass into a readable form
        for the interpreter
        """
        self._process_instance_attr(cls)
        self._process_static_attr(cls)
        self._process_methods(cls)

    def _process_instance_attr(self, cls): #TODO Check datatype
        for var in cls.instance_attr:
            typ = cls.instance_attr[var][0]
            if cls.instance_attr[var][1] == None:
                cls.instance_attr[var][1] = '0;'
            val = parse_eval(cls.instance_attr[var][1],
                        dict(), [dict()])
            self.instance_attr[var] = Variable(val, typ, var)

    def _process_static_attr(self, cls): #TODO
        for var in cls.static_attr:
            typ = cls.static_attr[var][0]
            val = parse_eval(cls.static_attr[var][1],
                        dict(), [dict()])
            self.static_attr[var] = Variable(val, typ, var)

    def _process_methods(self, cls): #TODO
        for method in cls.methods:
            pass
              
    def print_fields(self):
        print('INSTANCE ATTRIBUTES: \n {} \n'.format(self.instance_attr))
        print('STATIC ATTRIBUTES: \n {} \n'.format(self.static_attr))



###TESTING####

def test1():
    """Test suite 1"""
    print("----- Test Suite 1 -----")
    print("-- Test 1 --")
    b1 = Buffer("class Ex { int x = 3; }")
    s1 = read_statement(b1)
    c1 = ClassObj(s1)
    print(c1)

    print("-- Test 2 --")
    b2 = Buffer("class Ex { int x = 3; int x; }")
    s2 = read_statement(b2)
    try:
        c2 = ClassObj(s2)
    except SyntaxError:
        print("Raised SyntaxError -- passed\n")
    else:
        print("Did not raise SyntaxError: " + str(e)) + "\n"

    print("-- Test 3 --")
    b3 = Buffer("""class Ex { int foo(String x) {}
                double foo(String x, int y) {}  }""")
    s3 = read_statement(b3)
    c3 = ClassObj(s3)
    print(c3)


def repl():
    """For interactive testing purposes"""
    while True:
        try:
            line = input("Java> ")
        except KeyboardInterrupt:
            print('\nExiting compiler')
            exit(0)
        else:
            classes = read_line(line)
            for cls in classes:
                print(ClassObj(cls))

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '-t':
        test1()
    repl()

