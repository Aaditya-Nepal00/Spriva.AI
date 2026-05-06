"""
backend/mcp/calendar.py
-----------------------
Google Calendar MCP integration for tracking grant deadlines
and scheduling follow-up reminders.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from backend.config import settings
from datetime import datetime, timedelta
import os
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarMCP:
    def __init__(self):
        """Initialize the CalendarMCP instance with basic properties."""
        self.service = None
        self.credentials_file = "credentials.json"
        self.token_file = "calendar_token.json"
        self.calendar_id = "primary"

    def authenticate(self) -> bool:
        """
        Authenticate with the Google Calendar API.
        Checks if calendar_token.json exists, loads/refreshes credentials,
        and builds the calendar service.
        Returns True on success, False on failure.
        """
        creds = None
        try:
            if os.path.exists(self.token_file):
                creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open(self.token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Failed to authenticate with Google Calendar API: {e}")
            return False

    def add_grant_deadline(self, grant_title: str,
                           funder_name: str,
                           deadline_date: str,
                           org_name: str) -> dict:
        """
        Creates a calendar event for a grant deadline.
        The event is created as an all-day event and includes reminders.
        
        Args:
            grant_title: The title of the grant
            funder_name: The name of the funding organization
            deadline_date: The deadline date (YYYY-MM-DD format)
            org_name: The organization applying
        """
        try:
            # Parse the deadline_date string to calculate the end date (deadline + 1 day)
            # All-day events in Google Calendar require start and end dates to be specified
            # where the end date is exclusive (i.e. the day after the start date).
            start_date_obj = datetime.strptime(deadline_date, "%Y-%m-%d")
            end_date_obj = start_date_obj + timedelta(days=1)
            end_date = end_date_obj.strftime("%Y-%m-%d")

            event_body = {
                'summary': f"GRANT DEADLINE: {grant_title}",
                'description': f"Grant: {grant_title}\nFunder: {funder_name}\nOrg: {org_name}\nAdded by Spriva AI",
                'start': {
                    'date': deadline_date,
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': end_date,
                    'timeZone': 'UTC',
                },
                'colorId': "11", # color 11 is tomato/red for urgency
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 14 * 24 * 60}, # 14 days before
                        {'method': 'email', 'minutes': 3 * 24 * 60},  # 3 days before
                    ],
                },
            }

            event = self.service.events().insert(calendarId=self.calendar_id, body=event_body).execute()

            return {
                "status": "created",
                "event_id": event.get('id'),
                "grant_title": grant_title,
                "deadline": deadline_date,
                "calendar_link": event.get('htmlLink')
            }
        except Exception as e:
            print(f"Error adding grant deadline to calendar: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "grant_title": grant_title,
                "deadline": deadline_date
            }

    def add_followup_reminder(self, grant_title: str,
                              funder_name: str,
                              followup_date: str) -> dict:
        """
        Creates a reminder event on a specific followup_date (typically 7 days after initial outreach).
        """
        try:
            start_date_obj = datetime.strptime(followup_date, "%Y-%m-%d")
            end_date_obj = start_date_obj + timedelta(days=1)
            end_date = end_date_obj.strftime("%Y-%m-%d")

            event_body = {
                'summary': f"FOLLOW UP: {grant_title} — {funder_name}",
                'description': "Check for funder reply. If no reply, send follow-up email via Spriva AI.",
                'start': {
                    'date': followup_date,
                    'timeZone': 'UTC',
                },
                'end': {
                    'date': end_date,
                    'timeZone': 'UTC',
                },
            }

            event = self.service.events().insert(calendarId=self.calendar_id, body=event_body).execute()

            return {
                "status": "created",
                "event_id": event.get('id'),
                "grant_title": grant_title,
                "deadline": followup_date, # using deadline key to maintain consistent structure
                "calendar_link": event.get('htmlLink')
            }
        except Exception as e:
            print(f"Error adding followup reminder to calendar: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "grant_title": grant_title,
                "deadline": followup_date
            }

    def get_upcoming_deadlines(self, days_ahead: int = 30) -> list:
        """
        Fetches all grant deadline events in the next `days_ahead` days.
        Filters events where the summary starts with "GRANT DEADLINE:".
        """
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z' # 'Z' indicates UTC time
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            upcoming_deadlines = []

            for event in events:
                summary = event.get('summary', '')
                if summary.startswith("GRANT DEADLINE:"):
                    # Extract date (date format could be YYYY-MM-DD or full dateTime)
                    start_date_str = event['start'].get('date') or event['start'].get('dateTime')
                    if 'T' in start_date_str:
                        start_date_str = start_date_str.split('T')[0]
                        
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    days_remaining = (start_date - datetime.utcnow()).days

                    # Strip the prefix to get the clean title
                    grant_title = summary.replace("GRANT DEADLINE:", "").strip()
                    
                    upcoming_deadlines.append({
                        "event_id": event.get('id'),
                        "grant_title": grant_title,
                        "deadline_date": start_date_str,
                        "days_remaining": days_remaining,
                        "calendar_link": event.get('htmlLink')
                    })
            
            return upcoming_deadlines
        except Exception as e:
            print(f"Error fetching upcoming deadlines: {e}")
            return []

    def list_all_grant_events(self) -> list:
        """
        Returns all events added by Spriva (both deadlines and follow-up reminders).
        Filters where summary starts with "GRANT DEADLINE:" or "FOLLOW UP:".
        Returns sorted list by date.
        """
        try:
            # Note: We omit timeMin and timeMax to fetch a broader scope of events
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            spriva_events = []

            for event in events:
                summary = event.get('summary', '')
                if summary.startswith("GRANT DEADLINE:") or summary.startswith("FOLLOW UP:"):
                    start_date_str = event['start'].get('date') or event['start'].get('dateTime')
                    spriva_events.append({
                        "event_id": event.get('id'),
                        "summary": summary,
                        "start_date": start_date_str,
                        "calendar_link": event.get('htmlLink')
                    })
            
            # Sorting events by start_date to guarantee ascending chronological order
            spriva_events.sort(key=lambda x: x['start_date'])
            
            return spriva_events
        except Exception as e:
            print(f"Error listing all grant events: {e}")
            return []

# Instantiate the CalendarMCP at the bottom of the module
calendar_mcp = CalendarMCP()
