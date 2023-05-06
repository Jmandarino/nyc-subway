"""add inital data

Revision ID: a83abad07acf
Revises: 9516a7c4f8ab
Create Date: 2023-05-01 20:15:57.390407

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "a83abad07acf"
down_revision = "9516a7c4f8ab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("INSERT into stations values (0,'EOL',0)")


def downgrade() -> None:
    pass
