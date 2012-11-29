import sys
sys.path.append(sys.path[0] + '/../')

from compiler.compile_eval import eval_class
from compiler.compile_parse import read_line
from interface.primitives import Instance

cls = eval_class(read_line("""
class Ex { 
    int x; 

    Ex (String x) {

    } 

    int foo(String x) {

    }
    x = 3;
}
""")[0])
i = Instance(cls)
