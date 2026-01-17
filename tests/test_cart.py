"""Tests for cart functionality."""
import pytest
from fastapi.testclient import TestClient


class TestCart:
    """Test suite for cart operations."""
    
    def test_add_to_cart(self, client: TestClient):
        """Test adding item to cart."""
        response = client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["total_items"] == 1
        assert data["total_amount"] == 999.99
        assert len(data["items"]) == 1
    
    def test_add_multiple_items_to_cart(self, client: TestClient):
        """Test adding multiple items to cart."""
        # Add first item
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Add second item
        response = client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod2",
                "product_name": "Mouse",
                "price": 25.50,
                "quantity": 2
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["total_items"] == 3
        assert data["total_amount"] == 1050.99
        assert len(data["items"]) == 2
    
    def test_add_same_item_updates_quantity(self, client: TestClient):
        """Test adding same item twice updates quantity."""
        # Add item first time
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Add same item again
        response = client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 2
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["total_items"] == 3
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 3
    
    def test_get_cart(self, client: TestClient):
        """Test getting cart."""
        # Add item to cart
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Get cart
        response = client.get("/cart/user1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["total_items"] == 1
    
    def test_get_empty_cart(self, client: TestClient):
        """Test getting cart that doesn't exist returns empty cart."""
        response = client.get("/cart/user999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user999"
        assert data["total_items"] == 0
        assert data["total_amount"] == 0.0
        assert len(data["items"]) == 0
    
    def test_clear_cart(self, client: TestClient):
        """Test clearing cart."""
        # Add item to cart
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Clear cart
        response = client.delete("/cart/user1")
        assert response.status_code == 204
        
        # Verify cart is empty
        response = client.get("/cart/user1")
        data = response.json()
        assert data["total_items"] == 0
    
    def test_add_item_with_invalid_price(self, client: TestClient):
        """Test adding item with invalid price fails."""
        response = client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": -100,
                "quantity": 1
            }
        )
        
        assert response.status_code == 422
    
    def test_add_item_with_invalid_quantity(self, client: TestClient):
        """Test adding item with invalid quantity fails."""
        response = client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 0
            }
        )
        
        assert response.status_code == 422
