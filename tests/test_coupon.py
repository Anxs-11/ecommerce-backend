"""Tests for coupon functionality."""
import pytest
from fastapi.testclient import TestClient


class TestCoupon:
    """Test suite for coupon operations."""
    
    def test_coupon_generated_after_nth_order(self, client: TestClient):
        """Test coupon is generated after user completes 4 orders (N-1), usable on 5th order."""
        # User completes 3 orders - should not generate coupon
        for i in range(3):
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
        assert len(analytics.json()["discount_codes_generated"]) == 0
        
        # User completes 4th order - should generate coupon (usable on 5th order)
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
        coupons = analytics.json()["discount_codes_generated"]
        assert len(coupons) == 1
        assert coupons[0]["user_id"] == "user1"
    
    def test_multiple_coupons_generated(self, client: TestClient):
        """Test user gets multiple coupons after 4th and 9th orders (usable on 5th and 10th)."""
        # Complete 9 orders for same user - should generate 2 coupons (after 4th and 9th)
        for i in range(9):
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
        coupons = analytics.json()["discount_codes_generated"]
        assert len(coupons) == 2
        # Both coupons should belong to user1
        assert all(c["user_id"] == "user1" for c in coupons)
    
    def test_coupon_codes_are_unique(self, client: TestClient):
        """Test generated coupon codes are unique."""
        # Complete 9 orders for same user to generate 2 coupons (after 4th and 9th)
        for i in range(9):
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
        coupons = analytics.json()["discount_codes_generated"]
        codes = [c["code"] for c in coupons]
        
        assert len(codes) == 2
        assert len(set(codes)) == 2  # All codes are unique
    
    def test_coupon_applies_10_percent_discount(self, client: TestClient):
        """Test coupon applies 10% discount."""
        # Generate coupon for user1 (complete 5 orders)
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
        coupon_owner = analytics.json()["discount_codes_generated"][0]["user_id"]
        assert coupon_owner == "user1"
        
        # Use coupon with $500 order by the owner
        client.post(
            f"/cart/{coupon_owner}/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 500.0,
                "quantity": 1
            }
        )
        response = client.post(
            "/checkout",
            json={"user_id": coupon_owner, "coupon_code": coupon_code}
        )
        
        data = response.json()
        assert data["subtotal"] == 500.0
        assert data["discount_amount"] == 50.0  # 10% of 500
        assert data["total_amount"] == 450.0
    
    def test_manual_coupon_generation_success(self, client: TestClient):
        """Test manual coupon generation by admin."""
        # Admin can generate coupons anytime, no need for 5 orders
        # Just generate a coupon with custom parameters
        response = client.post(
            "/admin/coupons/generate",
            json={
                "user_id": "admin_user",
                "discount_percentage": 15.0,
                "reason": "Customer loyalty reward"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "coupon" in data
        assert data["coupon"]["user_id"] == "admin_user"
        assert data["coupon"]["discount_percentage"] == 15.0
        assert data["coupon"]["status"] == "unused"
        assert data["coupon"]["reason"] == "Customer loyalty reward"
        assert "admin" in data["message"].lower()
    
    def test_manual_coupon_generation_fails_when_missing_fields(self, client: TestClient):
        """Test manual coupon generation fails when required fields are missing."""
        # Try to generate without required fields - should return 422
        response = client.post("/admin/coupons/generate", json={})
        assert response.status_code == 422  # Unprocessable Entity
        
        # Try with only user_id (missing reason)
        response = client.post(
            "/admin/coupons/generate",
            json={"user_id": "test_user", "discount_percentage": 10.0}
        )
        assert response.status_code == 422  # Missing reason field
    
    def test_list_all_coupons(self, client: TestClient):
        """Test listing all coupons."""
        # Generate coupon for user1
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
        
        response = client.get("/admin/coupons")
        
        assert response.status_code == 200
        coupons = response.json()
        assert len(coupons) == 1
        assert coupons[0]["user_id"] == "user1"
        assert coupons[0]["status"] == "unused"
    
    def test_analytics_shows_correct_totals(self, client: TestClient):
        """Test analytics endpoint returns correct totals."""
        # User1 completes 5 orders with varying amounts
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        for price in prices:
            client.post(
                "/cart/user1/items",
                json={
                    "product_id": "prod1",
                    "product_name": "Product",
                    "price": price,
                    "quantity": 1
                }
            )
            client.post(
                "/checkout",
                json={"user_id": "user1"}
            )
        
        # Get generated coupon and use it by the owner
        analytics_before = client.get("/admin/analytics")
        coupon_code = analytics_before.json()["discount_codes_generated"][0]["code"]
        coupon_owner = analytics_before.json()["discount_codes_generated"][0]["user_id"]
        assert coupon_owner == "user1"
        
        client.post(
            f"/cart/{coupon_owner}/items",
            json={
                "product_id": "prod1",
                "product_name": "Product",
                "price": 1000.0,
                "quantity": 2
            }
        )
        client.post(
            "/checkout",
            json={"user_id": coupon_owner, "coupon_code": coupon_code}
        )
        
        # Check analytics
        analytics = client.get("/admin/analytics")
        data = analytics.json()
        
        assert data["total_orders"] == 6
        assert data["total_items_purchased"] == 7  # 5 singles + 2 in last order
        assert data["total_purchase_amount"] == 3500.0  # Sum of all subtotals
        assert data["total_discount_applied"] == 200.0  # 10% of 2000
        assert data["unused_coupons"] == 0
        assert data["used_coupons"] == 1
    
    def test_coupon_not_generated_if_previous_unused(self, client: TestClient):
        """Test new coupon generation continues after Nth orders."""
        # User1 completes 10 orders
        for i in range(10):
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
        data = analytics.json()
        
        # Should have 2 coupons (at 5th and 10th order) for user1
        assert len(data["discount_codes_generated"]) == 2
        assert all(c["user_id"] == "user1" for c in data["discount_codes_generated"])
