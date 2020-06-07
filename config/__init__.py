def load_config(app, env):
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config.from_object('default')
    app.config.from_object('instance')

    if env != 'production':
        app.config.from_object(env)
