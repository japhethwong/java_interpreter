'''
loops.py
Includes all functionality for handling loops
@author: Japheth Wong
'''
from util import clean_up_list_elems, flatten_list
from javarepl import parse_eval, evaluate_expression
from assign import get_current_frame
import re
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
    tokens = clean_up_list_elems(flatten_list(re.split("\)\s*\{", tokens)))
    tokens = clean_up_list_elems(flatten_list(re.split("\}", tokens)))
    print("tokens: " + str(tokens))
    
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
    return
