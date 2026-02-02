"""
FastAPI Backend untuk CV Landing Page
Handles contact form submissions dengan validation dan email integration via Resend API
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
from dotenv import load_dotenv
import logging
import os
import requests
import json
from pathlib import Path
import json
from pathlib import Path

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
allowed_origins = os.getenv("FRONTEND_URL", "http://localhost:5500,http://localhost:8080").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
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


class AdminAuthRequest(BaseModel):
    password: str


# Admin Models
class CVBasicInfo(BaseModel):
    nama: str
    panggilan: str
    peran: str
    bio: str


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


# Resend configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "onboarding@resend.dev")
TO_EMAIL = os.getenv("TO_EMAIL")

# Admin configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
DATA_FILE = Path(__file__).parent.parent / "data.json"


def load_cv_data() -> dict:
    """Load CV data from JSON file"""
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
    return {}


def save_cv_data(data: dict) -> bool:
    """Save CV data to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("✅ CV data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving data: {str(e)}")
        return False


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
class AdminAuthRequest(BaseModel):
    password: str


class CVBasicInfo(BaseModel):
    nama: str
    panggilan: str
    peran: str
    bio: str


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


# Admin Configuration
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
DATA_FILE = Path(__file__).parent.parent / "data.json"


def load_cv_data() -> dict:
    """Load CV data from JSON file"""
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
    return {}


def save_cv_data(data: dict) -> bool:
    """Save CV data to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("✅ CV data saved successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error saving data: {str(e)}")
        return False


# Admin Endpoints
@app.post("/api/admin/auth", tags=["Admin"])
async def admin_auth(auth: AdminAuthRequest):
    """Authenticate admin"""
    if auth.password == ADMIN_PASSWORD:
        logger.info("✅ Admin authenticated")
        return {"authenticated": True, "message": "Authentication successful"}
    
    logger.warning("❌ Invalid admin password attempt")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )


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
async def update_cv_basic(auth: AdminAuthRequest, info: CVBasicInfo):
    """Update CV basic information"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["nama"] = info.nama
    data["panggilan"] = info.panggilan
    data["peran"] = info.peran
    data["bio"] = info.bio
    
    if save_cv_data(data):
        return {"success": True, "message": "CV basic info updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.put("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def update_cv_skill(auth: AdminAuthRequest, skill_name: str, skill: CVSkill):
    """Update CV skill"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    skills = data.get("skills", [])
    
    updated = False
    for s in skills:
        if s["name"] == skill_name:
            s.update(skill.dict())
            updated = True
            break
    
    if not updated:
        skills.append(skill.dict())
    
    data["skills"] = skills
    
    if save_cv_data(data):
        return {"success": True, "message": f"Skill '{skill_name}' updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.delete("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def delete_cv_skill(auth: AdminAuthRequest, skill_name: str):
    """Delete CV skill"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["skills"] = [s for s in data.get("skills", []) if s["name"] != skill_name]
    
    if save_cv_data(data):
        return {"success": True, "message": f"Skill '{skill_name}' deleted"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.post("/api/admin/cv/project", tags=["Admin"])
async def add_cv_project(auth: AdminAuthRequest, project: CVProject):
    """Add new CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    projects = data.get("projects", [])
    projects.append(project.dict())
    data["projects"] = projects
    
    if save_cv_data(data):
        return {"success": True, "message": "Project added", "project": project.dict()}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.put("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def update_cv_project(auth: AdminAuthRequest, project_title: str, project: CVProject):
    """Update CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    projects = data.get("projects", [])
    
    updated = False
    for p in projects:
        if p["title"] == project_title:
            p.update(project.dict())
            updated = True
            break
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_title}' not found"
        )
    
    data["projects"] = projects
    
    if save_cv_data(data):
        return {"success": True, "message": f"Project '{project_title}' updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.delete("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def delete_cv_project(auth: AdminAuthRequest, project_title: str):
    """Delete CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["projects"] = [p for p in data.get("projects", []) if p["title"] != project_title]
    
    if save_cv_data(data):
        return {"success": True, "message": f"Project '{project_title}' deleted"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


# Admin endpoints
@app.post("/api/admin/auth", tags=["Admin"])
async def admin_auth(auth: AdminAuthRequest):
    """Authenticate admin"""
    if auth.password == ADMIN_PASSWORD:
        logger.info("✅ Admin authenticated")
        return {"authenticated": True, "message": "Authentication successful"}
    
    logger.warning("❌ Invalid admin password attempt")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )


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
async def update_cv_basic(auth: AdminAuthRequest, info: CVBasicInfo):
    """Update CV basic information"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["nama"] = info.nama
    data["panggilan"] = info.panggilan
    data["peran"] = info.peran
    data["bio"] = info.bio
    
    if save_cv_data(data):
        return {"success": True, "message": "CV basic info updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.put("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def update_cv_skill(auth: AdminAuthRequest, skill_name: str, skill: CVSkill):
    """Update CV skill"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    skills = data.get("skills", [])
    
    # Update existing skill or add new
    updated = False
    for s in skills:
        if s["name"] == skill_name:
            s.update(skill.dict())
            updated = True
            break
    
    if not updated:
        skills.append(skill.dict())
    
    data["skills"] = skills
    
    if save_cv_data(data):
        return {"success": True, "message": f"Skill '{skill_name}' updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.delete("/api/admin/cv/skill/{skill_name}", tags=["Admin"])
async def delete_cv_skill(auth: AdminAuthRequest, skill_name: str):
    """Delete CV skill"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["skills"] = [s for s in data.get("skills", []) if s["name"] != skill_name]
    
    if save_cv_data(data):
        return {"success": True, "message": f"Skill '{skill_name}' deleted"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.post("/api/admin/cv/project", tags=["Admin"])
async def add_cv_project(auth: AdminAuthRequest, project: CVProject):
    """Add new CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    projects = data.get("projects", [])
    projects.append(project.dict())
    data["projects"] = projects
    
    if save_cv_data(data):
        return {"success": True, "message": "Project added", "project": project.dict()}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.put("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def update_cv_project(auth: AdminAuthRequest, project_title: str, project: CVProject):
    """Update CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    projects = data.get("projects", [])
    
    updated = False
    for p in projects:
        if p["title"] == project_title:
            p.update(project.dict())
            updated = True
            break
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_title}' not found"
        )
    
    data["projects"] = projects
    
    if save_cv_data(data):
        return {"success": True, "message": f"Project '{project_title}' updated"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
    )


@app.delete("/api/admin/cv/project/{project_title}", tags=["Admin"])
async def delete_cv_project(auth: AdminAuthRequest, project_title: str):
    """Delete CV project"""
    if auth.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    data = load_cv_data()
    data["projects"] = [p for p in data.get("projects", []) if p["title"] != project_title]
    
    if save_cv_data(data):
        return {"success": True, "message": f"Project '{project_title}' deleted"}
    
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to save data"
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
