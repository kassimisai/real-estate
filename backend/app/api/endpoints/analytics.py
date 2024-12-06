from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from ...core.database import get_db
from ...core.auth import get_current_user
from ...mcp.base import MCPController, AgentMessage
from ...schemas.analytics import (
    AnalyticsRequest,
    AnalyticsResponse,
    VisualizationRequest
)

router = APIRouter()

@router.post("/report", response_model=AnalyticsResponse)
async def generate_report(
    request: AnalyticsRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    message = AgentMessage(
        content="Generate analytics report",
        metadata={
            "action": "generate_report",
            "data": {
                "user_id": str(current_user.id),
                "date_range": request.date_range,
                "send_email": request.send_email,
                "user_email": current_user.email if request.send_email else None
            }
        },
        source_agent="api",
        target_agent="analytics"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]

@router.post("/visualizations/{viz_type}")
async def create_visualization(
    viz_type: str,
    request: VisualizationRequest,
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    message = AgentMessage(
        content="Create visualization",
        metadata={
            "action": "create_visualization",
            "data": {
                "data": request.data,
                "viz_type": viz_type
            }
        },
        source_agent="api",
        target_agent="analytics"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]

@router.get("/metrics")
async def get_metrics(
    metric_type: Optional[str] = None,
    date_range: int = 30,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific metrics based on type"""
    message = AgentMessage(
        content="Get metrics",
        metadata={
            "action": "get_metrics",
            "data": {
                "user_id": str(current_user.id),
                "metric_type": metric_type,
                "date_range": date_range
            }
        },
        source_agent="api",
        target_agent="analytics"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]
