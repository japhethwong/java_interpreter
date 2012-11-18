from bottle import route, run, post, static_file, request

@route('/index')
def load():
    return static_file('index.html', root="./", mimetype='text/html')

@route('/style')
def css():
    return static_file('style.css', root='./', mimetype='text/css')

@route('/jquery')
def jquery():
    return static_file('jquery.js', root='./', mimetype='text/js')

@route('/stuff')
def stuff():
    return static_file('stuff.js', root='./', mimetype='text/js')

@post('/hello')
def hello():
    return request.forms.get('class_name') + request.forms.get('fields')

run(host='localhost', port=8080, debug=True)
