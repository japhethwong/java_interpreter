"""
primitives.py

Data structures used as the interface between the compiler and the 
interpreter.

Contents:
    Variable
    Method
    ClassObj
    Instance

Authors: Albert Wu

this file is designed to run on python3
"""

class Variable:
    """Wrapper class for variable definitions."""
    def __init__(self, name, datatype, static=False, private=False):
        self.name = name
        self.type = datatype
        self.static = static
        self.private = private
        self.value = None

    def clone(self):
        var = Variable(self.name, self.type, self.static, self.private)
        var.value = self.value
        return var

    def __str__(self):
        return "{private}{type} {name}: {value}".format(
                private='private ' if self.private else '',
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
            s = "Constructor("
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
        """Subroutine used to declare variables."""
        if var.name in self.instance_attr:
            raise SyntaxError(var.name + ' already defined')
        self.instance_attr[var.name] = var


    def assign_var(self, var_name, value):
        """Subroutine used to assign values to variables."""
        if var_name not in self.instance_attr:
            raise SyntaxError(var_name + ' not defined')
        self.instance_attr[var_name].value = value

    def declare_method(self, method):
        """Subroutine used to declare a method."""
        key = (method.name, len(method.args))
        if key in self.methods:
            raise SyntaxError(method.name + ' has already been ' + \
                              'defined with {} arguments'.format(
                                  len(method.args)))
        self.methods[key] = method

    def declare_constructor(self, constructor):
        """Subroutine used to declare constructors."""
        if not constructor.is_constructor:
            raise TypeError("Not a valid constructor")
        self.constructors[len(constructor.args)] = constructor

    def private(self, state=None):
        """Deals with protection modifier of class.

        RETURNS:
        if no argument is given, the method is used as a query, and
            will return True if the class is private.
        otherwise, the protection modifier is set to whatever state is
        """
        if state == None:
            return self._private
        assert isinstance(state, bool), 'arg to private must be bool'
        self._private = state

    def superclass(self, sup=None):
        """Deals with superclass.

        RETURNS:
        if no argument is given, the method is used as a query, and
            will return the superclass
        otherwise, the protection modifier is set to whatever sup is
        """
        if sup == None:
            return self._superclass
        assert isinstance(sup, str), 'arg to superclass must be str'
        self._superclass = sup

    def __str__(self):
        s = "{private}class {name}{extends}:\n"
        s = s.format(private='private ' if self.private() else '',
                     name=self.name,
                     extends=' extends '+self.superclass() if \
                             self.superclass() != 'Object' else '')
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


class Instance:
    """Wrapper class for Java instances. 
    
    DESCRIPTION:
    variables -- Instance objects duplicate their own copy of the
                 class's instance variables upon creation. Modifying
                 an Instance's instance variable will not affect the
                 class's instance variables.
    methods   -- Methods are not stored in Instances. Rather, to get
                 a method, Instance retrieve it from its parent class.
    Querying and setting variables and methods (no setting) can be
    done using index notation, for convenience.
    """
    def __init__(self, cls):
        """Constructor.

        ARGUMENTS:
        cls -- a ClassObj
        """
        self.type = cls
        self.instance_attr = {}
        for name, value in cls.instance_attr.items():
            self.instance_attr[name] = value.clone()

    def getattr(self, name):
        """Gets a variable called NAME.

        ARGUMENTS:
        name -- a string, the variable name

        RAISES:
        AttributeError -- if the instance has no such variable

        RETURNS:
        Variable object
        """
        if name not in self.instance_attr:
            raise AttributeError(self.type.name + 
                    ' has no variable called ' + name)
        return self.instance_attr[name]

    def setattr(self, name, value):
        """Sets the given variable NAME to the VALUE.

        ARGUMENTS:
        name  -- a string, the variable name
        value -- (any type), the variable's value

        RAISES:
        AttributeError -- if the instance has no such variable
        """
        if name not in self.instance_attr:
            raise AttributeError(self.type.name + 
                    ' has no variable called ' + name)
        self.instance_attr[name].value = value

    def get_method(self, name, num_args):
        """Gets the specified method by NAME and NUM_ARGS. NUM_ARGS is
        necessary to support overloading.

        ARGUMENTS:
        name     -- a string, the method name. If NAME is the same as
                    the class name, look for a constructor with 
                    NUM_ARGS instead
        num_args -- an int, the number of arguments

        RAISES:
        AttributeError -- if the instance has no such method

        RETURNS:
        Method object
        """
        if name == self.type.name:
            try:
                return self.type.constructors[num_args]
            except KeyError:
                raise AttributeError(self.type.name +
                    ' has no constructor of length ' + str(num_args))
        elif (name, num_args) in self.type.methods:
            return self.type.methods[(name, num_args)]
        else:
            raise AttributeError(self.type.name + ' has no method ' + 
                                 name)

    def __getitem__(self, key):
        """Convenience for getattr. Can be used for both variable and
        method lookup.

        ARGUMENTS:
        key -- string: look for variable
               2-tuple: look for method

        RETURNS:
        Variable object or Method object, depending on query.
        """
        if isinstance(key, tuple) and len(key) == 2:
            return self.get_method(*key)
        return self.getattr(key)

    def __setitem__(self, key, value):
        """Convenience for setattr. Can only be used to set variables.

        ARGUMENTS:
        key   -- a string, the variable name
        value -- (any type), the new value
        """
        if isinstance(key, tuple):
            raise TypeError("Can't re-define a method")
        self.setattr(key, value)

    def __str__(self):
        s = self.type.name + ' object:\n\tInstance Attrs:\n'
        for var in self.instance_attr.values():
            s += '\t\t{}\n'.format(var)
        return s

