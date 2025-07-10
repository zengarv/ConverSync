import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional
from config import Config

class EmailService:
    """Service for sending emails with attachments."""
    
    def __init__(self):
        try:
            Config.validate_config()
            self.smtp_server = Config.SMTP_SERVER
            self.smtp_port = Config.SMTP_PORT
            self.sender_email = Config.SENDER_EMAIL
            self.sender_name = Config.SENDER_NAME
            self.app_password = Config.APP_PASSWORD
            self.config_valid = True
        except ValueError as e:
            print(f"⚠️  Email configuration not complete: {e}")
            self.config_valid = False
            self.config_error = str(e)
    
    def send_email_with_pdf(self, pdf_path: str, 
                           recipients: List[str],
                           subject: str = None,
                           body: str = None,
                           additional_attachments: List[str] = None) -> bool:
        """
        Send an email with PDF attachment.
        
        Args:
            pdf_path (str): Path to the PDF file to attach
            recipients (List[str]): List of recipient email addresses
            subject (str, optional): Email subject
            body (str, optional): Email body text
            additional_attachments (List[str], optional): Additional files to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Set defaults
            if subject is None:
                subject = Config.DEFAULT_EMAIL_SUBJECT
            if body is None:
                body = Config.DEFAULT_EMAIL_BODY
            
            # Create message
            msg = EmailMessage()
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg.set_content(body)
            
            # Attach main PDF
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, "rb") as f:
                    file_data = f.read()
                    file_name = Path(pdf_path).name
                    msg.add_attachment(file_data, 
                                     maintype="application", 
                                     subtype="pdf", 
                                     filename=file_name)
            
            # Attach additional files if provided
            if additional_attachments:
                for attachment_path in additional_attachments:
                    if Path(attachment_path).exists():
                        self._add_attachment(msg, attachment_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.sender_email, self.app_password)
                smtp.send_message(msg)
            
            print(f"✅ Email sent successfully to: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_simple_email(self, recipients: List[str],
                         subject: str,
                         body: str,
                         attachments: List[str] = None) -> bool:
        """
        Send a simple email without predefined templates.
        
        Args:
            recipients (List[str]): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body text
            attachments (List[str], optional): List of file paths to attach
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            msg = EmailMessage()
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg.set_content(body)
            
            # Add attachments if provided
            if attachments:
                for attachment_path in attachments:
                    if Path(attachment_path).exists():
                        self._add_attachment(msg, attachment_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.sender_email, self.app_password)
                smtp.send_message(msg)
            
            print(f"✅ Email sent successfully to: {', '.join(recipients)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def _add_attachment(self, msg: EmailMessage, file_path: str):
        """
        Add an attachment to the email message.
        
        Args:
            msg (EmailMessage): The email message object
            file_path (str): Path to the file to attach
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Warning: Attachment file not found: {file_path}")
            return
        
        with open(file_path, "rb") as f:
            file_data = f.read()
            file_name = file_path.name
            
            # Determine MIME type based on file extension
            suffix = file_path.suffix.lower()
            if suffix == '.pdf':
                msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)
            elif suffix in ['.txt', '.log']:
                msg.add_attachment(file_data, maintype="text", subtype="plain", filename=file_name)
            elif suffix in ['.jpg', '.jpeg']:
                msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=file_name)
            elif suffix == '.png':
                msg.add_attachment(file_data, maintype="image", subtype="png", filename=file_name)
            elif suffix in ['.doc', '.docx']:
                msg.add_attachment(file_data, maintype="application", subtype="msword", filename=file_name)
            else:
                # Generic attachment
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
    
    def send_meeting_summary(self, pdf_path: str,
                           recipients: List[str],
                           meeting_title: str = None,
                           meeting_date: str = None,
                           custom_message: str = None) -> bool:
        """
        Send meeting summary with customized message.
        
        Args:
            pdf_path (str): Path to the meeting summary PDF
            recipients (List[str]): List of recipient email addresses
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            custom_message (str, optional): Custom message to include
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        
        if not self.config_valid:
            print(f"❌ Email configuration incomplete: {getattr(self, 'config_error', 'Unknown error')}")
            return False
        
        # Create customized subject
        if meeting_title and meeting_date:
            subject = f"Meeting Minutes: {meeting_title} - {meeting_date}"
        elif meeting_title:
            subject = f"Meeting Minutes: {meeting_title}"
        else:
            subject = "Meeting Minutes"
        
        # Create customized body
        body = "Dear Team,\n\n"
        
        if meeting_title and meeting_date:
            body += f"Please find attached the minutes from the {meeting_title} meeting held on {meeting_date}.\n\n"
        elif meeting_title:
            body += f"Please find attached the minutes from the {meeting_title} meeting.\n\n"
        else:
            body += "Please find attached the meeting minutes.\n\n"
        
        if custom_message:
            body += f"{custom_message}\n\n"
        
        body += "Please review the action items and follow up on your respective tasks.\n\n"
        body += "Best regards,\nMeeting Assistant"
        
        return self.send_email_with_pdf(pdf_path, recipients, subject, body)
    
    def send_meeting_minutes(self, recipients: List[str],
                           pdf_file_path: str,
                           meeting_title: str = None,
                           meeting_date: str = None,
                           custom_message: str = None) -> dict:
        """
        Send meeting minutes via email.
        
        Args:
            recipients (List[str]): List of recipient email addresses
            pdf_file_path (str): Path to the meeting minutes PDF
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            custom_message (str, optional): Custom message to include
            
        Returns:
            dict: Result dictionary with success status and details
        """
        try:
            if not self.config_valid:
                return {
                    'success': False,
                    'error': f'Email configuration incomplete: {getattr(self, "config_error", "Unknown error")}',
                    'message': 'Please set up email configuration in .env file'
                }
            
            success = self.send_meeting_summary(
                pdf_path=pdf_file_path,
                recipients=recipients,
                meeting_title=meeting_title,
                meeting_date=meeting_date,
                custom_message=custom_message
            )
            
            return {
                'success': success,
                'recipients': recipients,
                'pdf_file': pdf_file_path,
                'message': f"Email sent successfully to {len(recipients)} recipients" if success else "Failed to send email"
            }
            
        except Exception as e:
            print(f"❌ Error in send_meeting_minutes: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to send email: {str(e)}"
            }

    def test_connection(self) -> bool:
        """
        Test email connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if not self.config_valid:
                print(f"❌ Email configuration incomplete: {getattr(self, 'config_error', 'Unknown error')}")
                return False
                
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.starttls()
                smtp.login(self.sender_email, self.app_password)
            print("✅ Email connection test successful")
            return True
        except Exception as e:
            print(f"❌ Email connection test failed: {e}")
            return False
