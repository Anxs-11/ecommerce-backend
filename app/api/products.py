"""Products API endpoints."""
from fastapi import APIRouter, Query
from typing import List
from app.models import Product
from app.services.product_service import product_service

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/search", response_model=List[Product])
def search_products(
    q: str = Query(..., description="Search query for product name", min_length=1)
) -> List[Product]:
    """Search products by name (case-insensitive, partial match).
    
    Args:
        q: Search query string (required)
        
    Returns:
        List of matching products (max 20 items)
    """
    return product_service.search_products(q, limit=20)
