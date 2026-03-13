"""Product model."""
from pydantic import BaseModel, Field


class Product(BaseModel):
    """Product model."""
    
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    description: str = Field(default="", description="Product description")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "id": "prod_123",
                "name": "Wireless Mouse",
                "price": 29.99,
                "description": "Ergonomic wireless mouse with USB receiver"
            }
        }
