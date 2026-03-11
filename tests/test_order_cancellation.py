"""Tests for order cancellation functionality."""
import pytest
from fastapi.testclient import TestClient


class TestOrderCancellation:
    """Test suite for order cancellation operations."""
    
    def test_cancel_order_success(self, client: TestClient):
        """Test successful order cancellation."""
        # Create an order
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
        
        # Cancel the order
        response = client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["status"] == "cancelled"
        assert "cancelled successfully" in data["message"].lower()
        assert data["coupon_re_credited"] is False
        
        # Verify order status is updated
        order_response = client.get(f"/checkout/{order_id}")
        assert order_response.json()["status"] == "cancelled"
    
    def test_cancel_order_with_coupon_re_credit(self, client: TestClient):
        """Test order cancellation re-credits the coupon."""
        # Generate a coupon for user1
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
        
        # Get the generated coupon
        analytics = client.get("/admin/analytics")
        coupon_code = analytics.json()["discount_codes_generated"][0]["code"]
        
        # Create an order with the coupon
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 1000.0,
                "quantity": 1
            }
        )
        checkout_response = client.post(
            "/checkout",
            json={"user_id": "user1", "coupon_code": coupon_code}
        )
        order_id = checkout_response.json()["order_id"]
        
        # Verify coupon is used
        analytics_before = client.get("/admin/analytics")
        assert analytics_before.json()["used_coupons"] == 1
        assert analytics_before.json()["unused_coupons"] == 0
        
        # Cancel the order
        response = client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["coupon_re_credited"] is True
        assert data["coupon_code"] == coupon_code
        assert coupon_code in data["message"]
        
        # Verify coupon is now unused again
        analytics_after = client.get("/admin/analytics")
        assert analytics_after.json()["used_coupons"] == 0
        assert analytics_after.json()["unused_coupons"] == 1
        
        # Verify we can use the coupon again
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 500.0,
                "quantity": 1
            }
        )
        reuse_response = client.post(
            "/checkout",
            json={"user_id": "user1", "coupon_code": coupon_code}
        )
        assert reuse_response.status_code == 201
        assert reuse_response.json()["discount_amount"] == 50.0
    
    def test_cancel_order_not_owned_by_user(self, client: TestClient):
        """Test cancelling someone else's order is rejected."""
        # User1 creates an order
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
        
        # User2 tries to cancel user1's order
        response = client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user2"}
        )
        
        assert response.status_code == 403
        assert "does not belong to you" in response.json()["detail"].lower()
        
        # Verify order is still active
        order_response = client.get(f"/checkout/{order_id}")
        assert order_response.json()["status"] == "active"
    
    def test_cancel_already_cancelled_order(self, client: TestClient):
        """Test cancelling an already cancelled order fails."""
        # Create and cancel an order
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
        
        # First cancellation
        client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user1"}
        )
        
        # Try to cancel again
        response = client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user1"}
        )
        
        assert response.status_code == 400
        assert "already been cancelled" in response.json()["detail"].lower()
    
    def test_cancel_nonexistent_order(self, client: TestClient):
        """Test cancelling a nonexistent order fails."""
        response = client.post(
            "/checkout/nonexistent-order-id/cancel",
            json={"user_id": "user1"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_new_orders_default_to_active(self, client: TestClient):
        """Test new orders have active status by default."""
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Laptop",
                "price": 999.99,
                "quantity": 1
            }
        )
        response = client.post(
            "/checkout",
            json={"user_id": "user1"}
        )
        
        assert response.status_code == 201
        assert response.json()["status"] == "active"
    
    def test_discount_amount_adjusted_on_cancellation(self, client: TestClient):
        """Test total discount applied is adjusted when order with coupon is cancelled."""
        # Generate a coupon
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
        
        analytics = client.get("/admin/analytics")
        coupon_code = analytics.json()["discount_codes_generated"][0]["code"]
        
        # Create order with coupon
        client.post(
            "/cart/user1/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 1000.0,
                "quantity": 1
            }
        )
        checkout_response = client.post(
            "/checkout",
            json={"user_id": "user1", "coupon_code": coupon_code}
        )
        order_id = checkout_response.json()["order_id"]
        
        # Check discount applied
        analytics_before = client.get("/admin/analytics")
        assert analytics_before.json()["total_discount_applied"] == 100.0
        
        # Cancel order
        client.post(
            f"/checkout/{order_id}/cancel",
            json={"user_id": "user1"}
        )
        
        # Verify discount is removed
        analytics_after = client.get("/admin/analytics")
        assert analytics_after.json()["total_discount_applied"] == 0.0
