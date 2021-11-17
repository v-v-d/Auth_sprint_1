from app.api.admin import namespace
from app.settings import settings

role_parser = namespace.parser()
role_parser.add_argument(
    "name", type=str, required=True, location="form", help="Role name"
)
role_parser.add_argument(
    "description", type=str, location="form", help="Role description"
)

role_list_parser = namespace.parser()
role_list_parser.add_argument("page", type=int, default=0, help="page")
role_list_parser.add_argument(
    "per_page", type=int, default=settings.DEFAULT_PAGE_LIMIT, help="Items per page"
)
