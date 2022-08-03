from flask import Flask
from flask_mysqldb import MySQL
#import bootstrap: pip install flask_bootstrap
from flask_bootstrap import Bootstrap
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
UPLOAD_FOLDER = 'Capstone/upload_file'


def create_app():
    app = Flask(__name__)
    cors = CORS(app)
    global ma
    global db
    ma=Marshmallow(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:''@localhost/flask2'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db=SQLAlchemy(app)
    #Secret key for privacy DON'T SHARE!
    app.config['CORS_HEADER'] = 'Content-Type'
    app.config['SECRET_KEY'] = '14320edb76fb8c6018c28b07'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'flask2'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    global mysql
    mysql = MySQL(app)
    Bootstrap(app)

    from .views import views
    from .auth import auth
    from .project import project
    from .existedzone import existedzone
    from .refreshedzone import refreshedzone
    from .dashboard import dashboard
    from .layout import layout
    from .projecthistory import projecthistory
    from .zonehistory import zonehistory
    from .crates import crates
    from .zonestatistics import zonestatistics
    from .history import history
    from .playground import playground
    
    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    app.register_blueprint(project,url_prefix='/')
    app.register_blueprint(existedzone,url_prefix='/')
    app.register_blueprint(refreshedzone,url_prefix='/')
    app.register_blueprint(dashboard,url_prefix='/dashboard/')
    app.register_blueprint(layout,url_prefix='/layout/')
    app.register_blueprint(playground, url_prefix='/playground/')
    app.register_blueprint(projecthistory,url_prefix='/project/history/')

    app.register_blueprint(history, url_prefix='/history/')

    app.register_blueprint(zonehistory,url_prefix='/zone/history/')
    app.register_blueprint(crates,url_prefix='/')
    app.register_blueprint(zonestatistics,url_prefix='/stats/')






    return app
