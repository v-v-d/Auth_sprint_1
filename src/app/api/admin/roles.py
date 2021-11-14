

@admin_namespace.route("/roles")
class RolesView(BaseJWTResource):
    @admin_namespace.doc("get list of roles")
    @admin_namespace.expect(role_list_parser)
    @admin_namespace.marshal_with(admin_role_schema, as_list=True, code=http.HTTPStatus.OK)
    def get(self):
        args = role_list_parser.parse_args()
        queryset = Role.query.order_by(Role.created_on.asc())
        paginator = queryset.paginate(
            page=args["page"], per_page=args["per_page"], error_out=False
        )

        return paginator.items

    @admin_namespace.doc("create role", responses={
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.CREATED: "Created",
    })
    @admin_namespace.expect(role_parser)
    @admin_namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.CREATED)
    def post(self):
        new_role = user_datastore.create_role(**role_parser.parse_args())

        try:
            with session_scope() as session:
                session.add(new_role)
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return new_role, http.HTTPStatus.CREATED


@admin_namespace.route("/roles/<int:role_id>")
class SpecificRolesView(BaseJWTResource):
    @admin_namespace.doc("change role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
    })
    @admin_namespace.expect(role_parser)
    @admin_namespace.marshal_with(admin_role_schema, code=http.HTTPStatus.OK)
    def patch(self, role_id: int):
        role = Role.query.get_or_404(role_id)

        args = role_parser.parse_args()

        if args["name"] in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        try:
            with session_scope():
                role.update_or_skip(**role_parser.parse_args())
        except IntegrityError:
            raise exceptions.BadRequest("Already exists.")

        return role

    @admin_namespace.doc("delete role", responses={
        http.HTTPStatus.NOT_FOUND: "Not Found",
        http.HTTPStatus.BAD_REQUEST: "Bad Request",
        http.HTTPStatus.NO_CONTENT: "No Content",
    })
    def delete(self, role_id: int):
        role = Role.query.get_or_404(role_id)

        if role.name in Role.Meta.PROTECTED_ROLE_NAMES:
            raise exceptions.BadRequest("This role is protected.")

        with session_scope() as session:
            session.delete(role)

        return "", http.HTTPStatus.NO_CONTENT
