import os
import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_mysqldb import MySQL
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

mysql = MySQL()
mail = Mail()
serializer = URLSafeTimedSerializer(os.environ.get('SECRET_KEY', 'mi-clave-super-secreta-123456789'))

def create_app():
    app = Flask(__name__, template_folder="template")
    
    # Secret key desde variables de entorno
    app.secret_key = os.environ.get('SECRET_KEY', 'mi-clave-super-secreta-123456789')

    # ------------------ Configuración Base de Datos Railway ------------------
    app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST', 'maglev.proxy.rlwy.net')
    app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER', 'root')
    app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD', 'VFrVhNgTDBiaFcemtYnGGYkxyiUOAKsT')
    app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE', 'railway')
    app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 15970))
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    
    mysql.init_app(app)

    # ------------------ Configuración Correo ------------------
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'enviodecorreosparrilla51@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'tyga bjte atex xajy')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'enviodecorreosparrilla51@gmail.com')
    mail.init_app(app)
    
    # ------------------ Registrar Blueprints ------------------
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.cliente_routes import cliente_bp
    from routes.admin_routes import admin_bp
    from routes.empleado_routes import empleado_bp
    from routes.reportes import reportes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cliente_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(empleado_bp)
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    
    return app