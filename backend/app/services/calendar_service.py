from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os.path
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        self._initialize_service()

    def _initialize_service(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

    async def create_event(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendees: List[Dict[str, str]],
        location: str = None
    ) -> Dict[str, Any]:
        """Create a calendar event"""
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'attendees': attendees,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }

        if location:
            event['location'] = location

        try:
            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'
            ).execute()
            return event
        except Exception as e:
            raise Exception(f"Failed to create calendar event: {str(e)}")

    async def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        duration_minutes: int = 60
    ) -> List[Dict[str, datetime]]:
        """Get available time slots between start_date and end_date"""
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])

            # Convert events to busy times
            busy_times = []
            for event in events:
                start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
                end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
                busy_times.append({'start': start, 'end': end})

            # Find available slots
            available_slots = []
            current_time = start_date
            while current_time < end_date:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                is_available = True

                for busy in busy_times:
                    if (current_time >= busy['start'] and current_time < busy['end']) or \
                       (slot_end > busy['start'] and slot_end <= busy['end']):
                        is_available = False
                        current_time = busy['end']
                        break

                if is_available:
                    if current_time.hour >= 9 and (slot_end.hour < 17 or \
                        (slot_end.hour == 17 and slot_end.minute == 0)):
                        available_slots.append({
                            'start': current_time,
                            'end': slot_end
                        })
                    current_time += timedelta(minutes=30)
                
            return available_slots
        except Exception as e:
            raise Exception(f"Failed to get available slots: {str(e)}")

    async def update_event(
        self,
        event_id: str,
        summary: str = None,
        description: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        attendees: List[Dict[str, str]] = None,
        location: str = None
    ) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
            if attendees:
                event['attendees'] = attendees
            if location:
                event['location'] = location

            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            return updated_event
        except Exception as e:
            raise Exception(f"Failed to update calendar event: {str(e)}")

    async def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event"""
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Failed to delete calendar event: {str(e)}")
