"""initial migration

Revision ID: 8d5b345dbb08
Revises: 
Create Date: 2025-04-17 15:43:30.750167

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '8d5b345dbb08'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('street', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('state', sa.String(length=100), nullable=False),
    sa.Column('zip_code', sa.String(length=20), nullable=False),
    sa.Column('country', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cart',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inventory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_sales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity_sold', sa.Integer(), nullable=False),
    sa.Column('total_revenue', sa.Float(), nullable=False),
    sa.Column('recorded_on', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_views',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('viewed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('runner_location',
    sa.Column('runner_id', sa.Integer(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['runner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('runner_id')
    )
    op.create_table('delivery_analytics',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('runner_id', sa.Integer(), nullable=True),
    sa.Column('order_placed_at', sa.DateTime(), nullable=False),
    sa.Column('order_picked_at', sa.DateTime(), nullable=True),
    sa.Column('order_delivered_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['runner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('price_at_order_time', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_status_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('old_status', sa.String(length=50), nullable=False),
    sa.Column('new_status', sa.String(length=50), nullable=False),
    sa.Column('changed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('payment_method', sa.String(length=30), nullable=False),
    sa.Column('transaction_id', sa.String(length=100), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('runner_assignments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('runner_id', sa.Integer(), nullable=False),
    sa.Column('assigned_at', sa.DateTime(), nullable=True),
    sa.Column('picked_up_at', sa.DateTime(), nullable=True),
    sa.Column('delivered_at', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['runner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('delivery_boy', schema=None) as batch_op:
        batch_op.drop_index('email')
        batch_op.drop_index('phone')

    op.drop_table('delivery_boy')
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint('order_ibfk_1', type_='foreignkey')
        batch_op.drop_column('products')
        batch_op.drop_column('payment_mode')
        batch_op.drop_column('delivery_boy_id')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isActive', sa.Boolean(), nullable=False))
        batch_op.drop_column('isActive')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('isActive', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
        batch_op.drop_column('isActive')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('delivery_boy_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('payment_mode', mysql.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('products', mysql.JSON(), nullable=False))
        batch_op.create_foreign_key('order_ibfk_1', 'user', ['delivery_boy_id'], ['id'])

    op.create_table('delivery_boy',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('phone', mysql.VARCHAR(length=15), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('status', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('delivery_status', mysql.VARCHAR(length=15), nullable=True),
    sa.Column('isActive', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('delivery_boy', schema=None) as batch_op:
        batch_op.create_index('phone', ['phone'], unique=True)
        batch_op.create_index('email', ['email'], unique=True)

    op.drop_table('runner_assignments')
    op.drop_table('payments')
    op.drop_table('order_status_history')
    op.drop_table('order_items')
    op.drop_table('delivery_analytics')
    op.drop_table('runner_location')
    op.drop_table('product_views')
    op.drop_table('product_sales')
    op.drop_table('inventory')
    op.drop_table('cart')
    op.drop_table('address')
    # ### end Alembic commands ###
