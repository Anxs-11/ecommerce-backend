"""Checkout service for processing orders."""
import uuid
from typing import Optional, Tuple
from app.models import Order, OrderItem
from app.services.in_memory_store import data_store
from app.services.cart_service import cart_service
from app.services.coupon_service import coupon_service


class CheckoutService:
    """Service for checkout operations."""
    
    def calculate_order_totals(
        self, 
        subtotal: float, 
        coupon_code: Optional[str] = None
    ) -> Tuple[float, float]:
        """
        Calculate order totals with optional coupon discount.
        
        Returns:
            tuple: (discount_amount, total_amount)
        """
        discount_amount = 0.0
        
        if coupon_code:
            coupon = coupon_service.get_coupon(coupon_code)
            if coupon and coupon.is_valid():
                discount_amount = round(subtotal * (coupon.discount_percentage / 100), 2)
        
        total_amount = round(subtotal - discount_amount, 2)
        return discount_amount, total_amount
    
    def checkout(
        self, 
        user_id: str, 
        coupon_code: Optional[str] = None
    ) -> Tuple[Optional[Order], Optional[str]]:
        """
        Process checkout for user's cart.
        
        Returns:
            tuple: (order, error_message)
        """
        # Get user's cart
        cart = cart_service.get_cart(user_id)
        
        if not cart or len(cart.items) == 0:
            return None, "Cart is empty"
        
        # Validate coupon if provided
        if coupon_code:
            is_valid, error_msg = coupon_service.validate_coupon(coupon_code, user_id)
            if not is_valid:
                return None, error_msg
        
        # Create order
        order_id = str(uuid.uuid4())
        subtotal = cart.total_amount
        discount_amount, total_amount = self.calculate_order_totals(subtotal, coupon_code)
        
        # Convert cart items to order items
        order_items = [
            OrderItem(
                product_id=item.product_id,
                product_name=item.product_name,
                price=item.price,
                quantity=item.quantity
            )
            for item in cart.items
        ]
        
        # Create order
        order = Order(
            order_id=order_id,
            user_id=user_id,
            items=order_items,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=total_amount,
            coupon_code=coupon_code
        )
        
        # Save order
        data_store.orders[order_id] = order
        
        # Mark coupon as used if provided
        if coupon_code:
            coupon_service.mark_coupon_as_used(coupon_code, order_id)
            data_store.total_discount_applied += discount_amount
        
        # Increment successful order count
        data_store.order_count += 1
        
        # Check if we should generate a new coupon for this user
        if coupon_service.should_generate_coupon():
            coupon_service.create_coupon(user_id)
        
        # Clear cart
        cart_service.clear_cart(user_id)
        
        return order, None
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return data_store.orders.get(order_id)
    
    def get_all_orders(self):
        """Get all orders."""
        return list(data_store.orders.values())


# Global service instance
checkout_service = CheckoutService()
