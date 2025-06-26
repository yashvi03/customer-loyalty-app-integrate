import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = "ddca54dff0ff14707019155675890066ebe40a930e8ee474b82007a8f610dcc8"
    #DATABASE_URI = os.environ['DATABASE_URL']
    DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    ENV = os.environ.get('FLASK_ENV', 'production')
    #SQLALCHEMY_DATABASE_URI = "postgres://dbzgwivvjolpsl:ddca54dff0ff14707019155675890066ebe40a930e8ee474b82007a8f610dcc8@ec2-34-232-24-202.compute-1.amazonaws.com:5432/d1ac5qkrnv97fd?sslmode=require"


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    ENV = 'staging'


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    ENV = 'development'


class TestingConfig(Config):
    TESTING = True
    ENV = 'testing'