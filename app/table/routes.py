from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Cargo
from app.admin.utils import log_action



table_bp = Blueprint('table', __name__, url_prefix='/table')

@table_bp.before_request
@login_required
def check_admin():
    """
    При каждом обращении к /table/* проверяем, админ ли пользователь.
    Если нет, отдаем 403.
    Уберите этот код, если хотите разрешить CRUD всем авторизованным.
    """
    if not current_user.is_admin():
        return "Доступ запрещён: требуется уровень администратора.", 403

@table_bp.route('/')
def index():
    """Просмотр всех записей (список в виде таблицы) + CRUD-действия."""
    all_cargo = Cargo.query.all()
    return render_template('table/index.html', cargo_list=all_cargo)

@table_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Создание новой записи."""
    if request.method == 'POST':
        new_cargo = Cargo(
            # Новые поля авианакладной:
            airline_code=request.form.get('airline_code') or None,
            awb_number=request.form.get('awb_number') or None,

            # Отправитель:
            shipper_line1=request.form.get('shipper_line1') or None,
            shipper_line2=request.form.get('shipper_line2') or None,
            shipper_line3=request.form.get('shipper_line3') or None,
            shipper_line4=request.form.get('shipper_line4') or None,

            # Получатель:
            recipient_line1=request.form.get('recipient_line1') or None,
            recipient_line2=request.form.get('recipient_line2') or None,
            recipient_line3=request.form.get('recipient_line3') or None,
            recipient_line4=request.form.get('recipient_line4') or None,

            # Описание груза:
            cargo_description_line1=request.form.get('cargo_description_line1') or None,
            cargo_description_line2=request.form.get('cargo_description_line2') or None,
            cargo_description_line3=request.form.get('cargo_description_line3') or None,

            # Маршрут:
            route1_to=request.form.get('route1_to') or None,
            route1_by=request.form.get('route1_by') or None,
            route2_to=request.form.get('route2_to') or None,
            route2_by=request.form.get('route2_by') or None,
            route3_to=request.form.get('route3_to') or None,
            route3_by=request.form.get('route3_by') or None,

            # Инфо об агенте + аэропорты:
            agent_line1=request.form.get('agent_line1') or None,
            agent_line2=request.form.get('agent_line2') or None,
            agent_line3=request.form.get('agent_line3') or None,
            agent_code=request.form.get('agent_code') or None,
            airport_departure=request.form.get('airport_departure') or None,
            airport_arrival=request.form.get('airport_arrival') or None,
            booking=request.form.get('booking') or None,

            # Числовые поля:
            places_count=request.form.get('places_count') or None,
            weight_brutto=request.form.get('weight_brutto') or None,
            volume=request.form.get('volume') or None,

            # Дата, место, подпись:
            date_issued=request.form.get('date_issued') or None,
            place_issued=request.form.get('place_issued') or None,
            signature=request.form.get('signature') or None,

            # Разбитая инфо об оплате:
            payment_line1=request.form.get('payment_line1') or None,
            payment_line2=request.form.get('payment_line2') or None,
            payment_line3=request.form.get('payment_line3') or None,

            # Спец. таможенная инфо:
            special_customs_info=request.form.get('special_customs_info') or None
        )
        db.session.add(new_cargo)
        db.session.commit()
        log_action('create', 'Cargo', new_cargo.id, f'Создана накладная: {new_cargo.airline_code}-{new_cargo.awb_number}')

        return redirect(url_for('table.index'))
    return render_template('table/create.html')

@table_bp.route('/edit/<int:cargo_id>', methods=['GET', 'POST'])
def edit(cargo_id):
    """Редактирование записи."""
    cargo = Cargo.query.get_or_404(cargo_id)
    if request.method == 'POST':
        cargo.airline_code = request.form.get('airline_code') or None
        cargo.awb_number = request.form.get('awb_number') or None

        cargo.shipper_line1 = request.form.get('shipper_line1') or None
        cargo.shipper_line2 = request.form.get('shipper_line2') or None
        cargo.shipper_line3 = request.form.get('shipper_line3') or None
        cargo.shipper_line4 = request.form.get('shipper_line4') or None

        cargo.recipient_line1 = request.form.get('recipient_line1') or None
        cargo.recipient_line2 = request.form.get('recipient_line2') or None
        cargo.recipient_line3 = request.form.get('recipient_line3') or None
        cargo.recipient_line4 = request.form.get('recipient_line4') or None

        cargo.cargo_description_line1 = request.form.get('cargo_description_line1') or None
        cargo.cargo_description_line2 = request.form.get('cargo_description_line2') or None
        cargo.cargo_description_line3 = request.form.get('cargo_description_line3') or None

        cargo.route1_to = request.form.get('route1_to') or None
        cargo.route1_by = request.form.get('route1_by') or None
        cargo.route2_to = request.form.get('route2_to') or None
        cargo.route2_by = request.form.get('route2_by') or None
        cargo.route3_to = request.form.get('route3_to') or None
        cargo.route3_by = request.form.get('route3_by') or None

        cargo.agent_line1 = request.form.get('agent_line1') or None
        cargo.agent_line2 = request.form.get('agent_line2') or None
        cargo.agent_line3 = request.form.get('agent_line3') or None
        cargo.agent_code = request.form.get('agent_code') or None
        cargo.airport_departure = request.form.get('airport_departure') or None
        cargo.airport_arrival = request.form.get('airport_arrival') or None
        cargo.booking = request.form.get('booking') or None

        cargo.places_count = request.form.get('places_count') or None
        cargo.weight_brutto = request.form.get('weight_brutto') or None
        cargo.volume = request.form.get('volume') or None

        cargo.date_issued = request.form.get('date_issued') or None
        cargo.place_issued = request.form.get('place_issued') or None
        cargo.signature = request.form.get('signature') or None

        cargo.payment_line1 = request.form.get('payment_line1') or None
        cargo.payment_line2 = request.form.get('payment_line2') or None
        cargo.payment_line3 = request.form.get('payment_line3') or None

        cargo.special_customs_info = request.form.get('special_customs_info') or None

        db.session.commit()
        log_action('update', 'Cargo', cargo.id, f'Обновлена накладная: {cargo.airline_code}-{cargo.awb_number}')

        return redirect(url_for('table.index'))
    return render_template('table/edit.html', cargo=cargo)

@table_bp.route('/delete/<int:cargo_id>', methods=['POST'])
def delete(cargo_id):
    """Удаление записи."""
    cargo = Cargo.query.get_or_404(cargo_id)
    db.session.delete(cargo)
    db.session.commit()
    log_action('delete', 'Cargo', cargo.id, f'Удалена накладная: {cargo.airline_code}-{cargo.awb_number}')

    return redirect(url_for('table.index'))
