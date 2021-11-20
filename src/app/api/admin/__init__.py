from flask_restplus import Namespace

namespace = Namespace("Admin", path="/admin", description="Admin API operations")

from app.api.admin import roles, users
