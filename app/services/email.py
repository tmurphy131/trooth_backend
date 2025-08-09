import os
import logging
from typing import Dict, Optional, Tuple
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, From, Subject, HtmlContent, PlainTextContent
from datetime import datetime

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logging.warning("Jinja2 not available, using simple templates")

from app.core.settings import settings

logger = logging.getLogger("app.email")

def strftime_filter(value, format='%Y'):
    """Custom Jinja2 filter for strftime formatting."""
    if isinstance(value, str) and value == 'now':
        return datetime.now().strftime(format)
    return value

def get_email_template_env():
    """Get Jinja2 environment for email templates."""
    if not JINJA2_AVAILABLE:
        return None
    
    template_dir = os.path.join(os.path.dirname(__file__), '../templates/email')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['html', 'xml'])
    )
    # Add custom filters
    env.filters['strftime'] = strftime_filter
    return env

def get_sendgrid_client():
    """Get SendGrid client if configured."""
    api_key = os.getenv("SENDGRID_API_KEY")
    if not api_key or api_key.startswith("your_"):
        logger.warning("SendGrid API key not configured")
        return None
    return SendGridAPIClient(api_key)

def render_assessment_completion_email(mentor_name: str, apprentice_name: str, 
                                     scores: dict, recommendations: dict) -> Tuple[str, str]:
    """Render rich HTML email for assessment completion."""
    env = get_email_template_env()
    
    if env and JINJA2_AVAILABLE:
        try:
            template = env.get_template('assessment_complete.html')
            html_content = template.render(
                mentor_name=mentor_name,
                apprentice_name=apprentice_name,
                overall_score=scores.get('overall_score', 7.0),
                category_scores=scores.get('category_scores', {}),
                recommendations=recommendations,
                app_url=settings.app_url
            )
            
            # Generate plain text version
            plain_text = f"""
Assessment Complete - T[root]H

Dear {mentor_name},

{apprentice_name} has completed their spiritual assessment.

Overall Score: {scores.get('overall_score', 7.0)}/10

{recommendations.get('summary_recommendation', 'Continue growing in spiritual disciplines.')}

View full results: {settings.app_url}

Best regards,
T[root]H Assessment Team
            """.strip()
            
            return html_content, plain_text
            
        except Exception as e:
            logger.error(f"Failed to render assessment email template: {e}")
    
    # Fallback to simple text
    plain_text = f"""
Assessment Complete

Dear {mentor_name},

{apprentice_name} has completed their spiritual assessment with an overall score of {scores.get('overall_score', 7.0)}/10.

{recommendations.get('summary_recommendation', 'Continue growing in spiritual disciplines.')}

View full results at: {settings.app_url}

Best regards,
T[root]H Assessment Team
    """
    return plain_text, plain_text

def render_invitation_email(apprentice_name: str, mentor_name: str, token: str) -> Tuple[str, str]:
    """Render rich HTML email for apprentice invitation."""
    env = get_email_template_env()
    
    if env and JINJA2_AVAILABLE:
        try:
            template = env.get_template('invitation.html')
            html_content = template.render(
                apprentice_name=apprentice_name,
                mentor_name=mentor_name,
                token=token,
                app_url=settings.app_url
            )
            
            # Generate plain text version
            plain_text = f"""
You're Invited to Begin Your Spiritual Journey - T[root]H

Dear {apprentice_name},

{mentor_name} has invited you to begin a structured assessment and mentoring relationship through the T[root]H platform.

What is T[root]H Assessment?
T[root]H is a comprehensive spiritual assessment tool designed to help you and your mentor understand your current spiritual growth and identify areas for development.

Accept your invitation here: {settings.app_url}/accept-invitation?token={token}

This invitation will expire in 7 days.

Best regards,
T[root]H Assessment Team
            """.strip()
            
            return html_content, plain_text
            
        except Exception as e:
            logger.error(f"Failed to render invitation email template: {e}")
    
    # Fallback to simple text
    plain_text = f"""
Invitation to T[root]H Assessment

Dear {apprentice_name},

{mentor_name} has invited you to join the T[root]H assessment platform.

Accept your invitation: {settings.app_url}/accept-invitation?token={token}

Best regards,
T[root]H Assessment Team
    """
    return plain_text, plain_text

def send_email(to_email: str, subject: str, html_content: str, 
               plain_content: str, from_email: str = None) -> bool:
    """Send email using SendGrid."""
    client = get_sendgrid_client()
    
    if not client:
        logger.warning(f"Email not sent - SendGrid not configured. Would send to {to_email}: {subject}")
        return False
    
    try:
        from_email = from_email or settings.email_from_address
        
        message = Mail(
            from_email=From(from_email, "T[root]H Assessment"),
            to_emails=To(to_email),
            subject=Subject(subject),
            html_content=HtmlContent(html_content),
            plain_text_content=PlainTextContent(plain_content)
        )
        
        response = client.send(message)
        
        if response.status_code in [200, 202]:
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email to {to_email}: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_assessment_email(to_email: str, mentor_name: str, apprentice_name: str, 
                         scores: dict, recommendations: dict) -> bool:
    """Send assessment completion email with rich formatting."""
    html_content, plain_content = render_assessment_completion_email(
        mentor_name, apprentice_name, scores, recommendations
    )
    
    subject = f"Assessment Complete: {apprentice_name}'s Spiritual Growth Report"
    
    return send_email(to_email, subject, html_content, plain_content)

def send_invitation_email(to_email: str, apprentice_name: str, token: str, 
                         mentor_name: str = "Your Mentor") -> bool:
    """Send apprentice invitation email with rich formatting."""
    html_content, plain_content = render_invitation_email(
        apprentice_name, mentor_name, token
    )
    
    subject = f"You're Invited to Begin Your Spiritual Journey with {mentor_name}"
    
    return send_email(to_email, subject, html_content, plain_content)

def send_notification_email(to_email: str, subject: str, message: str, 
                           action_url: str = None) -> bool:
    """Send a general notification email."""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #007bff;">T[root]H Assessment</h2>
        <p>{message}</p>
        {f'<p><a href="{action_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Take Action</a></p>' if action_url else ''}
        <p style="color: #666; font-size: 14px;">Best regards,<br>T[root]H Assessment Team</p>
    </div>
    """
    
    plain_content = f"""
T[root]H Assessment

{message}

{f'Take action: {action_url}' if action_url else ''}

Best regards,
T[root]H Assessment Team
    """
    
    return send_email(to_email, subject, html_content, plain_content)