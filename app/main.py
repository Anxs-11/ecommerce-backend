"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.api import cart_router, checkout_router, admin_router

# Create FastAPI app
app = FastAPI(
    title="E-Commerce Backend API",
    description="A production-ready e-commerce backend with cart management, "
                "checkout, and automatic coupon generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "E-Commerce Backend API is running",
            "version": "1.0.0"
        }
    )


# Include routers
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
