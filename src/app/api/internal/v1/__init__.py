from flask_restplus import Namespace

namespace = Namespace(
    "Internal api v1", path="/api/internal/v1", description="Internal API v1 operations"
)

from app.api.internal.v1 import users
