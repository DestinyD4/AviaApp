from flask import Flask
from .extensions import db, login_manager
from .models import User
from .auth.routes import auth_bp
from .admin.routes import admin_bp
from .main.routes import main_bp
from .table.routes import table_bp
from .booking.routes import booking_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.secret_key = 'VERY_SECRET_KEY'  # Меняем на свой ключ в продакшен-окружении
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Инициализируем расширения
    db.init_app(app)
    login_manager.init_app(app)

    # Задаём, куда редиректить неавторизованных пользователей
    login_manager.login_view = 'auth.login'

    # Регистрируем блюпринты
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(table_bp)
    app.register_blueprint(booking_bp)

    # Создаём таблицы и абсолютного админа при первом запуске
    with app.app_context():
        db.create_all()

        # Создаём абсолютного админа, если его нет
        if not User.query.filter_by(username='superadmin').first():
            superadmin = User(username='superadmin')
            superadmin.set_password('superadmin')
            superadmin.access_level = 2  # абсолютный админ
            db.session.add(superadmin)
            db.session.commit()
            print("[INFO] Абсолютный админ 'superadmin' создан.")
        else:
            print("[INFO] Абсолютный админ 'superadmin' уже существует.")

    return app
