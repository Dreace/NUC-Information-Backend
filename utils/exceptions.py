class CustomHTTPException(Exception):
    def __init__(self, code: int, message: str = None):
        self.code = code
        self.message = message


_code_message = {
    -1: "服务器错误",
    -2: "认证失败",
    -3: "登录失败",
    -4: "暂停服务",
    -5: "访问过快",
    -6: "查询失败",
    -7: "查询失败",
}


def custom_abort(code: int, message: str = None):
    if not message:
        message = _code_message.get(code, '未知错误')
    raise CustomHTTPException(code, message)
