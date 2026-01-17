"""In-memory data store for the application."""
from typing import Dict
from app.models import Cart, Order, Coupon


class DataStore:
    """Singleton in-memory data store."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize data structures."""
        if self._initialized:
            return
            
        self.carts: Dict[str, Cart] = {}
        self.orders: Dict[str, Order] = {}
        self.coupons: Dict[str, Coupon] = {}
        self.user_order_counts: Dict[str, int] = {}  # Track orders per user
        self.total_discount_applied: float = 0.0
        self._initialized = True
    
    def reset(self) -> None:
        """Reset all data (useful for testing)."""
        self.carts.clear()
        self.orders.clear()
        self.coupons.clear()
        self.user_order_counts.clear()
        self.total_discount_applied = 0.0


# Global instance
data_store = DataStore()
