"""Fully prepared database tables. Revision ID: 62aa357c63ff Revises: None Create Date: 2024-09-18 11:52"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "62aa357c63ff"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column(
            "message_part_id", sa.String(), nullable=False, server_default="00000000-0000-0000-0000-000000000000"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_conversation_id"), "events", ["conversation_id"], unique=False)


    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True),  # VARCHAR to ensure compatibility
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("conversation_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversations_conversation_id"), "conversations", ["conversation_id"], unique=False)
    op.create_index(op.f("ix_conversations_user_id"), "conversations", ["user_id"], unique=False)


    op.create_table(
        "history",
        sa.Column("id", sa.Integer(), primary_key = True),
        sa.Column("conversation_id", sa.String(), nullable=False),
        # Now clearly defined as String to match conversations.id
        sa.Column("author_type", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("chatbot_label", sa.String(), nullable=False, server_default="unknown"),
        sa.Column(
            "message_part_id", sa.String(), nullable=False, server_default="00000000-0000-0000-0000-000000000000"
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("idx_history_conversation_label_date"),
        "history",
        ["conversation_id", "chatbot_label", "created_at"],
        unique=False,
    )

    table_names = ["conversations", "events", "history"]
    for table_name in table_names:
        op.alter_column(
            table_name,
            "updated_at",
            existing_type=postgresql.TIMESTAMP(),
            nullable=False,
            server_default=sa.text("NOW()"),
            existing_server_default=None,
        )

    for table_name in table_names:
        op.execute(
            f"""
            CREATE OR REPLACE FUNCTION update_{table_name}_updated_at_column() 
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """
        )
        op.execute(
            f"""
            CREATE TRIGGER update_{table_name}_updated_at_before_update
            BEFORE UPDATE ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION update_{table_name}_updated_at_column();
        """
        )


def downgrade() -> None:
    table_names = ["conversations", "events", "history"]
    for table_name in table_names:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table_name}_updated_at_before_update ON {table_name}")
        op.execute(f"DROP FUNCTION IF EXISTS update_{table_name}_updated_at_column()")

    for table_name in table_names:
        op.alter_column(
            table_name,
            "updated_at",
            existing_type=postgresql.TIMESTAMP(),
            nullable=True,
            server_default=None,
            existing_server_default=sa.text("NOW()"),
        )

    op.create_index("ix_history_conversation_id", "history", ["conversation_id"], unique=False)

    op.drop_index("idx_history_conversation_label_date", table_name="history")

    op.drop_column("history", "chatbot_label")
    op.drop_column("history", "message_part_id")

    op.drop_column("events", "message_part_id")

    op.drop_index(op.f("ix_history_conversation_id"), table_name="history")
    op.drop_table("history")

    op.drop_index(op.f("ix_conversations_user_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_conversation_id"), table_name="conversations")
    op.drop_table("conversations")

    op.drop_index(op.f("ix_events_conversation_id"), table_name="events")
    op.drop_table("events")
