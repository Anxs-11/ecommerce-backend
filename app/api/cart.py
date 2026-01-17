"""Cart API endpoints."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from app.models import AddToCartRequest, Cart
from app.services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])


class CartResponse(BaseModel):
    """Response model for cart operations."""
    
    user_id: str
    items: List[dict]
    total_items: int
    total_amount: float


@router.post("/{user_id}/items", status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_to_cart(user_id: str, item: AddToCartRequest):
    """
    Add item to cart.
    
    - **user_id**: User identifier
    - **item**: Item details including product_id, product_name, price, quantity
    """
    cart = cart_service.add_to_cart(user_id, item)
    
    return CartResponse(
        user_id=cart.user_id,
        items=[item.model_dump() for item in cart.items],
        total_items=cart.total_items,
        total_amount=cart.total_amount
    )


@router.get("/{user_id}", response_model=CartResponse)
def get_cart(user_id: str):
    """
    Get user's cart.
    
    - **user_id**: User identifier
    """
    cart = cart_service.get_cart(user_id)
    
    if not cart:
        # Return empty cart if doesn't exist
        return CartResponse(
            user_id=user_id,
            items=[],
            total_items=0,
            total_amount=0.0
        )
    
    return CartResponse(
        user_id=cart.user_id,
        items=[item.model_dump() for item in cart.items],
        total_items=cart.total_items,
        total_amount=cart.total_amount
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(user_id: str):
    """
    Clear user's cart.
    
    - **user_id**: User identifier
    """
    cart_service.clear_cart(user_id)
    return None
