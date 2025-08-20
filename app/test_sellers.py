import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000/sellers/"
USER_ID = 999  # Make sure this user exists

async def main():
    async with httpx.AsyncClient() as client:
        # -----------------------------
        # Create Seller
        # -----------------------------
        seller_data = {"name": "Async Test Seller", "description": "Created via test script"}
        response = await client.post(f"{BASE_URL}?user_id={USER_ID}", json=seller_data)
        print("Create Seller:", response.status_code, response.json())
        if response.status_code != 200:
            print("Create failed, aborting test.")
            return
        seller = response.json()
        seller_id = seller["id"]

        # -----------------------------
        # Get Seller by ID
        # -----------------------------
        response = await client.get(f"{BASE_URL}{seller_id}")
        print("Get Seller:", response.status_code, response.json())

        # -----------------------------
        # Update Seller
        # -----------------------------
        update_data = {"description": "Updated via test script"}
        response = await client.put(f"{BASE_URL}{seller_id}?user_id={USER_ID}", json=update_data)
        print("Update Seller:", response.status_code, response.json())

        # -----------------------------
        # List all sellers
        # -----------------------------
        response = await client.get(BASE_URL)
        print("List Sellers:", response.status_code, response.json())

        # -----------------------------
        # Search sellers
        # -----------------------------
        response = await client.get(f"{BASE_URL}search/?q=Async")
        print("Search Sellers:", response.status_code, response.json())

        # -----------------------------
        # Top-rated sellers
        # -----------------------------
        response = await client.get(f"{BASE_URL}top/")
        print("Top Sellers:", response.status_code, response.json())

        # -----------------------------
        # Filter by subscription (example)
        # -----------------------------
        response = await client.get(f"{BASE_URL}subscription/free")
        print("Subscription Filter:", response.status_code, response.json())

        # -----------------------------
        # Activate / Deactivate seller
        # -----------------------------
        response = await client.patch(f"{BASE_URL}{seller_id}/activate?user_id={USER_ID}&is_active=false")
        print("Deactivate Seller:", response.status_code, response.json())

        response = await client.patch(f"{BASE_URL}{seller_id}/activate?user_id={USER_ID}&is_active=true")
        print("Activate Seller:", response.status_code, response.json())

        # -----------------------------
        # Delete Seller
        # -----------------------------
        response = await client.delete(f"{BASE_URL}{seller_id}?user_id={USER_ID}")
        print("Delete Seller:", response.status_code, response.json())


if __name__ == "__main__":
    asyncio.run(main())
