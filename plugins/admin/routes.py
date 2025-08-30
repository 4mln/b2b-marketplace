"""
Admin Dashboard System Routes
Comprehensive administrative capabilities for the B2B marketplace
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.db.session import get_db
from app.core.auth import get_current_user_sync as get_current_user
from plugins.auth.models import User
from . import crud, schemas
from .models import AdminRole, AdminPermission, AdminActionType, AdminActionStatus

router = APIRouter(prefix="/admin", tags=["admin"])


# Admin Authentication and Authorization
def require_admin_permission(permission: AdminPermission):
    """Decorator to require specific admin permission"""
    def permission_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        admin_user = crud.get_admin_user_by_user_id(db, current_user.id)
        if not admin_user or not admin_user.is_active:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        if not crud.check_admin_permission(db, admin_user.id, permission):
            raise HTTPException(status_code=403, detail=f"Permission '{permission}' required")
        
        return admin_user
    return permission_checker


def require_admin_role(role: AdminRole):
    """Decorator to require specific admin role"""
    def role_checker(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        admin_user = crud.get_admin_user_by_user_id(db, current_user.id)
        if not admin_user or not admin_user.is_active:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        if admin_user.role != role and admin_user.role != AdminRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail=f"Role '{role}' required")
        
        return admin_user
    return role_checker


# Dashboard Overview Routes
@router.get("/dashboard/overview", response_model=schemas.DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get dashboard overview statistics"""
    return crud.get_dashboard_overview(db)


@router.get("/dashboard/user-stats", response_model=schemas.UserManagementStats)
def get_user_management_stats(
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_USERS))
):
    """Get user management statistics"""
    return crud.get_user_management_stats(db)


@router.get("/dashboard/financial-stats", response_model=schemas.FinancialStats)
def get_financial_stats(
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_FINANCIAL_REPORTS))
):
    """Get financial statistics"""
    return crud.get_financial_stats(db)


@router.get("/dashboard/content-stats", response_model=schemas.ContentModerationStats)
def get_content_moderation_stats(
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MODERATE_PRODUCTS))
):
    """Get content moderation statistics"""
    return crud.get_content_moderation_stats(db)


@router.get("/dashboard/system-health", response_model=schemas.SystemHealthStats)
def get_system_health_stats(
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get system health statistics"""
    return crud.get_system_health_stats(db)


# Admin User Management Routes
@router.post("/users", response_model=schemas.AdminUserOut)
def create_admin_user(
    admin_data: schemas.AdminUserCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_role(AdminRole.SUPER_ADMIN))
):
    """Create a new admin user (Super Admin only)"""
    # Check if user already exists as admin
    existing_admin = crud.get_admin_user_by_user_id(db, admin_data.user_id)
    if existing_admin:
        raise HTTPException(status_code=400, detail="User is already an admin")
    
    return crud.create_admin_user(db, admin_data)


@router.get("/users", response_model=schemas.AdminUserListResponse)
def get_admin_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[AdminRole] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_USERS))
):
    """Get admin users"""
    admin_users, total = crud.get_admin_users(db, skip, limit, role, is_active)
    return schemas.AdminUserListResponse(
        admin_users=admin_users,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/users/{admin_id}", response_model=schemas.AdminUserOut)
def get_admin_user(
    admin_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_USERS))
):
    """Get admin user by ID"""
    db_admin = crud.get_admin_user(db, admin_id)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    return db_admin


@router.patch("/users/{admin_id}", response_model=schemas.AdminUserOut)
def update_admin_user(
    admin_id: int,
    admin_data: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_role(AdminRole.SUPER_ADMIN))
):
    """Update admin user (Super Admin only)"""
    updated_admin = crud.update_admin_user(db, admin_id, admin_data)
    if not updated_admin:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    return updated_admin


@router.delete("/users/{admin_id}")
def delete_admin_user(
    admin_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_role(AdminRole.SUPER_ADMIN))
):
    """Delete admin user (Super Admin only)"""
    success = crud.delete_admin_user(db, admin_id)
    if not success:
        raise HTTPException(status_code=404, detail="Admin user not found")
    
    return {"message": "Admin user deleted successfully"}


# Admin Action Routes
@router.get("/actions", response_model=schemas.AdminActionListResponse)
def get_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[AdminActionType] = None,
    status: Optional[AdminActionStatus] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_AUDIT_LOGS))
):
    """Get admin actions"""
    actions, total = crud.get_admin_actions(db, None, skip, limit, action_type, status)
    return schemas.AdminActionListResponse(
        actions=actions,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/actions/my", response_model=schemas.AdminActionListResponse)
def get_my_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[AdminActionType] = None,
    status: Optional[AdminActionStatus] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_AUDIT_LOGS))
):
    """Get current admin's actions"""
    actions, total = crud.get_admin_actions(db, admin_user.id, skip, limit, action_type, status)
    return schemas.AdminActionListResponse(
        actions=actions,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


# System Configuration Routes
@router.post("/config", response_model=schemas.SystemConfigOut)
def create_system_config(
    config_data: schemas.SystemConfigCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.CONFIGURE_SYSTEM))
):
    """Create a new system configuration"""
    # Check if config key already exists
    existing_config = crud.get_system_config_by_key(db, config_data.key)
    if existing_config:
        raise HTTPException(status_code=400, detail="Configuration key already exists")
    
    return crud.create_system_config(db, config_data)


@router.get("/config", response_model=schemas.SystemConfigListResponse)
def get_system_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.CONFIGURE_SYSTEM))
):
    """Get system configurations"""
    configs, total = crud.get_system_configs(db, skip, limit, category, is_public)
    return schemas.SystemConfigListResponse(
        configs=configs,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/config/{config_id}", response_model=schemas.SystemConfigOut)
def get_system_config(
    config_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.CONFIGURE_SYSTEM))
):
    """Get system configuration by ID"""
    config = crud.get_system_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return config


@router.patch("/config/{config_id}", response_model=schemas.SystemConfigOut)
def update_system_config(
    config_id: int,
    config_data: schemas.SystemConfigUpdate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.CONFIGURE_SYSTEM))
):
    """Update system configuration"""
    updated_config = crud.update_system_config(db, config_id, config_data)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return updated_config


@router.delete("/config/{config_id}")
def delete_system_config(
    config_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.CONFIGURE_SYSTEM))
):
    """Delete system configuration"""
    success = crud.delete_system_config(db, config_id)
    if not success:
        raise HTTPException(status_code=404, detail="Configuration not found")
    
    return {"message": "Configuration deleted successfully"}


# Audit Log Routes
@router.get("/audit-logs", response_model=schemas.AuditLogListResponse)
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    event_type: Optional[str] = None,
    event_category: Optional[str] = None,
    user_id: Optional[int] = None,
    admin_user_id: Optional[int] = None,
    target_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_AUDIT_LOGS))
):
    """Get audit logs"""
    filters = schemas.AuditLogFilters(
        event_type=event_type,
        event_category=event_category,
        user_id=user_id,
        admin_user_id=admin_user_id,
        target_type=target_type,
        date_from=date_from,
        date_to=date_to
    )
    
    logs, total = crud.get_audit_logs(db, skip, limit, filters)
    return schemas.AuditLogListResponse(
        logs=logs,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


# Support Ticket Routes
@router.post("/support/tickets", response_model=schemas.SupportTicketOut)
def create_support_ticket(
    ticket_data: schemas.SupportTicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new support ticket"""
    return crud.create_support_ticket(db, ticket_data, current_user.id)


@router.get("/support/tickets", response_model=schemas.SupportTicketListResponse)
def get_support_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_admin_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MANAGE_TICKETS))
):
    """Get support tickets"""
    tickets, total = crud.get_support_tickets(db, skip, limit, status, priority, category, assigned_admin_id)
    return schemas.SupportTicketListResponse(
        tickets=tickets,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/support/tickets/{ticket_id}", response_model=schemas.SupportTicketOut)
def get_support_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MANAGE_TICKETS))
):
    """Get support ticket by ID"""
    ticket = crud.get_support_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    
    return ticket


@router.patch("/support/tickets/{ticket_id}", response_model=schemas.SupportTicketOut)
def update_support_ticket(
    ticket_id: int,
    ticket_data: schemas.SupportTicketUpdate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MANAGE_TICKETS))
):
    """Update support ticket"""
    updated_ticket = crud.update_support_ticket(db, ticket_id, ticket_data)
    if not updated_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")
    
    return updated_ticket


@router.post("/support/tickets/{ticket_id}/messages", response_model=schemas.SupportMessageOut)
def add_support_message(
    ticket_id: int,
    message_data: schemas.SupportMessageCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.RESPOND_TO_SUPPORT))
):
    """Add message to support ticket"""
    return crud.add_support_message(db, ticket_id, message_data, None, admin_user.id)


# Content Moderation Routes
@router.post("/moderation", response_model=schemas.ContentModerationOut)
def create_content_moderation(
    moderation_data: schemas.ContentModerationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content moderation entry"""
    return crud.create_content_moderation(db, moderation_data)


@router.get("/moderation", response_model=schemas.ContentModerationListResponse)
def get_content_moderations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    content_type: Optional[str] = None,
    status: Optional[str] = None,
    assigned_admin_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MODERATE_PRODUCTS))
):
    """Get content moderations"""
    moderations, total = crud.get_content_moderations(db, skip, limit, content_type, status, assigned_admin_id)
    return schemas.ContentModerationListResponse(
        items=moderations,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/moderation/{moderation_id}", response_model=schemas.ContentModerationOut)
def update_content_moderation(
    moderation_id: int,
    moderation_data: schemas.ContentModerationUpdate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MODERATE_PRODUCTS))
):
    """Update content moderation"""
    updated_moderation = crud.update_content_moderation(db, moderation_id, moderation_data)
    if not updated_moderation:
        raise HTTPException(status_code=404, detail="Content moderation not found")
    
    return updated_moderation


# Admin Dashboard Routes
@router.post("/dashboards", response_model=schemas.AdminDashboardOut)
def create_admin_dashboard(
    dashboard_data: schemas.AdminDashboardCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Create a new admin dashboard"""
    return crud.create_admin_dashboard(db, dashboard_data, admin_user.id)


@router.get("/dashboards", response_model=List[schemas.AdminDashboardOut])
def get_admin_dashboards(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get admin dashboards"""
    dashboards, total = crud.get_admin_dashboards(db, admin_user.id, skip, limit)
    return dashboards


@router.get("/dashboards/{dashboard_id}", response_model=schemas.AdminDashboardOut)
def get_admin_dashboard(
    dashboard_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get admin dashboard by ID"""
    dashboard = crud.get_admin_dashboard(db, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Check access permissions
    if dashboard.admin_user_id != admin_user.id and not dashboard.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return dashboard


@router.patch("/dashboards/{dashboard_id}", response_model=schemas.AdminDashboardOut)
def update_admin_dashboard(
    dashboard_id: int,
    dashboard_data: schemas.AdminDashboardUpdate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Update admin dashboard"""
    dashboard = crud.get_admin_dashboard(db, dashboard_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    # Check ownership
    if dashboard.admin_user_id != admin_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    updated_dashboard = crud.update_admin_dashboard(db, dashboard_id, dashboard_data)
    return updated_dashboard


# Admin Notification Routes
@router.get("/notifications", response_model=schemas.AdminNotificationListResponse)
def get_admin_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get admin notifications"""
    notifications, total = crud.get_admin_notifications(db, admin_user.id, skip, limit, is_read)
    return schemas.AdminNotificationListResponse(
        notifications=notifications,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.patch("/notifications/{notification_id}/read", response_model=schemas.AdminNotificationOut)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Mark notification as read"""
    notification = crud.mark_notification_read(db, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return notification


# IP Blocklist Routes
@router.post("/security/blocklist", response_model=schemas.IPBlocklistOut)
def add_ip_to_blocklist(
    blocklist_data: schemas.IPBlocklistCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.BLOCK_IPS))
):
    """Add IP to blocklist"""
    return crud.add_ip_to_blocklist(db, blocklist_data, admin_user.id)


@router.get("/security/blocklist", response_model=schemas.IPBlocklistListResponse)
def get_ip_blocklist(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    block_type: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.BLOCK_IPS))
):
    """Get IP blocklist"""
    blocklist, total = crud.get_ip_blocklist(db, skip, limit, block_type)
    return schemas.IPBlocklistListResponse(
        blocklist=blocklist,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.delete("/security/blocklist/{blocklist_id}")
def remove_ip_from_blocklist(
    blocklist_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.BLOCK_IPS))
):
    """Remove IP from blocklist"""
    success = crud.remove_ip_from_blocklist(db, blocklist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Blocklist entry not found")
    
    return {"message": "IP removed from blocklist"}


# Admin Report Routes
@router.post("/reports", response_model=schemas.AdminReportOut)
def create_admin_report(
    report_data: schemas.AdminReportCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_REPORTS))
):
    """Create a new admin report"""
    return crud.create_admin_report(db, report_data, admin_user.id)


@router.get("/reports", response_model=schemas.AdminReportListResponse)
def get_admin_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_REPORTS))
):
    """Get admin reports"""
    reports, total = crud.get_admin_reports(db, admin_user.id, skip, limit, status)
    return schemas.AdminReportListResponse(
        reports=reports,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/reports/{report_id}", response_model=schemas.AdminReportOut)
def get_admin_report(
    report_id: int,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_REPORTS))
):
    """Get admin report by ID"""
    report = db.query(crud.AdminReport).filter(crud.AdminReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check ownership
    if report.generated_by != admin_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report


# Bulk Operations Routes
@router.post("/bulk/users", response_model=Dict[str, Any])
def bulk_user_action(
    bulk_action: schemas.BulkUserAction,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.EDIT_USERS))
):
    """Perform bulk action on users"""
    return crud.bulk_user_action(db, bulk_action, admin_user.id)


@router.post("/bulk/content", response_model=Dict[str, Any])
def bulk_content_action(
    bulk_action: schemas.BulkContentAction,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.MODERATE_PRODUCTS))
):
    """Perform bulk action on content"""
    return crud.bulk_content_action(db, bulk_action, admin_user.id)


# Export Routes
@router.post("/export", response_model=schemas.ExportResponse)
def create_export_request(
    export_request: schemas.ExportRequest,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.EXPORT_DATA))
):
    """Create export request"""
    return crud.create_export_request(db, export_request, admin_user.id)


@router.get("/export/{export_id}", response_model=schemas.ExportResponse)
def get_export_status(
    export_id: str,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.EXPORT_DATA))
):
    """Get export status"""
    export_status = crud.get_export_status(db, export_id)
    if not export_status:
        raise HTTPException(status_code=404, detail="Export not found")
    
    return export_status


# System Metrics Routes
@router.get("/metrics", response_model=List[schemas.SystemMetricsOut])
def get_system_metrics(
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Get system metrics"""
    return crud.get_system_metrics(db, metric_name, category, start_date, end_date, limit)


@router.post("/metrics", response_model=schemas.SystemMetricsOut)
def create_system_metric(
    metric_data: schemas.SystemMetricsCreate,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_ANALYTICS))
):
    """Create a new system metric"""
    return crud.create_system_metric(db, metric_data)


# Permission Management Routes
@router.get("/permissions/check/{permission}", response_model=schemas.PermissionCheck)
def check_permission(
    permission: AdminPermission,
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_USERS))
):
    """Check if current admin has specific permission"""
    has_permission = crud.check_admin_permission(db, admin_user.id, permission)
    return schemas.PermissionCheck(
        permission=permission,
        has_permission=has_permission,
        message="Permission granted" if has_permission else "Permission denied"
    )


# Search Routes
@router.get("/search", response_model=Dict[str, Any])
def admin_search(
    query: str = Query(..., min_length=1),
    search_type: str = Query(..., regex="^(users|products|orders|payments|tickets)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin_user: schemas.AdminUserOut = Depends(require_admin_permission(AdminPermission.VIEW_USERS))
):
    """Search across different entities"""
    # This would integrate with the search system
    # For now, returning placeholder response
    return {
        "query": query,
        "search_type": search_type,
        "results": [],
        "total": 0,
        "page": skip // limit + 1,
        "page_size": limit
    }


