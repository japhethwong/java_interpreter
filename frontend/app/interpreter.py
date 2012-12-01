
"""
interpreter.py

Locally-run Tkinter app used to complement the online frontend. You 
can run the app from the home directory with

    make app

or, alternatively, you can move to <root dir>/frontend/app/ and run

    python3 interpreter.py

Authors: Albert Wu

This program is designed to run on Python3.
"""

import sys
sys.path.append(sys.path[0] + '/../../')

try:
    from tkinter import *
except ImportError:
    print("Couldn't import tkinter")
    exit(1)

from compiler.compile_eval import load_str
from interface.exceptions import CompileException

class MainContainer:
    """Main container of the interpreter GUI.
    
    DESCRIPTION:
    There are two major components: the Compiler component and the 
    Interpreter component.
    """
    def __init__(self, parent):
        self.display = Frame(parent)
        self.display.pack()

        self.compiler = Compiler(self.display)
        self.interpreter = Interpreter(self.display)
        

class Compiler:
    """Compiler component of the Interpreter GUI.

    DESCRIPTION:
    User can type Java code into the text area and press the Compile
    button to compile and load code into the interpreter.

    TODO:
    - load classes into interpreter after compiling
    """
    def __init__(self, parent):
        self.display = Frame(parent)
        self.display.pack(side=LEFT)

        self.title = Label(self.display, text="Compiler")
        self.title.pack()

        self.textarea = Text(self.display)
        self.textarea.pack()

        self.compile_btn = Button(self.display, text="Compile",
                                command=self.compile)
        self.compile_btn.pack()

    def compile(self):
        """Callback method used for the compile button."""
        try:
            classes = load_str(self.textarea.get(1.0, END))
        except CompileException as e:
            # TODO
            print(e)
        else:
            for cls in classes.values():
                print(cls)
        

class Interpreter:
    """Interpreter component of the Interpreter GUI.
    
    TODO:
    - connect display to interpreter
    - add a command line
    """
    def __init__(self, parent):
        self.display = Frame(parent)
        self.display.pack(side=LEFT)

        self.title = Label(self.display, text="Interpreter")
        self.title.pack()

        self.textarea = Text(self.display)
        self.write('')
        self.textarea.pack()

    def write(self, text):
        """Subroutine for writing to standard output (the screen)"""
        text = text.replace('\n', '\n      ')
        self.textarea.config(state=NORMAL)
        self.textarea.insert(END, text + '\nJava> ')
        self.textarea.config(state=DISABLED)

root = Tk()
root.title("Java Interpreter")

main = MainContainer(root)
root.mainloop()
