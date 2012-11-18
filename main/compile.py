from bottle import route, run, post, static_file, request
from compile_eval import *

@route('/index')
def load():
    return static_file('index.html', root="./", mimetype='text/html')

@route('/style')
def css():
    return static_file('style.css', root='./', mimetype='text/css')

@route('/jquery')
def jquery():
    return static_file('jquery.js', root='./', mimetype='text/js')

@route('/compile-script')
def compile_script():
    return static_file('compile.js', root='./', mimetype='text/js')

@post('/compile')
def compile():
    s = request.forms.get('data').replace('\n', ' ');
    return s;
    #return s.replace('\n', ' ')

@post('/interpret')
def interpret():
    s = request.forms.get('data');
    return s;


run(host='localhost', port=8080, debug=True)
