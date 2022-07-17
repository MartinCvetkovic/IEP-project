"""Added FK.

Revision ID: 0b73418d21f8
Revises: ba0a189b01d7
Create Date: 2022-07-10 23:19:38.438175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b73418d21f8'
down_revision = 'ba0a189b01d7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'users', 'roles', ['roleId'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    # ### end Alembic commands ###
