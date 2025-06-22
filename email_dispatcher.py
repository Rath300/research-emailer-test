import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import os
from datetime import datetime
import json
from data_models import EmailMatch, EmailConfig, UserProfile


class EmailDispatcher:
    def __init__(self, config: EmailConfig = None):
        self.config = config or self._load_config_from_env()
        self.sent_emails = []
        self.failed_emails = []
    
    def _load_config_from_env(self) -> EmailConfig:
        """Load email configuration from environment variables."""
        return EmailConfig(
            smtp_host=os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_username=os.getenv('SMTP_USERNAME', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            from_name=os.getenv('FROM_NAME', 'Cold Outreach AI'),
            from_email=os.getenv('FROM_EMAIL', ''),
            reply_to=os.getenv('REPLY_TO', '')
        )
    
    def _create_email_message(self, match: EmailMatch, user_profile: UserProfile) -> MIMEMultipart:
        """Create a properly formatted email message."""
        msg = MIMEMultipart()
        
        # Set headers
        msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
        msg['To'] = match.contact_email or f"team@{match.company_name.lower().replace(' ', '')}.com"
        msg['Subject'] = match.subject_line
        
        if self.config.reply_to:
            msg['Reply-To'] = self.config.reply_to
        
        # Add email body
        body = match.email_body
        
        # Replace placeholders
        contact_name = match.contact_name or "Team"
        body = body.replace("[Name]", contact_name)
        
        msg.attach(MIMEText(body, 'plain'))
        
        return msg
    
    def send_email(self, match: EmailMatch, user_profile: UserProfile) -> Dict:
        """Send a single email and return the result."""
        if not match.contact_email:
            return {
                "success": False,
                "error": "No contact email provided",
                "company": match.company_name,
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Create email message
            msg = self._create_email_message(match, user_profile)
            
            # Create SMTP connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.config.smtp_username, self.config.smtp_password)
                
                # Send email
                text = msg.as_string()
                server.sendmail(self.config.from_email, msg['To'], text)
            
            # Record successful send
            result = {
                "success": True,
                "company": match.company_name,
                "contact_email": match.contact_email,
                "subject": match.subject_line,
                "timestamp": datetime.now().isoformat(),
                "match_score": match.match_score
            }
            
            self.sent_emails.append(result)
            return result
            
        except Exception as e:
            # Record failed send
            result = {
                "success": False,
                "error": str(e),
                "company": match.company_name,
                "contact_email": match.contact_email,
                "timestamp": datetime.now().isoformat()
            }
            
            self.failed_emails.append(result)
            return result
    
    def send_batch_emails(self, matches: List[EmailMatch], user_profile: UserProfile, 
                         auto_send: bool = False) -> Dict:
        """Send emails for all matches, respecting auto_send flag."""
        results = {
            "total_matches": len(matches),
            "sent": 0,
            "failed": 0,
            "skipped": 0,
            "results": []
        }
        
        for match in matches:
            if auto_send and match.auto_send:
                # Send email
                result = self.send_email(match, user_profile)
                results["results"].append(result)
                
                if result["success"]:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
            else:
                # Skip sending, just record
                results["skipped"] += 1
                results["results"].append({
                    "success": True,
                    "skipped": True,
                    "company": match.company_name,
                    "reason": "Auto-send disabled or match not marked for auto-send"
                })
        
        return results
    
    def preview_email(self, match: EmailMatch, user_profile: UserProfile) -> Dict:
        """Preview an email without sending it."""
        msg = self._create_email_message(match, user_profile)
        
        return {
            "to": msg['To'],
            "subject": msg['Subject'],
            "body": msg.get_payload()[0].get_payload(),
            "headers": dict(msg.items())
        }
    
    def get_sending_stats(self) -> Dict:
        """Get statistics about sent and failed emails."""
        return {
            "total_sent": len(self.sent_emails),
            "total_failed": len(self.failed_emails),
            "success_rate": len(self.sent_emails) / (len(self.sent_emails) + len(self.failed_emails)) if (len(self.sent_emails) + len(self.failed_emails)) > 0 else 0,
            "last_sent": self.sent_emails[-1] if self.sent_emails else None,
            "last_failed": self.failed_emails[-1] if self.failed_emails else None
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export sending results to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_results_{timestamp}.json"
        
        results = {
            "sent_emails": self.sent_emails,
            "failed_emails": self.failed_emails,
            "stats": self.get_sending_stats(),
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        return filename
    
    def validate_config(self) -> Dict:
        """Validate email configuration."""
        errors = []
        warnings = []
        
        # Check required fields
        if not self.config.smtp_username:
            errors.append("SMTP username is required")
        
        if not self.config.smtp_password:
            errors.append("SMTP password is required")
        
        if not self.config.from_email:
            errors.append("From email is required")
        
        # Check SMTP settings
        if self.config.smtp_port not in [25, 465, 587]:
            warnings.append(f"Unusual SMTP port: {self.config.smtp_port}")
        
        # Test connection if credentials are provided
        if not errors and self.config.smtp_username and self.config.smtp_password:
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.config.smtp_username, self.config.smtp_password)
                warnings.append("SMTP connection test successful")
            except Exception as e:
                errors.append(f"SMTP connection test failed: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def create_email_queue(self, matches: List[EmailMatch], user_profile: UserProfile) -> List[Dict]:
        """Create a queue of emails ready for sending."""
        queue = []
        
        for match in matches:
            if match.auto_send:
                email_data = {
                    "match": match,
                    "user_profile": user_profile,
                    "preview": self.preview_email(match, user_profile),
                    "ready_to_send": True
                }
                queue.append(email_data)
        
        return queue
    
    def send_from_queue(self, queue: List[Dict]) -> Dict:
        """Send emails from a prepared queue."""
        results = {
            "total": len(queue),
            "sent": 0,
            "failed": 0,
            "results": []
        }
        
        for email_data in queue:
            if email_data["ready_to_send"]:
                result = self.send_email(email_data["match"], email_data["user_profile"])
                results["results"].append(result)
                
                if result["success"]:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
        
        return results 