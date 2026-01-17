# E-Commerce Backend API

## Overview

FastAPI-based backend system for e-commerce platform featuring shopping cart management, order checkout, and an intelligent coupon system that automatically generates discount codes every Nth successful order. Built with clean architecture, comprehensive test coverage, and production-ready patterns.

**Tech Stack**: Python 3.10+, FastAPI, Pydantic, Pytest, Uvicorn

---

## Features

### Core Functionality
- **Shopping Cart**: Add items, view cart contents, clear cart
- **Order Checkout**: Process orders with automatic cart clearing
- **Order History**: Retrieve order details by order ID

### Coupon System
- **Automatic Generation**: Coupons auto-generated every Nth order (configurable, default N=5)
- **User-Specific**: Each coupon is tied to a specific user and cannot be shared
- **One-Time Use**: Coupons become invalid after redemption
- **Discount**: 10% discount on order subtotal (default)

### Admin Features
- **Custom Coupon Generation**: Create coupons for any user with custom discount percentage and reason (no Nth-order restriction)
- **Analytics Dashboard**: View total orders, revenue, discounts, and coupon statistics
- **Coupon Management**: List all coupons with their status (used/unused)

### Technical Features
- RESTful API design with proper HTTP status codes
- Input validation using Pydantic models
- Auto-generated API documentation (Swagger/OpenAPI)
- In-memory data storage (easily replaceable with database)
- Comprehensive error handling
- Full test coverage (26 tests)

---

## How to Run

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Setup

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Start the Server**
```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

**3. Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Project Structure
```
app/
├── api/              # API endpoints
│   ├── cart.py
│   ├── checkout.py
│   └── admin.py
├── models/           # Pydantic models
│   ├── cart.py
│   ├── order.py
│   └── coupon.py
├── services/         # Business logic
│   ├── in_memory_store.py
│   ├── cart_service.py
│   ├── checkout_service.py
│   └── coupon_service.py
└── main.py           # FastAPI application

tests/                # Test suite (26 tests)
├── test_cart.py
├── test_checkout.py
└── test_coupon.py
```

### Configuration

To change the Nth-order value, modify `app/services/coupon_service.py`:
```python
# Default: every 5th order
coupon_service = CouponService(nth_order=5)
```

---

## Demo

The project includes a demo script that demonstrates the complete API flow.

**Prerequisites**: Start the API server first

### Running the Demo

**Terminal 1 - Start Server**:
```bash
uvicorn app.main:app --reload
```

**Terminal 2 - Run Demo**:
```bash
# Run demo
python demo.py
```

**What the demo shows**:
- Adding items to cart
- Viewing cart contents
- Completing multiple checkouts
- Automatic coupon generation after Nth order
- Using coupons for discounts
- Admin analytics viewing

---

## Testing

Comprehensive test suite with 26 tests covering all functionality.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_coupon.py

# Run specific test
pytest tests/test_coupon.py::TestCoupon::test_coupon_generated_after_nth_order
```

### Test Coverage

**Cart Tests (8 tests)**:
- Adding items (single, multiple, duplicate handling)
- Viewing cart
- Clearing cart
- Input validation (negative prices, invalid quantities)

**Checkout Tests (6 tests)**:
- Successful checkout
- Empty cart error handling
- Valid coupon application
- Invalid coupon rejection
- Used coupon rejection
- Cross-user coupon usage prevention

**Coupon Tests (12 tests)**:
- Nth order generation logic
- Per-user order tracking independence
- Multiple coupon generation
- Unique code generation
- Discount calculation accuracy
- Manual admin generation
- Coupon listing
- Analytics accuracy

All tests pass successfully with comprehensive edge case coverage.

---

## API Endpoints

### Cart Operations
- `POST /cart/{user_id}/items` - Add item to cart
- `GET /cart/{user_id}` - View cart contents
- `DELETE /cart/{user_id}` - Clear cart

### Checkout Operations
- `POST /checkout` - Process order (optional `coupon_code` in body)
- `GET /checkout/{order_id}` - Get order details

### Admin Operations
- `POST /admin/coupons/generate` - Generate custom coupon
  - **Body**: `{"user_id": "string", "discount_percentage": 0-100, "reason": "string"}`
- `GET /admin/analytics` - Get store analytics
- `GET /admin/coupons` - List all coupons

**Interactive API Documentation**: http://localhost:8000/docs (Swagger UI)

---

## Business Logic

### Coupon Generation Logic

**Automatic Generation (Every Nth Order)**:
1. System tracks successful orders **per user individually**
2. Coupon is generated after (N-1) orders so it can be used ON the Nth order
3. Default N = 5, meaning coupon generated after 4th order, usable on 5th order
4. Each user earns their own coupons independently
5. Default discount: 10%
6. Example with N=5: 
   - **User A**: Complete orders 1, 2, 3 → No coupon yet
   - **User A**: Complete **4th order** → Coupon generated for User A ✅
   - **User A**: Can use coupon ON **5th order (the Nth order)** or any later order
   - **User B**: Must complete their own 4 orders to get their coupon (independent tracking)
   - **User A**: Complete **9th order** → Another coupon for User A ✅
   - **User A**: Can use this coupon on **10th order** or later

**Admin Manual Generation**:
1. Admin can generate coupons anytime without order count restriction
2. Admin specifies: user_id, discount_percentage (0-100%), and reason
3. Reason is mandatory for audit trail

### Coupon Validation Rules
- Coupon must exist in the system
- Coupon must not have been used previously
- Coupon can only be used by the user it was assigned to
- Cross-user coupon usage is prevented (security feature)

### Checkout Flow
1. Verify cart is not empty
2. If coupon provided, validate coupon (exists, unused, belongs to user)
3. Calculate subtotal from cart items
4. Apply discount if coupon is valid
5. Create order with all details
6. Mark coupon as used
7. Clear user's cart
8. Return order confirmation

---

## What's Covered

### Functional Requirements ✅
- [x] Shopping cart with add/view/clear operations
- [x] Checkout with automatic cart clearing
- [x] Automatic coupon generation every Nth order
- [x] User-specific coupons (no sharing)
- [x] Coupon validation and usage
- [x] Admin manual coupon generation
- [x] Admin analytics dashboard

### Technical Implementation ✅
- [x] Clean architecture (API → Service → Model layers)
- [x] RESTful API design
- [x] Type-safe with Pydantic validation
- [x] Comprehensive error handling
- [x] Full test coverage
- [x] Auto-generated documentation
- [x] Configurable Nth-order value
- [x] In-memory data store

### Edge Cases Handled ✅
- [x] Empty cart checkout prevention
- [x] Invalid coupon rejection
- [x] Used coupon rejection
- [x] Cross-user coupon usage prevention
- [x] Concurrent operations support
- [x] Duplicate product quantity updates

---

## Future Improvements

If extending this to production, consider:

1. **Database Integration**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Authentication & Authorization**: Add JWT-based user authentication and role-based access control
3. **Payment Gateway**: Integrate Stripe/PayPal for actual payments
4. **Email Notifications**: Send order confirmations and coupon notifications
5. **Rate Limiting**: Prevent API abuse with request throttling
6. **Caching**: Implement Redis for cart data and session management
7. **Logging & Monitoring**: Add structured logging and metrics (Prometheus/Grafana)
8. **Docker**: Containerize application for easy deployment
9. **CI/CD Pipeline**: Automated testing and deployment
10. **Advanced Coupon Features**: 
    - Expiration dates
    - Minimum order value requirements
    - Product-specific discounts
    - Bulk coupon generation

---

**Status**: Ready for review and testing
