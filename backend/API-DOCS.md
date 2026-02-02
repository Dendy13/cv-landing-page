# Backend API Documentation

## Overview

FastAPI server untuk CV Landing Page. Handles:
- ✅ Contact form submissions dengan validation
- ✅ Email notifications (Gmail SMTP)
- ✅ Rate limiting (5 requests/minute)
- ✅ CORS configuration
- ✅ Request logging & error handling

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Email (Optional)
Edit `.env`:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your_app_password
```

**Get Gmail App Password:**
1. Go to https://myaccount.google.com/
2. Select "Security" → "App passwords"
3. Select "Mail & Windows"
4. Copy the generated 16-character password
5. Paste into `EMAIL_PASSWORD` in `.env`

### 3. Run Server
```bash
python main.py
# Server runs at http://localhost:8000
```

### 4. Test API
```bash
# Run test suite
./test_api.sh

# Or manually test
curl http://localhost:8000/health
```

---

## 📚 API Endpoints

### Health Check
```
GET /health
```

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-02-02T07:47:44.581017",
  "version": "1.0.0"
}
```

---

### Get Portfolio Info
```
GET /api/info
```

**Response (200):**
```json
{
  "name": "Dendy Fajar Kurniawan",
  "title": "Python Developer & Data Scraper",
  "email": "dendyfajark@gmail.com",
  "github": "https://github.com/Dendy13",
  "linkedin": "https://linkedin.com/"
}
```

---

### Get API Statistics
```
GET /api/stats
```

**Response (200):**
```json
{
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
```

---

### Submit Contact Form
```
POST /api/contact
```

**Rate Limit:** 5 requests per minute per IP

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Collaboration Request",
  "message": "I would like to work with you on a project..."
}
```

**Validation Rules:**
- `name`: 2-100 characters
- `email`: Valid email format
- `subject`: 3-200 characters
- `message`: 10-5000 characters

**Response Success (200):**
```json
{
  "success": true,
  "message": "Pesan Anda telah berhasil dikirim! Saya akan menghubungi Anda segera.",
  "timestamp": "2026-02-02T07:48:08.275276"
}
```

**Response Validation Error (422):**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "input": "invalid-email"
    }
  ]
}
```

**Response Rate Limited (429):**
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Response Server Error (500):**
```json
{
  "detail": "Terjadi kesalahan saat memproses request. Silakan coba lagi nanti."
}
```

---

## 🔄 CORS Configuration

**Allowed Origins:**
- `http://localhost:5500` (Development)
- `https://dendyfajar.com` (Production - update in .env)

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:** All

---

## 📊 Testing

### Run Full Test Suite
```bash
./test_api.sh
```

### Manual Tests

**Test Health:**
```bash
curl http://localhost:8000/health
```

**Test Contact Form:**
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test",
    "message": "This is a test message for validation"
  }'
```

**Test Validation:**
```bash
# Invalid email
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "email": "not-an-email",
    "subject": "Test",
    "message": "This is a test message"
  }'
```

**Test Rate Limiting:**
```bash
# Make 6 requests rapid-fire, 6th should fail
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/contact \
    -H "Content-Type: application/json" \
    -d '{"name":"Test","email":"test@example.com","subject":"Test","message":"This is a test message"}'
  echo ""
done
```

---

## 🔐 Security Features

### Input Validation
- ✅ Email format validation
- ✅ String length checks
- ✅ XSS protection (HTML escaping)
- ✅ Rate limiting per IP

### CORS
- ✅ Whitelist allowed origins
- ✅ Preflight request handling
- ✅ Credentials support

### Error Handling
- ✅ Detailed validation messages
- ✅ Generic error responses (no stack traces in production)
- ✅ Request logging

---

## 📝 Logging

Server logs to console. Key events logged:
- Server startup
- Incoming requests
- Email sending status
- Errors & validation failures
- Rate limit hits

### View Logs (Background Process)
```bash
cd backend
tail -f server.log
```

---

## 🚢 Production Deployment

### Environment Setup
```bash
# .env for production
ENVIRONMENT=production
DEBUG=False
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FRONTEND_URL=https://your-domain.com
API_URL=https://api.your-domain.com
```

### Deploy Options

#### 1. Railway.app
```bash
# Connect GitHub repo to Railway
# Add environment variables
# Deploy automatically
```

#### 2. Render.com
```bash
# Create new Web Service
# Set Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
# Add environment variables
```

#### 3. Self-Hosted (VPS)
```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# Setup Nginx reverse proxy
# Configure SSL with Let's Encrypt
```

---

## 📋 Dependencies

See `requirements.txt`:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation
- **slowapi**: Rate limiting
- **python-dotenv**: Environment variables
- **python-multipart**: Form data parsing

---

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Email Not Sending
- Verify EMAIL_ADDRESS & EMAIL_PASSWORD in .env
- Check Gmail App Password is correct (16 chars)
- Verify less secure apps is disabled
- Check server logs for errors

### CORS Errors
- Verify FRONTEND_URL in .env
- Check allowed_origins configuration
- Ensure browser CORS request headers match

### Rate Limit Too Strict
Edit `main.py`:
```python
@app.post("/api/contact")
@limiter.limit("10/minute")  # Change from 5 to 10
```

---

## 📞 Support

For issues or questions:
- Check logs: `tail -f server.log`
- Review test results: `./test_api.sh`
- Check API docs: http://localhost:8000/docs

---

**Version:** 1.0.0  
**Last Updated:** February 2, 2026  
**Status:** Production Ready ✅
