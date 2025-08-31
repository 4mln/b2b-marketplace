"""Create advanced search tables

Revision ID: 20
Revises: 19
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20'
down_revision = '19'
branch_labels = None
depends_on = None


def upgrade():
    # Create enums
    op.execute("CREATE TYPE search_index_type_enum AS ENUM ('product', 'seller', 'guild', 'rfq', 'user', 'order', 'ad')")
    op.execute("CREATE TYPE search_index_status_enum AS ENUM ('pending', 'indexed', 'failed', 'outdated')")
    
    # Create search_queries table
    op.create_table('search_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('search_type', sa.String(length=50), nullable=False),
        sa.Column('filters_applied', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('total_results', sa.Integer(), nullable=True),
        sa.Column('results_returned', sa.Integer(), nullable=True),
        sa.Column('search_time_ms', sa.Integer(), nullable=True),
        sa.Column('clicked_results', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('conversion_type', sa.String(length=100), nullable=True),
        sa.Column('conversion_value', sa.Float(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('referrer', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_queries_id'), 'search_queries', ['id'], unique=False)
    op.create_index('idx_search_query_text', 'search_queries', ['query_text'], unique=False)
    op.create_index('idx_search_query_type', 'search_queries', ['search_type'], unique=False)
    op.create_index('idx_search_query_user', 'search_queries', ['user_id'], unique=False)
    op.create_index('idx_search_query_created', 'search_queries', ['created_at'], unique=False)
    
    # Create search_index table
    op.create_table('search_index',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('categories', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('attributes', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('popularity_score', sa.Float(), nullable=True),
        sa.Column('recency_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('last_indexed', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('next_index', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_index_id'), 'search_index', ['id'], unique=False)
    op.create_index('idx_search_index_entity', 'search_index', ['entity_type', 'entity_id'], unique=False)
    op.create_index('idx_search_index_status', 'search_index', ['status'], unique=False)
    op.create_index('idx_search_index_relevance', 'search_index', ['relevance_score'], unique=False)
    op.create_index('idx_search_index_popularity', 'search_index', ['popularity_score'], unique=False)
    op.create_index('idx_search_index_recency', 'search_index', ['recency_score'], unique=False)
    
    # Create search_filters table
    op.create_table('search_filters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('filter_type', sa.String(length=50), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('filter_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('entity_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_filters_id'), 'search_filters', ['id'], unique=False)
    
    # Create search_suggestions table
    op.create_table('search_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('suggestion_text', sa.String(length=255), nullable=False),
        sa.Column('suggestion_type', sa.String(length=50), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_suggestions_id'), 'search_suggestions', ['id'], unique=False)
    op.create_index('idx_search_suggestion_text', 'search_suggestions', ['suggestion_text'], unique=False)
    op.create_index('idx_search_suggestion_type', 'search_suggestions', ['suggestion_type'], unique=False)
    op.create_index('idx_search_suggestion_frequency', 'search_suggestions', ['frequency'], unique=False)
    
    # Create search_analytics table
    op.create_table('search_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_queries', sa.Integer(), nullable=True),
        sa.Column('unique_queries', sa.Integer(), nullable=True),
        sa.Column('zero_result_queries', sa.Integer(), nullable=True),
        sa.Column('avg_search_time_ms', sa.Float(), nullable=True),
        sa.Column('avg_results_per_query', sa.Float(), nullable=True),
        sa.Column('queries_with_clicks', sa.Integer(), nullable=True),
        sa.Column('queries_with_conversions', sa.Integer(), nullable=True),
        sa.Column('conversion_rate', sa.Float(), nullable=True),
        sa.Column('top_queries', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('top_filters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('queries_by_type', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_analytics_id'), 'search_analytics', ['id'], unique=False)
    op.create_index('idx_search_analytics_date', 'search_analytics', ['date'], unique=False)
    op.create_index('idx_search_analytics_queries', 'search_analytics', ['total_queries'], unique=False)
    
    # Create search_synonyms table
    op.create_table('search_synonyms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('primary_term', sa.String(length=255), nullable=False),
        sa.Column('synonyms', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_synonyms_id'), 'search_synonyms', ['id'], unique=False)
    
    # Create search_blacklist table
    op.create_table('search_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('term', sa.String(length=255), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_blacklist_id'), 'search_blacklist', ['id'], unique=False)
    
    # Create search_boosts table
    op.create_table('search_boosts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('boost_type', sa.String(length=50), nullable=False),
        sa.Column('boost_field', sa.String(length=100), nullable=False),
        sa.Column('boost_value', sa.String(length=255), nullable=True),
        sa.Column('boost_multiplier', sa.Float(), nullable=True),
        sa.Column('entity_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_search_boosts_id'), 'search_boosts', ['id'], unique=False)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_search_boosts_id'), table_name='search_boosts')
    op.drop_table('search_boosts')
    
    op.drop_index(op.f('ix_search_blacklist_id'), table_name='search_blacklist')
    op.drop_table('search_blacklist')
    
    op.drop_index(op.f('ix_search_synonyms_id'), table_name='search_synonyms')
    op.drop_table('search_synonyms')
    
    op.drop_index('idx_search_analytics_queries', table_name='search_analytics')
    op.drop_index('idx_search_analytics_date', table_name='search_analytics')
    op.drop_index(op.f('ix_search_analytics_id'), table_name='search_analytics')
    op.drop_table('search_analytics')
    
    op.drop_index('idx_search_suggestion_frequency', table_name='search_suggestions')
    op.drop_index('idx_search_suggestion_type', table_name='search_suggestions')
    op.drop_index('idx_search_suggestion_text', table_name='search_suggestions')
    op.drop_index(op.f('ix_search_suggestions_id'), table_name='search_suggestions')
    op.drop_table('search_suggestions')
    
    op.drop_index(op.f('ix_search_filters_id'), table_name='search_filters')
    op.drop_table('search_filters')
    
    op.drop_index('idx_search_index_recency', table_name='search_index')
    op.drop_index('idx_search_index_popularity', table_name='search_index')
    op.drop_index('idx_search_index_relevance', table_name='search_index')
    op.drop_index('idx_search_index_status', table_name='search_index')
    op.drop_index('idx_search_index_entity', table_name='search_index')
    op.drop_index(op.f('ix_search_index_id'), table_name='search_index')
    op.drop_table('search_index')
    
    op.drop_index('idx_search_query_created', table_name='search_queries')
    op.drop_index('idx_search_query_user', table_name='search_queries')
    op.drop_index('idx_search_query_type', table_name='search_queries')
    op.drop_index('idx_search_query_text', table_name='search_queries')
    op.drop_index(op.f('ix_search_queries_id'), table_name='search_queries')
    op.drop_table('search_queries')
    
    # Drop enums
    op.execute("DROP TYPE search_index_status_enum")
    op.execute("DROP TYPE search_index_type_enum")


