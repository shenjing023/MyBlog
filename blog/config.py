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
    pass


class DevConfig(Config):
    """
    Development config class
    """
    DEBUG=True
    # MySQL connection
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:123@127.0.0.1:3306/LWBlog2'
    SQLALCHEMY_TRACK_MODIFICATIONS=True