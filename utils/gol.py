class GlobalValue():
    def __init__(self):
        self._values = {}

    def get_value(self, key: str):
        return self._values.get(key)

    def set_value(self, key: str, value):
        self._values[key] = value


global_values = GlobalValue()
