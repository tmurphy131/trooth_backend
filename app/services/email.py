import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_assessment_email(to_email: str, apprentice_name: str, assessment_title: str, score: int, feedback_summary: str, details: dict):
    subject = f"Assessment Results for {apprentice_name}: {assessment_title}"
    feedback_html = "".join([
        f"<h4>{section}</h4><p><strong>Score:</strong> {data['score']}<br><strong>Feedback:</strong> {data['feedback']}<br><strong>Recommendation:</strong> {data['recommendation']}</p>"
        for section, data in details.items()
    ])

    html_content = f"""
        <p>Hi Mentor,</p>
        <p>{apprentice_name} has completed the <strong>{assessment_title}</strong> assessment.</p>
        <p><strong>Overall Score:</strong> {score}</p>
        <p><strong>Summary:</strong> {feedback_summary}</p>
        <hr>
        {feedback_html}
        <p>Keep guiding them forward in their discipleship journey.</p>
    """

    message = Mail(
        from_email=os.getenv("EMAIL_FROM_ADDRESS"),
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print("SendGrid error:", e)
        return None

def send_invitation_email(to_email: str, apprentice_name: str, token: str):
    link = f"https://trooth-app.com/accept-invite/{token}"
    subject = "You're invited to join T[root]H as an apprentice"
    body = f"""
    Hello {apprentice_name},

    You've been invited to join the T[root]H app as an apprentice.

    Click the link below to sign up and accept your invitation:
    {link}

    This invitation will expire in 7 days.

    Grace and peace,  
    The T[root]H Team
    """

    message = Mail(
        from_email="your-email@example.com",  # Set your verified sender
        to_emails=to_email,
        subject=subject,
        plain_text_content=body,
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
    except Exception as e:
        print(f"Failed to send invite email: {e}")