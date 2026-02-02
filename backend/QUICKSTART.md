# 🚀 Backend Setup Quick Reference

## File Structure
```
backend/
├── main.py              # FastAPI application server
├── requirements.txt     # Python dependencies (pip install -r)
├── .env                 # Environment configuration (UPDATE THIS!)
├── .env.example         # Template for .env
├── API-DOCS.md          # Full API documentation
├── test_api.sh          # Automated test suite
├── server.log           # Server logs (production)
└── venv/                # Python virtual environment
```

## Start Server
```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
python main.py
```

## Test Server
```bash
cd backend
./test_api.sh
```

## API Endpoints (Running at http://localhost:8000)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/api/info` | Portfolio info |
| GET | `/api/stats` | API statistics |
| POST | `/api/contact` | Submit contact form |
| GET | `/docs` | Swagger UI documentation |

## Configuration (.env)
```bash
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your_app_password  # Get from Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FRONTEND_URL=http://localhost:5500  # Development
```

## Features
✅ Contact form with validation  
✅ Email notifications via Gmail  
✅ Rate limiting (5 req/min)  
✅ CORS enabled  
✅ Comprehensive logging  
✅ Error handling  

## Test Contact Form
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Name",
    "email": "your@email.com",
    "subject": "Subject",
    "message": "Your message here (min 10 chars)"
  }'
```

## See Full Docs
👉 [API-DOCS.md](./API-DOCS.md) - Complete documentation
👉 http://localhost:8000/docs - Interactive Swagger UI (when running)
