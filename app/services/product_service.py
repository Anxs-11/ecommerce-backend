"""Product service for managing product operations."""
from typing import List
from app.models import Product
from app.services.in_memory_store import data_store


class ProductService:
    """Service for product operations."""
    
    def __init__(self):
        """Initialize product service with sample data."""
        self._initialize_sample_products()
    
    def _initialize_sample_products(self) -> None:
        """Initialize sample products if not already present."""
        if not hasattr(data_store, 'products'):
            data_store.products = {}
        
        # Only initialize if empty
        if not data_store.products:
            sample_products = [
                Product(id="prod_001", name="Wireless Mouse", price=29.99, description="Ergonomic wireless mouse"),
                Product(id="prod_002", name="Mechanical Keyboard", price=89.99, description="RGB mechanical keyboard"),
                Product(id="prod_003", name="USB-C Cable", price=12.99, description="High-speed USB-C cable"),
                Product(id="prod_004", name="Laptop Stand", price=45.00, description="Adjustable aluminum laptop stand"),
                Product(id="prod_005", name="Webcam HD", price=79.99, description="1080p HD webcam with microphone"),
                Product(id="prod_006", name="Wireless Headphones", price=149.99, description="Noise-cancelling wireless headphones"),
                Product(id="prod_007", name="Phone Charger", price=19.99, description="Fast charging USB phone charger"),
                Product(id="prod_008", name="Monitor 27 inch", price=299.99, description="4K UHD 27-inch monitor"),
                Product(id="prod_009", name="Desk Lamp", price=34.99, description="LED desk lamp with adjustable brightness"),
                Product(id="prod_010", name="External SSD 1TB", price=129.99, description="Portable 1TB external SSD"),
            ]
            
            for product in sample_products:
                data_store.products[product.id] = product
    
    def search_products(self, query: str, limit: int = 20) -> List[Product]:
        """Search products by name (case-insensitive, partial match).
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default 20)
            
        Returns:
            List of matching products (empty list if no matches)
        """
        query_lower = query.lower().strip()
        
        # Filter products by name using case-insensitive partial match (ilike behavior)
        matching_products = [
            product for product in data_store.products.values()
            if query_lower in product.name.lower()
        ]
        
        # Sort by name for consistent ordering
        matching_products.sort(key=lambda p: p.name)
        
        # Limit results
        return matching_products[:limit]


# Global instance
product_service = ProductService()
