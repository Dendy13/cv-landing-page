"""
FastAPI Backend untuk CV Landing Page
Handles contact form submissions dengan validation dan email integration
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        logger.error(f"❌ Error in contact form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat memproses request. Silakan coba lagi nanti."
        )

@app.get("/api/info", tags=["Info"])
async def get_portfolio_info():
    """Get portfolio information"""
    logger.info("Portfolio info requested")
    return {
        "name": "Dendy Fajar Kurniawan",
        "title": "Python Developer & Data Scraper",
        "email": "dendyfajark@gmail.com",
        "github": "https://github.com/Dendy13",
        "linkedin": "https://linkedin.com/"
    }

@app.get("/api/stats", tags=["Stats"])
async def get_api_stats():
    """Get API statistics"""
    return {
        "status": "operational",
        "uptime": "24/7",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "contact": "/api/contact (POST)",
            "info": "/api/info",
            "docs": "/docs"
        }
    }

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"status": "ok"}

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

# Pydantic Models
class ContactFormRequest(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    
    @field_validator('name')
    @classmethod
    def name_validation(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        if len(v) > 100:
            raise ValueError('Name must not exceed 100 characters')
        return v.strip()
    
    @field_validator('subject')
    @classmethod
    def subject_validation(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('Subject must be at least 3 characters')
        if len(v) > 200:
            raise ValueError('Subject must not exceed 200 characters')
        return v.strip()
    
    @field_validator('message')
    @classmethod
    def message_validation(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Message must be at least 10 characters')
        if len(v) > 5000:
            raise ValueError('Message must not exceed 5000 characters')
        return v.strip()

class ContactResponse(BaseModel):
    success: bool
    message: str
    timestamp: str

# Email configuration
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "dendyfajark@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

def send_email(contact_data: ContactFormRequest) -> bool:
    """Send email notification untuk contact form submission"""
    try:
        # Create email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"New Contact Form: {contact_data.subject}"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Reply-To"] = contact_data.email
        
        # Plain text version
        text = f"""
Name: {contact_data.name}
Email: {contact_data.email}
Subject: {contact_data.subject}

Message:
{contact_data.message}
"""
        
        # HTML version
        html = f"""
<html>
  <body>
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> {contact_data.name}</p>
    <p><strong>Email:</strong> <a href="mailto:{contact_data.email}">{contact_data.email}</a></p>
    <p><strong>Subject:</strong> {contact_data.subject}</p>
    <hr>
    <h3>Message:</h3>
    <p>{contact_data.message.replace(chr(10), '<br>')}</p>
    <hr>
    <p style="color: gray; font-size: 12px;">
        Submitted at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </p>
  </body>
</html>
"""
        
        # Attach parts
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully from {contact_data.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

# Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/contact", response_model=ContactResponse, tags=["Contact"])
async def submit_contact_form(contact_data: ContactFormRequest) -> ContactResponse:
    """
    Submit contact form dengan validation dan email notification
    
    Args:
        contact_data: Contact form data
        
    Returns:
        ContactResponse dengan status dan message
    """
    try:
        # Send email
        email_sent = send_email(contact_data)
        
        if email_sent:
            return ContactResponse(
                success=True,
                message="Your message has been sent successfully! I'll get back to you soon.",
                timestamp=datetime.now().isoformat()
            )
        else:
            logger.warning("Email notification failed but form was validated")
            return ContactResponse(
                success=True,
                message="Your message has been received. I'll contact you shortly.",
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        logger.error(f"Error in contact form: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request. Please try again later."
        )

@app.get("/api/info", tags=["Info"])
async def get_portfolio_info():
    """Get portfolio information"""
    return {
        "name": "Dendy Fajar Kurniawan",
        "title": "Python Developer & Data Scraper",
        "email": "dendyfajark@gmail.com",
        "github": "https://github.com/Dendy13",
        "linkedin": "https://linkedin.com/"
    }

@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"status": "ok"}

# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
