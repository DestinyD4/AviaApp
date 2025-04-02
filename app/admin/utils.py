from datetime import datetime
from flask_login import current_user
from ..extensions import db
from ..models import ActionLog

def log_action(action_type, target_model, target_id=None, description=None):
    log = ActionLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        username=current_user.username if current_user.is_authenticated else 'anonymous',
        action_type=action_type,
        target_model=target_model,
        target_id=target_id,
        description=description,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
