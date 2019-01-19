from flask import Flask
from flask_login import LoginManager
from config import DevConfig


app=Flask(__name__)

login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='login'
login_manager.init_app(app)

# Import the views module
#views=__import__('views')
from views import *
# Get the config from object of DevConfig
# 使用 onfig.from_object() 而不使用 app.config['DEBUG'] 
# 是因为这样可以加载 class DevConfig 的配置变量集合，而不需要一项一项的添加和修改。
app.config.from_object(DevConfig)

if __name__=="__main__":
    app.run()
