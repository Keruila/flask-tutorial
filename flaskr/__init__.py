import os

from flask import Flask

from flaskr import blog
from . import db
from . import auth


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # @app.route('/')
    # def hello_world():
    #     return 'Hello World!'

    db.init_app(app)  # app和数据库连接db 进行整合

    app.register_blueprint(auth.bp)  # 注册蓝图
    app.register_blueprint(blog.bp)  # 注册蓝图
    app.add_url_rule('/', endpoint='index')

    return app


# if __name__ == '__main__':
#     create_app()
