"""Create enhanced advertising system tables

Revision ID: 18
Revises: 17
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '18'
down_revision = '17_create_messaging_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ad_types enum
    ad_type_enum = postgresql.ENUM('banner', 'popup', 'sidebar', 'in_feed', 'search_result', 'product_page', 'category_page', 'homepage', name='ad_type_enum')
    ad_type_enum.create(op.get_bind())
    
    # Create ad_status enum
    ad_status_enum = postgresql.ENUM('draft', 'pending', 'active', 'paused', 'rejected', 'expired', name='ad_status_enum')
    ad_status_enum.create(op.get_bind())
    
    # Create bidding_type enum
    bidding_type_enum = postgresql.ENUM('cpc', 'cpm', 'cpa', 'fixed', name='bidding_type_enum')
    bidding_type_enum.create(op.get_bind())
    
    # Create ads table
    op.create_table('ads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ad_type', postgresql.ENUM('banner', 'popup', 'sidebar', 'in_feed', 'search_result', 'product_page', 'category_page', 'homepage', name='ad_type_enum'), nullable=False),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'active', 'paused', 'rejected', 'expired', name='ad_status_enum'), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('video_url', sa.String(length=500), nullable=True),
        sa.Column('landing_page_url', sa.String(length=500), nullable=False),
        sa.Column('targeting_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_locations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_interests', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_devices', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('target_time_slots', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('bidding_type', postgresql.ENUM('cpc', 'cpm', 'cpa', 'fixed', name='bidding_type_enum'), nullable=True),
        sa.Column('bid_amount', sa.Float(), nullable=False),
        sa.Column('daily_budget', sa.Float(), nullable=True),
        sa.Column('total_budget', sa.Float(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('spend', sa.Float(), nullable=True),
        sa.Column('ctr', sa.Float(), nullable=True),
        sa.Column('cpc', sa.Float(), nullable=True),
        sa.Column('cpm', sa.Float(), nullable=True),
        sa.Column('is_priority', sa.Boolean(), nullable=True),
        sa.Column('priority_score', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_served_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ads_id'), 'ads', ['id'], unique=False)
    op.create_index(op.f('ix_ads_seller_id'), 'ads', ['seller_id'], unique=False)
    op.create_index(op.f('ix_ads_status'), 'ads', ['status'], unique=False)
    op.create_index(op.f('ix_ads_ad_type'), 'ads', ['ad_type'], unique=False)
    op.create_index(op.f('ix_ads_start_date'), 'ads', ['start_date'], unique=False)
    op.create_index(op.f('ix_ads_end_date'), 'ads', ['end_date'], unique=False)
    
    # Create ad_campaigns table
    op.create_table('ad_campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', postgresql.ENUM('draft', 'pending', 'active', 'paused', 'rejected', 'expired', name='ad_status_enum'), nullable=True),
        sa.Column('objective', sa.String(length=100), nullable=False),
        sa.Column('target_audience', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('budget_type', sa.String(length=50), nullable=True),
        sa.Column('daily_budget', sa.Float(), nullable=True),
        sa.Column('total_budget', sa.Float(), nullable=True),
        sa.Column('total_impressions', sa.Integer(), nullable=True),
        sa.Column('total_clicks', sa.Integer(), nullable=True),
        sa.Column('total_conversions', sa.Integer(), nullable=True),
        sa.Column('total_spend', sa.Float(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_campaigns_id'), 'ad_campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_ad_campaigns_seller_id'), 'ad_campaigns', ['seller_id'], unique=False)
    op.create_index(op.f('ix_ad_campaigns_status'), 'ad_campaigns', ['status'], unique=False)
    
    # Add campaign_id to ads table
    op.add_column('ads', sa.Column('campaign_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'ads', 'ad_campaigns', ['campaign_id'], ['id'])
    op.create_index(op.f('ix_ads_campaign_id'), 'ads', ['campaign_id'], unique=False)
    
    # Create ad_impressions table
    op.create_table('ad_impressions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ad_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('page_url', sa.String(length=500), nullable=True),
        sa.Column('referrer_url', sa.String(length=500), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=100), nullable=True),
        sa.Column('os', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_impressions_id'), 'ad_impressions', ['id'], unique=False)
    op.create_index(op.f('ix_ad_impressions_ad_id'), 'ad_impressions', ['ad_id'], unique=False)
    op.create_index(op.f('ix_ad_impressions_user_id'), 'ad_impressions', ['user_id'], unique=False)
    op.create_index(op.f('ix_ad_impressions_session_id'), 'ad_impressions', ['session_id'], unique=False)
    op.create_index(op.f('ix_ad_impressions_created_at'), 'ad_impressions', ['created_at'], unique=False)
    
    # Create ad_clicks table
    op.create_table('ad_clicks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ad_id', sa.Integer(), nullable=False),
        sa.Column('impression_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('click_position', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('page_url', sa.String(length=500), nullable=True),
        sa.Column('referrer_url', sa.String(length=500), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('device_type', sa.String(length=50), nullable=True),
        sa.Column('browser', sa.String(length=100), nullable=True),
        sa.Column('os', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ),
        sa.ForeignKeyConstraint(['impression_id'], ['ad_impressions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_clicks_id'), 'ad_clicks', ['id'], unique=False)
    op.create_index(op.f('ix_ad_clicks_ad_id'), 'ad_clicks', ['ad_id'], unique=False)
    op.create_index(op.f('ix_ad_clicks_impression_id'), 'ad_clicks', ['impression_id'], unique=False)
    op.create_index(op.f('ix_ad_clicks_user_id'), 'ad_clicks', ['user_id'], unique=False)
    op.create_index(op.f('ix_ad_clicks_created_at'), 'ad_clicks', ['created_at'], unique=False)
    
    # Create ad_conversions table
    op.create_table('ad_conversions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ad_id', sa.Integer(), nullable=False),
        sa.Column('click_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('conversion_type', sa.String(length=100), nullable=False),
        sa.Column('conversion_value', sa.Float(), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ),
        sa.ForeignKeyConstraint(['click_id'], ['ad_clicks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_conversions_id'), 'ad_conversions', ['id'], unique=False)
    op.create_index(op.f('ix_ad_conversions_ad_id'), 'ad_conversions', ['ad_id'], unique=False)
    op.create_index(op.f('ix_ad_conversions_click_id'), 'ad_conversions', ['click_id'], unique=False)
    op.create_index(op.f('ix_ad_conversions_user_id'), 'ad_conversions', ['user_id'], unique=False)
    op.create_index(op.f('ix_ad_conversions_conversion_type'), 'ad_conversions', ['conversion_type'], unique=False)
    op.create_index(op.f('ix_ad_conversions_created_at'), 'ad_conversions', ['created_at'], unique=False)
    
    # Create ad_bids table
    op.create_table('ad_bids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ad_id', sa.Integer(), nullable=False),
        sa.Column('auction_id', sa.String(length=255), nullable=False),
        sa.Column('bid_amount', sa.Float(), nullable=False),
        sa.Column('bid_type', postgresql.ENUM('cpc', 'cpm', 'cpa', 'fixed', name='bidding_type_enum'), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('won', sa.Boolean(), nullable=True),
        sa.Column('winning_bid', sa.Float(), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_bids_id'), 'ad_bids', ['id'], unique=False)
    op.create_index(op.f('ix_ad_bids_ad_id'), 'ad_bids', ['ad_id'], unique=False)
    op.create_index(op.f('ix_ad_bids_auction_id'), 'ad_bids', ['auction_id'], unique=False)
    op.create_index(op.f('ix_ad_bids_created_at'), 'ad_bids', ['created_at'], unique=False)
    
    # Create ad_spaces table
    op.create_table('ad_spaces',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('ad_type', postgresql.ENUM('banner', 'popup', 'sidebar', 'in_feed', 'search_result', 'product_page', 'category_page', 'homepage', name='ad_type_enum'), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('max_file_size', sa.Integer(), nullable=True),
        sa.Column('allowed_formats', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('page_type', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.Column('targeting_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('base_price', sa.Float(), nullable=True),
        sa.Column('min_bid', sa.Float(), nullable=True),
        sa.Column('reserve_price', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_spaces_id'), 'ad_spaces', ['id'], unique=False)
    op.create_index(op.f('ix_ad_spaces_name'), 'ad_spaces', ['name'], unique=False)
    op.create_index(op.f('ix_ad_spaces_ad_type'), 'ad_spaces', ['ad_type'], unique=False)
    op.create_index(op.f('ix_ad_spaces_is_active'), 'ad_spaces', ['is_active'], unique=False)
    
    # Create ad_blocklist table
    op.create_table('ad_blocklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('seller_id', sa.Integer(), nullable=True),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('url_pattern', sa.String(length=500), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('block_type', sa.String(length=50), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['seller_id'], ['sellers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_blocklist_id'), 'ad_blocklist', ['id'], unique=False)
    op.create_index(op.f('ix_ad_blocklist_seller_id'), 'ad_blocklist', ['seller_id'], unique=False)
    op.create_index(op.f('ix_ad_blocklist_block_type'), 'ad_blocklist', ['block_type'], unique=False)
    op.create_index(op.f('ix_ad_blocklist_is_active'), 'ad_blocklist', ['is_active'], unique=False)
    
    # Create ad_analytics table
    op.create_table('ad_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ad_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('impressions', sa.Integer(), nullable=True),
        sa.Column('clicks', sa.Integer(), nullable=True),
        sa.Column('conversions', sa.Integer(), nullable=True),
        sa.Column('spend', sa.Float(), nullable=True),
        sa.Column('ctr', sa.Float(), nullable=True),
        sa.Column('cpc', sa.Float(), nullable=True),
        sa.Column('cpm', sa.Float(), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('unique_users', sa.Integer(), nullable=True),
        sa.Column('new_users', sa.Integer(), nullable=True),
        sa.Column('returning_users', sa.Integer(), nullable=True),
        sa.Column('desktop_impressions', sa.Integer(), nullable=True),
        sa.Column('mobile_impressions', sa.Integer(), nullable=True),
        sa.Column('tablet_impressions', sa.Integer(), nullable=True),
        sa.Column('country_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('city_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['ad_id'], ['ads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ad_analytics_id'), 'ad_analytics', ['id'], unique=False)
    op.create_index(op.f('ix_ad_analytics_ad_id'), 'ad_analytics', ['ad_id'], unique=False)
    op.create_index(op.f('ix_ad_analytics_date'), 'ad_analytics', ['date'], unique=False)
    op.create_index(op.f('ix_ad_analytics_ad_id_date'), 'ad_analytics', ['ad_id', 'date'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_ad_analytics_ad_id_date'), table_name='ad_analytics')
    op.drop_index(op.f('ix_ad_analytics_date'), table_name='ad_analytics')
    op.drop_index(op.f('ix_ad_analytics_ad_id'), table_name='ad_analytics')
    op.drop_index(op.f('ix_ad_analytics_id'), table_name='ad_analytics')
    
    op.drop_index(op.f('ix_ad_blocklist_is_active'), table_name='ad_blocklist')
    op.drop_index(op.f('ix_ad_blocklist_block_type'), table_name='ad_blocklist')
    op.drop_index(op.f('ix_ad_blocklist_seller_id'), table_name='ad_blocklist')
    op.drop_index(op.f('ix_ad_blocklist_id'), table_name='ad_blocklist')
    
    op.drop_index(op.f('ix_ad_spaces_is_active'), table_name='ad_spaces')
    op.drop_index(op.f('ix_ad_spaces_ad_type'), table_name='ad_spaces')
    op.drop_index(op.f('ix_ad_spaces_name'), table_name='ad_spaces')
    op.drop_index(op.f('ix_ad_spaces_id'), table_name='ad_spaces')
    
    op.drop_index(op.f('ix_ad_bids_created_at'), table_name='ad_bids')
    op.drop_index(op.f('ix_ad_bids_auction_id'), table_name='ad_bids')
    op.drop_index(op.f('ix_ad_bids_ad_id'), table_name='ad_bids')
    op.drop_index(op.f('ix_ad_bids_id'), table_name='ad_bids')
    
    op.drop_index(op.f('ix_ad_conversions_created_at'), table_name='ad_conversions')
    op.drop_index(op.f('ix_ad_conversions_conversion_type'), table_name='ad_conversions')
    op.drop_index(op.f('ix_ad_conversions_user_id'), table_name='ad_conversions')
    op.drop_index(op.f('ix_ad_conversions_click_id'), table_name='ad_conversions')
    op.drop_index(op.f('ix_ad_conversions_ad_id'), table_name='ad_conversions')
    op.drop_index(op.f('ix_ad_conversions_id'), table_name='ad_conversions')
    
    op.drop_index(op.f('ix_ad_clicks_created_at'), table_name='ad_clicks')
    op.drop_index(op.f('ix_ad_clicks_user_id'), table_name='ad_clicks')
    op.drop_index(op.f('ix_ad_clicks_impression_id'), table_name='ad_clicks')
    op.drop_index(op.f('ix_ad_clicks_ad_id'), table_name='ad_clicks')
    op.drop_index(op.f('ix_ad_clicks_id'), table_name='ad_clicks')
    
    op.drop_index(op.f('ix_ad_impressions_created_at'), table_name='ad_impressions')
    op.drop_index(op.f('ix_ad_impressions_session_id'), table_name='ad_impressions')
    op.drop_index(op.f('ix_ad_impressions_user_id'), table_name='ad_impressions')
    op.drop_index(op.f('ix_ad_impressions_ad_id'), table_name='ad_impressions')
    op.drop_index(op.f('ix_ad_impressions_id'), table_name='ad_impressions')
    
    op.drop_index(op.f('ix_ads_campaign_id'), table_name='ads')
    op.drop_index(op.f('ix_ads_end_date'), table_name='ads')
    op.drop_index(op.f('ix_ads_start_date'), table_name='ads')
    op.drop_index(op.f('ix_ads_ad_type'), table_name='ads')
    op.drop_index(op.f('ix_ads_status'), table_name='ads')
    op.drop_index(op.f('ix_ads_seller_id'), table_name='ads')
    op.drop_index(op.f('ix_ads_id'), table_name='ads')
    
    op.drop_index(op.f('ix_ad_campaigns_status'), table_name='ad_campaigns')
    op.drop_index(op.f('ix_ad_campaigns_seller_id'), table_name='ad_campaigns')
    op.drop_index(op.f('ix_ad_campaigns_id'), table_name='ad_campaigns')
    
    # Drop tables
    op.drop_table('ad_analytics')
    op.drop_table('ad_blocklist')
    op.drop_table('ad_spaces')
    op.drop_table('ad_bids')
    op.drop_table('ad_conversions')
    op.drop_table('ad_clicks')
    op.drop_table('ad_impressions')
    
    # Drop campaign_id column from ads
    op.drop_constraint(None, 'ads', type_='foreignkey')
    op.drop_column('ads', 'campaign_id')
    
    op.drop_table('ad_campaigns')
    op.drop_table('ads')
    
    # Drop enums
    bidding_type_enum = postgresql.ENUM('cpc', 'cpm', 'cpa', 'fixed', name='bidding_type_enum')
    bidding_type_enum.drop(op.get_bind())
    
    ad_status_enum = postgresql.ENUM('draft', 'pending', 'active', 'paused', 'rejected', 'expired', name='ad_status_enum')
    ad_status_enum.drop(op.get_bind())
    
    ad_type_enum = postgresql.ENUM('banner', 'popup', 'sidebar', 'in_feed', 'search_result', 'product_page', 'category_page', 'homepage', name='ad_type_enum')
    ad_type_enum.drop(op.get_bind())


