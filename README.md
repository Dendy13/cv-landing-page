# Portfolio Dendy Fajar Kurniawan

Portfolio website modern dengan desain cyber-tech untuk Python Scraper & Web Developer.

## 🚀 Fitur Utama

- **Desain Modern**: Tema cyber-tech dengan warna neon (cyan & magenta)
- **Fully Responsive**: Tampilan optimal di desktop, tablet, dan mobile dengan hamburger menu
- **Smooth Animations**: Animasi halus dan micro-interactions dengan Intersection Observer
- **Dynamic Content**: Data loaded dari JSON untuk update mudah
- **Interactive Contact Form**: Form kontak dengan validasi dan integrasi FastAPI backend
- **Performance Optimized**: Fast loading dengan CSS animations dan lazy loading
- **SEO Optimized**: Open Graph, Twitter Cards, JSON-LD structured data
- **Accessibility**: ARIA labels, semantic HTML, keyboard navigation
- **Security**: XSS protection, input validation, CORS configuration

## 📁 Struktur File

```
cv-landing-page/
├── index.html                # Halaman utama dengan SEO optimizations
├── style.css                 # Styling, animasi, responsive design
├── script.js                 # JavaScript interaktivity dengan API integration
├── data.json                 # Data konten (skills, projects, kontak)
├── backend/                  # FastAPI backend
│   ├── main.py              # API server untuk contact form
│   ├── requirements.txt      # Python dependencies
│   └── .env.example         # Environment variables template
├── README.md                # Documentation
├── OPTIMIZATION-GUIDE.md    # Setup & deployment guide
└── public/                  # (Optional) Static files
```

## 🛠️ Quick Start

### Setup Frontend
```bash
# Option 1: VSCode Live Server
# Right-click index.html → Open with Live Server

# Option 2: Python HTTP Server
python -m http.server 5500 --directory .
```

### Setup Backend (Contact Form)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Setup .env dengan Gmail credentials
cp .env.example .env
# Edit .env: EMAIL_ADDRESS, EMAIL_PASSWORD

# Run backend
python main.py
```

Backend akan jalan di `http://localhost:8000`

**Lihat [OPTIMIZATION-GUIDE.md](./OPTIMIZATION-GUIDE.md) untuk setup lengkap & deployment.**

## ✏️ Customize Konten

### Update Data Personal

Edit file `data.json`:

```json
{
  "nama": "Nama Lengkap Anda",
  "panggilan": "Panggilan",
  "peran": "Job Title Anda",
  "bio": "Bio singkat tentang Anda...",
  "kontak": {
    "email": "email@anda.com",
    "github": "https://github.com/username-anda",
    "fiverr": "https://fiverr.com/username-anda",
    "linkedin": "https://linkedin.com/"
  }
}
```

### Tambah/Edit Skills

Di `data.json`, bagian `skills`:

```json
{
  "icon": "🐍",
  "name": "Nama Skill",
  "description": "Deskripsi skill Anda",
  "level": 90
}
```

Level: 0-100 (akan tampil sebagai progress bar)

### Tambah/Edit Projects

Di `data.json`, bagian `projects`:

```json
{
  "icon": "🛒",
  "title": "Nama Project",
  "description": "Deskripsi project...",
  "tags": ["Tag1", "Tag2", "Tag3"],
  "status": "Status (optional)",
  "link": "#atau-url-project"
}
```

## 🎨 Customize Warna

Edit variabel CSS di `style.css`:

```css
:root {
    --primary: #00fff5;        /* Warna utama (cyan) */
    --secondary: #ff006e;      /* Warna sekunder (magenta) */
    --accent: #ffbe0b;         /* Warna aksen (kuning) */
    --bg-dark: #0a0e27;        /* Background gelap */
    --bg-darker: #050816;      /* Background lebih gelap */
}
```

## 📊 API Endpoints

```
GET  /health                 → Health check
POST /api/contact            → Submit contact form
GET  /api/info               → Portfolio info
GET  /docs                   → Interactive API docs (Swagger UI)
```

### Contact Form Request
```bash
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Collaboration",
    "message": "I would like to work with you..."
  }'
```

## 📊 Stats Counter

Edit angka stats di `index.html` (cari `data-target`):

```html
<div class="stat-number" data-target="15">0</div>  <!-- Projects -->
<div class="stat-number" data-target="50">0</div>  <!-- Data Sources -->
<div class="stat-number" data-target="3">0</div>   <!-- Years -->
```

## 🎯 Fitur Interaktif

### Contact Form

Form akan menampilkan:
- ✅ Loading state saat submit
- ✅ Success message (simulasi)
- ✅ Error handling

**Catatan**: Saat ini form hanya simulasi. Untuk menghubungkan dengan email service:

1. Gunakan service seperti EmailJS, Formspree, atau SendGrid
2. Update event handler di `script.js` bagian `contactForm.addEventListener`

### Easter Egg 🎮

Ketik Konami Code di keyboard: `↑ ↑ ↓ ↓ ← → ← → B A`

## 🐧 Tips untuk Linux Mint Users

1. Jika menggunakan Firefox, pastikan hardware acceleration enabled untuk animasi smooth
2. Untuk development, gunakan Chromium untuk testing cross-browser
3. Install `python3-http.server` untuk quick local testing:
   ```bash
   python3 -m http.server 8000
   ```
   Buka `http://localhost:8000`

## 📝 Browser Support

- ✅ Chrome/Chromium 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🤝 Credits

Design & Development: Dendy Fajar Kurniawan
Fonts: Google Fonts (Orbitron, IBM Plex Mono)

## 📞 Contact

Butuh bantuan customize? Kontak:
- Email: emailmu@example.com
- GitHub: github.com/username
- Fiverr: fiverr.com/username

---

Made with ❤️ and Python
