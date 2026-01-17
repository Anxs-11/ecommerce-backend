"""Checkout API endpoints."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.services.checkout_service import checkout_service

router = APIRouter(prefix="/checkout", tags=["Checkout"])


class CheckoutRequest(BaseModel):
    """Request model for checkout."""
    
    user_id: str = Field(..., description="User identifier")
    coupon_code: Optional[str] = Field(None, description="Optional coupon code")


class OrderItemResponse(BaseModel):
    """Order item in response."""
    
    product_id: str
    product_name: str
    price: float
    quantity: int
    total_price: float


class CheckoutResponse(BaseModel):
    """Response model for checkout."""
    
    order_id: str
    user_id: str
    items: List[OrderItemResponse]
    total_items: int
    subtotal: float
    discount_amount: float
    total_amount: float
    coupon_code: Optional[str]
    created_at: datetime


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CheckoutResponse)
def checkout(request: CheckoutRequest):
    """
    Process checkout and create order.
    
    - **user_id**: User identifier
    - **coupon_code**: Optional discount coupon code
    
    Returns created order with applied discounts.
    """
    order, error = checkout_service.checkout(request.user_id, request.coupon_code)
    
    if error:
        if "empty" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        else:
            # Coupon validation errors
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
    
    return CheckoutResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                total_price=item.total_price
            )
            for item in order.items
        ],
        total_items=order.total_items,
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        coupon_code=order.coupon_code,
        created_at=order.created_at
    )


@router.get("/{order_id}", response_model=CheckoutResponse)
def get_order(order_id: str):
    """
    Get order details by order ID.
    
    - **order_id**: Order identifier
    """
    order = checkout_service.get_order(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return CheckoutResponse(
        order_id=order.order_id,
        user_id=order.user_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity,
                total_price=item.total_price
            )
            for item in order.items
        ],
        total_items=order.total_items,
        subtotal=order.subtotal,
        discount_amount=order.discount_amount,
        total_amount=order.total_amount,
        coupon_code=order.coupon_code,
        created_at=order.created_at
    )
