"""Cart models."""
from typing import Dict, List
from pydantic import BaseModel, Field, field_validator


class AddToCartRequest(BaseModel):
    """Request model for adding item to cart."""
    
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    price: float = Field(..., gt=0, description="Product price, must be positive")
    quantity: int = Field(..., gt=0, description="Quantity to add, must be positive")
    
    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        """Ensure price has at most 2 decimal places."""
        return round(v, 2)


class CartItem(BaseModel):
    """Individual cart item."""
    
    product_id: str
    product_name: str
    price: float
    quantity: int
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this cart item."""
        return round(self.price * self.quantity, 2)


class Cart(BaseModel):
    """Shopping cart for a user."""
    
    user_id: str
    items: List[CartItem] = Field(default_factory=list)
    
    @property
    def total_items(self) -> int:
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_amount(self) -> float:
        """Calculate total cart amount."""
        return round(sum(item.total_price for item in self.items), 2)
    
    def add_item(self, item: AddToCartRequest) -> None:
        """Add item to cart or update quantity if exists."""
        for cart_item in self.items:
            if cart_item.product_id == item.product_id:
                cart_item.quantity += item.quantity
                return
        
        # If item doesn't exist, add new one
        self.items.append(CartItem(
            product_id=item.product_id,
            product_name=item.product_name,
            price=item.price,
            quantity=item.quantity
        ))
    
    def clear(self) -> None:
        """Clear all items from cart."""
        self.items.clear()
