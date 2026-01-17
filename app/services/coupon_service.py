"""Coupon service for managing discount coupons."""
import secrets
import string
from typing import List, Optional
from app.models import Coupon, CouponStatus
from app.services.in_memory_store import data_store


class CouponService:
    """Service for coupon operations."""
    
    def __init__(self, nth_order: int = 5):
        """Initialize coupon service with configurable Nth order."""
        self.nth_order = nth_order
    
    def generate_coupon_code(self, length: int = 8) -> str:
        """Generate a unique random coupon code."""
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(length))
            if code not in data_store.coupons:
                return code
    
    def should_generate_coupon(self) -> bool:
        """Check if a coupon should be generated based on order count."""
        # Generate coupon on every Nth successful order
        return data_store.order_count > 0 and data_store.order_count % self.nth_order == 0
    
    def can_generate_manual_coupon(self) -> bool:
        """Check if manual coupon generation is allowed."""
        return self.should_generate_coupon()
    
    def create_coupon(self, user_id: str, discount_percentage: float = 10.0, reason: Optional[str] = None) -> Coupon:
        """Create a new coupon for a specific user."""
        code = self.generate_coupon_code()
        coupon = Coupon(code=code, user_id=user_id, discount_percentage=discount_percentage, reason=reason)
        data_store.coupons[code] = coupon
        return coupon
    
    def get_coupon(self, code: str) -> Optional[Coupon]:
        """Get coupon by code."""
        return data_store.coupons.get(code)
    
    def validate_coupon(self, code: str, user_id: str) -> tuple[bool, Optional[str]]:
        """
        Validate coupon for a specific user.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        coupon = self.get_coupon(code)
        
        if not coupon:
            return False, "Coupon code does not exist"
        
        if coupon.user_id != user_id:
            return False, "This coupon belongs to another user and cannot be used"
        
        if not coupon.is_valid():
            return False, "Coupon has already been used"
        
        return True, None
    
    def mark_coupon_as_used(self, code: str, order_id: str) -> None:
        """Mark coupon as used."""
        coupon = self.get_coupon(code)
        if coupon:
            coupon.mark_as_used(order_id)
    
    def get_all_coupons(self) -> List[Coupon]:
        """Get all coupons."""
        return list(data_store.coupons.values())
    
    def get_unused_coupons(self) -> List[Coupon]:
        """Get all unused coupons."""
        return [c for c in data_store.coupons.values() 
                if c.status == CouponStatus.UNUSED]
    
    def get_used_coupons(self) -> List[Coupon]:
        """Get all used coupons."""
        return [c for c in data_store.coupons.values() 
                if c.status == CouponStatus.USED]


# Global service instance
coupon_service = CouponService()
