"""Cart service for managing shopping carts."""
from typing import Optional
from app.models import Cart, AddToCartRequest
from app.services.in_memory_store import data_store


class CartService:
    """Service for cart operations."""
    
    def get_or_create_cart(self, user_id: str) -> Cart:
        """Get cart for user or create new one if doesn't exist."""
        if user_id not in data_store.carts:
            data_store.carts[user_id] = Cart(user_id=user_id)
        return data_store.carts[user_id]
    
    def get_cart(self, user_id: str) -> Optional[Cart]:
        """Get cart for user."""
        return data_store.carts.get(user_id)
    
    def add_to_cart(self, user_id: str, item: AddToCartRequest) -> Cart:
        """Add item to user's cart."""
        cart = self.get_or_create_cart(user_id)
        cart.add_item(item)
        return cart
    
    def clear_cart(self, user_id: str) -> None:
        """Clear user's cart."""
        if user_id in data_store.carts:
            data_store.carts[user_id].clear()


# Global service instance
cart_service = CartService()
