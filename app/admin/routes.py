from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..models import User, ActionLog
from .utils import log_action  

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if not current_user.is_admin():
        return "У вас нет прав доступа к этой странице.", 403

    message = {}

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create_user':
            new_username = request.form.get('username')
            new_password = request.form.get('password')
            if new_username and new_password:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    message['error'] = "Пользователь с таким именем уже существует"
                else:
                    new_user = User(username=new_username)
                    new_user.set_password(new_password)
                    db.session.add(new_user)
                    db.session.commit()
                    message['success'] = f"Пользователь {new_username} успешно создан."

                    log_action(
                        action_type='create',
                        target_model='User',
                        target_id=new_user.id,
                        description=f"Создан пользователь: {new_user.username}"
                    )
            else:
                message['error'] = "Укажите имя и пароль нового пользователя."

        elif action in ['promote', 'demote', 'delete_user']:
            if not current_user.is_superadmin():
                message['error'] = "У вас нет прав на изменение прав пользователей."
            else:
                user_id = request.form.get('user_id')
                user = User.query.get(user_id)
                if not user:
                    message['error'] = "Пользователь не найден."
                elif user.is_superadmin():
                    message['error'] = "Нельзя удалить или изменить абсолютного админа."
                elif action == 'promote':
                    user.access_level = 1
                    db.session.commit()
                    message['success'] = f"Пользователь {user.username} повышен до админа."

                    log_action(
                        action_type='update',
                        target_model='User',
                        target_id=user.id,
                        description=f"Назначен админом: {user.username}"
                    )
                elif action == 'demote':
                    user.access_level = 0
                    db.session.commit()
                    message['success'] = f"Пользователь {user.username} понижен до обычного."

                    log_action(
                        action_type='update',
                        target_model='User',
                        target_id=user.id,
                        description=f"Снят с админки: {user.username}"
                    )
                elif action == 'delete_user':
                    username = user.username
                    user_id = user.id
                    db.session.delete(user)
                    db.session.commit()
                    message['success'] = f"Пользователь {username} удалён."

                    log_action(
                        action_type='delete',
                        target_model='User',
                        target_id=user_id,
                        description=f"Удалён пользователь: {username}"
                    )

    # Фильтрация пользователей
    filter_value = request.args.get('filter', 'all')
    query = User.query
    if filter_value == 'users':
        query = query.filter(User.access_level == 0)
    elif filter_value == 'admins':
        query = query.filter(User.access_level == 1)
    elif filter_value == 'superadmins':
        query = query.filter(User.access_level == 2)

    users = query.order_by(User.access_level.desc(), User.username.asc()).all()

    # Журнал логов (только для супер-админа)
    logs = ActionLog.query.order_by(ActionLog.timestamp.desc()).limit(50).all() if current_user.is_superadmin() else []

    return render_template(
        'admin/admin.html',
        users=users,
        logs=logs,
        current_user=current_user,
        filter_value=filter_value,
        **message
    )
