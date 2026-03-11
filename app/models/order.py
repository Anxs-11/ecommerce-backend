"""Order models."""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enumeration."""
    
    ACTIVE = "active"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    """Individual order item."""
    
    product_id: str
    product_name: str
    price: float
    quantity: int
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this order item."""
        return round(self.price * self.quantity, 2)


class Order(BaseModel):
    """Customer order."""
    
    order_id: str
    user_id: str
    items: List[OrderItem]
    subtotal: float
    discount_amount: float = 0.0
    total_amount: float
    coupon_code: Optional[str] = None
    status: OrderStatus = Field(default=OrderStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    
    @property
    def total_items(self) -> int:
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    def cancel(self) -> None:
        """Cancel the order."""
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """Check if order is active."""
        return self.status == OrderStatus.ACTIVE
