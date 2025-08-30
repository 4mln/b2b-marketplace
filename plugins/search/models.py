"""
Advanced Search & Filters System Models
Comprehensive search capabilities for the B2B marketplace
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.db.base import Base


class SearchIndexType(str, enum.Enum):
    PRODUCT = "product"
    SELLER = "seller"
    GUILD = "guild"
    RFQ = "rfq"
    USER = "user"
    ORDER = "order"
    AD = "ad"


class SearchIndexStatus(str, enum.Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"
    OUTDATED = "outdated"


class SearchQuery(Base):
    """Search query history and analytics"""
    __tablename__ = "search_queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    search_type = Column(String(50), nullable=False)  # product, seller, etc.
    filters_applied = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # Results
    total_results = Column(Integer, default=0)
    results_returned = Column(Integer, default=0)
    search_time_ms = Column(Integer, default=0)
    
    # Analytics
    clicked_results = Column(JSON, nullable=True)  # Array of clicked result IDs
    conversion_type = Column(String(100), nullable=True)  # purchase, contact, etc.
    conversion_value = Column(Float, nullable=True)
    
    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


class SearchIndex(Base):
    """Search index for different entities"""
    __tablename__ = "search_index"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    
    # Searchable content
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    keywords = Column(JSON, nullable=True)  # Array of keywords
    tags = Column(JSON, nullable=True)  # Array of tags
    categories = Column(JSON, nullable=True)  # Array of category IDs
    
    # Metadata for filtering
    metadata = Column(JSON, nullable=True)  # Price, location, ratings, etc.
    attributes = Column(JSON, nullable=True)  # Product attributes, seller info, etc.
    
    # Search relevance
    relevance_score = Column(Float, default=0.0)
    popularity_score = Column(Float, default=0.0)
    recency_score = Column(Float, default=0.0)
    
    # Status
    status = Column(String(50), default="pending")
    last_indexed = Column(DateTime(timezone=True), server_default=func.now())
    next_index = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SearchFilter(Base):
    """Predefined search filters"""
    __tablename__ = "search_filters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Filter configuration
    filter_type = Column(String(50), nullable=False)  # range, select, multi_select, etc.
    field_name = Column(String(100), nullable=False)
    filter_config = Column(JSON, nullable=True)  # Min/max values, options, etc.
    
    # Applicable entities
    entity_types = Column(JSON, nullable=True)  # Array of entity types
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Display order
    sort_order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SearchSuggestion(Base):
    """Search suggestions and autocomplete"""
    __tablename__ = "search_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_text = Column(String(255), nullable=False)
    suggestion_type = Column(String(50), nullable=False)  # keyword, product, seller, etc.
    
    # Relevance
    frequency = Column(Integer, default=1)
    relevance_score = Column(Float, default=0.0)
    
    # Metadata
    entity_id = Column(Integer, nullable=True)
    entity_type = Column(String(50), nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SearchAnalytics(Base):
    """Search analytics and performance metrics"""
    __tablename__ = "search_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Query metrics
    total_queries = Column(Integer, default=0)
    unique_queries = Column(Integer, default=0)
    zero_result_queries = Column(Integer, default=0)
    
    # Performance metrics
    avg_search_time_ms = Column(Float, default=0.0)
    avg_results_per_query = Column(Float, default=0.0)
    
    # User engagement
    queries_with_clicks = Column(Integer, default=0)
    queries_with_conversions = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    
    # Popular searches
    top_queries = Column(JSON, nullable=True)  # Array of top queries with counts
    top_filters = Column(JSON, nullable=True)  # Array of most used filters
    
    # Entity type breakdown
    queries_by_type = Column(JSON, nullable=True)  # Breakdown by search type
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchSynonym(Base):
    """Search synonyms for better matching"""
    __tablename__ = "search_synonyms"

    id = Column(Integer, primary_key=True, index=True)
    primary_term = Column(String(255), nullable=False)
    synonyms = Column(JSON, nullable=False)  # Array of synonym terms
    
    # Context
    language = Column(String(10), default="en")
    entity_type = Column(String(50), nullable=True)  # Optional entity type restriction
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SearchBlacklist(Base):
    """Blacklisted search terms"""
    __tablename__ = "search_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    term = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    
    # Context
    language = Column(String(10), default="en")
    entity_type = Column(String(50), nullable=True)  # Optional entity type restriction
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SearchBoost(Base):
    """Search result boosting rules"""
    __tablename__ = "search_boosts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Boost configuration
    boost_type = Column(String(50), nullable=False)  # keyword, filter, attribute, etc.
    boost_field = Column(String(100), nullable=False)
    boost_value = Column(String(255), nullable=True)
    boost_multiplier = Column(Float, default=1.0)
    
    # Applicable entities
    entity_types = Column(JSON, nullable=True)  # Array of entity types
    is_active = Column(Boolean, default=True)
    
    # Priority
    priority = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# Create indexes for better search performance
Index('idx_search_index_entity', SearchIndex.entity_type, SearchIndex.entity_id)
Index('idx_search_index_status', SearchIndex.status)
Index('idx_search_index_relevance', SearchIndex.relevance_score.desc())
Index('idx_search_index_popularity', SearchIndex.popularity_score.desc())
Index('idx_search_index_recency', SearchIndex.recency_score.desc())

Index('idx_search_query_text', SearchQuery.query_text)
Index('idx_search_query_type', SearchQuery.search_type)
Index('idx_search_query_user', SearchQuery.user_id)
Index('idx_search_query_created', SearchQuery.created_at.desc())

Index('idx_search_suggestion_text', SearchSuggestion.suggestion_text)
Index('idx_search_suggestion_type', SearchSuggestion.suggestion_type)
Index('idx_search_suggestion_frequency', SearchSuggestion.frequency.desc())

Index('idx_search_analytics_date', SearchAnalytics.date)
Index('idx_search_analytics_queries', SearchAnalytics.total_queries.desc())


