"""DB更新

Revision ID: b90e2093e414
Revises: 01004774a0ce
Create Date: 2025-07-15 20:40:43.846054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b90e2093e414'
down_revision = '01004774a0ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('modbus_port', sa.Integer(), nullable=True))

    with op.batch_alter_table('plc_data_configs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plc_data_type', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plc_data_configs', schema=None) as batch_op:
        batch_op.drop_column('plc_data_type')

    with op.batch_alter_table('equipments', schema=None) as batch_op:
        batch_op.drop_column('modbus_port')

    # ### end Alembic commands ###
