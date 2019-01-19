import os

class Config():
    """
    Base config class
    """
    SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'


class ProdConfig(Config):
    """
    Production config class
    """
    # MySQL connection
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://test:test@localhost:3306/lwblog'
    SQLALCHEMY_TRACK_MODIFICATIONS=True


class DevConfig(Config):
    """
    Development config class
    """
    DEBUG=True
    # MySQL connection
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://test:test@localhost:3306/lwblog'
    SQLALCHEMY_TRACK_MODIFICATIONS=True
