"""Checkout API endpoints."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.services.checkout_service import checkout_service
from app.models.order import OrderStatus

router = APIRouter(prefix="/checkout", tags=["Checkout"])


class CheckoutRequest(BaseModel):
    """Request model for checkout."""
    
    user_id: str = Field(..., description="User identifier")
    coupon_code: Optional[str] = Field(None, description="Optional coupon code")


class CancelOrderRequest(BaseModel):
    """Request model for order cancellation."""
    
    user_id: str = Field(..., description="User identifier requesting cancellation")


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
    status: OrderStatus
    created_at: datetime
    cancelled_at: Optional[datetime] = None


class CancelOrderResponse(BaseModel):
    """Response model for order cancellation."""
    
    order_id: str
    status: OrderStatus
    message: str
    coupon_re_credited: bool
    coupon_code: Optional[str] = None


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
        status=order.status,
        created_at=order.created_at,
        cancelled_at=order.cancelled_at
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
        status=order.status,
        created_at=order.created_at,
        cancelled_at=order.cancelled_at
    )


@router.post("/{order_id}/cancel", response_model=CancelOrderResponse)
def cancel_order(order_id: str, request: CancelOrderRequest):
    """
    Cancel an order and re-credit coupon if applicable.
    
    - **order_id**: Order identifier to cancel
    - **user_id**: User identifier requesting cancellation (must be order owner)
    
    Returns cancellation confirmation with coupon re-credit status.
    """
    result, error = checkout_service.cancel_order(order_id, request.user_id)
    
    if error:
        if "not found" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )
        elif "does not belong" in error.lower() or "cannot cancel" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=error
            )
        elif "already cancelled" in error.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
    
    return CancelOrderResponse(
        order_id=result["order_id"],
        status=result["status"],
        message=result["message"],
        coupon_re_credited=result["coupon_re_credited"],
        coupon_code=result.get("coupon_code")
    )
