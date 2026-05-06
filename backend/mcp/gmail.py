"""
backend/mcp/gmail.py
---------------------
Gmail MCP integration for sending funder outreach emails and follow-ups.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from backend.config import settings
from backend.agent.core import agent
from backend.agent.prompts import followup_email_prompt
import base64
import json
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly']

class GmailMCP:
    # Class constant as requested: critical — never send email without approval.
    user_approval_required = True

    def __init__(self):
        self.service = None
        self.user_approval_required = True
        self.credentials_file = "credentials.json"
        self.token_file = "token.json"

    def authenticate(self) -> bool:
        """
        Authenticate with the Gmail API.
        Checks if token.json exists and loads credentials.
        If expired, refreshes them.
        If no token, runs InstalledAppFlow from credentials.json.
        Builds the gmail service.
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
            
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            print(f"Failed to authenticate with Gmail API: {e}")
            return False

    async def create_outreach_email(self, to_email: str, 
                                    funder_name: str,
                                    grant_title: str, 
                                    org_name: str,
                                    org_mission: str) -> dict:
        """
        Uses the agent to draft a professional cold outreach email.
        """
        prompt = (
            f"Draft a professional cold outreach email from {org_name} to {funder_name} "
            f"expressing interest in the {grant_title} grant program. The org mission is: "
            f"{org_mission}. Keep it under 200 words, professional but warm. "
            "Return JSON with keys: subject, body"
        )
        
        try:
            response = await agent.send_message(prompt)
            
            # Parse the response as JSON
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                raise ValueError("No JSON object found in model response.")
            email_data = json.loads(match.group())
            
            return {
                "to": to_email,
                "subject": email_data.get("subject", ""),
                "body": email_data.get("body", ""),
                "funder_name": funder_name,
                "grant_title": grant_title,
                "status": "pending_approval"
            }
        except Exception as e:
            print(f"Error drafting outreach email: {e}")
            return {
                "to": to_email,
                "funder_name": funder_name,
                "grant_title": grant_title,
                "status": "error",
                "error_message": str(e)
            }

    def send_email(self, email_draft: dict, user_approved: bool = False) -> dict:
        """
        Sends an email via the Gmail API if user_approved is True.
        """
        if not user_approved and self.user_approval_required:
            return {
                "status": "pending_approval", 
                "message": "Email requires user approval before sending",
                "draft": email_draft
            }
            
        try:
            message = MIMEMultipart()
            message['To'] = email_draft.get("to")
            message['Subject'] = email_draft.get("subject")
            
            body = MIMEText(email_draft.get("body", ""), 'plain')
            message.attach(body)
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()
            
            return {
                "status": "sent", 
                "message_id": sent_message.get("id"), 
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Failed to send email: {e}")
            return {"status": "error", "message": str(e)}

    def check_for_replies(self, funder_email: str, days_back: int = 7) -> dict:
        """
        Search Gmail for messages from the funder_email in the last {days_back} days.
        """
        try:
            query = f"from:{funder_email} newer_than:{days_back}d"
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            
            return {
                "has_reply": len(messages) > 0, 
                "message_count": len(messages),
                "funder_email": funder_email
            }
        except Exception as e:
            print(f"Error checking for replies: {e}")
            return {
                "has_reply": False, 
                "message_count": 0,
                "funder_email": funder_email,
                "error": str(e)
            }

    async def create_followup_if_no_reply(self, 
                                          org_name: str,
                                          funder_name: str,
                                          funder_email: str,
                                          grant_title: str,
                                          days_since_first: int = 7) -> dict:
        """
        Checks for replies from the funder. If no reply, drafts a follow-up email.
        """
        reply_status = self.check_for_replies(funder_email, days_back=days_since_first)
        
        if reply_status.get("has_reply"):
            return {
                "status": "replied", 
                "action": "no_followup_needed"
            }
            
        try:
            # Use the imported prompt generator
            prompt = followup_email_prompt(
                org_name=org_name,
                grant_title=grant_title,
                funder_name=funder_name,
                days_since_first=days_since_first
            )
            
            response = await agent.send_message(prompt)
            
            return {
                "to": funder_email,
                "subject": f"Following up: {grant_title}",
                "body": response.strip(),
                "funder_name": funder_name,
                "grant_title": grant_title,
                "status": "followup_pending_approval"
            }
        except Exception as e:
            print(f"Error drafting follow-up email: {e}")
            return {
                "to": funder_email,
                "funder_name": funder_name,
                "grant_title": grant_title,
                "status": "error",
                "error_message": str(e)
            }

# Create instance at bottom as requested
gmail_mcp = GmailMCP()
