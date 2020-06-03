#jsonform


with flask
----
To integrate jsonfrom with flask, use this workaround and inherit from `BaseForm` when defining you forms. It can extract json data from request and handle errors if they exist. Package `flaks_json` is required for this workaround, read [their doc](https://pythonhosted.org/Flask-JSON/) to learn more.

**However, using forms in the `SubForm` field, forms should keep inherit from `JsonForm`.**

    from flask import abort, request
    from flask_json import json_response

    from jsonform import FormError, JsonForm


    class BaseForm(JsonForm):
        def __init__(self, data=None):
            if data is None and BaseForm.is_submitted():
                data = request.get_json()
            try:
                super().__init__(data=data)
            except FormError as e:
                abort(json_response(status_=400, data_=e))

        @staticmethod
        def is_submitted():
            return bool(request)
