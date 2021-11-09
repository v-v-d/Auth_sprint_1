from app.api import admin

common_args = {
    "name": "Authorization",
    "location": "headers",
    "type": str,
    "help": "Bearer Access Token",
}

role_parser = admin.namespace.parser()
role_parser.add_argument("name", type=str, required=True, help="Role name")
role_parser.add_argument("description", type=str, help="Role description")
