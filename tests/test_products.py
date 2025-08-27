import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_product(client, auth_headers, db_session):
    # First create a test seller
    seller_response = await client.post(
        "/sellers/",
        json={"name": "Test Seller", "contact_email": "seller@example.com"},
        headers=auth_headers
    )
    assert seller_response.status_code == status.HTTP_201_CREATED
    seller_id = seller_response.json()["id"]
    
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "A test product description",
        "price": 29.99,
        "stock": 100,
        "seller_id": seller_id,
        "custom_metadata": {"color": "blue", "size": "medium"}
    }
    
    response = await client.post(
        "/products/",
        json=product_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]
    assert data["seller_id"] == seller_id
    assert data["custom_metadata"] == product_data["custom_metadata"]
    assert "id" in data
    
    # Verify product was created in the database
    product_id = data["id"]
    get_response = await client.get(f"/products/{product_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["id"] == product_id


@pytest.mark.asyncio
async def test_get_product(client, auth_headers, db_session):
    # Create test data (seller, product) first
    # ... (similar to test_create_product)
    
    # Then test getting the product
    response = await client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"


@pytest.mark.asyncio
async def test_update_product(client, auth_headers, db_session):
    # Create test data (seller, product) first
    # ... (similar to test_create_product)
    
    # Update the product
    update_data = {
        "name": "Updated Product Name",
        "price": 39.99,
        "stock": 50
    }
    
    response = await client.put(
        f"/products/{product_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]
    assert data["stock"] == update_data["stock"]


@pytest.mark.asyncio
async def test_delete_product(client, auth_headers, db_session):
    # Create test data (seller, product) first
    # ... (similar to test_create_product)
    
    # Delete the product
    response = await client.delete(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify product was deleted
    get_response = await client.get(f"/products/{product_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_products(client, auth_headers, db_session):
    # Create multiple test products
    # ... (create several products)
    
    # Test listing all products
    response = await client.get("/products/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Should have at least one product
    
    # Test filtering by seller
    response = await client.get(f"/products/?seller_id={seller_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(product["seller_id"] == seller_id for product in data)
    
    # Test pagination
    response = await client.get("/products/?skip=0&limit=1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1  # Should only return one product