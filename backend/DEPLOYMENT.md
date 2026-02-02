# Backend Deployment Guide

## Current Status ✅

- **Server Status**: Running & Healthy
- **API Version**: 1.0.0
- **Port**: 8000 (localhost)
- **Features**: Contact form, Email notifications, Rate limiting, CORS

---

## 🔧 Development Setup (Local)

### Already Completed ✅
```
✅ Python environment created (venv)
✅ Dependencies installed (requirements.txt)
✅ Server running on http://localhost:8000
✅ All tests passing
```

### To Start Server
```bash
cd backend
source venv/bin/activate
python main.py
```

Server will be available at: **http://localhost:8000**

---

## 🌍 Production Deployment

### Option 1: Railway (Recommended for Beginners)

**Setup:**
1. Push code to GitHub
2. Go to https://railway.app
3. Connect GitHub account
4. Create new project → Select repository
5. Set variables in Railway UI (EMAIL_ADDRESS, EMAIL_PASSWORD, etc.)
6. Deploy automatically

**Result:**
- API at: `https://<project>.railway.app`
- Auto-scaling & SSL included
- Easy monitoring & logs

---

### Option 2: Render.com

**Setup:**
1. Push code to GitHub
2. Go to https://render.com
3. Create "Web Service" → Connect GitHub
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy

**Result:**
- API at: `https://<service>.onrender.com`
- Free tier available (with sleep)
- Easy environment management

---

### Option 3: Heroku (Legacy)

**Setup:**
1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT main:app
```
3. Install gunicorn: `pip install gunicorn`
4. Update `requirements.txt`
5. Deploy:
```bash
heroku login
heroku create
git push heroku main
```

---

### Option 4: Self-Hosted (VPS)

**Requirements:**
- Linux VPS (Ubuntu 20.04+)
- SSH access
- Domain name (optional)

**Setup:**

1. **SSH to VPS:**
```bash
ssh root@your-vps-ip
```

2. **Install dependencies:**
```bash
apt update && apt install python3-pip python3-venv nginx certbot python3-certbot-nginx
```

3. **Clone project:**
```bash
git clone https://github.com/yourusername/cv-landing-page.git
cd cv-landing-page/backend
```

4. **Setup Python:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure .env:**
```bash
nano .env
# Add EMAIL_ADDRESS, EMAIL_PASSWORD, etc.
```

6. **Install Gunicorn:**
```bash
pip install gunicorn
```

7. **Create systemd service:**

Create `/etc/systemd/system/cv-backend.service`:
```ini
[Unit]
Description=CV Landing Page Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/root/cv-landing-page/backend
ExecStart=/root/cv-landing-page/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

8. **Enable service:**
```bash
systemctl enable cv-backend
systemctl start cv-backend
```

9. **Setup Nginx reverse proxy:**

Create `/etc/nginx/sites-available/cv-api`:
```nginx
server {
    listen 80;
    server_name api.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/cv-api /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

10. **Enable HTTPS (Let's Encrypt):**
```bash
certbot --nginx -d api.your-domain.com
```

---

## 📋 Environment Variables (Production)

Update `.env` for production:

```bash
# Email (Gmail)
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your_app_password  # 16-char from Gmail

# SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# API Configuration
API_URL=https://api.your-domain.com
FRONTEND_URL=https://your-domain.com

# Deployment
ENVIRONMENT=production
DEBUG=False
```

---

## 🔐 Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong, unique EMAIL_PASSWORD
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure CORS for allowed origins
- [ ] Rate limiting active (5 req/min)
- [ ] Add input validation ✅
- [ ] Enable request logging
- [ ] Regular backups of contact logs (if stored)
- [ ] Monitor API usage & errors

---

## 📊 Monitoring & Maintenance

### Check Server Status
```bash
# Local
curl http://localhost:8000/health

# Production
curl https://api.your-domain.com/health
```

### View Logs

**Local:**
```bash
tail -f server.log
```

**Systemd Service:**
```bash
journalctl -u cv-backend -f
```

**Nginx:**
```bash
tail -f /var/log/nginx/error.log
```

### Performance Optimization

1. **Add caching headers:**
```python
@app.get("/api/info", headers={"Cache-Control": "public, max-age=3600"})
```

2. **Database (if needed):**
- Store contact submissions in PostgreSQL
- Add async database operations

3. **Email queuing:**
- Use Celery for async email sending
- Prevent blocking API responses

---

## 🚀 Deployment Workflow

1. **Update code locally**
2. **Test thoroughly** - `./test_api.sh`
3. **Commit & push** to GitHub
4. **Deploy automatically** (Railway/Render) or manually (Heroku/VPS)
5. **Test production** - curl endpoints
6. **Monitor** logs & performance

---

## 📞 Support Resources

- [FastAPI Deployment Docs](https://fastapi.tiangolo.com/deployment/)
- [Railway Deployment Docs](https://docs.railway.app/)
- [Render Deployment Docs](https://render.com/docs/)
- [Nginx Reverse Proxy](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)

---

**Version:** 1.0.0  
**Status:** Ready for Deployment ✅
