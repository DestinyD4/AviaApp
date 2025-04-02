from .extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import login_manager
from .extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # 0 – обычный пользователь, 1 – админ, 2 – супер-админ
    access_level = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.access_level >= 1

    def is_superadmin(self):
        return self.access_level == 2


#
# Модель Cargo (авианакладная)
#
class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = db.Column(db.Integer, primary_key=True)

    # Поля для авианакладной (1А, 1B)
    airline_code = db.Column(db.String(10), nullable=True)   # Код авиакомпании (IATA-префикс)
    awb_number = db.Column(db.String(20), nullable=True)     # Номер авианакладной

    # Отправитель
    shipper_line1 = db.Column(db.String(200), nullable=True)
    shipper_line2 = db.Column(db.String(200), nullable=True)
    shipper_line3 = db.Column(db.String(200), nullable=True)
    shipper_line4 = db.Column(db.String(200), nullable=True)

    # Получатель
    recipient_line1 = db.Column(db.String(200), nullable=True)
    recipient_line2 = db.Column(db.String(200), nullable=True)
    recipient_line3 = db.Column(db.String(200), nullable=True)
    recipient_line4 = db.Column(db.String(200), nullable=True)

    # Описание груза
    cargo_description_line1 = db.Column(db.String(300), nullable=True)
    cargo_description_line2 = db.Column(db.String(300), nullable=True)
    cargo_description_line3 = db.Column(db.String(300), nullable=True)

    # Маршрут («Куда – кем»)
    route1_to = db.Column(db.String(100), nullable=True)
    route1_by = db.Column(db.String(100), nullable=True)
    route2_to = db.Column(db.String(100), nullable=True)
    route2_by = db.Column(db.String(100), nullable=True)
    route3_to = db.Column(db.String(100), nullable=True)
    route3_by = db.Column(db.String(100), nullable=True)

    # Информация об агенте
    agent_line1 = db.Column(db.String(200), nullable=True)
    agent_line2 = db.Column(db.String(200), nullable=True)
    agent_line3 = db.Column(db.String(200), nullable=True)
    agent_code = db.Column(db.String(50), nullable=True)
    airport_departure = db.Column(db.Text, nullable=True)
    airport_arrival = db.Column(db.Text, nullable=True)
    booking = db.Column(db.String(50), nullable=True)

    # Параметры груза
    places_count = db.Column(db.Integer, nullable=True)
    weight_brutto = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=True)

    # Дата, место, подпись
    date_issued = db.Column(db.String(50), nullable=True)
    place_issued = db.Column(db.String(100), nullable=True)
    signature = db.Column(db.String(100), nullable=True)

    # Разбитая информация об оплате (3 строки)
    payment_line1 = db.Column(db.String(200), nullable=True)
    payment_line2 = db.Column(db.String(200), nullable=True)
    payment_line3 = db.Column(db.String(200), nullable=True)

    # Спец. таможенная информация
    special_customs_info = db.Column(db.Text, nullable=True)

class ActionLog(db.Model):
    __tablename__ = 'action_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(150))
    action_type = db.Column(db.String(50))  # 'create', 'update', 'delete'
    target_model = db.Column(db.String(50))  # 'Cargo'
    target_id = db.Column(db.Integer)        # ID объекта, если применимо
    description = db.Column(db.Text)         # Доп. описание
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Log {self.action_type} {self.target_model}:{self.target_id} by {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
