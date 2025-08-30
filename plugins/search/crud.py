"""
Advanced Search & Filters System CRUD Operations
Comprehensive search capabilities for the B2B marketplace
"""
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc, asc, text
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import re

from .models import (
    SearchQuery, SearchIndex, SearchFilter, SearchSuggestion, SearchAnalytics,
    SearchSynonym, SearchBlacklist, SearchBoost, SearchIndexType, SearchIndexStatus
)
from .schemas import (
    SearchRequest, SearchResponse, SearchResult, SearchFacet, SearchSuggestion as SearchSuggestionSchema,
    SearchIndexCreate, SearchIndexUpdate, SearchIndexOut, SearchQueryCreate, SearchQueryUpdate,
    SearchFilterCreate, SearchFilterUpdate, SearchFilterOut, SearchSuggestionCreate,
    SearchSuggestionUpdate, SearchSuggestionOut, SearchAnalyticsCreate, SearchAnalyticsOut,
    SearchSynonymCreate, SearchSynonymUpdate, SearchSynonymOut, SearchBlacklistCreate,
    SearchBlacklistUpdate, SearchBlacklistOut, SearchBoostCreate, SearchBoostUpdate,
    SearchBoostOut, AdvancedSearchRequest, SearchFacetRequest, SearchSuggestionRequest,
    SearchIndexRequest, SearchIndexResponse, SearchAnalyticsSummary, SearchPerformanceMetrics,
    SearchTrends, PriceRangeFilter, DateRangeFilter, LocationFilter
)


# Search Engine Core Functions
def perform_search(
    db: Session, 
    search_request: SearchRequest,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None
) -> SearchResponse:
    """Perform a search query"""
    start_time = datetime.utcnow()
    
    # Build search query
    query = build_search_query(db, search_request)
    
    # Apply filters
    if search_request.filters:
        query = apply_filters(query, search_request.filters)
    
    # Apply sorting
    query = apply_sorting(query, search_request.sort_by, search_request.sort_order)
    
    # Get total count
    total_results = query.count()
    
    # Apply pagination
    offset = (search_request.page - 1) * search_request.page_size
    query = query.offset(offset).limit(search_request.page_size)
    
    # Execute query
    search_results = query.all()
    
    # Convert to response format
    results = []
    for result in search_results:
        search_result = SearchResult(
            entity_id=result.entity_id,
            entity_type=result.entity_type,
            title=result.title or "",
            description=result.description,
            relevance_score=result.relevance_score,
            metadata=result.metadata,
            attributes=result.attributes,
            url=f"/{result.entity_type}/{result.entity_id}",
            image_url=result.metadata.get("image_url") if result.metadata else None
        )
        results.append(search_result)
    
    # Calculate search time
    search_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    # Get facets if requested
    facets = None
    if search_request.include_facets:
        facets = get_search_facets(db, search_request)
    
    # Get suggestions if requested
    suggestions = None
    if search_request.include_suggestions:
        suggestions = get_search_suggestions(db, search_request.query, search_request.search_type)
    
    # Log search query
    log_search_query(
        db, search_request, total_results, len(results), search_time_ms,
        user_id, session_id, ip_address, user_agent, referrer
    )
    
    return SearchResponse(
        query=search_request.query,
        total_results=total_results,
        page=search_request.page,
        page_size=search_request.page_size,
        total_pages=(total_results + search_request.page_size - 1) // search_request.page_size,
        results=results,
        facets=facets,
        suggestions=suggestions,
        search_time_ms=search_time_ms,
        filters_applied=search_request.filters
    )


def build_search_query(db: Session, search_request: SearchRequest):
    """Build the base search query"""
    query = db.query(SearchIndex)
    
    # Apply search type filter
    if search_request.search_type:
        query = query.filter(SearchIndex.entity_type == search_request.search_type.value)
    
    # Apply text search
    if search_request.query:
        # Simple text search - in production, you'd use a proper search engine
        search_terms = search_request.query.lower().split()
        conditions = []
        for term in search_terms:
            conditions.append(
                or_(
                    SearchIndex.title.ilike(f"%{term}%"),
                    SearchIndex.description.ilike(f"%{term}%"),
                    SearchIndex.keywords.contains([term])
                )
            )
        if conditions:
            query = query.filter(or_(*conditions))
    
    return query


def apply_filters(query, filters: Dict[str, Any]):
    """Apply filters to the search query"""
    if not filters:
        return query
    
    for field, value in filters.items():
        if value is None:
            continue
            
        if field == "price_range" and isinstance(value, dict):
            min_price = value.get("min_price")
            max_price = value.get("max_price")
            if min_price is not None:
                query = query.filter(SearchIndex.metadata['price'].astext.cast(Float) >= min_price)
            if max_price is not None:
                query = query.filter(SearchIndex.metadata['price'].astext.cast(Float) <= max_price)
        
        elif field == "date_range" and isinstance(value, dict):
            start_date = value.get("start_date")
            end_date = value.get("end_date")
            if start_date:
                query = query.filter(SearchIndex.created_at >= start_date)
            if end_date:
                query = query.filter(SearchIndex.created_at <= end_date)
        
        elif field == "categories" and isinstance(value, list):
            query = query.filter(SearchIndex.categories.contains(value))
        
        elif field == "tags" and isinstance(value, list):
            query = query.filter(SearchIndex.tags.contains(value))
        
        elif field == "attributes" and isinstance(value, dict):
            for attr_key, attr_value in value.items():
                query = query.filter(SearchIndex.attributes[attr_key].astext == str(attr_value))
    
    return query


def apply_sorting(query, sort_by: SortField, sort_order: SortOrder):
    """Apply sorting to the search query"""
    if sort_by == SortField.RELEVANCE:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.relevance_score))
        else:
            query = query.order_by(asc(SearchIndex.relevance_score))
    
    elif sort_by == SortField.PRICE:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.metadata['price'].astext.cast(Float)))
        else:
            query = query.order_by(asc(SearchIndex.metadata['price'].astext.cast(Float)))
    
    elif sort_by == SortField.RATING:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.metadata['rating'].astext.cast(Float)))
        else:
            query = query.order_by(asc(SearchIndex.metadata['rating'].astext.cast(Float)))
    
    elif sort_by == SortField.POPULARITY:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.popularity_score))
        else:
            query = query.order_by(asc(SearchIndex.popularity_score))
    
    elif sort_by == SortField.RECENCY:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.created_at))
        else:
            query = query.order_by(asc(SearchIndex.created_at))
    
    elif sort_by == SortField.NAME:
        if sort_order == SortOrder.DESC:
            query = query.order_by(desc(SearchIndex.title))
        else:
            query = query.order_by(asc(SearchIndex.title))
    
    return query


def get_search_facets(db: Session, search_request: SearchRequest) -> List[SearchFacet]:
    """Get search facets for filtering"""
    facets = []
    
    # Price range facet
    price_stats = db.query(
        func.min(SearchIndex.metadata['price'].astext.cast(Float)).label('min_price'),
        func.max(SearchIndex.metadata['price'].astext.cast(Float)).label('max_price'),
        func.avg(SearchIndex.metadata['price'].astext.cast(Float)).label('avg_price')
    ).filter(SearchIndex.metadata['price'].astext.isnot(None)).first()
    
    if price_stats and price_stats.min_price and price_stats.max_price:
        facets.append(SearchFacet(
            field="price",
            type=FilterType.PRICE_RANGE,
            values=[
                {"value": "0-1000", "count": 0, "selected": False},
                {"value": "1000-5000", "count": 0, "selected": False},
                {"value": "5000-10000", "count": 0, "selected": False},
                {"value": "10000+", "count": 0, "selected": False}
            ]
        ))
    
    # Category facet
    categories = db.query(SearchIndex.categories).filter(
        SearchIndex.categories.isnot(None)
    ).all()
    
    category_counts = {}
    for cat in categories:
        if cat.categories:
            for category_id in cat.categories:
                category_counts[category_id] = category_counts.get(category_id, 0) + 1
    
    if category_counts:
        facets.append(SearchFacet(
            field="categories",
            type=FilterType.MULTI_SELECT,
            values=[{"value": str(cat_id), "count": count, "selected": False} 
                   for cat_id, count in category_counts.items()]
        ))
    
    return facets


def get_search_suggestions(db: Session, query: str, search_type: Optional[str] = None, limit: int = 10) -> List[SearchSuggestionSchema]:
    """Get search suggestions for autocomplete"""
    suggestions = []
    
    # Get suggestions from search_suggestions table
    db_suggestions = db.query(SearchSuggestion).filter(
        SearchSuggestion.suggestion_text.ilike(f"%{query}%"),
        SearchSuggestion.is_active == True
    )
    
    if search_type:
        db_suggestions = db_suggestions.filter(SearchSuggestion.suggestion_type == search_type)
    
    db_suggestions = db_suggestions.order_by(desc(SearchSuggestion.frequency)).limit(limit).all()
    
    for suggestion in db_suggestions:
        suggestions.append(SearchSuggestionSchema(
            text=suggestion.suggestion_text,
            type=suggestion.suggestion_type,
            relevance_score=suggestion.relevance_score,
            entity_id=suggestion.entity_id,
            entity_type=suggestion.entity_type
        ))
    
    return suggestions


def log_search_query(
    db: Session,
    search_request: SearchRequest,
    total_results: int,
    results_returned: int,
    search_time_ms: int,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None
):
    """Log search query for analytics"""
    search_query = SearchQueryCreate(
        query_text=search_request.query,
        search_type=search_request.search_type.value if search_request.search_type else "general",
        filters_applied=search_request.filters,
        user_id=user_id,
        session_id=session_id,
        total_results=total_results,
        results_returned=results_returned,
        search_time_ms=search_time_ms,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    create_search_query(db, search_query)


# Search Index CRUD Operations
def create_search_index(db: Session, index_data: SearchIndexCreate) -> SearchIndexOut:
    """Create a new search index entry"""
    db_index = SearchIndex(**index_data.dict())
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return SearchIndexOut.from_orm(db_index)


def get_search_index(db: Session, index_id: int) -> Optional[SearchIndexOut]:
    """Get search index by ID"""
    db_index = db.query(SearchIndex).filter(SearchIndex.id == index_id).first()
    return SearchIndexOut.from_orm(db_index) if db_index else None


def get_search_indexes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    status: Optional[str] = None
) -> Tuple[List[SearchIndexOut], int]:
    """Get search indexes with pagination"""
    query = db.query(SearchIndex)
    
    if entity_type:
        query = query.filter(SearchIndex.entity_type == entity_type)
    if status:
        query = query.filter(SearchIndex.status == status)
    
    total = query.count()
    indexes = query.offset(skip).limit(limit).all()
    
    return [SearchIndexOut.from_orm(index) for index in indexes], total


def update_search_index(db: Session, index_id: int, index_data: SearchIndexUpdate) -> Optional[SearchIndexOut]:
    """Update search index"""
    db_index = db.query(SearchIndex).filter(SearchIndex.id == index_id).first()
    if not db_index:
        return None
    
    for field, value in index_data.dict(exclude_unset=True).items():
        setattr(db_index, field, value)
    
    db.commit()
    db.refresh(db_index)
    return SearchIndexOut.from_orm(db_index)


def delete_search_index(db: Session, index_id: int) -> bool:
    """Delete search index"""
    db_index = db.query(SearchIndex).filter(SearchIndex.id == index_id).first()
    if not db_index:
        return False
    
    db.delete(db_index)
    db.commit()
    return True


def reindex_entities(
    db: Session,
    entity_type: SearchIndexType,
    entity_ids: Optional[List[int]] = None,
    force_reindex: bool = False
) -> SearchIndexResponse:
    """Reindex entities for search"""
    start_time = datetime.utcnow()
    indexed_count = 0
    failed_count = 0
    errors = []
    
    # This is a placeholder implementation
    # In a real system, you would:
    # 1. Fetch entities from their respective tables
    # 2. Process and index them
    # 3. Update search index entries
    
    processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return SearchIndexResponse(
        indexed_count=indexed_count,
        failed_count=failed_count,
        errors=errors if errors else None,
        processing_time_ms=processing_time_ms
    )


# Search Query CRUD Operations
def create_search_query(db: Session, query_data: SearchQueryCreate) -> SearchQueryOut:
    """Create a new search query entry"""
    db_query = SearchQuery(**query_data.dict())
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return SearchQueryOut.from_orm(db_query)


def get_search_query(db: Session, query_id: int) -> Optional[SearchQueryOut]:
    """Get search query by ID"""
    db_query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    return SearchQueryOut.from_orm(db_query) if db_query else None


def get_search_queries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search_type: Optional[str] = None,
    user_id: Optional[int] = None
) -> Tuple[List[SearchQueryOut], int]:
    """Get search queries with pagination"""
    query = db.query(SearchQuery)
    
    if search_type:
        query = query.filter(SearchQuery.search_type == search_type)
    if user_id:
        query = query.filter(SearchQuery.user_id == user_id)
    
    total = query.count()
    queries = query.order_by(desc(SearchQuery.created_at)).offset(skip).limit(limit).all()
    
    return [SearchQueryOut.from_orm(query) for query in queries], total


def update_search_query(db: Session, query_id: int, query_data: SearchQueryUpdate) -> Optional[SearchQueryOut]:
    """Update search query"""
    db_query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if not db_query:
        return None
    
    for field, value in query_data.dict(exclude_unset=True).items():
        setattr(db_query, field, value)
    
    db.commit()
    db.refresh(db_query)
    return SearchQueryOut.from_orm(db_query)


# Search Filter CRUD Operations
def create_search_filter(db: Session, filter_data: SearchFilterCreate) -> SearchFilterOut:
    """Create a new search filter"""
    db_filter = SearchFilter(**filter_data.dict())
    db.add(db_filter)
    db.commit()
    db.refresh(db_filter)
    return SearchFilterOut.from_orm(db_filter)


def get_search_filter(db: Session, filter_id: int) -> Optional[SearchFilterOut]:
    """Get search filter by ID"""
    db_filter = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    return SearchFilterOut.from_orm(db_filter) if db_filter else None


def get_search_filters(
    db: Session,
    entity_types: Optional[List[str]] = None,
    is_active: Optional[bool] = None
) -> List[SearchFilterOut]:
    """Get search filters"""
    query = db.query(SearchFilter)
    
    if entity_types:
        query = query.filter(SearchFilter.entity_types.contains(entity_types))
    if is_active is not None:
        query = query.filter(SearchFilter.is_active == is_active)
    
    filters = query.order_by(SearchFilter.sort_order).all()
    return [SearchFilterOut.from_orm(filter) for filter in filters]


def update_search_filter(db: Session, filter_id: int, filter_data: SearchFilterUpdate) -> Optional[SearchFilterOut]:
    """Update search filter"""
    db_filter = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    if not db_filter:
        return None
    
    for field, value in filter_data.dict(exclude_unset=True).items():
        setattr(db_filter, field, value)
    
    db.commit()
    db.refresh(db_filter)
    return SearchFilterOut.from_orm(db_filter)


# Search Suggestion CRUD Operations
def create_search_suggestion(db: Session, suggestion_data: SearchSuggestionCreate) -> SearchSuggestionOut:
    """Create a new search suggestion"""
    db_suggestion = SearchSuggestion(**suggestion_data.dict())
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return SearchSuggestionOut.from_orm(db_suggestion)


def get_search_suggestion(db: Session, suggestion_id: int) -> Optional[SearchSuggestionOut]:
    """Get search suggestion by ID"""
    db_suggestion = db.query(SearchSuggestion).filter(SearchSuggestion.id == suggestion_id).first()
    return SearchSuggestionOut.from_orm(db_suggestion) if db_suggestion else None


def get_search_suggestions_crud(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    suggestion_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[SearchSuggestionOut], int]:
    """Get search suggestions for management"""
    query = db.query(SearchSuggestion)
    
    if suggestion_type:
        query = query.filter(SearchSuggestion.suggestion_type == suggestion_type)
    if is_active is not None:
        query = query.filter(SearchSuggestion.is_active == is_active)
    
    total = query.count()
    suggestions = query.order_by(desc(SearchSuggestion.frequency)).offset(skip).limit(limit).all()
    
    return [SearchSuggestionOut.from_orm(suggestion) for suggestion in suggestions], total


def update_search_suggestion(db: Session, suggestion_id: int, suggestion_data: SearchSuggestionUpdate) -> Optional[SearchSuggestionOut]:
    """Update search suggestion"""
    db_suggestion = db.query(SearchSuggestion).filter(SearchSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        return None
    
    for field, value in suggestion_data.dict(exclude_unset=True).items():
        setattr(db_suggestion, field, value)
    
    db.commit()
    db.refresh(db_suggestion)
    return SearchSuggestionOut.from_orm(db_suggestion)


# Search Analytics CRUD Operations
def create_search_analytics(db: Session, analytics_data: SearchAnalyticsCreate) -> SearchAnalyticsOut:
    """Create a new search analytics entry"""
    db_analytics = SearchAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return SearchAnalyticsOut.from_orm(db_analytics)


def get_search_analytics(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[SearchAnalyticsOut], int]:
    """Get search analytics"""
    query = db.query(SearchAnalytics).filter(
        SearchAnalytics.date >= start_date,
        SearchAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(SearchAnalytics.date)).offset(skip).limit(limit).all()
    
    return [SearchAnalyticsOut.from_orm(analytics) for analytics in analytics], total


def get_search_analytics_summary(db: Session, start_date: datetime, end_date: datetime) -> SearchAnalyticsSummary:
    """Get search analytics summary"""
    # This would calculate actual analytics
    # For now, returning placeholder data
    return SearchAnalyticsSummary(
        total_queries=1000,
        unique_queries=500,
        avg_search_time_ms=150.0,
        conversion_rate=0.05,
        top_queries=[{"query": "test", "count": 100}],
        queries_by_type={"product": 600, "seller": 400},
        date_range={"start": start_date, "end": end_date}
    )


# Search Synonym CRUD Operations
def create_search_synonym(db: Session, synonym_data: SearchSynonymCreate) -> SearchSynonymOut:
    """Create a new search synonym"""
    db_synonym = SearchSynonym(**synonym_data.dict())
    db.add(db_synonym)
    db.commit()
    db.refresh(db_synonym)
    return SearchSynonymOut.from_orm(db_synonym)


def get_search_synonym(db: Session, synonym_id: int) -> Optional[SearchSynonymOut]:
    """Get search synonym by ID"""
    db_synonym = db.query(SearchSynonym).filter(SearchSynonym.id == synonym_id).first()
    return SearchSynonymOut.from_orm(db_synonym) if db_synonym else None


def get_search_synonyms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    entity_type: Optional[str] = None
) -> Tuple[List[SearchSynonymOut], int]:
    """Get search synonyms"""
    query = db.query(SearchSynonym)
    
    if language:
        query = query.filter(SearchSynonym.language == language)
    if entity_type:
        query = query.filter(SearchSynonym.entity_type == entity_type)
    
    total = query.count()
    synonyms = query.offset(skip).limit(limit).all()
    
    return [SearchSynonymOut.from_orm(synonym) for synonym in synonyms], total


def update_search_synonym(db: Session, synonym_id: int, synonym_data: SearchSynonymUpdate) -> Optional[SearchSynonymOut]:
    """Update search synonym"""
    db_synonym = db.query(SearchSynonym).filter(SearchSynonym.id == synonym_id).first()
    if not db_synonym:
        return None
    
    for field, value in synonym_data.dict(exclude_unset=True).items():
        setattr(db_synonym, field, value)
    
    db.commit()
    db.refresh(db_synonym)
    return SearchSynonymOut.from_orm(db_synonym)


def get_synonyms(db: Session, term: str, language: str = "en", entity_type: Optional[str] = None) -> List[str]:
    """Get synonyms for a specific term"""
    query = db.query(SearchSynonym).filter(
        SearchSynonym.primary_term == term,
        SearchSynonym.language == language,
        SearchSynonym.is_active == True
    )
    
    if entity_type:
        query = query.filter(SearchSynonym.entity_type == entity_type)
    
    synonym_entry = query.first()
    return synonym_entry.synonyms if synonym_entry else []


# Search Blacklist CRUD Operations
def create_search_blacklist(db: Session, blacklist_data: SearchBlacklistCreate) -> SearchBlacklistOut:
    """Create a new search blacklist entry"""
    db_blacklist = SearchBlacklist(**blacklist_data.dict())
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return SearchBlacklistOut.from_orm(db_blacklist)


def get_search_blacklist(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    entity_type: Optional[str] = None
) -> Tuple[List[SearchBlacklistOut], int]:
    """Get search blacklist"""
    query = db.query(SearchBlacklist)
    
    if language:
        query = query.filter(SearchBlacklist.language == language)
    if entity_type:
        query = query.filter(SearchBlacklist.entity_type == entity_type)
    
    total = query.count()
    blacklist = query.offset(skip).limit(limit).all()
    
    return [SearchBlacklistOut.from_orm(entry) for entry in blacklist], total


def update_search_blacklist(db: Session, blacklist_id: int, blacklist_data: SearchBlacklistUpdate) -> Optional[SearchBlacklistOut]:
    """Update search blacklist entry"""
    db_blacklist = db.query(SearchBlacklist).filter(SearchBlacklist.id == blacklist_id).first()
    if not db_blacklist:
        return None
    
    for field, value in blacklist_data.dict(exclude_unset=True).items():
        setattr(db_blacklist, field, value)
    
    db.commit()
    db.refresh(db_blacklist)
    return SearchBlacklistOut.from_orm(db_blacklist)


def is_term_blacklisted(db: Session, term: str, language: str = "en") -> bool:
    """Check if a term is blacklisted"""
    blacklist_entry = db.query(SearchBlacklist).filter(
        SearchBlacklist.term == term,
        SearchBlacklist.language == language,
        SearchBlacklist.is_active == True
    ).first()
    
    return blacklist_entry is not None


# Search Boost CRUD Operations
def create_search_boost(db: Session, boost_data: SearchBoostCreate) -> SearchBoostOut:
    """Create a new search boost rule"""
    db_boost = SearchBoost(**boost_data.dict())
    db.add(db_boost)
    db.commit()
    db.refresh(db_boost)
    return SearchBoostOut.from_orm(db_boost)


def get_search_boost(db: Session, boost_id: int) -> Optional[SearchBoostOut]:
    """Get search boost by ID"""
    db_boost = db.query(SearchBoost).filter(SearchBoost.id == boost_id).first()
    return SearchBoostOut.from_orm(db_boost) if db_boost else None


def get_search_boosts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    boost_type: Optional[str] = None,
    entity_types: Optional[List[str]] = None
) -> Tuple[List[SearchBoostOut], int]:
    """Get search boosts"""
    query = db.query(SearchBoost)
    
    if boost_type:
        query = query.filter(SearchBoost.boost_type == boost_type)
    if entity_types:
        query = query.filter(SearchBoost.entity_types.contains(entity_types))
    
    total = query.count()
    boosts = query.order_by(SearchBoost.priority).offset(skip).limit(limit).all()
    
    return [SearchBoostOut.from_orm(boost) for boost in boosts], total


def update_search_boost(db: Session, boost_id: int, boost_data: SearchBoostUpdate) -> Optional[SearchBoostOut]:
    """Update search boost rule"""
    db_boost = db.query(SearchBoost).filter(SearchBoost.id == boost_id).first()
    if not db_boost:
        return None
    
    for field, value in boost_data.dict(exclude_unset=True).items():
        setattr(db_boost, field, value)
    
    db.commit()
    db.refresh(db_boost)
    return SearchBoostOut.from_orm(db_boost)
        page_size=search_request.page_size,
        total_pages=(total_results + search_request.page_size - 1) // search_request.page_size,
        results=results,
        facets=facets,
        suggestions=suggestions,
        search_time_ms=search_time_ms,
        filters_applied=search_request.filters
    )


def build_search_query(db: Session, search_request: SearchRequest):
    """Build the base search query"""
    query = db.query(SearchIndex).filter(SearchIndex.status == "indexed")
    
    # Apply search type filter
    if search_request.search_type:
        query = query.filter(SearchIndex.entity_type == search_request.search_type.value)
    
    # Apply text search
    if search_request.query:
        # Simple text search - in production, use full-text search like PostgreSQL tsvector
        search_terms = search_request.query.lower().split()
        search_conditions = []
        
        for term in search_terms:
            term_condition = or_(
                func.lower(SearchIndex.title).contains(term),
                func.lower(SearchIndex.description).contains(term),
                func.lower(SearchIndex.keywords.cast(String)).contains(term),
                func.lower(SearchIndex.tags.cast(String)).contains(term)
            )
            search_conditions.append(term_condition)
        
        if search_conditions:
            query = query.filter(and_(*search_conditions))
    
    return query


def apply_filters(query, filters: Dict[str, Any]):
    """Apply search filters"""
    for field, value in filters.items():
        if field == "price_range" and value:
            if value.get("min_price"):
                query = query.filter(SearchIndex.metadata["price"].astext.cast(Float) >= value["min_price"])
            if value.get("max_price"):
                query = query.filter(SearchIndex.metadata["price"].astext.cast(Float) <= value["max_price"])
        
        elif field == "categories" and value:
            query = query.filter(SearchIndex.categories.overlap(value))
        
        elif field == "tags" and value:
            query = query.filter(SearchIndex.tags.overlap(value))
        
        elif field == "location" and value:
            # Location filtering would require geospatial queries
            # For now, filter by country/city in metadata
            if value.get("country"):
                query = query.filter(SearchIndex.metadata["country"].astext == value["country"])
            if value.get("city"):
                query = query.filter(SearchIndex.metadata["city"].astext == value["city"])
        
        elif field == "date_range" and value:
            if value.get("start_date"):
                query = query.filter(SearchIndex.metadata["created_at"].astext.cast(DateTime) >= value["start_date"])
            if value.get("end_date"):
                query = query.filter(SearchIndex.metadata["created_at"].astext.cast(DateTime) <= value["end_date"])
        
        elif field == "attributes" and value:
            for attr_name, attr_value in value.items():
                query = query.filter(SearchIndex.attributes[attr_name].astext == str(attr_value))
    
    return query


def apply_sorting(query, sort_by: str, sort_order: str):
    """Apply sorting to search results"""
    if sort_by == "relevance":
        query = query.order_by(desc(SearchIndex.relevance_score))
    elif sort_by == "price":
        query = query.order_by(SearchIndex.metadata["price"].astext.cast(Float))
        if sort_order == "desc":
            query = query.order_by(desc(SearchIndex.metadata["price"].astext.cast(Float)))
    elif sort_by == "rating":
        query = query.order_by(desc(SearchIndex.metadata["rating"].astext.cast(Float)))
    elif sort_by == "popularity":
        query = query.order_by(desc(SearchIndex.popularity_score))
    elif sort_by == "recency":
        query = query.order_by(desc(SearchIndex.recency_score))
    elif sort_by == "name":
        query = query.order_by(SearchIndex.title)
        if sort_order == "desc":
            query = query.order_by(desc(SearchIndex.title))
    elif sort_by == "created_at":
        query = query.order_by(desc(SearchIndex.created_at))
    
    return query


def get_search_facets(db: Session, search_request: SearchRequest) -> List[SearchFacet]:
    """Get search facets for filtering"""
    facets = []
    
    # Get category facets
    category_facets = db.query(
        func.jsonb_array_elements(SearchIndex.categories).label('category'),
        func.count().label('count')
    ).filter(
        SearchIndex.status == "indexed"
    ).group_by('category').all()
    
    if category_facets:
        facets.append(SearchFacet(
            field="categories",
            values=[{"value": str(f.category), "count": f.count, "selected": False} for f in category_facets],
            type="multi_select"
        ))
    
    # Get price range facets
    price_facets = db.query(
        func.avg(SearchIndex.metadata["price"].astext.cast(Float)).label('avg_price'),
        func.min(SearchIndex.metadata["price"].astext.cast(Float)).label('min_price'),
        func.max(SearchIndex.metadata["price"].astext.cast(Float)).label('max_price')
    ).filter(
        SearchIndex.status == "indexed"
    ).first()
    
    if price_facets and price_facets.min_price and price_facets.max_price:
        facets.append(SearchFacet(
            field="price_range",
            values=[{
                "min": price_facets.min_price,
                "max": price_facets.max_price,
                "avg": price_facets.avg_price
            }],
            type="range"
        ))
    
    return facets


def get_search_suggestions(
    db: Session, 
    query: str, 
    search_type: Optional[str] = None,
    limit: int = 10
) -> List[SearchSuggestionSchema]:
    """Get search suggestions for autocomplete"""
    suggestions = []
    
    # Get suggestions from search_suggestions table
    suggestion_query = db.query(SearchSuggestion).filter(
        SearchSuggestion.is_active == True,
        func.lower(SearchSuggestion.suggestion_text).contains(query.lower())
    )
    
    if search_type:
        suggestion_query = suggestion_query.filter(SearchSuggestion.suggestion_type == search_type)
    
    db_suggestions = suggestion_query.order_by(
        desc(SearchSuggestion.relevance_score),
        desc(SearchSuggestion.frequency)
    ).limit(limit).all()
    
    for suggestion in db_suggestions:
        suggestions.append(SearchSuggestionSchema(
            text=suggestion.suggestion_text,
            type=suggestion.suggestion_type,
            relevance_score=suggestion.relevance_score,
            entity_id=suggestion.entity_id,
            entity_type=suggestion.entity_type
        ))
    
    return suggestions


def log_search_query(
    db: Session,
    search_request: SearchRequest,
    total_results: int,
    results_returned: int,
    search_time_ms: int,
    user_id: Optional[int] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    referrer: Optional[str] = None
):
    """Log search query for analytics"""
    search_query = SearchQuery(
        query_text=search_request.query,
        search_type=search_request.search_type.value if search_request.search_type else "all",
        filters_applied=search_request.filters,
        user_id=user_id,
        session_id=session_id,
        total_results=total_results,
        results_returned=results_returned,
        search_time_ms=search_time_ms,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer
    )
    
    db.add(search_query)
    db.commit()


# Search Index CRUD Operations
def create_search_index(db: Session, index_data: SearchIndexCreate) -> SearchIndex:
    """Create a new search index entry"""
    db_index = SearchIndex(
        entity_type=index_data.entity_type.value,
        entity_id=index_data.entity_id,
        title=index_data.title,
        description=index_data.description,
        keywords=index_data.keywords,
        tags=index_data.tags,
        categories=index_data.categories,
        metadata=index_data.metadata,
        attributes=index_data.attributes,
        status="pending"
    )
    db.add(db_index)
    db.commit()
    db.refresh(db_index)
    return db_index


def get_search_index(db: Session, index_id: int) -> Optional[SearchIndex]:
    """Get search index by ID"""
    return db.query(SearchIndex).filter(SearchIndex.id == index_id).first()


def get_search_index_by_entity(db: Session, entity_type: str, entity_id: int) -> Optional[SearchIndex]:
    """Get search index by entity type and ID"""
    return db.query(SearchIndex).filter(
        SearchIndex.entity_type == entity_type,
        SearchIndex.entity_id == entity_id
    ).first()


def get_search_indexes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    status: Optional[str] = None
) -> Tuple[List[SearchIndex], int]:
    """Get search indexes with filtering"""
    query = db.query(SearchIndex)
    
    if entity_type:
        query = query.filter(SearchIndex.entity_type == entity_type)
    if status:
        query = query.filter(SearchIndex.status == status)
    
    total = query.count()
    indexes = query.offset(skip).limit(limit).all()
    
    return indexes, total


def update_search_index(db: Session, index_id: int, index_data: SearchIndexUpdate) -> Optional[SearchIndex]:
    """Update search index"""
    db_index = get_search_index(db, index_id)
    if not db_index:
        return None
    
    update_data = index_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_index, field, value)
    
    db_index.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_index)
    return db_index


def delete_search_index(db: Session, index_id: int) -> bool:
    """Delete search index"""
    db_index = get_search_index(db, index_id)
    if not db_index:
        return False
    
    db.delete(db_index)
    db.commit()
    return True


def reindex_entities(
    db: Session,
    entity_type: SearchIndexType,
    entity_ids: Optional[List[int]] = None,
    force_reindex: bool = False
) -> SearchIndexResponse:
    """Reindex entities for search"""
    start_time = datetime.utcnow()
    indexed_count = 0
    failed_count = 0
    errors = []
    
    # This would typically involve:
    # 1. Fetching entities from their respective tables
    # 2. Processing and indexing them
    # 3. Updating the search index
    
    # For now, returning placeholder response
    processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
    
    return SearchIndexResponse(
        indexed_count=indexed_count,
        failed_count=failed_count,
        errors=errors,
        processing_time_ms=processing_time_ms
    )


# Search Query CRUD Operations
def get_search_queries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search_type: Optional[str] = None,
    user_id: Optional[int] = None
) -> Tuple[List[SearchQuery], int]:
    """Get search queries with filtering"""
    query = db.query(SearchQuery)
    
    if search_type:
        query = query.filter(SearchQuery.search_type == search_type)
    if user_id:
        query = query.filter(SearchQuery.user_id == user_id)
    
    total = query.count()
    queries = query.order_by(desc(SearchQuery.created_at)).offset(skip).limit(limit).all()
    
    return queries, total


def update_search_query(db: Session, query_id: int, query_data: SearchQueryUpdate) -> Optional[SearchQuery]:
    """Update search query with analytics data"""
    db_query = db.query(SearchQuery).filter(SearchQuery.id == query_id).first()
    if not db_query:
        return None
    
    update_data = query_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_query, field, value)
    
    db.commit()
    db.refresh(db_query)
    return db_query


# Search Filter CRUD Operations
def create_search_filter(db: Session, filter_data: SearchFilterCreate) -> SearchFilter:
    """Create a new search filter"""
    db_filter = SearchFilter(**filter_data.dict())
    db.add(db_filter)
    db.commit()
    db.refresh(db_filter)
    return db_filter


def get_search_filters(
    db: Session,
    entity_types: Optional[List[str]] = None,
    is_active: Optional[bool] = None
) -> List[SearchFilter]:
    """Get search filters"""
    query = db.query(SearchFilter)
    
    if entity_types:
        query = query.filter(SearchFilter.entity_types.overlap(entity_types))
    if is_active is not None:
        query = query.filter(SearchFilter.is_active == is_active)
    
    return query.order_by(SearchFilter.sort_order).all()


def update_search_filter(db: Session, filter_id: int, filter_data: SearchFilterUpdate) -> Optional[SearchFilter]:
    """Update search filter"""
    db_filter = db.query(SearchFilter).filter(SearchFilter.id == filter_id).first()
    if not db_filter:
        return None
    
    update_data = filter_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_filter, field, value)
    
    db_filter.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_filter)
    return db_filter


# Search Suggestion CRUD Operations
def create_search_suggestion(db: Session, suggestion_data: SearchSuggestionCreate) -> SearchSuggestion:
    """Create a new search suggestion"""
    db_suggestion = SearchSuggestion(**suggestion_data.dict())
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def get_search_suggestions_crud(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    suggestion_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> Tuple[List[SearchSuggestion], int]:
    """Get search suggestions with filtering"""
    query = db.query(SearchSuggestion)
    
    if suggestion_type:
        query = query.filter(SearchSuggestion.suggestion_type == suggestion_type)
    if is_active is not None:
        query = query.filter(SearchSuggestion.is_active == is_active)
    
    total = query.count()
    suggestions = query.order_by(desc(SearchSuggestion.frequency)).offset(skip).limit(limit).all()
    
    return suggestions, total


def update_search_suggestion(db: Session, suggestion_id: int, suggestion_data: SearchSuggestionUpdate) -> Optional[SearchSuggestion]:
    """Update search suggestion"""
    db_suggestion = db.query(SearchSuggestion).filter(SearchSuggestion.id == suggestion_id).first()
    if not db_suggestion:
        return None
    
    update_data = suggestion_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_suggestion, field, value)
    
    db_suggestion.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


# Search Analytics CRUD Operations
def create_search_analytics(db: Session, analytics_data: SearchAnalyticsCreate) -> SearchAnalytics:
    """Create search analytics entry"""
    db_analytics = SearchAnalytics(**analytics_data.dict())
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    return db_analytics


def get_search_analytics(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[SearchAnalytics], int]:
    """Get search analytics for date range"""
    query = db.query(SearchAnalytics).filter(
        SearchAnalytics.date >= start_date,
        SearchAnalytics.date <= end_date
    )
    
    total = query.count()
    analytics = query.order_by(desc(SearchAnalytics.date)).offset(skip).limit(limit).all()
    
    return analytics, total


def get_search_analytics_summary(db: Session, start_date: datetime, end_date: datetime) -> SearchAnalyticsSummary:
    """Get search analytics summary"""
    # This would aggregate analytics data
    # For now, returning placeholder data
    return SearchAnalyticsSummary(
        total_queries=1000,
        unique_queries=800,
        avg_search_time_ms=150.0,
        conversion_rate=0.05,
        top_queries=[{"query": "product", "count": 100}],
        queries_by_type={"product": 600, "seller": 400},
        date_range={"start": start_date, "end": end_date}
    )


# Search Synonym CRUD Operations
def create_search_synonym(db: Session, synonym_data: SearchSynonymCreate) -> SearchSynonym:
    """Create a new search synonym"""
    db_synonym = SearchSynonym(**synonym_data.dict())
    db.add(db_synonym)
    db.commit()
    db.refresh(db_synonym)
    return db_synonym


def get_search_synonyms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    entity_type: Optional[str] = None
) -> Tuple[List[SearchSynonym], int]:
    """Get search synonyms with filtering"""
    query = db.query(SearchSynonym)
    
    if language:
        query = query.filter(SearchSynonym.language == language)
    if entity_type:
        query = query.filter(SearchSynonym.entity_type == entity_type)
    
    total = query.count()
    synonyms = query.offset(skip).limit(limit).all()
    
    return synonyms, total


def update_search_synonym(db: Session, synonym_id: int, synonym_data: SearchSynonymUpdate) -> Optional[SearchSynonym]:
    """Update search synonym"""
    db_synonym = db.query(SearchSynonym).filter(SearchSynonym.id == synonym_id).first()
    if not db_synonym:
        return None
    
    update_data = synonym_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_synonym, field, value)
    
    db_synonym.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_synonym)
    return db_synonym


# Search Blacklist CRUD Operations
def create_search_blacklist(db: Session, blacklist_data: SearchBlacklistCreate) -> SearchBlacklist:
    """Create a new search blacklist entry"""
    db_blacklist = SearchBlacklist(**blacklist_data.dict())
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist


def get_search_blacklist(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    language: Optional[str] = None,
    entity_type: Optional[str] = None
) -> Tuple[List[SearchBlacklist], int]:
    """Get search blacklist with filtering"""
    query = db.query(SearchBlacklist)
    
    if language:
        query = query.filter(SearchBlacklist.language == language)
    if entity_type:
        query = query.filter(SearchBlacklist.entity_type == entity_type)
    
    total = query.count()
    blacklist = query.offset(skip).limit(limit).all()
    
    return blacklist, total


def update_search_blacklist(db: Session, blacklist_id: int, blacklist_data: SearchBlacklistUpdate) -> Optional[SearchBlacklist]:
    """Update search blacklist entry"""
    db_blacklist = db.query(SearchBlacklist).filter(SearchBlacklist.id == blacklist_id).first()
    if not db_blacklist:
        return None
    
    update_data = blacklist_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_blacklist, field, value)
    
    db_blacklist.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist


# Search Boost CRUD Operations
def create_search_boost(db: Session, boost_data: SearchBoostCreate) -> SearchBoost:
    """Create a new search boost rule"""
    db_boost = SearchBoost(**boost_data.dict())
    db.add(db_boost)
    db.commit()
    db.refresh(db_boost)
    return db_boost


def get_search_boosts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    boost_type: Optional[str] = None,
    entity_types: Optional[List[str]] = None
) -> Tuple[List[SearchBoost], int]:
    """Get search boosts with filtering"""
    query = db.query(SearchBoost)
    
    if boost_type:
        query = query.filter(SearchBoost.boost_type == boost_type)
    if entity_types:
        query = query.filter(SearchBoost.entity_types.overlap(entity_types))
    
    total = query.count()
    boosts = query.order_by(desc(SearchBoost.priority)).offset(skip).limit(limit).all()
    
    return boosts, total


def update_search_boost(db: Session, boost_id: int, boost_data: SearchBoostUpdate) -> Optional[SearchBoost]:
    """Update search boost rule"""
    db_boost = db.query(SearchBoost).filter(SearchBoost.id == boost_id).first()
    if not db_boost:
        return None
    
    update_data = boost_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_boost, field, value)
    
    db_boost.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_boost)
    return db_boost


# Utility Functions
def is_term_blacklisted(db: Session, term: str, language: str = "en") -> bool:
    """Check if a search term is blacklisted"""
    blacklisted = db.query(SearchBlacklist).filter(
        SearchBlacklist.term == term.lower(),
        SearchBlacklist.language == language,
        SearchBlacklist.is_active == True
    ).first()
    
    return blacklisted is not None


def get_synonyms(db: Session, term: str, language: str = "en", entity_type: Optional[str] = None) -> List[str]:
    """Get synonyms for a search term"""
    synonyms = db.query(SearchSynonym).filter(
        SearchSynonym.primary_term == term.lower(),
        SearchSynonym.language == language,
        SearchSynonym.is_active == True
    )
    
    if entity_type:
        synonyms = synonyms.filter(
            or_(
                SearchSynonym.entity_type.is_(None),
                SearchSynonym.entity_type == entity_type
            )
        )
    
    synonym_entry = synonyms.first()
    return synonym_entry.synonyms if synonym_entry else []


def apply_search_boosts(db: Session, query, entity_type: str):
    """Apply search boost rules to query"""
    boosts = db.query(SearchBoost).filter(
        SearchBoost.is_active == True,
        SearchBoost.entity_types.contains([entity_type])
    ).order_by(desc(SearchBoost.priority)).all()
    
    for boost in boosts:
        if boost.boost_type == "keyword" and boost.boost_value:
            # Apply keyword boost
            query = query.filter(
                or_(
                    func.lower(SearchIndex.title).contains(boost.boost_value.lower()),
                    func.lower(SearchIndex.description).contains(boost.boost_value.lower())
                )
            )
        elif boost.boost_type == "attribute" and boost.boost_field:
            # Apply attribute boost
            query = query.filter(
                SearchIndex.attributes[boost.boost_field].astext == boost.boost_value
            )
    
    return query


