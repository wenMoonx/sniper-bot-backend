"""create_user_table

Revision ID: 2bdcabfa3587
Create Date: 2023-11-17 07:05:26.928896

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '2bdcabfa3587'
down_revision = '187a4823ff78'
branch_labels = None
depends_on = None

def upgrade() -> None:
  op.create_table(
    'users',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('username', sa.String()),
    sa.Column('public_address', sa.String()),
    sa.Column('nonce', sa.INTEGER()),
    sa.Column('wallet_count', sa.INTEGER()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('users')