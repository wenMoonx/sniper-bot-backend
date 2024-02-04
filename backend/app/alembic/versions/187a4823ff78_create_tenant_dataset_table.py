"""create_tenant_cyber_security_application_table

Revision ID: 187a4823ff78
Revises: 8e6e805181dd
Create Date: 2023-11-09 02:09:11.445670

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '187a4823ff78'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
  op.create_table(
    "wallets",
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('wallet_address', sa.String()),
    sa.Column('private_key', sa.String()),
    sa.Column('user', sa.String()),
    sa.Column('created_at', sa.DateTime()),
    sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table("wallets")