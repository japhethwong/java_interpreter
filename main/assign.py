'''
assign.py
Handles all functions related to variable assignment.
@author: Japheth Wong
'''
import re
from exceptions import *
from variable import *
from constants import *
# from javarepl import evaluate_expression
from util import clean_up_list_elems

"""
tokenize_assignment_statement() takes an assignment statement, pads it with spaces, and preserves 
comparison operators.  A list of tokens is returned (such that items to be passed to the evaluator 
are preserved.

Ex.  "a = b<=c"  -- should return -> ["a", "b <= c"]

Arguments:
statement -- the assignment statement to be parsed (semicolon removed)

Returns:
tokens -- list of tokens for assignment 
"""
def tokenize_assignment_statement(statement):
    statement = re.sub("\s*! =\s*", " != ", re.sub("\s*> =\s*", " >= ", re.sub("\s*< =\s*", " <= ", re.sub("\s*=  =\s*", " == " , re.sub("[\s]*=[\s]*", " = ", statement)))))
    tokens = re.split("[^=<>!]=[^=]", statement)
    return tokens

"""
assign_variable() takes an assignment statement and evaluates it.  If the variable is being 
declared here, it is declared and initialized.  Otherwise, it will simply update the value 
of the variable.  This function is responsible for splitting the statement into the declaration 
and updates.

Arguments:
statement -- the statement to be evaluated, passed as a string (untokenized)
instance_vars -- the dictionary holding all the instance variables
stack -- the dictionary containing the entire stack

Returns:
None

Exceptions:
InvalidAssignmentException -- raised if the statement is not a well-formed assignment statement
InvalidDeclarationException -- raised if the declaration portion is not a well-formed declaration
"""
def assign_variable(statement, instance_vars, stack):
    tokens = tokenize_assignment_statement(statement)
    if len(tokens) != 2:
        raise InvalidAssignmentException("Statement provided was: " + str(statement))
    
    # Split declaration into datatype and variable_name parts.
    declaration = tokens[0].strip()
    datatype, variable_name = split_declaration(declaration)    # datatype is None if this is a normal assignment, not declaration.
    
    # Build assignment portion.
    assignment = variable_name + " = " + tokens[1].strip()
    if datatype != None:
        declare_variable(declaration, instance_vars, stack)   # Adds the variable to dictionary.
    update_variable(assignment, instance_vars, stack, datatype != None)   # If datatype != None, then it was just declared.
    
"""
split_declaration() takes a declaration statement and splits it into the datatype and variable name 
components.  If the declaration is an assignment statement, datatype will be None.  If invalid, this 
function will raise an exception.

Arguments:
declaration -- the declaration statement to be evaluated

Returns:
datatype -- the datatype of the variable
name -- the name of the variable

Exceptions:
InvalidDeclarationException -- raised if the declaration provided is not a well-formed variable declaration
"""
def split_declaration(declaration):
    declaration_tokens = clean_up_list_elems(declaration.split(" ")) 
    
    if len(declaration_tokens) == 1:   # Represents an assignment statement to a variable previously declared.
        datatype, name = None, declaration_tokens[0].strip()
    elif len(declaration_tokens) == 2:  # Represents an assignment statement to a variable being declared now.
        datatype, name = declaration_tokens[0].strip(), declaration_tokens[1].strip()
    else:
        raise InvalidDeclarationException("Invalid declaration provided: " + str(declaration))
    
    return datatype, name

"""
declare_variable() takes a declaration statement and puts the variable into the dictionary.

Arguments:
statement -- the declaration statement to be evaluated, passed as a string (untokenized)
is_global -- True if the variable is a global variable, false otherwise
instance_vars -- the dictionary holding all the instance variables
stack -- the dictionary containing the entire stack

Returns:
None

Exceptions:
InvalidDeclarationException -- raised if the statement is not a well-formed declaration statement, 
or if the variable has already been declared.  MAY BE RAISED BY split_declaration() INSTEAD!
"""
def declare_variable(statement, instance_vars, stack, is_global=False):
    datatype, variable_name = split_declaration(statement)
    local_variables = get_current_frame(stack)
    
    if datatype not in TYPES:
        raise InvalidDeclarationException("Datatype is invalid: " + str(datatype))
    
    if get_variable_frame(variable_name, instance_vars, stack) != None:
    # if variable_name in instance_vars or variable_name in local_variables:
        raise InvalidDeclarationException("Variable already declared: " + str(statement))
    
    variable_object = Variable(None, datatype, variable_name)
    if is_global:
        instance_vars[variable_name] = variable_object
    else:
        local_variables[variable_name] = variable_object
    
    
"""
update_variable() takes an update statement and updates the value of the variable.  This function 
DOES perform datatype error-checking.

Arguments:
statement -- the assignment statement to be evaluated, passed as a string (untokenized)
instance_vars -- the dictionary holding all the instance variables
stack -- the dictionary containing the entire stack

Returns:
None

Exceptions:
InvalidDatatypeException -- the datatype does not match the variable value
"""
def update_variable(statement, instance_vars, stack, just_declared=False):
    from javarepl import evaluate_expression
    tokens = tokenize_assignment_statement(statement)
    if len(tokens) != 2:
        raise InvalidAssignmentException("Statement provided was: " + statement)
    variable_name, variable_value = tokens[0].strip(), tokens[1].strip()
    variable_frame = get_variable_frame(variable_name, instance_vars, stack)
    
    if variable_frame == None:
        raise InvalidAssignmentException("")
    
    # Compute the result to update the value of expression with.
    result = evaluate_expression(variable_value, instance_vars, stack)
    result_type = type(result)
    stored_variable_type = variable_frame[variable_name].get_datatype()
    stored_variable_value = variable_frame[variable_name].get_value()
    
    # Check to ensure result datatype matches variable datatype
    verify_result_datatype(result, variable_name, just_declared, stored_variable_type, instance_vars, stack)

    # Now that we know it is  valid, write to variable.
    variable_frame[variable_name].set_value(result)
    
"""
verify_result_datatype() checks the datatype of the result and sees if it matches the variable's declared datatype.  If it 
does not, an exception is raised.  If the variable was declared on the same line, then the variable declaration is removed 
from the frame.

Arguments:
result -- the result whose datatype will be evaluated
variable_name -- the name of the variable being manipulated
just_declared -- True if the variable was declared on the same line as this assignment
stored_variable_type -- the datatype of the stored variable
"""
def verify_result_datatype(result, variable_name, just_declared, stored_variable_type, instance_vars, stack):
    result_type = type(result)
    variable_frame = get_variable_frame(variable_name, instance_vars, stack)
    if result_type is bool and stored_variable_type != BOOLEAN:
        if just_declared: # and stored_variable_type == None:
            variable_frame.pop(variable_name)
        raise InvalidDatatypeException("Invalid datatype: result_type is " + str(result_type) + ", variable type is " + stored_variable_type)
    elif result_type is int and stored_variable_type not in INT_TYPES:
        if just_declared:# and stored_variable_value == None:
            variable_frame.pop(variable_name)
        raise InvalidDatatypeException("Invalid datatype: result_type is " + str(result_type) + ", variable type is " + stored_variable_type)
    elif result_type is float and stored_variable_type not in FLOAT_TYPES:
        if just_declared: # and stored_variable_value == None:
            variable_frame.pop(variable_name)
        raise InvalidDatatypeException("Invalid datatype: result_type is " + str(result_type) + ", variable type is " + stored_variable_type)
    elif result_type is str:
        if stored_variable_type == CHAR and len(result) != 1:
            if just_declared: # and stored_variable_value == None:
                variable_frame.pop(variable_name)
            raise InvalidDatatypeException("Invalid datatype: result_type is " + str(result_type) + ", variable type is " + stored_variable_type)
        elif stored_variable_type != STRING:
            if just_declared: # and stored_variable_value == None:
                variable_frame.pop(variable_name)
            raise InvalidDatatypeException("Invalid datatype: result_type is " + str(result_type) + ", variable type is " + stored_variable_type)

"""
get_current_frame() returns the current frame in the stack.

Arguments:
stack -- the entire stack in our representation of the environment

Returns:
The current stack frame
"""
def get_current_frame(stack):
    assert len(stack) != 0, "stack has length 0!"
    return stack[-1]

"""
get_variable_frame() returns the frame in which the variable is found: either the stack frame or 
the instance_variables list.  Returns None if the variable is not found in either frame.

Arguments:
var -- the name of the variable we are looking up
instance_variables -- the dictionary containing all of the defined instance variables
stack -- the list of dictionaries representing the stack frames on the stack

Returns:
The frame in which the variable is found, or None if the variable cannot be located
"""
def get_variable_frame(var, instance_variables, stack):
    frame = get_current_frame(stack)
    if var in frame:
        return frame
    if var in instance_variables:
        return instance_variables
    return None