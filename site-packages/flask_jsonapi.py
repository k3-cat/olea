from flask import abort, request
from flask_json import json_response
from json_api.containers import Container

__all__ = ['Container', 'BaseForm']


class BaseForm(Container):
    def __init__(self, data=None):
        if data is None:
            if request.method == 'POST':
                data = request.get_json()
            elif request.method == 'GET':
                data = request.args

        super().__init__()
        self.process_input(data=data)
        if self.errors:
            abort(json_response(status_=400, data_=self.errors))
