"""normalize car make model year and id type

Revision ID: 4810f0cfe801
Revises: 05f3f6bbbd5c
Create Date: 2026-06-26 18:17:00.395301

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '4810f0cfe801'
down_revision: Union[str, None] = '05f3f6bbbd5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### lookup tables for normalized make/model/year ###
    op.create_table('car_makes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_car_makes_id'), 'car_makes', ['id'], unique=False)

    op.create_table('car_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_car_models_id'), 'car_models', ['id'], unique=False)

    op.create_table('car_years',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('year')
    )
    op.create_index(op.f('ix_car_years_id'), 'car_years', ['id'], unique=False)

    # ### cars table: drop flat make/model/year, add FK columns ###
    op.drop_column('cars', 'make')
    op.drop_column('cars', 'model')
    op.drop_column('cars', 'year')

    op.add_column('cars', sa.Column('make_id', sa.Integer(), nullable=False))
    op.add_column('cars', sa.Column('model_id', sa.Integer(), nullable=False))
    op.add_column('cars', sa.Column('year_id', sa.Integer(), nullable=True))

    op.create_foreign_key('fk_cars_make_id_car_makes', 'cars', 'car_makes', ['make_id'], ['id'])
    op.create_foreign_key('fk_cars_model_id_car_models', 'cars', 'car_models', ['model_id'], ['id'])
    op.create_foreign_key('fk_cars_year_id_car_years', 'cars', 'car_years', ['year_id'], ['id'])

    # ### cars.id: switch from auto-increment integer to a 32-char uuid string ###
    op.alter_column('cars', 'id',
        existing_type=sa.Integer(),
        type_=sa.String(length=32),
        existing_nullable=False)


def downgrade() -> None:
    op.alter_column('cars', 'id',
        existing_type=sa.String(length=32),
        type_=sa.Integer(),
        existing_nullable=False)

    op.drop_constraint('fk_cars_year_id_car_years', 'cars', type_='foreignkey')
    op.drop_constraint('fk_cars_model_id_car_models', 'cars', type_='foreignkey')
    op.drop_constraint('fk_cars_make_id_car_makes', 'cars', type_='foreignkey')

    op.drop_column('cars', 'year_id')
    op.drop_column('cars', 'model_id')
    op.drop_column('cars', 'make_id')

    op.add_column('cars', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('cars', sa.Column('model', sa.String(length=100), nullable=False))
    op.add_column('cars', sa.Column('make', sa.String(length=100), nullable=False))

    op.drop_index(op.f('ix_car_years_id'), table_name='car_years')
    op.drop_table('car_years')

    op.drop_index(op.f('ix_car_models_id'), table_name='car_models')
    op.drop_table('car_models')

    op.drop_index(op.f('ix_car_makes_id'), table_name='car_makes')
    op.drop_table('car_makes')
