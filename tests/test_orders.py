import pytest
from httpx import AsyncClient
from fastapi import status
from plugins.orders.schemas import OrderStatus


@pytest.mark.asyncio
async def test_create_order(client, auth_headers, db_session):
    # First create a test seller
    seller_response = await client.post(
        "/sellers/",
        json={"name": "Test Seller", "contact_email": "seller@example.com"},
        headers=auth_headers
    )
    assert seller_response.status_code == status.HTTP_201_CREATED
    seller_id = seller_response.json()["id"]
    
    # Then create a test product
    product_response = await client.post(
        "/products/",
        json={
            "name": "Test Product",
            "description": "A test product",
            "price": 10.99,
            "stock": 100,
            "seller_id": seller_id
        },
        headers=auth_headers
    )
    assert product_response.status_code == status.HTTP_201_CREATED
    product_id = product_response.json()["id"]
    
    # Create an order
    order_data = {
        "seller_id": seller_id,
        "items": [
            {
                "product_id": product_id,
                "quantity": 2,
                "unit_price": 10.99
            }
        ],
        "shipping_address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip": "12345",
            "country": "Test Country"
        },
        "notes": "Test order"
    }
    
    response = await client.post(
        "/orders/",
        json=order_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["seller_id"] == seller_id
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == product_id
    assert data["status"] == OrderStatus.pending.value
    assert data["total_amount"] == 21.98  # 2 * 10.99
    assert "id" in data
    
    # Verify order was created in the database
    order_id = data["id"]
    get_response = await client.get(f"/orders/{order_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json()["id"] == order_id


@pytest.mark.asyncio
async def test_get_order(client, auth_headers, db_session):
    # Create test data (seller, product, order) first
    # ... (similar to test_create_order)
    
    # Then test getting the order
    response = await client.get(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == order_id
    assert data["status"] == OrderStatus.pending.value


@pytest.mark.asyncio
async def test_update_order(client, auth_headers, db_session):
    # Create test data (seller, product, order) first
    # ... (similar to test_create_order)
    
    # Update the order status
    update_data = {
        "status": OrderStatus.processing.value,
        "notes": "Updated order notes"
    }
    
    response = await client.put(
        f"/orders/{order_id}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == OrderStatus.processing.value
    assert data["notes"] == "Updated order notes"


@pytest.mark.asyncio
async def test_delete_order(client, auth_headers, db_session):
    # Create test data (seller, product, order) first
    # ... (similar to test_create_order)
    
    # Delete the order
    response = await client.delete(f"/orders/{order_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Verify order was deleted
    get_response = await client.get(f"/orders/{order_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_list_orders(client, auth_headers, db_session):
    # Create multiple test orders
    # ... (create several orders)
    
    # Test listing all orders
    response = await client.get("/orders/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0  # Should have at least one order
    
    # Test pagination
    response = await client.get("/orders/?skip=0&limit=1", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1  # Should only return one order