# 🏀 Greg Logins Jr — Professional Portfolio Website

A modern, high-performance portfolio website built for **Greg Logins Jr**, a professional basketball player, mentor, educator, father, and international leader.  
This platform showcases his **career**, **media highlights**, **blog**, and **personal brand**, offering a premium and immersive digital experience.

---

## 🚀 Tech Stack

### **Frontend**
- 🟦 HTML5  
- 🎨 CSS3 + Bootstrap 5  
- ⚡ Custom JS animations (fade-in, reels, audio controls)  
- 🎬 Optimized images & videos  

### **Backend**
- 🐍 Python 3  
- 🧩 Django 5  
- 🖼️ Pillow (image processing)  
- 🌐 SEO-friendly metadata & slugs  

### **Database**
- 🗄️ SQLite / MySQL (configurable)

---

## 📁 Project Structure

```
project/
│── config/  
│── core/            # Base templates, global utilities, audio scripts
│── blog/            # Blog: categories, posts, slugs, share system
│── highlights/      # Photos, videos, press gallery
│── career/          # High School, College & Pro experience
│── static/          # CSS, JS, images, animations
│── media/           # Uploaded media
│── templates/       # Global templates (base.html, UI components)
└── ...
```

---

## ✨ Features

### 📸 Highlights Gallery
- Responsive photo & video grid  
- **16:9 video wrapper**  
- External press links  
- Lazy-loading + smooth fade animations  

### 📝 Blog System
- Category filtering  
- SEO-ready slugs  
- Modern article layout  
- Cover images  
- **Built-in social sharing (FB, X, LinkedIn, Copy Link)**  

### 🏀 Career Timeline
Structured into:
- High School  
- College  
- Professional (international)

Each entry includes:
- Team  
- Years  
- League  
- Country  
- Achievements  
- Photo/logo  

### 🔊 Recovery Reel System
- Mixed images + videos  
- Auto-transitioning  
- iOS-safe autoplay  
- Integrated narration with user-controlled audio  
- Optimized for performance  

### 🎨 Design System
- Black & Gold premium palette  
- Elegant typography  
- Consistent cards, headers, spacing  
- Professional fade, slide & hover animations  

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

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-user/greg-logins-portfolio.git
cd greg-logins-portfolio
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Migrations
```bash
python manage.py migrate
```

### 5. Start Server
```bash
python manage.py runserver
```

---

## 📸 Media Configuration (settings.py)
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
```

---

## 📤 Social Sharing

Blog posts automatically generate full URLs using:
```python
request.build_absolute_uri()
```

JS sharing supports:
- Facebook  
- LinkedIn  
- X (Twitter)  
- Copy Link  

Placed inside the blog sidebar for visibility.

---

## 📈 SEO & Performance
- Dynamic meta tags  
- OpenGraph support  
- Lazy loading  
- Minified CSS/JS  
- Preconnected fonts  
- Clean slugs  

---

## ♿ Accessibility
- Semantic HTML5  
- ARIA labels  
- Keyboard-ready components  
- Accessible narration toggle  

---

## 📬 Contact
**Developer:** Your Name  
🌍 Website: your-website  
💼 LinkedIn: your-linkedin  
📧 Email: your-email  

---

## 📜 License
This project is proprietary.  
All rights reserved to **Greg Logins Jr**.
