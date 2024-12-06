from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader
from ..core.config import settings
import os

class EmailService:
    def __init__(self):
        self.smtp_config = {
            'hostname': settings.SMTP_HOST,
            'port': settings.SMTP_PORT,
            'username': settings.SMTP_USER,
            'password': settings.SMTP_PASSWORD,
            'use_tls': True
        }
        self.from_email = settings.SMTP_USER
        self.template_env = Environment(
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), '../templates/email'))
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send an email using a template"""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.from_email
            message['To'] = to_email
            message['Subject'] = subject

            if cc:
                message['Cc'] = ', '.join(cc)
            if bcc:
                message['Bcc'] = ', '.join(bcc)

            # Render template
            template = self.template_env.get_template(f"{template_name}.html")
            html_content = template.render(**template_data)
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # Send email
            async with SMTP(**self.smtp_config) as smtp:
                await smtp.send_message(message)
            
            return True
        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")

    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new users"""
        template_data = {
            'user_name': user_name,
            'login_url': f"{settings.APP_URL}/login"
        }
        return await self.send_email(
            to_email=user_email,
            subject="Welcome to Ready Set Realtor!",
            template_name="welcome",
            template_data=template_data
        )

    async def send_lead_notification(
        self,
        user_email: str,
        lead_name: str,
        lead_details: Dict[str, Any]
    ) -> bool:
        """Send notification about new lead"""
        template_data = {
            'lead_name': lead_name,
            'lead_details': lead_details,
            'dashboard_url': f"{settings.APP_URL}/leads"
        }
        return await self.send_email(
            to_email=user_email,
            subject=f"New Lead: {lead_name}",
            template_name="new_lead",
            template_data=template_data
        )

    async def send_transaction_update(
        self,
        user_email: str,
        transaction_id: str,
        update_details: Dict[str, Any]
    ) -> bool:
        """Send notification about transaction updates"""
        template_data = {
            'transaction_id': transaction_id,
            'update_details': update_details,
            'transaction_url': f"{settings.APP_URL}/transactions/{transaction_id}"
        }
        return await self.send_email(
            to_email=user_email,
            subject=f"Transaction Update: {transaction_id}",
            template_name="transaction_update",
            template_data=template_data
        )

    async def send_deadline_reminder(
        self,
        user_email: str,
        deadline_details: Dict[str, Any]
    ) -> bool:
        """Send reminder about upcoming deadlines"""
        template_data = {
            'deadline_details': deadline_details,
            'dashboard_url': f"{settings.APP_URL}/dashboard"
        }
        return await self.send_email(
            to_email=user_email,
            subject="Upcoming Deadline Reminder",
            template_name="deadline_reminder",
            template_data=template_data
        )
