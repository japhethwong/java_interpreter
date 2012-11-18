"""java interpreter"""
import re
from constants import *
from variable import *
#from assign import *#assign_variable, declare_variable
#from conditionals import *#handle_conditional_statements
#from loops import *
from compile_eval import *
from exceptions import *
from util import clean_up_list_elems, flatten_list


try:
    import readline  # Enables access to previous expressions in the REPL
except ImportError:
    pass # Readline is not necessary; it's just a convenience
    
unevaled = ''
memory = []
stack = [{}]
instance_variables = {}
prompt_types = {False: "java> ", True: "...  "}
continue_prompt = False

def print_vars():
    return
    print("-------------Printing variables------------")
    print("STACK: ", stack)
    print("STACK ID: ", id(stack))
    print("INSTANCE VARS", instance_variables)
    print("-----------------------------------------")

    
def get_variable_frame(var, env, s):
    if var in s:
        return s
    if var in env:
        return env
    return None
    
def variable_lookup(var, env, s):
    frame = get_variable_frame(var, env, s)
    if frame:
        return frame[var]
    raise JavaNameError(" name '{0}' is not defined".format(var))
    
def handle_constructor(exp_str, instance_env, exp_stack):
    exp_str = exp_str.strip()
    tokens = tokenize_one_expression(exp_str)
    if len(tokens) < 4:
        raise InvalidConstructorException('too few fields')
    if tokens.pop(0) != 'new':
        raise InvalidConstructorException("'new' in wrong place")
    if tokens.pop(2) != '(':
        raise InvalidConstructorException("'(' in wrong place")
    if tokens.pop() != ')':
        raise InvalidConstructorException("')' in wrong place")
        
    exp_stack.append(dict())
    #thing = initialize(tokens.pop(0), len(tokens))
    
    #handle params
    for param in thing['args']:
        assign_variable(param + ' = ' + tokens.pop(0), instance_attributes, exp_stack)
    
    #handle body
    parse_eval(thing['constructor'], thing['obj'].get_instance_attributes())    
    
    exp_stack.pop()
    
    return thing['obj']
        

def evaluate_expression(exp_str, instance_environment, exp_stack):
    #print('here!, string is: ', exp_str)
    # replace all variables with their values
    print_vars()
    "######################################"
    if (re.search('[a-z]', exp_str)): # match potential variable names
        tokens = tokenize_one_expression(exp_str)
        for i, item in enumerate(tokens):
            if (re.search('[a-z]', item) and item not in KEYWORDS):
                #print("HERE!!", item)
                if not ((item[0] == '"' and item[-1] == '"') or (item[0] == "'" and item[-1] == "'")):
                    #print("HERE2")
                    tokens[i] = str(variable_lookup(item, instance_environment, exp_stack).get_value())
        exp_str = " ".join(tokens)
    
    # handle constructor
    if re.search('new\s*[A-Z][A-Za-z]*\(', exp_str):
        return handle_constructor(exp_str)
        
    
    for java_exp, python_exp in JAVA_TO_PYTHON.items():
        exp_str = exp_str.replace(java_exp, ' ' + python_exp + ' ')
    
    floatdouble_casting = "\s*\(\s*(float|double)\s*\)\s"
    if re.search(floatdouble_casting, exp_str): # match casting
        new_str = re.sub(floatdouble_casting, '', exp_str)
        # make sure division works
        exp_str = str(float(eval(new_str)))
    if '//' in exp_str:
        raise SyntaxError("// is invalid")
    if "/"  in exp_str and (re.search('\d+\.\d+', exp_str) is None):
        exp_str = exp_str.replace('/', '//')  
    
    if exp_str.strip() == '':
        return None
    return eval(exp_str)
    
def tokenize_one_expression(str):
    match_string = '".*"'
    replaced = ''
    while re.search(match_string, str):
        replaced = re.search(match_string, str)
        str = re.sub(match_string, THING_TO_REPLACE, str)
    spaced = str
    for key, val in DELIMITERS.items():
        spaced = spaced.replace(key, ' ' + key + ' ').replace(val, ' ' + val + ' ')
    for item in SPACE:
        spaced = spaced.replace(item, ' ' + item + ' ')
        spaced = re.sub("\s*! =\s*", " != ", re.sub("\s*=  =\s*", " == ", re.sub("\s*>  =\s*"," >= ",re.sub("\s*<  =\s*"," <= ", spaced))))
    tokenized = spaced.strip().split()
    for i, item in enumerate(tokenized):
        if item  ==  THING_TO_REPLACE:
            tokenized[i] = replaced.string
    return tokenized

class Expression:
    def __init__(self, str=None, env=None, s=None):
        self.str = str.strip()
        self.value = 'n/a'
        self.env = env if env is not None else instance_variables
        self.stack = s if s is not None else stack
        
    def eval(self):
        if self.str == None:
            return
        tokens = tokenize_one_expression(self.str)
        control_statement = None
        for token in tokens:
            if token in CONTINUE_KEYWORDS:
                control_statement = token                
                break
        if control_statement:
            if control_statement == 'for':
                self.value = handle_for(self.str, self.env, self.stack)
            elif control_statement == 'while':
                self. value = handle_while(self.str, self.env, self.stack)
            elif control_statement == 'if':
                result = handle_conditional_statements(self.str, self.env, self.stack)
                if result:
                    self.value = parse_eval(result)
                else:
                    self.value = result
            else:
                raise WhatTheHeckHappenedException("control statement: ", control_statement)
        elif 'System.out.println' in self.str:
            self.value = handle_println(self.str)
        elif re.match('[a-zA-Z][\w\s]*[^=<>!]=[^=]', self.str):
            self.value = assign_variable(self.str, self.env, self.stack)
        elif len(tokens) == 2 and tokens[0] in TYPES:
            self.value = declare_variable(self.str, self.env, self.stack)
        else:
            self.value = evaluate_expression(self.str, self.env, self.stack)            
        print_vars()
        "######################################"
        return self.value
        
        
        
        
    def __repr__(self):
        self.eval()
        return 'Exp({0})'.format(self.value)
        
    
def parse(str, env=None, s=None):
    tokens = tokenize(str) # is a list of lists
    return analyze(tokens, env, s) # is a list of analyzed expressions
    
def tokenize(cur_read):
    global unevaled, continue_prompt
    s = cur_read.strip() 
    
    expressions = unevaled + ' ' + s
    for item in CONTINUE_KEYWORDS:
        if item in expressions:
            continue_prompt = True
    
    if continue_prompt and cur_read == '':
        continue_prompt = False
        unevaled = ''
        exp_lst = [expressions]
    elif continue_prompt:
        unevaled = expressions
        exp_lst = []
    else:
        # handle multiple expressions on one line
        exp_lst = expressions.split(';')
        unevaled = exp_lst.pop()

    # expressions!
    for i, str in enumerate(exp_lst):
        exp_lst[i] = str
        
    return remove_empty(exp_lst)
    
def remove_empty(ls):
    w = len(ls) - 1
    while w >= 0:
        if ls[w] == '':
            ls.pop(w)
        w = w - 1
    return ls
        
    
def analyze(lst, env=None, s=None):
    expressions = []
    for item in lst:
        expressions.append(Expression(item, env,s))
    return expressions
    
    
def eval_commands(commands, should_print=True):
    for exp in commands:
        value = exp.eval()
        if value != None and should_print:
            print(java_form(value))
    return
    
def java_form(item):
    if str(item) in PYTHON_TO_JAVA:
        return PYTHON_TO_JAVA[str(item)]
    return item
    
def handle_println(exp_str):
    thing_to_eval = exp_str.replace("System.out.println(", '')
    if thing_to_eval[-1] != ')':
        raise InvalidSystemCallException("println statement malformed")
    thing_to_eval = thing_to_eval[:-1]
    print(Expression(thing_to_eval).eval())

def parse_eval(strg, env = None, s=None):
    return eval_commands(parse(strg, env,s),not continue_prompt)
    
def read_eval_print_loop():
    """Run a read-eval-print loop for JavaInterpreter."""
    while True:
        try:
            parse_eval(input(prompt_types[continue_prompt]))
        except (JavaException) as err:#, SyntaxError, TypeError, ZeroDivisionError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print('<(^ ^)>')
            return

"""
handle_conditional_statements() takes a conditional block, divides the branches into cases, 
evaluates the cases, and determines which piece of code should be executed.  This function 
is responsible for parsing the branches, but the evaluator is responsible for parsing the 
statements once the branch is chosen.

Arguments:
if_else_block -- this is a complete if-else block, beginning with "if ... " and ending with 
the closing curly brace of the last branch in the block.
instance_vars -- dictionary representing the instance variables
stack -- the stack as represented in our system

Returns:
The statements associated with the correct branch, or None if none of the conditions are met

Exceptions Raised:
InvalidIfElseBlockException -- raised if the syntax is invalid for an if-else block.
"""
def handle_conditional_statements(if_else_block, instance_vars, stack):
    #import javarepl# import evaluate_expression
    has_else_clause = verify_if_else_syntax(if_else_block)
    
    # Tokenize if-else block: split conditions from statements
    tokens = clean_up_list_elems(flatten_list(re.split("\s*\}\s*else if\s*\(", if_else_block))) # Split by } else if (
    tokens = clean_up_list_elems(flatten_list(list(map(lambda elem: re.split("\s*if\s*\(", elem), tokens))))    # Split by if (
    tokens = clean_up_list_elems(flatten_list(list(map(lambda elem: re.split("\s*\}\s*else\s*\{", elem), tokens)))) # Split by } else {, insert True as condition
    if has_else_clause:
        tokens.insert(-1, "True")
    tokens = clean_up_list_elems(flatten_list(list(map(lambda elem: re.split("\s*\)\s*\{", elem), tokens))))    # Split  by ) {
    tokens = clean_up_list_elems(flatten_list(list(map(lambda elem: re.split("\}", elem), tokens))))    # Split by }
    
    # Split tokens into list of conditions and statements
    conditions_list, statements_list = [], []
    for index in range(0, len(tokens)):
        if index % 2 == 0:  # Even, is a condition.
            conditions_list.append(tokens[index])
        else:
            statements_list.append(tokens[index])
    
    assert len(conditions_list) == len(statements_list), "conditions_list and statements_list are of different lengths"
    
    # Check the conditions; if True, return the associated statements
    for index in range(0, len(conditions_list)):
        curr_condition = evaluate_expression(conditions_list[index], instance_vars, stack)
        if type(curr_condition) is not bool:
            raise InvalidIfElseBlockException("Condition parsed was not a boolean expression.  Condition was: " + str(curr_condition))
        if curr_condition:
            return statements_list[index]
        
    return None
"""
# For testing purposes only.
def evaluate_expression(condition):
    print("Evaluating " + str(condition))
    x, y, z = 0, 0, 0
    return eval(condition)
"""
"""
verify_if_else_syntax() takes an if-else block and scans it to ensure that it is a 
valid if-else block.  Only verifies general format; does NOT check to ensure that 
a boolean expression is included in conditional.  This HAS a return value -- it 
also scans to see if an else statement exists!

Arguments:
block -- the block that is being verified

Returns:
True if else clause exists, False otherwise

Exceptions Raised:
InvalidIfElseBlockException -- thrown if the block has determined to be invalid syntax
"""
def verify_if_else_syntax(block):
    has_else = True
    block = block.strip()
    block = re.sub("\)[\s\n]*\{", ") { ", block)
    block = re.sub("[\s\n]*\{", " { ", block)
    block = re.sub("[\s\n]*\([\s\n]*", " ( ", block)
    block = re.sub("[\s\n]*\)[\s\n]*", " ) ", block)
    
    assert len(block) > 0, "len(block) is NOT > 0, it is " + str(len(block))
    last_position = block.find("if (")
    if last_position != 0:
        raise InvalidIfElseBlockException("0th word is NOT if, it is: " + block[0])
    
    if block.find("else if {") != -1:
        raise InvalidIfElseBlockException("else if has no condition")
    
    curr_position = 0
    while curr_position != -1:
        last_position, curr_position = curr_position, block.find(") {", curr_position)
        if last_position >= curr_position or curr_position == -1:
            raise InvalidIfElseBlockException("if or else if NOT followed by ') {'")
        
        last_position, curr_position = curr_position, block.find("} else if (", curr_position)
    
    # At this point, curr_position is -1 from searching for '} else if ('
    curr_position = block.find("} else {", last_position)
    if curr_position == -1:
        curr_position = block.find("}", last_position)
        if curr_position == -1:
            raise InvalidIfElseBlockException("else-if clause is not terminated with '}'")
        has_else = False
    else:
        last_position, curr_position = curr_position, block.find("}", curr_position+1)
        if last_position >= curr_position:
            raise InvalidIfElseBlockException("else clause not terminated with '}'")
    return has_else

"""
handle_switch_statements() takes a switch statement, divides the cases, evaluates the 
cases, and determines which piece of code should be executed.  This function is responsible 
for parsing the branches, but the evaluator is responsible for parsing the statements once 
the branch is chosen.

Arguments:
switch_block -- this is a complete switch statement, beginning with "switch ()" and ending 
with the curly brace following the last break in the statement.

Returns:
None

Exceptions Raised:

"""
def handle_switch_statements(switch_block):
    # TODO
    return

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
    #from javarepl import evaluate_expression
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

    # If string type, put quotes around it.
    if result_type is str:
        result = '"' + result + '"'
    
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
        elif stored_variable_type not in STRING_TYPES:
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
    
"""
handle_while() takes a while loop block and parses it.  This function is responsible for 
controlling how many times the loop executes.

Arguments:
block -- the while loop  block that is being parsed
instance_vars -- the dictionary which represents the instance variables
stack -- the list of dictionaries which represents our stack

Returns:
None.  Calls parse_eval() instead of returning.

Exceptions raised:
InvalidWhileLoopException -- raised if the syntax does not follow the form of a valid while loop
"""
def handle_while(block, instance_vars, stack):
    validate_while_loop_syntax(block)
    
    tokens = clean_up_list_elems(flatten_list(re.split("while\s*\(", block)))
    tokens = clean_up_list_elems(flatten_list(list(map(lambda x: re.split("\)\s*\{", x), tokens))))
    tokens = clean_up_list_elems(flatten_list(list(map(lambda x: re.split("\}", x), tokens))))
    
    assert len(tokens) == 2, "There should be 2 tokens, but there are " + str(len(tokens))
    
    condition, statements = tokens[0], tokens[1]
    
    while evaluate_expression(condition, instance_vars, stack):
        parse_eval(statements, instance_vars, stack)    # We will NOT support different scoping for variables inside.
        
    return  # Call parse_eval with instance_vars

"""
validate_while_loop_syntax() walks through the syntax to ensure that the basic syntax of a while 
loop has been followed.

Arguments:
block -- the snippet of code to be analyzed

Returns:
None.

Exceptions raised:
InvalidWhileLoopException -- raised if the syntax does not follow the structure of a while loop
"""
def validate_while_loop_syntax(block):
    return

def handle_for(block, instance_vars, stack):
    validate_for_loop_syntax(block)
    
    tokens = clean_up_list_elems(flatten_list(re.split("for\s*\(", block)))
    tokens = clean_up_list_elems(flatten_list(list(map(lambda x: re.split("\)\s*\{", x), tokens))))
    tokens = clean_up_list_elems(flatten_list(list(map(lambda x: re.split("\}", x), tokens))))
    
    tokens = tokens[0].split(";") + [tokens[1]]
    initialize, condition, update, statements = tokens
    
    assign_variable(initialize, instance_vars, stack)
    """
    evaluated_condition = evaluate_expression(condition, instance_vars, stack)
    if type(evaluated_condition) is not bool:
        raise InvalidForLoopException("Boolean condition is of wrong type")
    """
    while evaluate_expression(condition, instance_vars, stack):
        parse_eval(statements, instance_vars, stack)
        assign_variable(update, instance_vars, stack)
        
    # Assumes well-formed expression.
    var_name = initialize.split(" ")[1]
    get_variable_frame(var_name, instance_vars, stack).pop(var_name)
    
    return
    
def validate_for_loop_syntax(block):
    return

            
if __name__ == '__main__':
    read_eval_print_loop()
