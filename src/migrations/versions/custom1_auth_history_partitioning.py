"""auth history partitioning

This is custom auth_history table partitioning migration.
Native SQLAlchemy partitioning features like this don't work:

    class AuthHistory(TimestampMixin, db.Model):
        __tablename__ = "auth_history"
        __table_args__ = (
            db.PrimaryKeyConstraint("id", "platform"),
            {
                "postgresql_partition_by": "LIST (platform)",
            },
        )

        ...
        platform = db.Column(db.Enum(PlatformEnum), nullable=False, server_default=PlatformEnum.pc)

        @classmethod
        def __declare_last__(cls):
            ddl = db.DDL(
                '''
                CREATE TABLE IF NOT EXISTS "auth_history_pc" PARTITION OF content."auth_history" FOR VALUES IN ('pc');
                CREATE TABLE IF NOT EXISTS "auth_history_mobile" PARTITION OF content."auth_history" FOR VALUES IN ('mobile');
                CREATE TABLE IF NOT EXISTS "auth_history_tablet" PARTITION OF content."auth_history" FOR VALUES IN ('tablet');
                '''
            )
            event.listen(cls.__table__, "after_create", ddl)

Revision ID: custom1
Revises: c40eccbbe099
Create Date: 2022-01-17 23:46:05.419465

"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, select
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "custom1"
down_revision = "c40eccbbe099"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE content."auth_history_partitioned"
        (
            id uuid not null,
            user_id uuid references content."users",
            timestamp timestamp default now(),
            user_agent text not null,
            ip_addr varchar(100),
            device text,
            created_on timestamp default now(),
            updated_on timestamp default now(),
            platform platformenum default 'pc'::platformenum not null,
            constraint id_platform_uc_ primary key (id, platform)
        )
        PARTITION BY LIST (platform);
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content."auth_history_pc"
        PARTITION OF content."auth_history_partitioned"
        FOR VALUES IN ('pc');
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content."auth_history_mobile"
        PARTITION OF content."auth_history_partitioned"
        FOR VALUES IN ('mobile');
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS content."auth_history_tablet"
        PARTITION OF content."auth_history_partitioned"
        FOR VALUES IN ('tablet');
        """
    )

    # find existing tables
    meta = MetaData(bind=op.get_bind())
    meta.reflect(only=("auth_history", "auth_history_partitioned"), schema="content")
    auth_history_table = Table("auth_history", meta, schema="content")
    auth_history_partitioned_table = Table(
        "auth_history_partitioned", meta, schema="content"
    )

    # insert existing data into partitioned table
    select_stmt = select(auth_history_table)
    insert_stmt = auth_history_partitioned_table.insert().from_select(
        auth_history_partitioned_table.columns, select_stmt
    )
    op.execute(insert_stmt)

    # replace tables
    op.drop_table("auth_history", schema="content")
    op.rename_table("auth_history_partitioned", "auth_history", schema="content")


def downgrade():
    op.rename_table("auth_history", "auth_history_partitioned", schema="content")

    op.create_table(
        "auth_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), default=uuid4, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "timestamp", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("ip_addr", sa.String(length=100)),
        sa.Column("device", sa.Text()),
        sa.Column(
            "created_on", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column(
            "updated_on", sa.DateTime(), server_default=sa.text("now()"), nullable=True
        ),
        sa.Column(
            "platform",
            postgresql.ENUM(
                "pc", "mobile", "tablet", name="platformenum", create_type=False
            ),
            server_default="pc",
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["content.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id", name="auth_history_uc"),
        schema="content",
    )

    # find existing tables
    meta = MetaData(bind=op.get_bind())
    meta.reflect(only=("auth_history", "auth_history_partitioned"), schema="content")
    auth_history_partitioned_table = Table(
        "auth_history_partitioned", meta, schema="content"
    )
    auth_history_table = Table("auth_history", meta, schema="content")

    # insert existing data from partitioned table
    select_stmt = select(auth_history_partitioned_table)
    insert_stmt = auth_history_table.insert().from_select(
        auth_history_table.columns, select_stmt
    )
    op.execute(insert_stmt)

    op.drop_table("auth_history_tablet", schema="content")
    op.drop_table("auth_history_mobile", schema="content")
    op.drop_table("auth_history_pc", schema="content")
    op.drop_table("auth_history_partitioned", schema="content")
