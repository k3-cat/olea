from flask import Blueprint

_name = __name__.split('.')[-1]
bp = Blueprint(_name, __name__, url_prefix=f'/{_name}')
