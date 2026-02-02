// Configuration
const API_BASE_URL = 'https://cv-landing-page-production-029a.up.railway.app/api';

// Smooth scroll polyfill untuk browser lama
if (!('scrollBehavior' in document.documentElement.style)) {
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/smoothscroll-polyfill/dist/smoothscroll.min.js';
    document.head.appendChild(script);
}

// DOM Elements
const navLinks = document.querySelectorAll('.nav-link');
const navToggle = document.getElementById('navToggle');
const navLinksContainer = document.getElementById('navLinks');
const skillsGrid = document.getElementById('skillsGrid');
const projectsGrid = document.getElementById('projectsGrid');
const contactForm = document.getElementById('contactForm');
const formStatus = document.getElementById('formStatus');
const statNumbers = document.querySelectorAll('.stat-number');

// Helper function untuk escape HTML (XSS protection)
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// Mobile navigation toggle
if (navToggle) {
    navToggle.addEventListener('click', () => {
        const isExpanded = navToggle.getAttribute('aria-expanded') === 'true';
        navToggle.setAttribute('aria-expanded', !isExpanded);
        navLinksContainer.classList.toggle('active');
    });
}

// Close mobile menu when link clicked
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navToggle.setAttribute('aria-expanded', 'false');
        navLinksContainer.classList.remove('active');
    });
});

// Load data from JSON
async function loadData() {
    try {
        let data = null;

        // Try load from backend API first
        try {
            const apiResponse = await fetch(`${API_BASE_URL}/admin/cv`);
            if (apiResponse.ok) {
                data = await apiResponse.json();
            }
        } catch (apiError) {
            console.warn('API load failed, fallback to local data.json:', apiError);
        }

        // Fallback to local data.json
        if (!data) {
            const response = await fetch('data.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            data = await response.json();
        }
        
        // Update hero section
        if (data.nama) {
            document.getElementById('heroName').textContent = data.nama.toUpperCase();
        }
        if (data.peran) {
            document.getElementById('heroRole').textContent = data.peran;
        }
        if (data.bio) {
            document.getElementById('heroBio').textContent = data.bio;
        }
        
        // Update contact info
        if (data.kontak) {
            if (data.kontak.email) {
                const emailLink = document.getElementById('contactEmail');
                emailLink.href = `mailto:${data.kontak.email}`;
                emailLink.querySelector('.method-value').textContent = data.kontak.email;
            }
            if (data.kontak.github) {
                const githubLink = document.getElementById('contactGithub');
                githubLink.href = data.kontak.github;
                githubLink.querySelector('.method-value').textContent = data.kontak.github.replace('https://', '');
            }
            if (data.kontak.fiverr) {
                const fiverrLink = document.getElementById('contactFiverr');
                fiverrLink.href = data.kontak.fiverr;
                fiverrLink.querySelector('.method-value').textContent = data.kontak.fiverr.replace('https://', '');
            }
            if (data.kontak.linkedin) {
                const linkedinLink = document.getElementById('contactLinkedin');
                linkedinLink.href = data.kontak.linkedin;
                linkedinLink.querySelector('.method-value').textContent = data.kontak.linkedin.replace('https://', '');
            }
        }
        
        // Render skills
        renderSkills(data.skills);
        
        // Render projects
        renderProjects(data.projects);
        
    } catch (error) {
        console.error('Error loading data:', error);
        
        // Show error notification to user
        showNotification('Failed to load portfolio data. Please refresh the page.', 'error');
        
        // Fallback
        renderSkills([]);
        renderProjects([]);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed; 
        top: 20px; 
        right: 20px; 
        background: ${type === 'error' ? 'rgba(239, 68, 68, 0.95)' : 'rgba(16, 185, 129, 0.95)'}; 
        color: white; 
        padding: 15px 25px; 
        border-radius: 8px;
        z-index: 10000;
        font-family: var(--font-mono);
        font-size: 14px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        animation: slideInRight 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Render Skills
function renderSkills(skills) {
    if (!skills || skills.length === 0) {
        skillsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Skills data tidak tersedia</p>';
        return;
    }
    
    skillsGrid.innerHTML = skills.map((skill, index) => `
        <div class="skill-card" style="animation-delay: ${index * 0.1}s">
            <span class="skill-icon">${escapeHtml(skill.icon)}</span>
            <h3 class="skill-name">${escapeHtml(skill.name)}</h3>
            <p class="skill-description">${escapeHtml(skill.description)}</p>
            <div class="skill-level">
                <div class="skill-level-fill" data-level="${escapeHtml(skill.level)}"></div>
            </div>
        </div>
    `).join('');
    
    // Animate skill levels when in viewport
    observeSkillLevels();
}

// Render Projects
function renderProjects(projects) {
    if (!projects || projects.length === 0) {
        projectsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Projects data tidak tersedia</p>';
        return;
    }
    
    projectsGrid.innerHTML = projects.map((project, index) => `
        <div class="project-card" style="animation-delay: ${index * 0.1}s">
            <div class="project-image">
                ${escapeHtml(project.icon)}
            </div>
            <div class="project-content">
                <h3 class="project-title">${escapeHtml(project.title)}</h3>
                <p class="project-description">${escapeHtml(project.description)}</p>
                <div class="project-tags">
                    ${project.tags.map(tag => `<span class="project-tag">${escapeHtml(tag)}</span>`).join('')}
                    ${project.status ? `<span class="project-tag" style="background: rgba(16, 185, 129, 0.1); color: #10b981; border-color: rgba(16, 185, 129, 0.2);">${escapeHtml(project.status)}</span>` : ''}
                </div>
                <a href="${escapeHtml(project.link)}" class="project-link">
                    View Details →
                </a>
            </div>
        </div>
    `).join('');
}

// Intersection Observer for skill levels animation
function observeSkillLevels() {
    const skillLevels = document.querySelectorAll('.skill-level-fill');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const level = entry.target.dataset.level;
                entry.target.style.width = level + '%';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    skillLevels.forEach(level => observer.observe(level));
}

// Animate stat numbers
function animateStats() {
    statNumbers.forEach(stat => {
        const target = parseInt(stat.dataset.target);
        const increment = target / 50;
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                stat.textContent = target + '+';
                clearInterval(timer);
            } else {
                stat.textContent = Math.floor(current);
            }
        }, 30);
    });
}

// Smooth scroll for navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Remove active class from all links
        navLinks.forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        link.classList.add('active');
        
        // Smooth scroll to section
        const targetId = link.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        if (targetSection) {
            const offsetTop = targetSection.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// Update active nav link on scroll
function updateActiveNavLink() {
    const sections = document.querySelectorAll('section');
    const scrollPosition = window.scrollY + 100;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}

// Contact form handling dengan API integration
contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = contactForm.querySelector('.btn-submit');
    
    // Get form data
    const formData = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        subject: document.getElementById('subject').value.trim(),
        message: document.getElementById('message').value.trim()
    };
    
    // Basic validation
    if (!formData.name || !formData.email || !formData.subject || !formData.message) {
        showNotification('Semua field harus diisi!', 'error');
        return;
    }
    
    // Email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
        showNotification('Email format tidak valid!', 'error');
        return;
    }
    
    // Show loading state
    submitBtn.classList.add('loading');
    submitBtn.disabled = true;
    formStatus.style.display = 'none';
    
    try {
        // Try to send via API
        const response = await fetch(`${API_BASE_URL}/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Success
        formStatus.textContent = result.message || 'Pesan berhasil dikirim! Saya akan segera menghubungi Anda.';
        formStatus.className = 'form-status success';
        formStatus.style.display = 'block';
        formStatus.setAttribute('role', 'alert');
        
        // Reset form
        contactForm.reset();
        
        // Show success notification
        showNotification('Pesan berhasil dikirim!', 'success');
        
        // Scroll to form for feedback visibility
        formStatus.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        console.error('Form submission error:', error);
        
        // Error
        formStatus.textContent = 'Terjadi kesalahan. Silakan coba lagi atau hubungi melalui email.';
        formStatus.className = 'form-status error';
        formStatus.style.display = 'block';
        formStatus.setAttribute('role', 'alert');
        
        showNotification('Gagal mengirim pesan. Silakan coba lagi.', 'error');
    } finally {
        // Remove loading state
        submitBtn.classList.remove('loading');
        submitBtn.disabled = false;
    }
});

// Parallax effect for hero section
function parallaxEffect() {
    const scrolled = window.pageYOffset;
    const heroVisual = document.querySelector('.hero-visual');
    
    if (heroVisual && scrolled < window.innerHeight) {
        heroVisual.style.transform = `translateY(-50%) translateX(${scrolled * 0.2}px)`;
    }
}

// Scroll event listeners with throttle
let scrollTimer;
let ticking = false;

window.addEventListener('scroll', () => {
    if (!ticking) {
        window.requestAnimationFrame(() => {
            updateActiveNavLink();
            parallaxEffect();
            ticking = false;
        });
        ticking = true;
    }
});

// Intersection Observer for fade-in animations
function observeElements() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe skill cards and project cards
    const cards = document.querySelectorAll('.skill-card, .project-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Form input animations
const formInputs = document.querySelectorAll('.form-input');
formInputs.forEach(input => {
    input.addEventListener('focus', () => {
        input.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', () => {
        if (input.value === '') {
            input.parentElement.classList.remove('focused');
        }
    });
});

// Add glow effect to buttons on mouse move
const buttons = document.querySelectorAll('.btn');
buttons.forEach(btn => {
    btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        btn.style.setProperty('--mouse-x', `${x}px`);
        btn.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Cursor trail effect (optimized)
function createCursorTrail() {
    let trails = [];
    const maxTrails = 10;
    let lastTrailTime = 0;
    const trailDelay = 50; // ms
    
    document.addEventListener('mousemove', (e) => {
        const now = Date.now();
        if (now - lastTrailTime < trailDelay) return;
        lastTrailTime = now;
        
        // Create trail element
        const trail = document.createElement('div');
        trail.style.cssText = `
            position: fixed;
            width: 4px;
            height: 4px;
            border-radius: 50%;
            background: var(--primary);
            pointer-events: none;
            left: ${e.clientX}px;
            top: ${e.clientY}px;
            opacity: 0.6;
            transition: all 0.3s ease;
            z-index: 9999;
        `;
        
        document.body.appendChild(trail);
        trails.push(trail);
        
        // Remove old trails
        if (trails.length > maxTrails) {
            const oldTrail = trails.shift();
            oldTrail.style.opacity = '0';
            setTimeout(() => oldTrail.remove(), 300);
        }
        
        // Fade out current trail
        setTimeout(() => {
            trail.style.opacity = '0';
            trail.style.transform = 'scale(0)';
        }, 100);
    });
}

// Easter egg: Konami code
let konamiCode = [];
const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.key);
    konamiCode = konamiCode.slice(-konamiSequence.length);
    
    if (konamiCode.join('') === konamiSequence.join('')) {
        activateEasterEgg();
    }
});

function activateEasterEgg() {
    // Change theme colors temporarily
    document.documentElement.style.setProperty('--primary', '#ff00ff');
    document.documentElement.style.setProperty('--secondary', '#00ffff');
    
    // Show message
    showNotification('🎉 EASTER EGG ACTIVATED! 🎉', 'success');
    
    setTimeout(() => {
        document.documentElement.style.setProperty('--primary', '#00fff5');
        document.documentElement.style.setProperty('--secondary', '#ff006e');
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Load data
    loadData();
    
    // Animate stats after a delay
    setTimeout(animateStats, 1000);
    
    // Setup intersection observers
    setTimeout(observeElements, 500);
    
    // Add cursor trail effect (optional - comment out if too heavy)
    createCursorTrail();
    
    // Log welcome message
    console.log('%c👋 Halo Developer!', 'font-size: 20px; font-weight: bold; color: #00fff5;');
    console.log('%cTertarik dengan kode saya? Mari berkolaborasi!', 'font-size: 14px; color: #94a3b8;');
    console.log('%cEmail: emailmu@example.com', 'font-size: 12px; color: #00fff5;');
});

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
