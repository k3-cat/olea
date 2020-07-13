import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class Template():
    def __init__(self, client, path):
        self.path = path / 'sendergrid_templates.json'

        try:
            with self.path.open('r') as f:
                self.templates = json.load(f)

        except FileNotFoundError:
            # missing api
            raise

    def __getitem__(self, key):
        return self.templates[key]


class SendGrid():
    def __init__(self, app=None):
        self.sender = ''
        self.client = None
        self.templates = None

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.sender = app.config['SENDGRID_SENDER']
        self.client = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
        self.templates = Template(self.client, app.config['DATA_FOLDER'])

    def send(self, to, template_name, **template_data):
        mail = Mail(from_email=self.sender, to_emails=to)
        mail.template_id = self.templates[template_name]
        mail.dynamic_template_data = template_data

        self.client.send(mail)
