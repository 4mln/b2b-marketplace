# B2B Marketplace Setup Guide

## 🔧 **Critical Fixes Applied**

### 1. **Authentication System Fixed**
- ✅ Created centralized `app/core/auth.py` with consistent authentication functions
- ✅ Fixed multiple conflicting `get_current_user` implementations
- ✅ Added `get_current_user_optional` function
- ✅ Standardized import paths across all plugins

### 2. **Database Session Management Fixed**
- ✅ Created `app/db/session.py` with both async and sync session providers
- ✅ Fixed missing `get_db()` function that plugins were importing
- ✅ Consolidated database Base classes to avoid conflicts

### 3. **Configuration Issues Fixed**
- ✅ Updated `app/core/config.py` with environment-aware settings
- ✅ Fixed database URL inconsistencies
- ✅ Added proper environment variable handling
- ✅ Removed hardcoded secret keys

### 4. **Import Inconsistencies Fixed**
- ✅ Standardized all plugin imports to use centralized auth module
- ✅ Fixed relative import issues in analytics and mobile plugins
- ✅ Created `app/core/deps.py` for common dependencies

## 🚀 **Quick Start**

### 1. **Environment Setup**
Create a `.env` file in the root directory:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=development
DEBUG=true

# Rate Limiting
RATE_LIMIT_WINDOW_SECONDS=60
RATE_LIMIT_MAX_REQUESTS=100

# Plugin Configuration
ENABLE_PLUGIN_HOT_RELOAD=false
```

### 2. **Start Services**
```bash
# Start all services with Docker Compose
docker-compose up -d

# Or start individual services
docker-compose up db redis rabbitmq
```

### 3. **Run Database Migrations**
```bash
# Run all migrations
alembic upgrade head
```

### 4. **Start the Application**
```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Docker
docker-compose up api
```

### 5. **Verify Installation**
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api/docs
```

## 🔍 **What Was Fixed**

### **Before (Issues)**
- ❌ Multiple conflicting `get_current_user` implementations
- ❌ Missing `app/core/auth.py` and `app/db/session.py`
- ❌ Inconsistent import paths across plugins
- ❌ Database URL mismatches
- ❌ Hardcoded secret keys
- ❌ Missing `get_current_user_optional` function

### **After (Fixed)**
- ✅ Single centralized authentication system
- ✅ Consistent import paths: `from app.core.auth import get_current_user_sync`
- ✅ Environment-aware configuration
- ✅ Proper database session management
- ✅ All plugins use standardized dependencies

## 📁 **Key Files Created/Modified**

### **New Files**
- `app/core/auth.py` - Centralized authentication
- `app/db/session.py` - Database session management
- `app/core/deps.py` - Common dependencies

### **Modified Files**
- `app/core/config.py` - Environment-aware configuration
- `plugins/*/routes.py` - Fixed import paths
- `app/main.py` - Added health check endpoint
- `app/db/base.py` - Consolidated Base classes

## 🧪 **Testing**

### **Health Check**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "B2B Marketplace",
  "version": "0.1.0",
  "environment": "development",
  "debug": true
}
```

### **Plugin Loading**
The application will now load all plugins without import errors. Check the startup logs for:
```
[loader] Loaded plugin: auth (0.1.0)
[loader] Loaded plugin: analytics (0.1.0)
[loader] Loaded plugin: mobile (0.1.0)
...
```

## 🔒 **Security Notes**

1. **Change the SECRET_KEY** in production
2. **Update CORS origins** for production domains
3. **Set ENVIRONMENT=production** in production
4. **Use proper SSL certificates** in production

## 🐛 **Troubleshooting**

### **Import Errors**
If you see import errors, ensure:
- All plugins use `from app.core.auth import get_current_user_sync`
- Database sessions use `from app.db.session import get_db`

### **Database Connection Issues**
- Check that PostgreSQL is running on port 5432
- Verify database name is `marketplace`
- Ensure user `postgres` with password `postgres` exists

### **Plugin Loading Issues**
- Check that all plugin `__init__.py` files follow the standard pattern
- Verify plugin dependencies are correctly declared
- Check startup logs for specific error messages

## 📈 **Next Steps**

1. **Run the application** and verify all endpoints work
2. **Test authentication** with the `/auth/token` endpoint
3. **Verify plugin functionality** by testing each plugin's endpoints
4. **Set up monitoring** and logging for production
5. **Configure external services** (Twilio, payment gateways, etc.)
