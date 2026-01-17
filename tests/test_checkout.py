"""Tests for checkout functionality."""
import pytest
from fastapi.testclient import TestClient


class TestCheckout:
    """Test suite for checkout operations."""
    
    def test_checkout_success(self, client: TestClient):
        """Test successful checkout."""
        # Add items to cart
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Checkout
        response = client.post(
            "/checkout",
            json={
                "user_id": "user1"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["subtotal"] == 999.99
        assert data["discount_amount"] == 0.0
        assert data["total_amount"] == 999.99
        assert data["total_items"] == 1
        assert "order_id" in data
        
        # Verify cart is cleared
        cart_response = client.get("/cart/user1")
        cart_data = cart_response.json()
        assert cart_data["total_items"] == 0
    
    def test_checkout_empty_cart(self, client: TestClient):
        """Test checkout with empty cart fails."""
        response = client.post(
            "/checkout",
            json={
                "user_id": "user1"
            }
        )
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_checkout_with_valid_coupon(self, client: TestClient):
        """Test checkout with valid coupon by the coupon owner."""
        # User1 completes 5 orders to generate a coupon
        for i in range(5):
            client.post(
                "/cart/user1/items",
                json={
                    "product_id": "prod1",
                    "product_name": "Product",
                    "price": 100.0,
                    "quantity": 1
                }
            )
            client.post(
                "/checkout",
                json={"user_id": "user1"}
            )
        
        # Get generated coupon (should be for user1)
        analytics = client.get("/admin/analytics")
        coupons = analytics.json()["discount_codes_generated"]
        assert len(coupons) == 1
        coupon_code = coupons[0]["code"]
        coupon_user = coupons[0]["user_id"]
        assert coupon_user == "user1"
        
        # Add items to cart for the coupon owner
        client.post(
            f"/cart/{coupon_user}/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 1000.0,
                "quantity": 1
            }
        )
        
        # Checkout with coupon as the owner
        response = client.post(
            "/checkout",
            json={
                "user_id": coupon_user,
                "coupon_code": coupon_code
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["subtotal"] == 1000.0
        assert data["discount_amount"] == 100.0  # 10% of 1000
        assert data["total_amount"] == 900.0
        assert data["coupon_code"] == coupon_code
    
    def test_checkout_with_invalid_coupon(self, client: TestClient):
        """Test checkout with invalid coupon fails."""
        # Add items to cart
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        
        # Checkout with invalid coupon
        response = client.post(
            "/checkout",
            json={
                "user_id": "user1",
                "coupon_code": "INVALID"
            }
        )
        
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]
    
    def test_checkout_with_used_coupon(self, client: TestClient):
        """Test checkout with already used coupon fails."""
        # User1 completes 5 orders to generate a coupon
        for i in range(5):
            client.post(
                "/cart/user1/items",
                json={
                    "product_id": "prod1",
                    "product_name": "Product",
                    "price": 100.0,
                    "quantity": 1
                }
            )
            client.post(
                "/checkout",
                json={"user_id": "user1"}
            )
        
        # Get generated coupon
        analytics = client.get("/admin/analytics")
        coupon_code = analytics.json()["discount_codes_generated"][0]["code"]
        coupon_user = analytics.json()["discount_codes_generated"][0]["user_id"]
        assert coupon_user == "user1"
        
        # Use coupon in first checkout by the owner
        client.post(
            f"/cart/{coupon_user}/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 100.0,
                "quantity": 1
            }
        )
        client.post(
            "/checkout",
            json={"user_id": coupon_user, "coupon_code": coupon_code}
        )
        
        # Try to use same coupon again by the same user
        client.post(
            f"/cart/{coupon_user}/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 100.0,
                "quantity": 1
            }
        )
        response = client.post(
            "/checkout",
            json={"user_id": coupon_user, "coupon_code": coupon_code}
        )
        
        assert response.status_code == 400
        assert "already been used" in response.json()["detail"]
    
    def test_checkout_with_coupon_belonging_to_another_user(self, client: TestClient):
        """Test that a user cannot use another user's coupon."""
        # User1 completes 5 orders to generate a coupon
        for i in range(5):
            client.post(
                "/cart/user1/items",
                json={
                    "product_id": "prod1",
                    "product_name": "Product",
                    "price": 100.0,
                    "quantity": 1
                }
            )
            client.post(
                "/checkout",
                json={"user_id": "user1"}
            )
        
        # Get generated coupon (belongs to user1)
        analytics = client.get("/admin/analytics")
        coupon_code = analytics.json()["discount_codes_generated"][0]["code"]
        coupon_owner = analytics.json()["discount_codes_generated"][0]["user_id"]
        assert coupon_owner == "user1"
        
        # Try to use the coupon with a different user
        different_user = "user999"
        assert different_user != coupon_owner
        
        client.post(
            f"/cart/{different_user}/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 100.0,
                "quantity": 1
            }
        )
        response = client.post(
            "/checkout",
            json={"user_id": different_user, "coupon_code": coupon_code}
        )
        
        assert response.status_code == 400
        assert "belongs to another user" in response.json()["detail"]
    
    def test_get_order(self, client: TestClient):
        """Test getting order by ID."""
        # Create order
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        checkout_response = client.post(
            "/checkout",
            json={"user_id": "user1"}
        )
        order_id = checkout_response.json()["order_id"]
        
        # Get order
        response = client.get(f"/checkout/{order_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["total_amount"] == 999.99
    
    def test_get_nonexistent_order(self, client: TestClient):
        """Test getting nonexistent order fails."""
        response = client.get("/checkout/nonexistent-order-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
