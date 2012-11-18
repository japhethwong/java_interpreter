"""java interpreter"""
import re
from constants import *
from variable import *
from assign import *

try:
    import readline  # Enables access to previous expressions in the REPL
except ImportError:
    pass # Readline is not necessary; it's just a convenience
    
unevaled = ''
memory = []
stack = [{}]
instance_variables = {}

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

def evaluate_expression(exp_str):
    #print('here!, string is: ', exp_str)
    
    # replace all variables with their values
    if (re.search('[a-z]', exp_str)): # match potential variable names
        tokens = tokenize_one_expression(exp_str)
        for i, item in enumerate(tokens):
            if (re.search('[a-z]', item) and item not in KEYWORDS):
                if not (item[0] == '"' and item[-1] == '"'):
                    tokens[i] = str(variable_lookup(item).get_value())
        exp_str = " ".join(tokens)
    
    for java_exp, python_exp in JAVA_TO_PYTHON.items():
        exp_str = exp_str.replace(java_exp, ' ' + python_exp + ' ')
    
    floatdouble_casting = "\s*\(\s*(float|double)\s*\)\s"
    if re.search(floatdouble_casting, exp_str): # match casting
        new_str = re.sub(floatdouble_casting, '', exp_str)
        # make sure division works
        exp_str = str(float(eval(new_str)))
        print("THHISSS")
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
    def __init__(self, str=None):
        self.str = str.strip()
        self.value = 'n/a'
        
    def eval(self):
        if self.str == None:
            return
        tokens = tokenize_one_expression(self.str)
        if 'System.out.println' in self.str:
            self.value = handle_println(self.str)
        elif re.match('[a-zA-Z][\w\s]*[^=]=[^=]', self.str):
            self.value = assign_variable(self.str, instance_variables, stack)
        elif len(tokens) == 2 and tokens[0] in TYPES:
            self.value = declare_variable(self.str, instance_variables, stack)
        else:
            self.value = evaluate_expression(self.str)            
            
        return self.value
        
        
        
        
    def __repr__(self):
        self.eval()
        return 'Exp({0})'.format(self.value)
        
    
def parse(str):
    tokens = tokenize(str) # is a list of lists
    return analyze(tokens) # is a list of analyzed expressions
    
def tokenize(str):
    global unevaled
    s = str.strip() 
    
    # handle multiple expressions on one line
    expressions = (unevaled + ' ' + s).split(';')
    unevaled = expressions.pop()   

    # expressions!
    for i, str in enumerate(expressions):
        expressions[i] = str
        
    return expressions
    
def analyze(lst):
    expressions = []
    for item in lst:
        expressions.append(Expression(item))
    return expressions
    
    
def eval_commands(commands):
    for exp in commands:
        value = exp.eval()
        if value != None:
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

def read_eval_print_loop():
    """Run a read-eval-print loop for JavaInterpreter."""
    while True:
        try:
            exp = parse(input('java> '))
            eval_commands(exp)
        except (JavaException, SyntaxError, TypeError, ZeroDivisionError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print('<(^ ^)>')
            return

if __name__ == '__main__':
    read_eval_print_loop()
