# 🏀 Greg Logins Jr — Professional Portfolio Website

A modern, high-performance portfolio platform built for **Greg Logins Jr**, a professional basketball player, mentor, educator, father, and international leader.  
This website showcases his **career**, **media highlights**, **blog**, and **personal brand**, delivering a premium, cinematic and production-grade digital experience.

Live at: **https://gloginsjr.com**

---

## 🚀 Tech Stack

### **Frontend**
- 🟦 HTML5  
- 🎨 CSS3 + Bootstrap 5  
- ⚡ Custom JavaScript animations (fade-in, reels, audio controls)  
- 🎬 Optimized images & video playback  
- 🔊 Narration audio system  

### **Backend**
- 🐍 Python 3  
- 🧩 Django 5  
- 🖼️ Pillow (image processing)  
- 🌐 SEO-friendly slugs & metadata  
- 🔐 Production-ready security settings  

### **Database**
- 🐘 PostgreSQL (Railway – production)  
- 🗄️ SQLite (local development)

### **Media & CDN**
- ☁️ Cloudinary (images & uploads CDN)
- ⚡ Global delivery, optimization & resizing

---

## ☁️ Production Infrastructure

- 🚄 Hosting: **Railway**
- ⚙️ Gunicorn + WhiteNoise
- 🔒 Automatic HTTPS (Let's Encrypt)
- 🌍 Custom domain with canonical redirects
- 🐘 Managed PostgreSQL
- ☁️ Cloudinary for media storage
- ✉️ SMTP email (contact form)
- 🔁 301 Canonical Domain Redirection (SEO safe)

---

## 📁 Project Structure

```
project/
│── config/          # Django settings & WSGI
│── core/            # Base templates, middleware, UI logic
│── blog/            # Articles, categories, SEO, sharing
│── highlights/      # Photos, videos, press gallery
│── career/          # High School, College & Pro timeline
│── static/          # CSS, JS, audio, video, images
│── templates/       # Global layout & components
└── ...
```

---

## ✨ Features

### 📸 Highlights Gallery
- Responsive photo & video grid  
- **16:9 cinematic video wrapper**  
- External press links  
- Lazy-loading + smooth transitions  

### 📝 Blog System
- Category filtering  
- SEO-ready slugs  
- Cover images  
- **Built-in social sharing (Facebook, X, LinkedIn, Copy Link)**  
- OpenGraph preview optimization  

### 🏀 Career Timeline
Structured into:
- High School  
- College  
- Professional (International)

Each entry includes:
- Team  
- Years  
- League  
- Country  
- Achievements  
- Image / Logo  

### 🔊 Recovery Reel System
- Mixed images & videos  
- Auto-transition cinematic slideshow  
- iOS-safe autoplay  
- Integrated narration with audio controls  

### 🎨 Design System
- Black & Gold premium palette  
- Elegant typography  
- Unified card system  
- Professional hover, fade & motion animations  

---

## 🛠️ Models Overview

### **Blog — `Post`**
```
title
slug
category
excerpt
content
cover_image
is_published
created_at
updated_at
```

### **Highlights — `Highlight`**
```
title
category (photo | video | press)
image
video_url
press_link
created_at
```

### **Career — `Experience`**
```
team
years
league
country
achievements
image
```

---

## 📸 Media & Static Configuration

```python
MEDIA_URL = "/media/"
STATIC_URL = "/static/"
```

Production:
- Static files served by **WhiteNoise**
- Media files served by **Cloudinary CDN**

---

## ✉️ Contact System

- SMTP email delivery
- Secure app-password authentication
- Reply-To support
- Production-safe headers

---

## 🌐 SEO & Performance

- Canonical domain enforcement
- 301 redirects
- OpenGraph tags
- Lazy loading
- CDN delivery
- Manifest-hashed static assets
- Optimized fonts & media

---

## ♿ Accessibility

- Semantic HTML5
- ARIA labels
- Keyboard navigation
- Screen reader friendly
- Audio controls with reduced-motion support

---

## 🔐 Security

- HTTPS only
- CSRF protection
- Secure cookies
- Environment-based configuration
- Production-ready middleware stack

---

## 📜 License

This project is proprietary.
All rights reserved to **Greg Logins Jr**.
