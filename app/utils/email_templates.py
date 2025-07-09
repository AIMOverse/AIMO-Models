from jinja2 import Template

"""
Author: Jack Pan
Date: 2025-7-9
Description:
    Email templates for various email communications
"""


class EmailTemplates:
    """Email template management class"""
    
    @staticmethod
    def get_invitation_code_template() -> str:
        """Get the invitation code email template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome to AIMO - Your Invitation Code</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
        .invitation-code { background: #fff; border: 2px dashed #667eea; padding: 20px; margin: 20px 0; text-align: center; border-radius: 8px; }
        .code { font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 4px; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        .btn { display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to AIMO!</h1>
            <p>Your journey with AI begins here</p>
        </div>
        <div class="content">
            <h2>Hello there! 👋</h2>
            <p>We're excited to have you join our community! We've generated a special invitation code just for you.</p>
            
            <div class="invitation-code">
                <p><strong>Your Invitation Code:</strong></p>
                <div class="code">{{ invitation_code }}</div>
                <p><em>This code will expire in {{ expiry_minutes }} minutes</em></p>
            </div>
            
            <p>Use this code to complete your registration and start exploring the amazing world of AI with AIMO.</p>
            
            <p><strong>What's next?</strong></p>
            <ul>
                <li>Copy your invitation code above</li>
                <li>Return to the AIMO application</li>
                <li>Enter your code to complete the login process</li>
                <li>Start your AI journey!</li>
            </ul>
            
            <p>If you didn't request this invitation code, you can safely ignore this email.</p>
            
            <div class="footer">
                <p>Best regards,<br>The AIMO Team</p>
                <p><em>Empowering the future with AI</em></p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def render_invitation_email(invitation_code: str, expiry_minutes: int = 30) -> str:
        """Render the invitation code email with dynamic content"""
        template = Template(EmailTemplates.get_invitation_code_template())
        return template.render(
            invitation_code=invitation_code,
            expiry_minutes=expiry_minutes
        )
    
    @staticmethod
    def get_plain_text_template() -> str:
        """Get plain text version of the email"""
        return """
Welcome to AIMO! 🎉

Hello there! 👋

We're excited to have you join our community! We've generated a special invitation code just for you.

Your Invitation Code: {{ invitation_code }}

This code will expire in {{ expiry_minutes }} minutes.

Use this code to complete your registration and start exploring the amazing world of AI with AIMO.

What's next?
1. Copy your invitation code above
2. Return to the AIMO application  
3. Enter your code to complete the login process
4. Start your AI journey!

If you didn't request this invitation code, you can safely ignore this email.

Best regards,
The AIMO Team
Empowering the future with AI
"""
    
    @staticmethod
    def render_plain_text_email(invitation_code: str, expiry_minutes: int = 30) -> str:
        """Render the plain text email with dynamic content"""
        template = Template(EmailTemplates.get_plain_text_template())
        return template.render(
            invitation_code=invitation_code,
            expiry_minutes=expiry_minutes
        )
