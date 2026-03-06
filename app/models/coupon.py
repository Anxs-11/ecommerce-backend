"""Coupon models."""
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CouponStatus(str, Enum):
    """Coupon status enumeration."""
    
    UNUSED = "unused"
    USED = "used"


class Coupon(BaseModel):
    """Discount coupon."""
    
    code: str = Field(..., description="Unique coupon code")
    user_id: str = Field(..., description="User ID this coupon belongs to")
    discount_percentage: float = Field(default=10.0, description="Discount percentage")
    status: CouponStatus = Field(default=CouponStatus.UNUSED)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default=None, description="Expiration timestamp")
    used_at: Optional[datetime] = None
    order_id: Optional[str] = None
    reason: Optional[str] = Field(default=None, description="Reason for coupon generation (for admin-generated coupons)")
    
    def __init__(self, **data):
        """Initialize coupon with expiration date."""
        super().__init__(**data)
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(days=60)  # 2 months = 60 days
    
    def mark_as_used(self, order_id: str) -> None:
        """Mark coupon as used."""
        self.status = CouponStatus.USED
        self.used_at = datetime.utcnow()
        self.order_id = order_id
    
    def is_expired(self) -> bool:
        """Check if coupon has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if coupon is valid for use."""
        return self.status == CouponStatus.UNUSED and not self.is_expired()
