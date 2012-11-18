"""java interpreter"""
import re
from constants import *
from variable import *
from assign import *#assign_variable, declare_variable
from conditionals import *#handle_conditional_statements
#from loops import *
#from compile_eval import *
from exceptions import *

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
    print("-------------Printing variables-------------")
    print("STACK: ", stack)
    print("INSTANCE VARS", instance_variables)
    print("-----------------------------------------")

def get_current_frame():
    return stack[-1]
    
def get_variable_frame(var):
    frame = get_current_frame()
    if var in frame:
        return frame
    if var in instance_variables:
        return instance_variables
    return None
    
def variable_lookup(var):
    frame = get_variable_frame(var)
    if frame:
        return frame[var]
    raise JavaNameError(" name '{0}' is not defined".format(var))
    
def handle_constructor(exp_str):
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
        
    stack.append(dict())
    #thing = initialize(tokens.pop(0), len(tokens))
    
    #handle params
    for param in thing['args']:
        assign_variable(param + ' = ' + tokens.pop(0), instance_attributes, stack)
    
    #handle body
    parse_eval(thing['constructor'], thing['obj'].get_instance_attributes())    
    
    stack.pop()
    
    return thing['obj']
        

def evaluate_expression(exp_str, instance_environment=False):
    #print('here!, string is: ', exp_str)
    # replace all variables with their values
    print_vars()
    "######################################"
    if (re.search('[a-z]', exp_str)): # match potential variable names
        tokens = tokenize_one_expression(exp_str)
        for i, item in enumerate(tokens):
            if (re.search('[a-z]', item) and item not in KEYWORDS):
                if not (item[0] == '"' and item[-1] == '"'):
                    tokens[i] = str(variable_lookup(item).get_value())
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
    
    
    return eval(exp_str)
    
def tokenize_one_expression(str):
    memory.append(str)
    spaced = str
    for key, val in DELIMITERS.items():
        spaced = spaced.replace(key, ' ' + key + ' ').replace(val, ' ' + val + ' ')
    return spaced.strip().split()

class Expression:
    def __init__(self, str=None, env=None):
        self.str = str.strip()
        self.value = 'n/a'
        self.env = env if env is not None else instance_variables
        
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
                self.value = handle_for(self.str, self.env, stack)
            elif control_statement == 'while':
                self. value = handle_while(self.str, self.env, stack)
            elif control_statement == 'if':
                self.value = parse_eval(handle_conditional_statements(self.str, self.env, stack), self.env)
            else:
                raise WhatTheHeckHappenedException("control statement: ", control_statement)
        elif 'System.out.println' in self.str:
            self.value = handle_println(self.str)
        elif re.match('[a-zA-Z][\w\s]*[^=]=[^=]', self.str):
            self.value = assign_variable(self.str, self.env, stack)
        elif len(tokens) == 2 and tokens[0] in TYPES:
            self.value = declare_variable(self.str, self.env, stack)
        else:
            self.value = evaluate_expression(self.str)            
        print_vars()
        "######################################"
        return self.value
        
        
        
        
    def __repr__(self):
        self.eval()
        return 'Exp({0})'.format(self.value)
        
    
def parse(str, env=None):
    tokens = tokenize(str) # is a list of lists
    return analyze(tokens, env) # is a list of analyzed expressions
    
def tokenize(cur_read):
    global unevaled, continue_prompt
    s = cur_read.strip() 
    
    expressions = (unevaled + ' ' + s)
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
        exp_lst = cur_read.split(';')
        unevaled = exp_lst.pop()   

    # expressions!
    for i, str in enumerate(exp_lst):
        exp_lst[i] = str
        
    return exp_lst
    
    
def analyze(lst, env=None):
    expressions = []
    for item in lst:
        expressions.append(Expression(item, env))
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

def parse_eval(strg, env = None):
    return eval_commands(parse(strg, env))
    
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
            
if __name__ == '__main__':
    read_eval_print_loop()
