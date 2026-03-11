"""Product service for managing product data and search."""
from typing import List
from app.models import Product


class ProductService:
    """Service for product operations."""
    
    def __init__(self):
        """Initialize with sample product data."""
        self.products: List[Product] = [
            Product(
                id="prod_001",
                name="Wireless Mouse",
                price=29.99,
                description="Ergonomic wireless mouse with USB receiver",
                stock=50
            ),
            Product(
                id="prod_002",
                name="Mechanical Keyboard",
                price=89.99,
                description="RGB mechanical gaming keyboard",
                stock=30
            ),
            Product(
                id="prod_003",
                name="USB-C Cable",
                price=12.99,
                description="High-speed USB-C charging cable",
                stock=100
            ),
            Product(
                id="prod_004",
                name="Laptop Stand",
                price=45.00,
                description="Adjustable aluminum laptop stand",
                stock=25
            ),
            Product(
                id="prod_005",
                name="Wireless Headphones",
                price=149.99,
                description="Noise-cancelling wireless headphones",
                stock=15
            ),
            Product(
                id="prod_006",
                name="Phone Case",
                price=19.99,
                description="Protective phone case with card holder",
                stock=75
            ),
            Product(
                id="prod_007",
                name="Monitor Stand",
                price=55.00,
                description="Dual monitor stand with cable management",
                stock=20
            ),
            Product(
                id="prod_008",
                name="Wireless Charger",
                price=34.99,
                description="Fast wireless charging pad",
                stock=40
            ),
        ]
    
    def search_products(self, query: str, limit: int = 20) -> List[Product]:
        """Search products by name (case-insensitive, partial match).
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            
        Returns:
            List of matching products (up to limit)
        """
        query_lower = query.lower()
        matching_products = [
            product for product in self.products
            if query_lower in product.name.lower()
        ]
        return matching_products[:limit]


# Global instance
product_service = ProductService()
