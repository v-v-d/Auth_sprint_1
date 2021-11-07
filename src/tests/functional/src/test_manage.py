from app.models import User
from app.settings import settings
from manage import create_superuser


def test_create_superuser():
    create_superuser()
    user = User.query.filter_by(login=settings.ADMIN_LOGIN).first()

    assert user
    assert user.is_superuser
    assert user.check_password(settings.ADMIN_PASSWORD)
