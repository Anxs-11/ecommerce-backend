"""Products API endpoints."""
from fastapi import APIRouter, Query
from typing import List
from app.models import Product
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/search", response_model=List[Product])
def search_products(
    q: str = Query(..., description="Search query for product name (case-insensitive, partial match)")
) -> List[Product]:
    """Search products by name.
    
    Args:
        q: Search query string (required)
        
    Returns:
        List of matching products (max 20 items)
        Returns empty list if no matches found
    """
    return product_service.search_products(query=q, limit=20)
