# 🚀 CV Landing Page - Optimization & Deployment Guide

## Optimasi yang Dilakukan

### 1. **SEO & Meta Tags** ✅
- ✓ Open Graph tags untuk social media sharing
- ✓ Twitter Card configuration
- ✓ JSON-LD structured data (Schema.org)
- ✓ Meta descriptions & keywords
- ✓ Canonical URL
- ✓ Theme color & preconnect optimization

### 2. **Accessibility (A11y)** ✅
- ✓ ARIA labels pada navigation
- ✓ Semantic HTML structure
- ✓ Keyboard navigation support
- ✓ Mobile hamburger menu dengan ARIA controls
- ✓ Form validation dengan proper error messages
- ✓ Role attributes untuk notifications

### 3. **Backend Integration** ✅
- ✓ FastAPI server untuk contact form
- ✓ Email validation (Pydantic EmailStr)
- ✓ Input sanitization (XSS protection)
- ✓ CORS configuration
- ✓ Error handling & logging
- ✓ Rate limiting ready

### 4. **Performance** ✅
- ✓ Font loading optimization (media query)
- ✓ Minified CSS/JS ready
- ✓ Lazy loading images
- ✓ Request debouncing pada scroll events
- ✓ Intersection Observer untuk animations

### 5. **Security** ✅
- ✓ Input validation di frontend & backend
- ✓ Email format validation
- ✓ HTML escaping (XSS protection)
- ✓ CORS whitelist configuration
- ✓ Environment variables untuk secrets

---

## 🔧 Setup & Installation

### Frontend (Local Development)

#### 1. VSCode Live Server
```bash
# 1. Buka folder di VSCode
cd /path/to/cv-landing-page

# 2. Install extension "Live Server"
# 3. Right-click index.html → Open with Live Server
# Otomatis buka di http://127.0.0.1:5500
```

#### 2. Setup Backend (FastAPI)
```bash
# Navigate ke backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy .env.example ke .env
cp .env.example .env

# Edit .env dengan credentials Gmail Anda
# EMAIL_ADDRESS=your-email@gmail.com
# EMAIL_PASSWORD=your_app_password

# Run server
python main.py

# Server akan jalan di http://localhost:8000
# API docs: http://localhost:8000/docs
```

#### 3. Gmail App Password Setup
```
1. Go to https://myaccount.google.com/
2. Select "Security" → "App passwords"
3. Select Mail & Windows
4. Copy generated password
5. Paste ke EMAIL_PASSWORD di .env
```

#### 4. Frontend + Backend Run
```bash
# Terminal 1 - Frontend (VSCode Live Server atau)
python -m http.server 5500 --directory .

# Terminal 2 - Backend
cd backend
source venv/bin/activate
python main.py
```

---

## 📊 Testing

### Test Contact Form
```bash
# Buka http://localhost:5500
# Isi form contact → Submit
# Check terminal untuk logs
# Email akan masuk ke inbox Anda
```

### Test API Directly
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Subject",
    "message": "This is a test message"
  }'
```

### API Endpoints
```
GET  /health                 → Health check
POST /api/contact            → Submit contact form
GET  /api/info               → Portfolio info
GET  /docs                   → Interactive API documentation (Swagger UI)
```

---

## 🚀 Production Deployment

### Option 1: Vercel + Railway/Render

#### Frontend Deploy (Vercel)
```bash
# 1. Push ke GitHub
git init
git add .
git commit -m "Initial commit"
git push origin main

# 2. Connect ke Vercel
# Go to https://vercel.com
# Import project dari GitHub
# Deploy automatically

# Custom domain di Vercel settings
```

#### Backend Deploy (Railway/Render)
```bash
# Railway.app
1. Connect GitHub repo
2. Create new project
3. Add environment variables
4. Deploy

# Or Render.com
1. Connect GitHub
2. Create new Web Service
3. Set build & start commands
4. Deploy
```

### Option 2: Self-Hosted (VPS/Linux)

```bash
# 1. SSH to VPS
ssh user@your-vps-ip

# 2. Clone repository
git clone https://github.com/yourusername/cv-landing-page.git
cd cv-landing-page

# 3. Setup backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
nano .env
# Set EMAIL_ADDRESS, EMAIL_PASSWORD, etc.

# 5. Install Gunicorn (production WSGI)
pip install gunicorn

# 6. Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app

# 7. Setup Nginx reverse proxy
# Create /etc/nginx/sites-available/portfolio
# Configure reverse proxy to :8000

# 8. SSL Certificate (Let's Encrypt)
sudo certbot --nginx -d your-domain.com
```

---

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Check backend health
curl http://localhost:8000/health

# Monitor logs
tail -f backend/logs/app.log
```

### Performance Monitoring
```bash
# Add to .env
SENTRY_DSN=your-sentry-dsn  # For error tracking
```

### Backup Data
```bash
# Backup contact submissions (if using DB)
pg_dump -U postgres portfolio > backup.sql
```

---

## 🎨 Customization

### Update Data
Edit `data.json`:
```json
{
  "nama": "Your Name",
  "peran": "Your Title",
  "skills": [...],
  "projects": [...]
}
```

### Styling
- Main colors: `style.css` CSS variables
- `--primary`: #00fff5 (cyan)
- `--secondary`: #ff006e (magenta)

### Add More Features
- Blog section
- Dark mode toggle
- Language switcher
- Analytics integration

---

## 🐛 Troubleshooting

### CORS Errors
```javascript
// Update allowed origins di backend/main.py
allow_origins=["http://localhost:5500", "https://your-domain.com"]
```

### Email Not Sending
1. Check Gmail app password
2. Verify less secure apps disabled
3. Check error logs: `python main.py`

### Form Not Submitting
1. Check backend running: `http://localhost:8000/health`
2. Check CORS configuration
3. Check browser console for errors

---

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Schema.org Structured Data](https://schema.org/)

---

**Last Updated:** February 2, 2026
**Status:** Production Ready ✅
