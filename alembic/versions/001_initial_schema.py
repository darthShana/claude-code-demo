"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-12-23 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create quotes table
    op.create_table('quotes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quote_ref', sa.String(length=50), nullable=False),
        sa.Column('rego_or_vin', sa.String(length=100), nullable=False),
        sa.Column('max_shortfall', sa.String(length=20), nullable=False),
        sa.Column('quote_expiry_date', sa.String(length=20), nullable=True),
        sa.Column('gst_rate', sa.String(length=10), nullable=True),
        sa.Column('policy_status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('agent_code', sa.String(length=50), nullable=True),
        sa.Column('brand_code', sa.String(length=50), nullable=True),
        sa.Column('user_code', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quotes_id'), 'quotes', ['id'], unique=False)
    op.create_index(op.f('ix_quotes_quote_ref'), 'quotes', ['quote_ref'], unique=True)

    # Create vehicle_details table
    op.create_table('vehicle_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quote_id', sa.Integer(), nullable=False),
        sa.Column('registration', sa.String(length=20), nullable=True),
        sa.Column('vin', sa.String(length=100), nullable=False),
        sa.Column('make', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('year', sa.String(length=10), nullable=False),
        sa.Column('cc_rating', sa.String(length=20), nullable=False),
        sa.Column('fuel_type', sa.String(length=30), nullable=False),
        sa.Column('odometer_reading', sa.String(length=20), nullable=False),
        sa.Column('body_colour', sa.String(length=50), nullable=False),
        sa.Column('body_style', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['quote_id'], ['quotes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vehicle_details_id'), 'vehicle_details', ['id'], unique=False)

    # Create gap_premiums table
    op.create_table('gap_premiums',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quote_id', sa.Integer(), nullable=False),
        sa.Column('wholesale_amount', sa.Float(), nullable=False),
        sa.Column('retail_amount', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['quote_id'], ['quotes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gap_premiums_id'), 'gap_premiums', ['id'], unique=False)

    # Create bind_requests table
    op.create_table('bind_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quote_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_value', sa.Integer(), nullable=False),
        sa.Column('vehicle_insurer', sa.String(length=100), nullable=False),
        sa.Column('retail_premium_adjustment', sa.Float(), nullable=True),
        sa.Column('agree_to_declaration', sa.Boolean(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('loan_contract_number', sa.String(length=100), nullable=True),
        sa.Column('applicants_email', sa.Text(), nullable=True),
        sa.Column('vehicle_deposit_provided', sa.Boolean(), nullable=False),
        sa.Column('continue_purchase', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('agent_code', sa.String(length=50), nullable=True),
        sa.Column('brand_code', sa.String(length=50), nullable=True),
        sa.Column('user_code', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['quote_id'], ['quotes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bind_requests_id'), 'bind_requests', ['id'], unique=False)

    # Create finance_details table
    op.create_table('finance_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bind_request_id', sa.Integer(), nullable=False),
        sa.Column('company', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('balance_payable', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.String(length=20), nullable=False),
        sa.Column('contract_length', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['bind_request_id'], ['bind_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_finance_details_id'), 'finance_details', ['id'], unique=False)

    # Create applicants table
    op.create_table('applicants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bind_request_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('sur_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['bind_request_id'], ['bind_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applicants_id'), 'applicants', ['id'], unique=False)

    # Create applicant_postal_addresses table
    op.create_table('applicant_postal_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('address_line1', sa.String(length=200), nullable=False),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('suburb', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('postcode', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applicant_postal_addresses_id'), 'applicant_postal_addresses', ['id'], unique=False)

    # Create applicant_contacts table
    op.create_table('applicant_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('mobile_num', sa.String(length=50), nullable=True),
        sa.Column('email_address', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_applicant_contacts_id'), 'applicant_contacts', ['id'], unique=False)

    # Create business_applicants table
    op.create_table('business_applicants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(length=200), nullable=False),
        sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_applicants_id'), 'business_applicants', ['id'], unique=False)

    # Create joint_applicants table
    op.create_table('joint_applicants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('surname', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['applicant_id'], ['applicants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_joint_applicants_id'), 'joint_applicants', ['id'], unique=False)

    # Create business_contact_persons table
    op.create_table('business_contact_persons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_applicant_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('surname', sa.String(length=100), nullable=False),
        sa.Column('business_contact_type', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['business_applicant_id'], ['business_applicants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_contact_persons_id'), 'business_contact_persons', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_business_contact_persons_id'), table_name='business_contact_persons')
    op.drop_table('business_contact_persons')
    op.drop_index(op.f('ix_joint_applicants_id'), table_name='joint_applicants')
    op.drop_table('joint_applicants')
    op.drop_index(op.f('ix_business_applicants_id'), table_name='business_applicants')
    op.drop_table('business_applicants')
    op.drop_index(op.f('ix_applicant_contacts_id'), table_name='applicant_contacts')
    op.drop_table('applicant_contacts')
    op.drop_index(op.f('ix_applicant_postal_addresses_id'), table_name='applicant_postal_addresses')
    op.drop_table('applicant_postal_addresses')
    op.drop_index(op.f('ix_applicants_id'), table_name='applicants')
    op.drop_table('applicants')
    op.drop_index(op.f('ix_finance_details_id'), table_name='finance_details')
    op.drop_table('finance_details')
    op.drop_index(op.f('ix_bind_requests_id'), table_name='bind_requests')
    op.drop_table('bind_requests')
    op.drop_index(op.f('ix_gap_premiums_id'), table_name='gap_premiums')
    op.drop_table('gap_premiums')
    op.drop_index(op.f('ix_vehicle_details_id'), table_name='vehicle_details')
    op.drop_table('vehicle_details')
    op.drop_index(op.f('ix_quotes_quote_ref'), table_name='quotes')
    op.drop_index(op.f('ix_quotes_id'), table_name='quotes')
    op.drop_table('quotes')