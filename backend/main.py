"""
FastAPI Backend untuk CV Landing Page
Handles contact form submissions dengan validation dan email integration via Resend API
"""

from fastapi import FastAPI, HTTPException, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from dotenv import load_dotenv
import logging
import os
import secrets
import httpx
import json
from pathlib import Path
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CV Landing Page API",
    description="API untuk contact form dan portfolio management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(
    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
    content={"detail": "Rate limit exceeded. Please try again later."}
))

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
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


# Resend configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
TO_EMAIL = os.getenv("TO_EMAIL")

# Admin configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
KUPAS_ADMIN_URL = os.getenv("KUPAS_ADMIN_URL", "http://localhost:8001")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    logger.warning("⚠️ SUPABASE_URL or SUPABASE_KEY is missing!")

def get_supabase():
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    return supabase

def load_cv_data() -> dict:
    """Load CV data from Supabase"""
    try:
        if not supabase:
            return {}
            
        profile_res = supabase.table('profile').select('*').eq('id', 1).execute()
        skills_res = supabase.table('skills').select('*').execute()
        projects_res = supabase.table('projects').select('*').execute()
        
        if not profile_res.data:
            return {}
            
        profile = profile_res.data[0]
        return {
            "nama": profile.get("nama", ""),
            "panggilan": profile.get("panggilan", ""),
            "peran": profile.get("peran", ""),
            "bio": profile.get("bio", ""),
            "about": profile.get("about", ""),
            "kontak": profile.get("kontak", {}),
            "skills": skills_res.data,
            "projects": projects_res.data
        }
    except Exception as e:
        logger.error(f"Error loading data from Supabase: {str(e)}")
        return {}


def send_email(contact_data: ContactFormRequest) -> bool:
    """Send email notification using Resend API"""
    if not RESEND_API_KEY:
        logger.error("❌ RESEND_API_KEY is not set")
        return False
    if not TO_EMAIL:
        logger.error("❌ TO_EMAIL is not set")
        return False

    subject = f"New Contact Form: {contact_data.subject}"
    text = f"""
Name: {contact_data.name}
Email: {contact_data.email}
Subject: {contact_data.subject}

Message:
{contact_data.message}
"""

    html = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; background: #f9f9f9; padding: 20px; border-radius: 8px;">
      <h2 style="color: #00fff5; border-bottom: 2px solid #ff006e; padding-bottom: 10px;">New Contact Form Submission</h2>

      <table style="width: 100%; margin: 20px 0;">
        <tr style="background: #f0f0f0;">
          <td style="padding: 10px; font-weight: bold; width: 20%;">Name:</td>
          <td style="padding: 10px;">{contact_data.name}</td>
        </tr>
        <tr>
          <td style="padding: 10px; font-weight: bold;">Email:</td>
          <td style="padding: 10px;"><a href="mailto:{contact_data.email}" style="color: #00fff5;">{contact_data.email}</a></td>
        </tr>
        <tr style="background: #f0f0f0;">
          <td style="padding: 10px; font-weight: bold;">Subject:</td>
          <td style="padding: 10px;">{contact_data.subject}</td>
        </tr>
      </table>

      <h3 style="color: #ff006e;">Message:</h3>
      <div style="background: white; padding: 15px; border-left: 4px solid #00fff5; margin: 20px 0;">
        <p style="white-space: pre-wrap; line-height: 1.6;">{contact_data.message}</p>
      </div>

      <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
      <p style="color: #999; font-size: 12px;">
        Submitted at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
        From IP: Check server logs
      </p>
    </div>
  </body>
</html>
"""

    payload = {
        "from": FROM_EMAIL,
        "to": [TO_EMAIL],
        "subject": subject,
        "text": text,
        "html": html,
        "reply_to": contact_data.email
    }

    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=15
        )

        if 200 <= response.status_code < 300:
            logger.info(f"✅ Email sent successfully from {contact_data.email}")
            return True

        logger.error(f"❌ Resend error {response.status_code}: {response.text}")
        return False

    except Exception as e:
        logger.error(f"❌ Failed to send email: {str(e)}")
        return False


# Routes
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    logger.info("Health check called")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.post("/api/contact", response_model=ContactResponse, tags=["Contact"])
@limiter.limit("5/minute")
async def submit_contact_form(request: Request, contact_data: ContactFormRequest) -> ContactResponse:
    """
    Submit contact form dengan validation dan email notification

    Rate Limit: 5 requests per minute
    """
    try:
        logger.info(f"📧 New contact form submission from {contact_data.email}")

        # Send email
        email_sent = send_email(contact_data)

        if email_sent:
            logger.info(f"✅ Form processed successfully for {contact_data.email}")
            return ContactResponse(
                success=True,
                message="Pesan Anda telah berhasil dikirim! Saya akan menghubungi Anda segera.",
                timestamp=datetime.now().isoformat()
            )

        logger.warning("Email notification failed but form was validated")
        return ContactResponse(
            success=True,
            message="Pesan Anda telah diterima. Saya akan menghubungi Anda dalam waktu singkat.",
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


# Admin Models
class CVBasicInfo(BaseModel):
    nama: str
    panggilan: str
    peran: str
    bio: str
    about: str


class CVSkill(BaseModel):
    icon: str
    name: str
    description: str
    level: int


class CVProject(BaseModel):
    icon: str
    title: str
    description: str
    tags: list
    status: str
    link: str


# Admin Endpoints
@app.post("/api/admin/auth", tags=["Admin"])
async def admin_auth(credentials: HTTPBasicCredentials = Depends(verify_admin)):
    """Authenticate admin via HTTP Basic Auth"""
    logger.info("✅ Admin authenticated")
    return {"authenticated": True, "message": "Authentication successful"}


@app.get("/api/admin/cv", tags=["Admin"])
async def get_cv_data():
    """Get CV data for editing"""
    data = load_cv_data()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV data not found"
        )
    return data


@app.put("/api/admin/cv/basic", tags=["Admin"])
async def update_cv_basic(
    info: CVBasicInfo,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Update CV basic information"""
    db = get_supabase()
    try:
        db.table('profile').update({
            "nama": info.nama,
            "panggilan": info.panggilan,
            "peran": info.peran,
            "bio": info.bio,
            "about": info.about
        }).eq('id', 1).execute()
        return {"success": True, "message": "CV basic info updated"}
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


@app.put("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def update_cv_skill(
    skill_name: str,
    skill: CVSkill,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Update CV skill or add if not exists"""
    db = get_supabase()
    try:
        # Check if exists
        existing = db.table('skills').select('*').eq('name', skill_name).execute()
        data_to_save = {
            "icon": skill.icon,
            "name": skill.name,
            "description": skill.description,
            "level": skill.level
        }
        if existing.data:
            db.table('skills').update(data_to_save).eq('name', skill_name).execute()
        else:
            db.table('skills').insert(data_to_save).execute()
            
        return {"success": True, "message": f"Skill '{skill_name}' updated"}
    except Exception as e:
        logger.error(f"Failed to update skill: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


@app.delete("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def delete_cv_skill(
    skill_name: str,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Delete CV skill"""
    db = get_supabase()
    try:
        db.table('skills').delete().eq('name', skill_name).execute()
        return {"success": True, "message": f"Skill '{skill_name}' deleted"}
    except Exception as e:
        logger.error(f"Failed to delete skill: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


@app.post("/api/admin/cv/project", tags=["Admin"])
async def add_cv_project(
    project: CVProject,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Add new CV project"""
    db = get_supabase()
    try:
        data_to_save = {
            "icon": project.icon,
            "title": project.title,
            "description": project.description,
            "tags": project.tags,
            "status": project.status,
            "link": project.link
        }
        db.table('projects').insert(data_to_save).execute()
        return {"success": True, "message": "Project added", "project": project.dict()}
    except Exception as e:
        logger.error(f"Failed to add project: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


@app.put("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def update_cv_project(
    project_title: str,
    project: CVProject,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Update CV project"""
    db = get_supabase()
    try:
        data_to_save = {
            "icon": project.icon,
            "title": project.title,
            "description": project.description,
            "tags": project.tags,
            "status": project.status,
            "link": project.link
        }
        db.table('projects').update(data_to_save).eq('title', project_title).execute()
        return {"success": True, "message": f"Project '{project_title}' updated"}
    except Exception as e:
        logger.error(f"Failed to update project: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


@app.delete("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def delete_cv_project(
    project_title: str,
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    """Delete CV project"""
    db = get_supabase()
    try:
        db.table('projects').delete().eq('title', project_title).execute()
        return {"success": True, "message": f"Project '{project_title}' deleted"}
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save data")


# Kupas Proxy Endpoint
@app.get("/api/kupas/stats", tags=["Kupas"])
async def get_kupas_stats(request: Request):
    """Proxy endpoint to fetch stats from Kupas admin service"""
    headers = {}
    auth_header = request.headers.get("Authorization")
    if auth_header:
        headers["Authorization"] = auth_header

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{KUPAS_ADMIN_URL}/stats",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Kupas service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error connecting to Kupas service: {str(e)}"
            )


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
