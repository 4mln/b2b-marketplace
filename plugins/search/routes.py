"""
Advanced Search & Filters System Routes
Comprehensive search capabilities for the B2B marketplace
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.auth import get_current_user_sync as get_current_user, get_current_user_optional_sync as get_current_user_optional
from plugins.auth.models import User
from . import crud, schemas
from .schemas import SearchIndexType, FilterType, SortField, SortOrder

router = APIRouter(prefix="/search", tags=["search"])


# Core Search Routes
@router.post("/", response_model=schemas.SearchResponse)
def search(
    search_request: schemas.SearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Perform a search query"""
    # Get client information
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")
    
    # Check for blacklisted terms
    if crud.is_term_blacklisted(db, search_request.query):
        raise HTTPException(status_code=400, detail="Search term is not allowed")
    
    return crud.perform_search(
        db=db,
        search_request=search_request,
        user_id=current_user.id if current_user else None,
        session_id=request.headers.get("x-session-id"),
        ip_address=client_ip,
        user_agent=user_agent,
        referrer=referrer
    )


@router.post("/advanced", response_model=schemas.SearchResponse)
def advanced_search(
    search_request: schemas.AdvancedSearchRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Perform an advanced search with multiple filters"""
    # Convert advanced search to regular search request
    regular_search = schemas.SearchRequest(
        query=search_request.query or "",
        search_type=search_request.search_types[0] if search_request.search_types else None,
        filters={
            "price_range": search_request.price_range.dict() if search_request.price_range else None,
            "date_range": search_request.date_range.dict() if search_request.date_range else None,
            "location": search_request.location.dict() if search_request.location else None,
            "categories": search_request.categories,
            "tags": search_request.tags,
            "attributes": search_request.attributes
        },
        sort_by=search_request.sort_by,
        sort_order=search_request.sort_order,
        page=search_request.page,
        page_size=search_request.page_size,
        include_facets=search_request.include_facets,
        include_suggestions=search_request.include_suggestions
    )
    
    # Get client information
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")
    
    return crud.perform_search(
        db=db,
        search_request=regular_search,
        user_id=current_user.id if current_user else None,
        session_id=request.headers.get("x-session-id"),
        ip_address=client_ip,
        user_agent=user_agent,
        referrer=referrer
    )


@router.get("/suggestions", response_model=List[schemas.SearchSuggestion])
def get_suggestions(
    query: str = Query(..., min_length=1),
    search_type: Optional[SearchIndexType] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get search suggestions for autocomplete"""
    return crud.get_search_suggestions(db, query, search_type.value if search_type else None, limit)


@router.get("/facets", response_model=List[schemas.SearchFacet])
def get_facets(
    search_type: Optional[SearchIndexType] = None,
    filters: Optional[str] = None,  # JSON string of filters
    facet_fields: Optional[str] = None,  # JSON string of facet fields
    db: Session = Depends(get_db)
):
    """Get search facets for filtering"""
    # Parse filters and facet fields from JSON strings
    parsed_filters = None
    parsed_facet_fields = None
    
    if filters:
        try:
            import json
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid filters format")
    
    if facet_fields:
        try:
            import json
            parsed_facet_fields = json.loads(facet_fields)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid facet fields format")
    
    # Create a mock search request for facet generation
    search_request = schemas.SearchRequest(
        query="",
        search_type=search_type,
        filters=parsed_filters,
        include_facets=True
    )
    
    return crud.get_search_facets(db, search_request)


# Search Index Management Routes
@router.post("/index", response_model=schemas.SearchIndexResponse)
def create_search_index(
    index_request: schemas.SearchIndexRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update search index for entities"""
    return crud.reindex_entities(
        db=db,
        entity_type=index_request.entity_type,
        entity_ids=index_request.entity_ids,
        force_reindex=index_request.force_reindex
    )


@router.get("/index", response_model=schemas.SearchIndexListResponse)
def get_search_indexes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_type: Optional[SearchIndexType] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search indexes"""
    indexes, total = crud.get_search_indexes(
        db=db,
        skip=skip,
        limit=limit,
        entity_type=entity_type.value if entity_type else None,
        status=status
    )
    
    return schemas.SearchIndexListResponse(
        items=indexes,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/index/{index_id}", response_model=schemas.SearchIndexOut)
def get_search_index(
    index_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search index by ID"""
    index = crud.get_search_index(db, index_id)
    if not index:
        raise HTTPException(status_code=404, detail="Search index not found")
    
    return index


@router.patch("/index/{index_id}", response_model=schemas.SearchIndexOut)
def update_search_index(
    index_id: int,
    index_data: schemas.SearchIndexUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search index"""
    updated_index = crud.update_search_index(db, index_id, index_data)
    if not updated_index:
        raise HTTPException(status_code=404, detail="Search index not found")
    
    return updated_index


@router.delete("/index/{index_id}")
def delete_search_index(
    index_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete search index"""
    success = crud.delete_search_index(db, index_id)
    if not success:
        raise HTTPException(status_code=404, detail="Search index not found")
    
    return {"message": "Search index deleted successfully"}


# Search Query Analytics Routes
@router.get("/queries", response_model=schemas.SearchQueryListResponse)
def get_search_queries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search query history"""
    queries, total = crud.get_search_queries(
        db=db,
        skip=skip,
        limit=limit,
        search_type=search_type,
        user_id=user_id
    )
    
    return schemas.SearchQueryListResponse(
        queries=queries,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/queries/{query_id}", response_model=schemas.SearchQueryOut)
def update_search_query(
    query_id: int,
    query_data: schemas.SearchQueryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search query with analytics data"""
    updated_query = crud.update_search_query(db, query_id, query_data)
    if not updated_query:
        raise HTTPException(status_code=404, detail="Search query not found")
    
    return updated_query


# Search Filter Management Routes
@router.post("/filters", response_model=schemas.SearchFilterOut)
def create_search_filter(
    filter_data: schemas.SearchFilterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new search filter"""
    return crud.create_search_filter(db, filter_data)


@router.get("/filters", response_model=schemas.SearchFilterListResponse)
def get_search_filters(
    entity_types: Optional[str] = None,  # JSON string of entity types
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get search filters"""
    parsed_entity_types = None
    if entity_types:
        try:
            import json
            parsed_entity_types = json.loads(entity_types)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid entity types format")
    
    filters = crud.get_search_filters(
        db=db,
        entity_types=parsed_entity_types,
        is_active=is_active
    )
    
    return schemas.SearchFilterListResponse(filters=filters, total=len(filters))


@router.patch("/filters/{filter_id}", response_model=schemas.SearchFilterOut)
def update_search_filter(
    filter_id: int,
    filter_data: schemas.SearchFilterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search filter"""
    updated_filter = crud.update_search_filter(db, filter_id, filter_data)
    if not updated_filter:
        raise HTTPException(status_code=404, detail="Search filter not found")
    
    return updated_filter


# Search Suggestion Management Routes
@router.post("/suggestions", response_model=schemas.SearchSuggestionOut)
def create_search_suggestion(
    suggestion_data: schemas.SearchSuggestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new search suggestion"""
    return crud.create_search_suggestion(db, suggestion_data)


@router.get("/suggestions/manage", response_model=schemas.SearchSuggestionListResponse)
def get_search_suggestions_manage(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    suggestion_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search suggestions for management"""
    suggestions, total = crud.get_search_suggestions_crud(
        db=db,
        skip=skip,
        limit=limit,
        suggestion_type=suggestion_type,
        is_active=is_active
    )
    
    return schemas.SearchSuggestionListResponse(
        suggestions=suggestions,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/suggestions/{suggestion_id}", response_model=schemas.SearchSuggestionOut)
def update_search_suggestion(
    suggestion_id: int,
    suggestion_data: schemas.SearchSuggestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search suggestion"""
    updated_suggestion = crud.update_search_suggestion(db, suggestion_id, suggestion_data)
    if not updated_suggestion:
        raise HTTPException(status_code=404, detail="Search suggestion not found")
    
    return updated_suggestion


# Search Analytics Routes
@router.get("/analytics", response_model=schemas.SearchAnalyticsListResponse)
def get_search_analytics(
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search analytics"""
    analytics, total = crud.get_search_analytics(
        db=db,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return schemas.SearchAnalyticsListResponse(
        analytics=analytics,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/analytics/summary", response_model=schemas.SearchAnalyticsSummary)
def get_search_analytics_summary(
    start_date: datetime = Query(default_factory=lambda: datetime.utcnow() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=lambda: datetime.utcnow()),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search analytics summary"""
    return crud.get_search_analytics_summary(db, start_date, end_date)


# Search Synonym Management Routes
@router.post("/synonyms", response_model=schemas.SearchSynonymOut)
def create_search_synonym(
    synonym_data: schemas.SearchSynonymCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new search synonym"""
    return crud.create_search_synonym(db, synonym_data)


@router.get("/synonyms", response_model=schemas.SearchSynonymListResponse)
def get_search_synonyms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    language: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search synonyms"""
    synonyms, total = crud.get_search_synonyms(
        db=db,
        skip=skip,
        limit=limit,
        language=language,
        entity_type=entity_type
    )
    
    return schemas.SearchSynonymListResponse(
        synonyms=synonyms,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/synonyms/{synonym_id}", response_model=schemas.SearchSynonymOut)
def update_search_synonym(
    synonym_id: int,
    synonym_data: schemas.SearchSynonymUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search synonym"""
    updated_synonym = crud.update_search_synonym(db, synonym_id, synonym_data)
    if not updated_synonym:
        raise HTTPException(status_code=404, detail="Search synonym not found")
    
    return updated_synonym


# Search Blacklist Management Routes
@router.post("/blacklist", response_model=schemas.SearchBlacklistOut)
def create_search_blacklist(
    blacklist_data: schemas.SearchBlacklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new search blacklist entry"""
    return crud.create_search_blacklist(db, blacklist_data)


@router.get("/blacklist", response_model=schemas.SearchBlacklistListResponse)
def get_search_blacklist(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    language: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search blacklist"""
    blacklist, total = crud.get_search_blacklist(
        db=db,
        skip=skip,
        limit=limit,
        language=language,
        entity_type=entity_type
    )
    
    return schemas.SearchBlacklistListResponse(
        blacklist=blacklist,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/blacklist/{blacklist_id}", response_model=schemas.SearchBlacklistOut)
def update_search_blacklist(
    blacklist_id: int,
    blacklist_data: schemas.SearchBlacklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search blacklist entry"""
    updated_blacklist = crud.update_search_blacklist(db, blacklist_id, blacklist_data)
    if not updated_blacklist:
        raise HTTPException(status_code=404, detail="Search blacklist entry not found")
    
    return updated_blacklist


# Search Boost Management Routes
@router.post("/boosts", response_model=schemas.SearchBoostOut)
def create_search_boost(
    boost_data: schemas.SearchBoostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new search boost rule"""
    return crud.create_search_boost(db, boost_data)


@router.get("/boosts", response_model=schemas.SearchBoostListResponse)
def get_search_boosts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    boost_type: Optional[str] = None,
    entity_types: Optional[str] = None,  # JSON string of entity types
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search boosts"""
    parsed_entity_types = None
    if entity_types:
        try:
            import json
            parsed_entity_types = json.loads(entity_types)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid entity types format")
    
    boosts, total = crud.get_search_boosts(
        db=db,
        skip=skip,
        limit=limit,
        boost_type=boost_type,
        entity_types=parsed_entity_types
    )
    
    return schemas.SearchBoostListResponse(
        boosts=boosts,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/boosts/{boost_id}", response_model=schemas.SearchBoostOut)
def update_search_boost(
    boost_id: int,
    boost_data: schemas.SearchBoostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update search boost rule"""
    updated_boost = crud.update_search_boost(db, boost_id, boost_data)
    if not updated_boost:
        raise HTTPException(status_code=404, detail="Search boost rule not found")
    
    return updated_boost


# Utility Routes
@router.get("/check-blacklist/{term}")
def check_blacklist(
    term: str,
    language: str = Query("en"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if a term is blacklisted"""
    is_blacklisted = crud.is_term_blacklisted(db, term, language)
    return {"term": term, "is_blacklisted": is_blacklisted}


@router.get("/synonyms/{term}")
def get_term_synonyms(
    term: str,
    language: str = Query("en"),
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get synonyms for a specific term"""
    synonyms = crud.get_synonyms(db, term, language, entity_type)
    return {"term": term, "synonyms": synonyms}


# Search Performance Routes
@router.get("/performance", response_model=schemas.SearchPerformanceMetrics)
def get_search_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search performance metrics"""
    # This would calculate actual performance metrics
    # For now, returning placeholder data
    return schemas.SearchPerformanceMetrics(
        avg_response_time_ms=150.0,
        queries_per_second=10.5,
        cache_hit_rate=0.75,
        index_size_mb=1024.0,
        last_index_update=datetime.utcnow()
    )


# Search Trends Routes
@router.get("/trends", response_model=List[schemas.SearchTrends])
def get_search_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get search trends over time"""
    # This would calculate actual search trends
    # For now, returning placeholder data
    trends = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=i)
        trends.append(schemas.SearchTrends(
            date=date,
            query_count=100 + i * 10,
            unique_users=50 + i * 5,
            avg_results_per_query=15.5,
            zero_result_rate=0.05
        ))
    
    return trends


