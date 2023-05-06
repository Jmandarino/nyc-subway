"""create inital tables

Revision ID: 9516a7c4f8ab
Revises: 
Create Date: 2023-05-01 19:38:02.816843

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9516a7c4f8ab"
down_revision = None
branch_labels = None
depends_on = None

ENUM_NAME = "transaction_type"


def upgrade() -> None:
    # we want to avoid tying the most up-to-date declarative_base
    # to a Db migration, models can be updated
    op.create_table(
        "train_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50)),
        sa.Column("cost", sa.DECIMAL),
    )
    op.create_table(
        "stations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(50)),
        sa.Column("cost", sa.DECIMAL),
    )

    op.create_table(
        "connections",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "from_station_id", sa.Integer, sa.ForeignKey("stations.id"), nullable=False
        ),
        sa.Column(
            "to_station_id", sa.Integer, sa.ForeignKey("stations.id"), nullable=False
        ),
        sa.Column("distance", sa.Integer, default=0),
        sa.Column("line", sa.Integer, sa.ForeignKey("train_lines.id"), nullable=False),
    )

    op.create_table(
        "cards",
        sa.Column("number", sa.VARCHAR(64), primary_key=True),
        sa.Column("balance", sa.DECIMAL),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "card", sa.VARCHAR(64), sa.ForeignKey("cards.number"), nullable=False
        ),
        sa.Column("station", sa.Integer, sa.ForeignKey("stations.id"), nullable=False),
        sa.Column("cost", sa.DECIMAL, nullable=False),
        sa.Column("balance_remaining", sa.DECIMAL, nullable=False),
        sa.Column(
            "type",
            sa.Enum("exit", "enter", name=ENUM_NAME),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("connections")
    op.drop_table("stations")
    op.drop_table("train_lines")
    op.drop_table("cards")

    op.execute(f"DROP TYPE IF EXISTS {ENUM_NAME}")
