'''
conditionals.py
Contains functions which handle conditional statements (if-else).
@author: Japheth Wong
'''
import re
from exceptions import *
from constants import *
from javarepl import evaluate_expression
from util import clean_up_list_elems, flatten_list

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
        curr_condition = evaluate_expression(conditions_list[index])
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

