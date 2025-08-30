"""
Advanced Search & Filters System Schemas
Comprehensive search capabilities for the B2B marketplace
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class SearchIndexType(str, Enum):
    PRODUCT = "product"
    SELLER = "seller"
    GUILD = "guild"
    RFQ = "rfq"
    USER = "user"
    ORDER = "order"
    AD = "ad"


class SearchIndexStatus(str, Enum):
    PENDING = "pending"
    INDEXED = "indexed"
    FAILED = "failed"
    OUTDATED = "outdated"


class FilterType(str, Enum):
    RANGE = "range"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    BOOLEAN = "boolean"
    DATE_RANGE = "date_range"
    LOCATION = "location"
    PRICE_RANGE = "price_range"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    RELEVANCE = "relevance"
    PRICE = "price"
    RATING = "rating"
    POPULARITY = "popularity"
    RECENCY = "recency"
    NAME = "name"
    CREATED_AT = "created_at"


# Search Request/Response Schemas
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    search_type: Optional[SearchIndexType] = None
    filters: Optional[Dict[str, Any]] = None
    sort_by: Optional[SortField] = SortField.RELEVANCE
    sort_order: Optional[SortOrder] = SortOrder.DESC
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    include_facets: bool = True
    include_suggestions: bool = True


class SearchFilter(BaseModel):
    field: str
    value: Any
    operator: Optional[str] = "eq"  # eq, gt, lt, gte, lte, in, not_in, contains, etc.


class RangeFilter(BaseModel):
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None


class DateRangeFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class LocationFilter(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
    country: Optional[str] = None
    city: Optional[str] = None


class PriceRangeFilter(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    currency: Optional[str] = "IRR"


class SearchResult(BaseModel):
    entity_id: int
    entity_type: SearchIndexType
    title: str
    description: Optional[str] = None
    relevance_score: float
    metadata: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


class SearchFacet(BaseModel):
    field: str
    values: List[Dict[str, Any]]  # [{value: "value", count: 10, selected: false}]
    type: FilterType


class SearchSuggestion(BaseModel):
    text: str
    type: str
    relevance_score: float
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    page_size: int
    total_pages: int
    results: List[SearchResult]
    facets: Optional[List[SearchFacet]] = None
    suggestions: Optional[List[SearchSuggestion]] = None
    search_time_ms: int
    filters_applied: Optional[Dict[str, Any]] = None


# Search Index Schemas
class SearchIndexBase(BaseModel):
    entity_type: SearchIndexType
    entity_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None


class SearchIndexCreate(SearchIndexBase):
    pass


class SearchIndexUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    categories: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None
    attributes: Optional[Dict[str, Any]] = None
    relevance_score: Optional[float] = None
    popularity_score: Optional[float] = None
    recency_score: Optional[float] = None


class SearchIndexOut(SearchIndexBase):
    id: int
    relevance_score: float = 0.0
    popularity_score: float = 0.0
    recency_score: float = 0.0
    status: SearchIndexStatus
    last_indexed: datetime
    next_index: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Query Schemas
class SearchQueryBase(BaseModel):
    query_text: str
    search_type: str
    filters_applied: Optional[Dict[str, Any]] = None
    total_results: int = 0
    results_returned: int = 0
    search_time_ms: int = 0


class SearchQueryCreate(SearchQueryBase):
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None


class SearchQueryUpdate(BaseModel):
    clicked_results: Optional[List[int]] = None
    conversion_type: Optional[str] = None
    conversion_value: Optional[float] = None


class SearchQueryOut(SearchQueryBase):
    id: int
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    clicked_results: Optional[List[int]] = None
    conversion_type: Optional[str] = None
    conversion_value: Optional[float] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referrer: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search Filter Schemas
class SearchFilterBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    filter_type: FilterType
    field_name: str
    filter_config: Optional[Dict[str, Any]] = None
    entity_types: Optional[List[str]] = None
    is_active: bool = True
    is_public: bool = True
    sort_order: int = 0


class SearchFilterCreate(SearchFilterBase):
    pass


class SearchFilterUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    filter_config: Optional[Dict[str, Any]] = None
    entity_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    sort_order: Optional[int] = None


class SearchFilterOut(SearchFilterBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Suggestion Schemas
class SearchSuggestionBase(BaseModel):
    suggestion_text: str
    suggestion_type: str
    frequency: int = 1
    relevance_score: float = 0.0
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: bool = True


class SearchSuggestionCreate(SearchSuggestionBase):
    pass


class SearchSuggestionUpdate(BaseModel):
    frequency: Optional[int] = None
    relevance_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SearchSuggestionOut(SearchSuggestionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Analytics Schemas
class SearchAnalyticsBase(BaseModel):
    date: datetime
    total_queries: int = 0
    unique_queries: int = 0
    zero_result_queries: int = 0
    avg_search_time_ms: float = 0.0
    avg_results_per_query: float = 0.0
    queries_with_clicks: int = 0
    queries_with_conversions: int = 0
    conversion_rate: float = 0.0
    top_queries: Optional[List[Dict[str, Any]]] = None
    top_filters: Optional[List[Dict[str, Any]]] = None
    queries_by_type: Optional[Dict[str, int]] = None


class SearchAnalyticsCreate(SearchAnalyticsBase):
    pass


class SearchAnalyticsOut(SearchAnalyticsBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search Synonym Schemas
class SearchSynonymBase(BaseModel):
    primary_term: str
    synonyms: List[str]
    language: str = "en"
    entity_type: Optional[str] = None
    is_active: bool = True


class SearchSynonymCreate(SearchSynonymBase):
    pass


class SearchSynonymUpdate(BaseModel):
    synonyms: Optional[List[str]] = None
    language: Optional[str] = None
    entity_type: Optional[str] = None
    is_active: Optional[bool] = None


class SearchSynonymOut(SearchSynonymBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Blacklist Schemas
class SearchBlacklistBase(BaseModel):
    term: str
    reason: Optional[str] = None
    language: str = "en"
    entity_type: Optional[str] = None
    is_active: bool = True


class SearchBlacklistCreate(SearchBlacklistBase):
    pass


class SearchBlacklistUpdate(BaseModel):
    reason: Optional[str] = None
    language: Optional[str] = None
    entity_type: Optional[str] = None
    is_active: Optional[bool] = None


class SearchBlacklistOut(SearchBlacklistBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Search Boost Schemas
class SearchBoostBase(BaseModel):
    name: str
    description: Optional[str] = None
    boost_type: str
    boost_field: str
    boost_value: Optional[str] = None
    boost_multiplier: float = 1.0
    entity_types: Optional[List[str]] = None
    is_active: bool = True
    priority: int = 0


class SearchBoostCreate(SearchBoostBase):
    pass


class SearchBoostUpdate(BaseModel):
    description: Optional[str] = None
    boost_value: Optional[str] = None
    boost_multiplier: Optional[float] = None
    entity_types: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class SearchBoostOut(SearchBoostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Response Schemas
class SearchIndexListResponse(BaseModel):
    items: List[SearchIndexOut]
    total: int
    page: int
    page_size: int


class SearchQueryListResponse(BaseModel):
    queries: List[SearchQueryOut]
    total: int
    page: int
    page_size: int


class SearchFilterListResponse(BaseModel):
    filters: List[SearchFilterOut]
    total: int


class SearchSuggestionListResponse(BaseModel):
    suggestions: List[SearchSuggestionOut]
    total: int
    page: int
    page_size: int


class SearchAnalyticsListResponse(BaseModel):
    analytics: List[SearchAnalyticsOut]
    total: int
    page: int
    page_size: int


class SearchSynonymListResponse(BaseModel):
    synonyms: List[SearchSynonymOut]
    total: int
    page: int
    page_size: int


class SearchBlacklistListResponse(BaseModel):
    blacklist: List[SearchBlacklistOut]
    total: int
    page: int
    page_size: int


class SearchBoostListResponse(BaseModel):
    boosts: List[SearchBoostOut]
    total: int
    page: int
    page_size: int


# Advanced Search Schemas
class AdvancedSearchRequest(BaseModel):
    query: Optional[str] = None
    search_types: Optional[List[SearchIndexType]] = None
    
    # Filters
    price_range: Optional[PriceRangeFilter] = None
    date_range: Optional[DateRangeFilter] = None
    location: Optional[LocationFilter] = None
    categories: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    
    # Sorting
    sort_by: Optional[SortField] = SortField.RELEVANCE
    sort_order: Optional[SortOrder] = SortOrder.DESC
    
    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    # Options
    include_facets: bool = True
    include_suggestions: bool = True
    fuzzy_search: bool = True
    use_synonyms: bool = True


class SearchFacetRequest(BaseModel):
    search_type: Optional[SearchIndexType] = None
    filters: Optional[Dict[str, Any]] = None
    facet_fields: Optional[List[str]] = None


class SearchSuggestionRequest(BaseModel):
    query: str
    search_type: Optional[SearchIndexType] = None
    limit: int = Field(10, ge=1, le=50)


class SearchIndexRequest(BaseModel):
    entity_type: SearchIndexType
    entity_ids: Optional[List[int]] = None
    force_reindex: bool = False


class SearchIndexResponse(BaseModel):
    indexed_count: int
    failed_count: int
    errors: Optional[List[str]] = None
    processing_time_ms: int


# Analytics and Reporting Schemas
class SearchAnalyticsSummary(BaseModel):
    total_queries: int
    unique_queries: int
    avg_search_time_ms: float
    conversion_rate: float
    top_queries: List[Dict[str, Any]]
    queries_by_type: Dict[str, int]
    date_range: Dict[str, datetime]


class SearchPerformanceMetrics(BaseModel):
    avg_response_time_ms: float
    queries_per_second: float
    cache_hit_rate: float
    index_size_mb: float
    last_index_update: datetime


class SearchTrends(BaseModel):
    date: datetime
    query_count: int
    unique_users: int
    avg_results_per_query: float
    zero_result_rate: float


