#! usr/bin/python3

from compile_parse import *
        

### INTERFACE METHODS ####

def initialize(cls_name, num_args):
    """
    Interface method to interpreter
    After receiving constructor in interpreter, return a instance 
    of the ExternalClass object to send to the interpreter.
    """
    # create an instance_obj
    constructor = CLASSES[type].constructors[num_args]
    #create instance_obj = (ExternalClass) constructor

    return (instance_obj, constructor)

def get_method(instance_obj, method_name, num_args):
    """
    Returns the body of a specific method
    """
    typ = instance_obj.name
    return CLASSES[typ].methods[[method_name, num_args]]

CLASSES = {}

class InternalClass(object):

    def __init__(self, cls):
        """
        Constructor for internal representation of a class

        Args: cls = 
        """
        self.name = cls['name'] 
        self.instance_attr = {} #{name : [typ, value]}  
        self.static_attr = {}   #{name : [typ, value]}
        self.methods = {}       #{[name,num_args] : [type, args, body]}
        self.constructors = {}  #{num_args : body}
        self.eval_class(cls)

    def add_attribute(self, typ, name, static):
        """
        ARGS: typ = string of type i.e.'string', 'bool', 'int', etc. 
             name = string name of attribute
           static = bool if attribute is static
        Adds an attribute known to the the class
        """
        if static: 
            self.static_attr[name] = [typ, None]
        else:
            self.instance_attr[name] = [typ, None]

    def update_attribute(self, name, val, static):
        if static:
            self.static_attr[name][1] = val 
        else:
            self.instance_attr[name][1] = val

    def add_method(self,typ, name, body, args): 
        self.methods[name, len[args]] = [typ,args,body]

    def add_constructor(self, num_args, body):
        self.constructors[num_args] = body

    def get_attributes(self):
        return self.static_attr

    def get_methods(self):
        return self.methods

    def eval_class(self, cls):
        """
        Evaluates the contents of a class
        Call only once per loading of file
        """ 
        cls_name = self.name
        for expr in cls['body']:
            if expr['op'] == 'declare':
                self.eval_declare(expr,cls_name)
            elif expr['op'] == 'assign':
                self.eval_assign(expr, cls_name)
            elif expr['op'] == 'method':
                self.eval_method(expr, cls_name)
            elif expr['op'] == 'constructor':
                self.eval_constructor(expr, cls_name)

    def eval_declare(self,expr, cls_name):
        """
        Declares a variable in a class
        """
        self.add_attribute(expr['type'],expr['name'],expr['static']) 


    def eval_assign(self, expr,cls_name):
        """
        Assigns a variable with a value
        """
        self.update_attribute(expr['name'],expr['value'],expr['static'])


    def eval_method(self,expr,cls_name):
        """
        Assigns a method to a specific class
        """
        self.add_method(expr['type'], expr['name'], expr['body'], expr['args'])
    
    
    def eval_constructor(self, expr, cls_name):
        self.add_constructor(len(expr['args']), expr['body'])


    def print_attributes(self):
        print('STATIC ATTRIBUTES:\n \t {} '.format(self.static_attr))
        print('INSTANCE ATTRIBUTES:\n \t {}'.format(self.instance_attr))


    def print_methods(self):
        print('METHODS:\n \t {} \n'.format(self.methods))
    

class ExternalClass(object):
    
    def __init__(self):
        """
        Constructor for external representation of a class.
        Used to send class information to the Interpreter
        """
        self.name           # Name of the class 
        self.methods        # Dict: 
        self.body           # Body of the function



###TESTING####
if __name__ == '__main__':
    code1 = 'class Ex { int x = 3; int y=4; int z; x=4+3; int foo() { x+y;}}'
    input1 = read_line(code1)
    print('Read_line: \n {} \n'.format(input1))
    env = InternalEnvironment()
    env.eval(input1)
    env.print_classes()

