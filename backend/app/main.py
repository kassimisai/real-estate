from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import auth, leads, transactions, scheduling, analytics
from .mcp.base import MCPController
from .core.config import settings

app = FastAPI(title="Ready Set Realtor API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP Controller
mcp_controller = MCPController()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(leads.router, prefix="/leads", tags=["leads"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(scheduling.router, prefix="/scheduling", tags=["scheduling"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Welcome to Ready Set Realtor API"}
