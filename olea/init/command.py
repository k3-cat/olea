import click
from flask.cli import with_appcontext


def register_commands(app):
    '''Register Click commands.'''

    from ..exts import db

    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        '''Clear existing data and create new tables.'''
        db.drop_all()
        db.create_all()
        click.echo('\nDatabase Initialized')

    app.cli.add_command(init_db_command)
