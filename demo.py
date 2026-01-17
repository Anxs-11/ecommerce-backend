"""
Demo Script - E-Commerce Backend
==================================
This script demonstrates the complete flow of the e-commerce backend.
Run the FastAPI server first: uvicorn app.main:app --reload
"""

import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_response(response: requests.Response):
    """Print formatted API response."""
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 204:
        print("Success (No Content)")
    else:
        print(f"Error: {response.json()}")
    print()


def demo_cart_operations():
    """Demonstrate cart operations."""
    print_section("1. CART OPERATIONS")
    
    # Add laptop to cart
    print("► Adding Laptop to cart...")
    response = requests.post(
        f"{BASE_URL}/cart/demo_user/items",
        json={
            "product_id": "laptop_001",
            "product_name": "MacBook Pro",
            "price": 1999.99,
            "quantity": 1
        }
    )
    print_response(response)
    
    # Add mouse to cart
    print("► Adding Mouse to cart...")
    response = requests.post(
        f"{BASE_URL}/cart/demo_user/items",
        json={
            "product_id": "mouse_001",
            "product_name": "Magic Mouse",
            "price": 79.99,
            "quantity": 2
        }
    )
    print_response(response)
    
    # View cart
    print("► Viewing cart...")
    response = requests.get(f"{BASE_URL}/cart/demo_user")
    print_response(response)


def demo_checkout_without_coupon():
    """Demonstrate checkout without coupon."""
    print_section("2. CHECKOUT WITHOUT COUPON")
    
    print("► Processing checkout...")
    response = requests.post(
        f"{BASE_URL}/checkout",
        json={"user_id": "demo_user"}
    )
    print_response(response)
    return response.json().get("order_id") if response.status_code == 201 else None


def demo_generate_coupon():
    """Generate coupon by completing 5 orders."""
    print_section("3. GENERATING COUPON (5th ORDER)")
    
    print("► Completing 5 orders to generate coupon...\n")
    
    for i in range(1, 6):
        print(f"Order {i}/5:")
        
        # Add item
        requests.post(
            f"{BASE_URL}/cart/user{i}/items",
            json={
                "product_id": f"prod{i}",
                "product_name": f"Product {i}",
                "price": 100.00 * i,
                "quantity": 1
            }
        )
        
        # Checkout
        response = requests.post(
            f"{BASE_URL}/checkout",
            json={"user_id": f"user{i}"}
        )
        
        if response.status_code == 201:
            print(f"  ✅ Order completed - ${response.json()['total_amount']}")
        
        time.sleep(0.1)
    
    # Check if coupon was generated
    print("\n► Checking for generated coupon...")
    response = requests.get(f"{BASE_URL}/admin/analytics")
    data = response.json()
    
    if data["discount_codes_generated"]:
        coupon = data["discount_codes_generated"][0]
        print(f"\n🎉 Coupon Generated!")
        print(f"   Code: {coupon['code']}")
        print(f"   Discount: {coupon['discount_percentage']}%")
        print(f"   Status: {coupon['status']}")
        return coupon['code']
    
    return None


def demo_checkout_with_coupon(coupon_code: str):
    """Demonstrate checkout with coupon."""
    print_section("4. CHECKOUT WITH COUPON")
    
    # Add items to cart
    print("► Adding items to cart...")
    response = requests.post(
        f"{BASE_URL}/cart/coupon_user/items",
        json={
            "product_id": "premium_laptop",
            "product_name": "Gaming Laptop",
            "price": 2500.00,
            "quantity": 1
        }
    )
    print(f"Cart Total: ${response.json()['total_amount']}\n")
    
    # Checkout with coupon
    print(f"► Applying coupon: {coupon_code}")
    response = requests.post(
        f"{BASE_URL}/checkout",
        json={
            "user_id": "coupon_user",
            "coupon_code": coupon_code
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"\n✅ Order completed with discount!")
        print(f"   Subtotal: ${data['subtotal']}")
        print(f"   Discount: -${data['discount_amount']}")
        print(f"   Total: ${data['total_amount']}")
        print(f"   Saved: ${data['discount_amount']} (10%)")
    else:
        print_response(response)


def demo_coupon_reuse_attempt(coupon_code: str):
    """Demonstrate coupon reuse prevention."""
    print_section("5. COUPON REUSE PREVENTION")
    
    # Add items to cart
    print("► Adding items to cart...")
    requests.post(
        f"{BASE_URL}/cart/another_user/items",
        json={
            "product_id": "tablet",
            "product_name": "iPad Pro",
            "price": 1099.00,
            "quantity": 1
        }
    )
    
    # Try to use same coupon
    print(f"► Attempting to reuse coupon: {coupon_code}")
    response = requests.post(
        f"{BASE_URL}/checkout",
        json={
            "user_id": "another_user",
            "coupon_code": coupon_code
        }
    )
    
    if response.status_code == 400:
        print(f"\n❌ Coupon reuse blocked (as expected)")
        print(f"   Error: {response.json()['detail']}")
    else:
        print_response(response)


def demo_analytics():
    """Demonstrate admin analytics."""
    print_section("6. ADMIN ANALYTICS")
    
    print("► Fetching store analytics...")
    response = requests.get(f"{BASE_URL}/admin/analytics")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Store Statistics:")
        print(f"   Total Orders: {data['total_orders']}")
        print(f"   Total Items Sold: {data['total_items_purchased']}")
        print(f"   Total Revenue: ${data['total_purchase_amount']:.2f}")
        print(f"   Total Discounts: ${data['total_discount_applied']:.2f}")
        print(f"   Coupons Generated: {len(data['discount_codes_generated'])}")
        print(f"   Unused Coupons: {data['unused_coupons']}")
        print(f"   Used Coupons: {data['used_coupons']}")
    else:
        print_response(response)


def demo_empty_cart_checkout():
    """Demonstrate empty cart checkout error."""
    print_section("7. EDGE CASE: EMPTY CART")
    
    print("► Attempting checkout with empty cart...")
    response = requests.post(
        f"{BASE_URL}/checkout",
        json={"user_id": "empty_cart_user"}
    )
    
    if response.status_code == 400:
        print(f"❌ Checkout blocked (as expected)")
        print(f"   Error: {response.json()['detail']}")
    else:
        print_response(response)


def demo_invalid_coupon():
    """Demonstrate invalid coupon error."""
    print_section("8. EDGE CASE: INVALID COUPON")
    
    # Add items
    requests.post(
        f"{BASE_URL}/cart/invalid_coupon_user/items",
        json={
            "product_id": "phone",
            "product_name": "iPhone",
            "price": 999.00,
            "quantity": 1
        }
    )
    
    print("► Attempting checkout with invalid coupon...")
    response = requests.post(
        f"{BASE_URL}/checkout",
        json={
            "user_id": "invalid_coupon_user",
            "coupon_code": "INVALID_CODE_123"
        }
    )
    
    if response.status_code == 400:
        print(f"❌ Invalid coupon rejected (as expected)")
        print(f"   Error: {response.json()['detail']}")
    else:
        print_response(response)


def main():
    """Run the complete demo."""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           E-COMMERCE BACKEND - LIVE DEMONSTRATION           ║
    ║                                                              ║
    ║  This demo showcases all features of the e-commerce API     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Make sure the server is running at http://localhost:8000")
    print("Start server with: uvicorn app.main:app --reload")
    input("\nPress Enter to start the demo...")
    
    try:
        # Test connection
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Cannot connect to server. Please start it first.")
            return
        
        # Run demos
        demo_cart_operations()
        demo_checkout_without_coupon()
        coupon_code = demo_generate_coupon()
        
        if coupon_code:
            demo_checkout_with_coupon(coupon_code)
            demo_coupon_reuse_attempt(coupon_code)
        
        demo_analytics()
        demo_empty_cart_checkout()
        demo_invalid_coupon()
        
        print_section("DEMO COMPLETE")
        print("✅ All features demonstrated successfully!")
        print("\n📚 For more information:")
        print("   - API Docs: http://localhost:8000/docs")
        print("   - README: See README.md file")
        print("   - Tests: Run 'pytest' to see all tests pass")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Please start the server first:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
