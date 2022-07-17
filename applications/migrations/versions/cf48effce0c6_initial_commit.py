"""Initial commit

Revision ID: cf48effce0c6
Revises: 
Create Date: 2022-07-17 00:18:44.884375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf48effce0c6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('overallPrice', sa.Float(), nullable=False),
    sa.Column('status', sa.String(length=256), nullable=False),
    sa.Column('timeCreated', sa.DateTime(), nullable=False),
    sa.Column('ownerId', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('productcategory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('productId', sa.Integer(), nullable=False),
    sa.Column('categoryId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['categoryId'], ['categories.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('productorder',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('requestedQuantity', sa.Integer(), nullable=False),
    sa.Column('receivedQuantity', sa.Integer(), nullable=False),
    sa.Column('buyingPrice', sa.Float(), nullable=False),
    sa.Column('productId', sa.Integer(), nullable=False),
    sa.Column('orderId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['orderId'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['productId'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('productorder')
    op.drop_table('productcategory')
    op.drop_table('products')
    op.drop_table('orders')
    op.drop_table('categories')
    # ### end Alembic commands ###
