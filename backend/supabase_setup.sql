-- Create profile table
CREATE TABLE profile (
    id integer PRIMARY KEY DEFAULT 1,
    nama text,
    panggilan text,
    peran text,
    bio text,
    about text,
    kontak jsonb
);

-- Insert initial profile data
INSERT INTO profile (id, nama, panggilan, peran, bio, about, kontak)
VALUES (
    1,
    'Dendy Fajar Kurniawan',
    'Dendy',
    'Python Scraper & Web Developer',
    'Spesialis automasi data dan pengembangan web berbasis Linux. Fokus pada efisiensi, akurasi data, dan solusi yang scalable.',
    'Saya adalah Dendy Fajar Kurniawan, seorang Python Developer yang berspesialisasi dalam Web Scraping dan Automasi Data. Menggunakan Linux Mint sebagai daily driver untuk development environment yang optimal.

Dengan keahlian dalam Playwright, FastAPI, dan Python automation, saya fokus membangun solusi yang efisien dan scalable. Setiap project dirancang dengan perhatian pada akurasi data, performa, dan maintainability.',
    '{"email": "dendyfajark@gmail.com", "github": "https://github.com/Dendy13", "fiverr": "https://fiverr.com/username", "linkedin": "https://linkedin.com/"}'::jsonb
);

-- Create skills table
CREATE TABLE skills (
    id serial PRIMARY KEY,
    icon text,
    name text UNIQUE,
    description text,
    level integer
);

-- Insert initial skills
INSERT INTO skills (icon, name, description, level) VALUES
('🐍', 'Python', 'Expert dalam Python untuk web scraping, automation, dan data processing', 95),
('⚡', 'FastAPI', 'Advanced dalam membangun REST API yang cepat dan modern', 88),
('🎭', 'Playwright', 'Advanced web automation dan scraping untuk aplikasi modern', 90),
('🐧', 'Linux Mint', 'Daily driver untuk development environment dan automation', 92),
('📊', 'Data Scraping', 'Specialist dalam ekstraksi dan automasi pengumpulan data', 95);

-- Create projects table
CREATE TABLE projects (
    id serial PRIMARY KEY,
    icon text,
    title text UNIQUE,
    description text,
    tags jsonb,
    status text,
    link text
);

-- Insert initial projects
INSERT INTO projects (icon, title, description, tags, status, link) VALUES
('🛒', 'E-commerce SaaS Scraper', 'Platform automasi riset pasar yang mengambil data dari Tokopedia secara real-time menggunakan Playwright.', '["Python", "Playwright", "FastAPI", "Data Engineering"]'::jsonb, '70% Completed', '#'),
('🐧', 'Linux Virtual Environment Manager', 'Script untuk automasi setup venv dan library Python di distro berbasis Debian.', '["Python", "Linux", "Bash", "Automation"]'::jsonb, 'Production', '#');
