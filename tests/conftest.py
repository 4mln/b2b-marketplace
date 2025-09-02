import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import get_session
from app.core.config import settings

# Create test database URL
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/b2b_marketplace", "/test_b2b_marketplace")

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        # Import all models to ensure they are registered with metadata
        from plugins.orders.models import Base as OrdersBase
        from plugins.products.models import Base as ProductsBase
        from plugins.user.models import Base as UserBase
        from plugins.rfq.models import Base as RFQBase
        from plugins.payments.models import Base as PaymentsBase
        
        # Drop tables
        await conn.run_sync(OrdersBase.metadata.drop_all)
        await conn.run_sync(ProductsBase.metadata.drop_all)
        await conn.run_sync(UserBase.metadata.drop_all)
        await conn.run_sync(RFQBase.metadata.drop_all)
        await conn.run_sync(PaymentsBase.metadata.drop_all)
        
        # Create tables
        await conn.run_sync(OrdersBase.metadata.create_all)
        await conn.run_sync(ProductsBase.metadata.create_all)
        await conn.run_sync(UserBase.metadata.create_all)
        await conn.run_sync(RFQBase.metadata.create_all)
        await conn.run_sync(PaymentsBase.metadata.create_all)
    
    yield
    
    # Clean up after tests
    async with test_engine.begin() as conn:
        from plugins.orders.models import Base as OrdersBase
        from plugins.products.models import Base as ProductsBase
        from plugins.user.models import Base as UserBase
        from plugins.rfq.models import Base as RFQBase
        from plugins.payments.models import Base as PaymentsBase
        await conn.run_sync(OrdersBase.metadata.drop_all)
        await conn.run_sync(ProductsBase.metadata.drop_all)
        await conn.run_sync(UserBase.metadata.drop_all)
        await conn.run_sync(RFQBase.metadata.drop_all)
        await conn.run_sync(PaymentsBase.metadata.drop_all)


@pytest.fixture
async def db_session(setup_test_db):
    """Create a fresh database session for a test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency."""
    async def _override_get_db():
        yield db_session
    return _override_get_db


@pytest.fixture
def client(override_get_db):
    """Create a test client with the test database."""
    app.dependency_overrides[get_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    from plugins.user.models import User
    from plugins.user.security import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create authentication headers for test user."""
    from plugins.auth.jwt import create_access_token
    
    access_token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
async def test_user_2(db_session):
    """Create a second test user."""
    from plugins.user.models import User
    from plugins.user.security import get_password_hash
    user = User(
        email="seller@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers_user2(test_user_2):
    from plugins.auth.jwt import create_access_token
    access_token = create_access_token(data={"sub": test_user_2.email})
    return {"Authorization": f"Bearer {access_token}"}