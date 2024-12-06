from typing import Dict, Any, List
from datetime import datetime, timedelta
from ..base import AgentContext, AgentState, AgentMessage
from ...services.calendar_service import CalendarService
from ...services.email_service import EmailService

class SchedulingAgent:
    def __init__(self, context: AgentContext):
        self.context = context
        self.calendar_service = CalendarService()
        self.email_service = EmailService()
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        return {
            "find_available_slots": self._find_available_slots,
            "schedule_appointment": self._schedule_appointment,
            "send_confirmation": self._send_confirmation,
            "reschedule_appointment": self._reschedule_appointment
        }
    
    async def _find_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60
    ) -> List[Dict[str, datetime]]:
        """Find available time slots"""
        try:
            return await self.calendar_service.get_available_slots(
                start_date, end_date, duration_minutes
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to find available slots: {str(e)}")
    
    async def _schedule_appointment(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[Dict[str, str]],
        location: str = None
    ) -> Dict[str, Any]:
        """Schedule a new appointment"""
        try:
            return await self.calendar_service.create_event(
                summary=summary,
                description=description,
                start_time=start_time,
                end_time=end_time,
                attendees=attendees,
                location=location
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to schedule appointment: {str(e)}")
    
    async def _send_confirmation(
        self,
        to_email: str,
        appointment_details: Dict[str, Any]
    ) -> bool:
        """Send appointment confirmation email"""
        try:
            template_data = {
                'appointment_details': appointment_details,
                'calendar_url': f"{appointment_details.get('htmlLink', '')}"
            }
            return await self.email_service.send_email(
                to_email=to_email,
                subject="Appointment Confirmation",
                template_name="appointment_confirmation",
                template_data=template_data
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to send confirmation: {str(e)}")
    
    async def _reschedule_appointment(
        self,
        event_id: str,
        new_start_time: datetime,
        new_end_time: datetime
    ) -> Dict[str, Any]:
        """Reschedule an existing appointment"""
        try:
            return await self.calendar_service.update_event(
                event_id=event_id,
                start_time=new_start_time,
                end_time=new_end_time
            )
        except Exception as e:
            self.context.state = AgentState.ERROR
            raise Exception(f"Failed to reschedule appointment: {str(e)}")
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Process incoming scheduling requests"""
        self.context.state = AgentState.WORKING
        
        try:
            action = message.metadata.get('action')
            data = message.metadata.get('data', {})
            
            response = {"status": "success", "data": None}
            
            if action == "find_slots":
                start_date = datetime.fromisoformat(data['start_date'])
                end_date = datetime.fromisoformat(data['end_date'])
                duration = data.get('duration_minutes', 60)
                
                slots = await self._find_available_slots(start_date, end_date, duration)
                response["data"] = {"available_slots": slots}
            
            elif action == "schedule":
                event = await self._schedule_appointment(**data)
                await self._send_confirmation(
                    to_email=data['attendees'][0]['email'],
                    appointment_details=event
                )
                response["data"] = {"event": event}
            
            elif action == "reschedule":
                event = await self._reschedule_appointment(
                    event_id=data['event_id'],
                    new_start_time=datetime.fromisoformat(data['new_start_time']),
                    new_end_time=datetime.fromisoformat(data['new_end_time'])
                )
                response["data"] = {"event": event}
            
            self.context.state = AgentState.IDLE
            return AgentMessage(
                content="Task completed",
                metadata=response,
                source_agent=self.context.agent_id
            )
            
        except Exception as e:
            self.context.state = AgentState.ERROR
            return AgentMessage(
                content="Error processing task",
                metadata={"status": "error", "message": str(e)},
                source_agent=self.context.agent_id
            )
