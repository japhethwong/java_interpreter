
class JavaException(BaseException):
    def __init__(self, error_type, msg):
        assert isinstance(error_type, str), 'Not a valid error type'
        self.type = error_type
        self.msg = msg

    def __str__(self):
        return self.msg

class CompileException(JavaException):
    def __init__(self, msg):
        super().__init__('CompileException', msg)

class RuntimeException(JavaException):
    pass

