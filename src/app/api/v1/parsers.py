from app.api.v1 import namespace
from app.settings import settings


login_parser = namespace.parser()
login_parser.add_argument(
    "login", type=str, required=True, location="form", help="Login"
)
login_parser.add_argument(
    "password", type=str, required=True, location="form", help="Password"
)

signup_parser = namespace.parser()
signup_parser.add_argument(
    "login", type=str, required=True, location="form", help="Login"
)
signup_parser.add_argument(
    "password", type=str, required=True, location="form", help="Password"
)
signup_parser.add_argument(
    "email", type=str, location="form", help="Email"
)  # TODO: add email validation

user_password_parser = namespace.parser()
user_password_parser.add_argument(
    "old_password", type=str, required=True, location="form", help="Old password"
)
user_password_parser.add_argument(
    "new_password", type=str, required=True, location="form", help="New password"
)

user_history_parser = namespace.parser()
user_history_parser.add_argument("page", type=int, default=0, help="page")
user_history_parser.add_argument(
    "per_page", type=int, default=settings.DEFAULT_PAGE_LIMIT, help="Items per page"
)
