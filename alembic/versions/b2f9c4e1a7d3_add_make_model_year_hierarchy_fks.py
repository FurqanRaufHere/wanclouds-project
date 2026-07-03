"""add make/model/year hierarchy fks

Revision ID: b2f9c4e1a7d3
Revises: 4810f0cfe801
Create Date: 2026-07-04 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'b2f9c4e1a7d3'
down_revision: Union[str, None] = '4810f0cfe801'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The lookup tables change from flat (globally-unique) rows to a make -> model
    # -> year hierarchy. Existing rows have no parent and would violate the new
    # NOT NULL foreign keys, so clear them; the fetch task repopulates on next run.
    # Delete children first to respect existing foreign keys.
    op.execute("DELETE FROM cars")
    op.execute("DELETE FROM car_years")
    op.execute("DELETE FROM car_models")

    # ### car_models: model name is now unique per make, not globally ###
    op.drop_constraint('name', 'car_models', type_='unique')
    op.add_column('car_models', sa.Column('make_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_car_models_make_id_car_makes', 'car_models', 'car_makes', ['make_id'], ['id']
    )
    op.create_unique_constraint('uq_model_make_name', 'car_models', ['make_id', 'name'])

    # ### car_years: year is now unique per model, not globally ###
    op.drop_constraint('year', 'car_years', type_='unique')
    op.add_column('car_years', sa.Column('model_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_car_years_model_id_car_models', 'car_years', 'car_models', ['model_id'], ['id']
    )
    op.create_unique_constraint('uq_year_model_year', 'car_years', ['model_id', 'year'])


def downgrade() -> None:
    op.drop_constraint('uq_year_model_year', 'car_years', type_='unique')
    op.drop_constraint('fk_car_years_model_id_car_models', 'car_years', type_='foreignkey')
    op.drop_column('car_years', 'model_id')
    op.create_unique_constraint('year', 'car_years', ['year'])

    op.drop_constraint('uq_model_make_name', 'car_models', type_='unique')
    op.drop_constraint('fk_car_models_make_id_car_makes', 'car_models', type_='foreignkey')
    op.drop_column('car_models', 'make_id')
    op.create_unique_constraint('name', 'car_models', ['name'])
