from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from ...core.database import get_db
from ...core.auth import get_current_user
from ...mcp.base import MCPController, AgentMessage
from ...schemas.scheduling import (
    AvailabilityRequest,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)

router = APIRouter()

@router.post("/availability", response_model=Dict[str, List])
async def get_availability(
    request: AvailabilityRequest,
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    message = AgentMessage(
        content="Find available slots",
        metadata={
            "action": "find_slots",
            "data": {
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "duration_minutes": request.duration_minutes
            }
        },
        source_agent="api",
        target_agent="scheduling"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]

@router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    message = AgentMessage(
        content="Schedule appointment",
        metadata={
            "action": "schedule",
            "data": {
                "summary": appointment.summary,
                "description": appointment.description,
                "start_time": appointment.start_time.isoformat(),
                "end_time": appointment.end_time.isoformat(),
                "attendees": [{"email": email} for email in appointment.attendees],
                "location": appointment.location
            }
        },
        source_agent="api",
        target_agent="scheduling"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]["event"]

@router.put("/appointments/{event_id}", response_model=AppointmentResponse)
async def update_appointment(
    event_id: str,
    appointment: AppointmentUpdate,
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    message = AgentMessage(
        content="Reschedule appointment",
        metadata={
            "action": "reschedule",
            "data": {
                "event_id": event_id,
                "new_start_time": appointment.start_time.isoformat(),
                "new_end_time": appointment.end_time.isoformat()
            }
        },
        source_agent="api",
        target_agent="scheduling"
    )
    
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]["event"]
