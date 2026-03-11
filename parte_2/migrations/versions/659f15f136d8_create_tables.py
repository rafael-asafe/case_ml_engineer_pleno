"""create tables

Revision ID: 659f15f136d8
Revises:
Create Date: 2026-03-10 17:45:34.531141

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '659f15f136d8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'models',
        sa.Column('model_version', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('model_version'),
    )
    op.create_table(
        'predict_logs',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('input', sa.JSON(), nullable=False),
        sa.Column('output', sa.JSON(), nullable=False),
        sa.Column(
            'timestamp',
            sa.DateTime(),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=False,
        ),
        sa.Column('model_version', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['model_version'], ['models.model_version']),
        sa.PrimaryKeyConstraint('log_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('predict_logs')
    op.drop_table('models')
