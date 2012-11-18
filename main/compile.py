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
    s = 'class ' + request.forms.get('class_name') + ' {'
    s += request.forms.get('fields').replace('\n', ' ')
    s += 'public void ' + request.forms.get('name0') + '() { '
    s += request.forms.get('bind0') + ' } ' 
    if request.forms.get('bind1'):
        s += 'public void ' + request.forms.get('name1') + '() { '
        s += request.forms.get('bind1') + ' } ' 

    if request.forms.get('bind2'):
        s += 'public void ' + request.forms.get('name2') + '() { '
        s += request.forms.get('bind2')+ ' } ' 
    if request.forms.get('bind3'):
        s += 'public void ' + request.forms.get('name3') + '() { '
        s += request.forms.get('bind3')+ ' } ' 
    if request.forms.get('bind4'):
        s += 'public void ' + request.forms.get('name4') + '() { '
        s += request.forms.get('bind4') + ' } '
    if request.forms.get('bind5'):
        s += 'public void ' + request.forms.get('name5') + '() { '
        s += request.forms.get('bind5') + ' } '
    if request.forms.get('bind6'):
        s += 'public void ' + request.forms.get('name6') + '() { '
        s += request.forms.get('bind6') + ' } '

    return str(read_line(s.replace('\n', ' ') +' }'))
    #return s.replace('\n', ' ')

run(host='localhost', port=8080, debug=True)
