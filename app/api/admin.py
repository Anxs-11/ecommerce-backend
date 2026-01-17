"""Admin API endpoints."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.services.coupon_service import coupon_service
from app.services.checkout_service import checkout_service
from app.services.in_memory_store import data_store

router = APIRouter(prefix="/admin", tags=["Admin"])


class CouponResponse(BaseModel):
    """Response model for coupon."""
    
    code: str
    user_id: str
    discount_percentage: float
    status: str
    created_at: datetime
    used_at: datetime | None
    order_id: str | None
    reason: str | None


class GenerateCouponResponse(BaseModel):
    """Response for manual coupon generation."""
    
    coupon: CouponResponse
    message: str


class AnalyticsResponse(BaseModel):
    """Response model for analytics."""
    
    total_orders: int
    total_items_purchased: int
    total_purchase_amount: float
    total_discount_applied: float
    discount_codes_generated: List[CouponResponse]
    unused_coupons: int
    used_coupons: int


class GenerateCouponRequest(BaseModel):
    """Request model for manual coupon generation."""
    
    user_id: str = Field(..., description="User ID to assign the coupon to")
    discount_percentage: float = Field(10.0, ge=0, le=100, description="Discount percentage (0-100)")
    reason: str = Field(..., description="Reason for generating this coupon")


@router.post("/coupons/generate", status_code=status.HTTP_201_CREATED, response_model=GenerateCouponResponse)
def generate_coupon(request: GenerateCouponRequest):
    """
    Manually generate a discount coupon for a specific user.
    
    Admin can generate coupons at any time without Nth order restriction.
    """
    coupon = coupon_service.create_coupon(
        user_id=request.user_id,
        discount_percentage=request.discount_percentage,
        reason=request.reason
    )
    
    return GenerateCouponResponse(
        coupon=CouponResponse(
            code=coupon.code,
            user_id=coupon.user_id,
            discount_percentage=coupon.discount_percentage,
            status=coupon.status.value,
            created_at=coupon.created_at,
            used_at=coupon.used_at,
            order_id=coupon.order_id,
            reason=coupon.reason
        ),
        message="Coupon generated successfully by admin"
    )


@router.get("/analytics", response_model=AnalyticsResponse)
def get_analytics():
    """
    Get store analytics.
    
    Returns:
    - Total number of orders
    - Total items purchased across all orders
    - Total purchase amount (before discounts)
    - Total discount amount applied
    - List of all generated discount codes
    - Count of unused and used coupons
    """
    orders = checkout_service.get_all_orders()
    coupons = coupon_service.get_all_coupons()
    
    total_items = sum(order.total_items for order in orders)
    total_purchase_amount = sum(order.subtotal for order in orders)
    
    coupon_responses = [
        CouponResponse(
            code=coupon.code,
            user_id=coupon.user_id,
            discount_percentage=coupon.discount_percentage,
            status=coupon.status.value,
            created_at=coupon.created_at,
            used_at=coupon.used_at,
            order_id=coupon.order_id,
            reason=coupon.reason
        )
        for coupon in coupons
    ]
    
    unused_coupons = len(coupon_service.get_unused_coupons())
    used_coupons = len(coupon_service.get_used_coupons())
    
    return AnalyticsResponse(
        total_orders=len(orders),
        total_items_purchased=total_items,
        total_purchase_amount=round(total_purchase_amount, 2),
        total_discount_applied=round(data_store.total_discount_applied, 2),
        discount_codes_generated=coupon_responses,
        unused_coupons=unused_coupons,
        used_coupons=used_coupons
    )


@router.get("/coupons", response_model=List[CouponResponse])
def list_coupons():
    """
    List all coupons.
    
    Returns all generated discount coupons with their status.
    """
    coupons = coupon_service.get_all_coupons()
    
    return [
        CouponResponse(
            code=coupon.code,
            user_id=coupon.user_id,
            discount_percentage=coupon.discount_percentage,
            status=coupon.status.value,
            created_at=coupon.created_at,
            used_at=coupon.used_at,
            order_id=coupon.order_id,
            reason=coupon.reason
        )
        for coupon in coupons
    ]
