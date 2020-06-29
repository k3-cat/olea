__all__ = ['InputError']


class InputError(BaseException):
    def __init__(self, errors):
        self.errors = errors
        super().__init__()
