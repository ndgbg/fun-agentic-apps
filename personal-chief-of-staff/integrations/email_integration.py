#!/usr/bin/env python3
"""
Email Integration - Auto-add tasks from emails
Real IMAP/Gmail API integration.
"""

import os
import email
import imaplib
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class EmailTask:
    subject: str
    from_email: str
    body: str
    received_at: str
    priority: str
    estimated_hours: float

class GmailIntegration:
    """Real Gmail API integration."""
    
    def __init__(self, credentials_path: str = "credentials.json"):
        self.credentials_path = credentials_path
        self.service = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gmail API."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
            
            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            
            creds = None
            if os.path.exists('gmail_token.json'):
                creds = Credentials.from_authorized_user_file('gmail_token.json', SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(self.credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                
                with open('gmail_token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
            
        except Exception as e:
            print(f"⚠️  Gmail setup needed: {e}")
            self.service = None
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """Get unread emails."""
        
        if not self.service:
            return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Get body
                body = ""
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            import base64
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                
                emails.append({
                    'id': msg['id'],
                    'subject': subject,
                    'from': from_email,
                    'body': body[:500],  # First 500 chars
                    'date': date
                })
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

class IMAPIntegration:
    """Generic IMAP integration for any email provider."""
    
    def __init__(self, server: str, email: str, password: str):
        self.server = server
        self.email = email
        self.password = password
        self.connection = None
    
    def connect(self):
        """Connect to IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.server)
            self.connection.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return False
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict]:
        """Get unread emails via IMAP."""
        
        if not self.connection and not self.connect():
            return []
        
        try:
            self.connection.select('INBOX')
            
            _, message_numbers = self.connection.search(None, 'UNSEEN')
            
            emails = []
            for num in message_numbers[0].split()[:max_results]:
                _, msg_data = self.connection.fetch(num, '(RFC822)')
                
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = email_message['subject']
                from_email = email_message['from']
                date = email_message['date']
                
                # Get body
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                emails.append({
                    'subject': subject,
                    'from': from_email,
                    'body': body[:500],
                    'date': date
                })
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.connection:
            self.connection.close()
            self.connection.logout()

class EmailTaskExtractor:
    """Extract tasks from emails using AI."""
    
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def extract_tasks_from_emails(self, emails: List[Dict]) -> List[EmailTask]:
        """Analyze emails and extract actionable tasks."""
        
        if not emails:
            return []
        
        emails_text = "\n\n".join([
            f"From: {e['from']}\nSubject: {e['subject']}\nBody: {e['body'][:200]}..."
            for e in emails[:5]  # Limit to 5 emails
        ])
        
        prompt = f"""Analyze these emails and extract actionable tasks.

Emails:
{emails_text}

For each email, identify:
1. Action items requested
2. Deadlines mentioned
3. Priority level (critical/high/medium/low)
4. Estimated time needed

Return JSON array:
[
  {{
    "subject": "Review Q1 report",
    "from_email": "boss@company.com",
    "body": "Please review the attached Q1 report by Friday",
    "received_at": "2026-02-03T10:00:00",
    "priority": "high",
    "estimated_hours": 2.0
  }}
]

Only include emails that contain clear action items."""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Extract JSON
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            tasks_data = json.loads(json_match.group())
            return [EmailTask(**task) for task in tasks_data]
        
        return []

async def main():
    """Demo email integration."""
    
    print("📧 EMAIL INTEGRATION")
    print("="*70)
    
    # Try Gmail first
    print("\n🔵 Gmail")
    gmail = GmailIntegration()
    emails = gmail.get_unread_emails(max_results=5)
    
    if emails:
        print(f"Found {len(emails)} unread emails:")
        for email in emails:
            print(f"  • {email['subject']} from {email['from']}")
    else:
        print("  No emails found (setup credentials.json for Gmail API)")
    
    # Extract tasks
    if emails and os.getenv("ANTHROPIC_API_KEY"):
        print("\n🤖 Extracting tasks from emails...")
        extractor = EmailTaskExtractor(os.getenv("ANTHROPIC_API_KEY"))
        tasks = await extractor.extract_tasks_from_emails(emails)
        
        print(f"Extracted {len(tasks)} tasks:")
        for task in tasks:
            print(f"  • {task.subject} (Priority: {task.priority}, Est: {task.estimated_hours}h)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
