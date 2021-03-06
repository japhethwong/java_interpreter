#! usr/bin/python3

from compile_parse import *
        
### INTERFACE METHODS ####

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

class InternalClass(object):

    def __init__(self, cls):
        """
        Constructor for internal representation of a class
        """
        self.name = cls['name'] 
        self.instance_attr = {} #{name : [typ, value]}  
        self.static_attr = {}   #{name : [typ, value]}
        self.methods = {}       #{[name,num_args] : [type, args, body]}
        self.constructors = {}  #{num_args : body}
        self.eval_class(cls)


    def add_attribute(self, typ, name, static):
        """
        Adds an attribute to the class
        ARGS:   typ = string of type i.e.'string', 'bool', 'int', etc. 
                name = string name of attribute
                static = bool if attribute is static
        """
        if static: 
            self.static_attr[name] = [typ, None]
        else:
            self.instance_attr[name] = [typ, None]


    def update_attribute(self, name, val):
        """
        Reassigns the value of 'name' to val
        ARGS:   name = name of attribute
                val = value to assign to attribute
        """
        if name in self.static_attr:
            self.static_attr[name][1] = val 
        else:
            self.instance_attr[name][1] = val


    def add_method(self,typ, name, body, args): 
        self.methods[(name, len(args))] = [typ,args,body]


    def add_constructor(self, num_args, args, body):
        self.constructors[num_args] = [args, body]

    def eval_class(self, cls):
        """
        Evaluates the contents of a class
        Call only once per loading of file
        """
        CLASSES[self.name] = self
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
        ARGS:   expr = dictionary of 
        """
        self.add_attribute(expr['type'],expr['name'],expr['static']) 


    def eval_assign(self, expr,cls_name):
        """
        Assigns a variable with a value
        """
        self.update_attribute(expr['name'],expr['value'])

    def eval_method(self,expr,cls_name):
        """
        Assigns a method to a specific class
        """
        self.add_method(expr['type'], expr['name'], expr['body'], expr['args'])
    
    
    def eval_constructor(self, expr, cls_name):
        if cls_name != expr['name']:
            raise TypeError("Constructor does not match class")
        self.add_constructor(len(expr['args']),expr['args'], expr['body'])


    def print_fields(self):
        print('STATIC ATTRIBUTES:\n \t {} '.format(self.static_attr))
        print('INSTANCE ATTRIBUTES:\n \t {}'.format(self.instance_attr))
        print('METHODS:\n \t {} \n'.format(self.methods))
        print('CONSTRUCTORS: \n \t {} \n'.format(self.constructors))




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
            val = cls.instance_attr[var][1]      # parse_eval(cls.instance_attr[var][1])
            self.instance_attr[var] = (val, typ,var)          #Variable(val, typ, var)

    def _process_static_attr(self, cls): #TODO
        for var in cls.static_attr:
            typ = cls.static_attr[var][0]
            val = cls.static_attr[var][1]#parse_eval(cls.static_attr[var][1])
            self.static_attr[var] = (val, typ, var)        #Variable(val, typ, var)

    def _process_methods(self, cls): #TODO
        for method in cls.methods:
            pass
              
    def print_fields(self):
        print(self.name)
        print('INSTANCE ATTRIBUTES: \n {} \n'.format(self.instance_attr))
        print('STATIC ATTRIBUTES: \n {} \n'.format(self.static_attr))


def test(code1):
    input1 = read_line(code1)
    for c in input1:
        ic = InternalClass(c)
    print('Read_line: \n {} \n'.format(input1))
    print(CLASSES)
    for cls in CLASSES.values():
        cls.print_fields() 
    print('Processing to InternalClass now:')
    ic = ExternalClass(CLASSES.values()[0])
    ic.print_fields()

###TESTING####
if __name__ == '__main__':

    code1 = 'class Ex { static int x = 3; int y=4; int z; x=4+3; int foo(int a, int b) { a + b;} public Ex (int b, int c) {b = 4; c = 5; } }'
    test(code1)
