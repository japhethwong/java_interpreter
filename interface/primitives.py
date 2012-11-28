"""
primitives.py
"""

###################
# DATA STRUCTURES #
###################

class Variable:
    """Wrapper class for variable definitions."""
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
    """Wrapper class for method definitions. By definition, a 
    constructor is a Method whose name and datatype are None."""
    def __init__(self, name, datatype, args, body):
        self.name = name
        self.type = datatype
        self.args = []
        for arg in args:
            self.args.append(Variable(arg[1], arg[0]))
        self.body = body

    def is_constructor(self):
        """Returns True if self is a constructor, False otherwise."""
        return not self.name and not self.type

    def __str__(self):
        if self.is_constructor():
            s = "("
        else:
            s = "{type} {name}(".format(type=self.type, name=self.name)
        for arg in self.args:
            s += "{}, ".format(arg.type)
        return s + ")"


class ClassObj:
    """Representation of a Java class.

    DESCRIPTION:
    All information of the Java class will be processed upon
    initialization. The body of the class will be sorted by statement
    type, and then placed into correct dictionaries.
    """
    def __init__(self, name):
        """Constructor. CLS should be a Statement object of type
        'class'.
        """
        self.name = name
        self._private = False
        self._superclass = 'Object'
        self.instance_attr = {} 
        self.methods = {}      
        self.constructors = {} 

    def declare_var(self, var):
        if var.name in self.instance_attr:
            raise SyntaxError(var.name + ' already defined')
        self.instance_attr[var.name] = var


    def assign_var(self, var_name, value):
        if var_name not in self.instance_attr:
            raise SyntaxError(var_name + ' not defined')
        self.instance_attr[var_name].value = value

    def declare_method(self, method):
        key = (method.name, len(method.args))
        if key in self.methods:
            raise SyntaxError(method.name + ' has already been ' + \
                              'defined with {} arguments'.format(
                                  len(method.args)))
        self.methods[key] = method

    def declare_constructor(self, constructor):
        if not constructor.is_constructor:
            raise TypeError("Not a valid constructor")
        self.constructors[len(constructor.args)] = constructor

    def private(self, state=None):
        if state == None:
            return self._private
        assert isinstance(state, bool), 'arg to private must be bool'
        self._private = state

    def superclass(self, sup=None):
        if sup == None:
            return self._superclass
        assert isinstance(sup, str), 'arg to superclass must be str'
        self._superclass = sup

    def __str__(self):
        s = "class {}:\n".format(self.name)
        s += "\tprivate: {}\n".format(self.private())
        s += "\tsuper: {}\n".format(self.superclass())
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
