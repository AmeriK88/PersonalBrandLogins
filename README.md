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
- Per-article narration and ordered reel items managed in Django Admin

### Family Section
- Single unpublished-by-default page, managed through Django Admin
- Optional editorial content, approved hero image, and ordered, hideable gallery
- Uploads use UUID filenames and reject photos containing GPS EXIF metadata

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
narration_audio (optional)
reel_title (optional)
reel_description (optional)
```

### **Blog — `PostReelMedia`**
```
post
media_type (image | video)
image or video file
order
caption
alt_text
```

## Blog Multimedia Management

Edit a post in Django Admin to set its optional reel title and description, upload narration, and add reel items in the inline. Choose the media type, upload the matching image or video, set its order, and provide alt text where appropriate. Reel items are private to their post; posts can have narration, a reel, both, or neither.

In development, blog uploads are stored under `media/blog/`. With `ENVIRONMENT=production`, image files use Cloudinary's image resource type and narration/video files use its video resource type. Keep Cloudinary credentials configured on Railway; Railway's local filesystem is ephemeral and is not used for these production uploads.

The original static recovery media remains as a compatibility fallback only for the article whose slug is `watch-this-the-story-of-my-comeback`. No database migration assigns those files to a post. Before removing that fallback, verify the corresponding production article and each original asset, upload its narration and reel through Admin, and confirm the public article works. Do not delete the old static files until that verification is complete. If the legacy article is not present under that slug in a target database, identify it manually before making any compatibility change; do not assign its media to another post.

Before deploying this schema to Railway, run the migrations and verify `ENVIRONMENT=production`, the Cloudinary credentials, and the resulting image/video/audio delivery URLs. Then upload or re-upload the legacy article's media through Admin if it is not already available in Cloudinary. Do not rely on Railway's local disk for uploads.

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

### Family Page Management

Create the single Family page in Django Admin, add only Greg-approved text and photographs, and publish it when it is ready. The page returns 404 until explicitly published. Gallery images use the existing default media storage (local storage in development and Cloudinary in production); generated UUID filenames avoid exposing original filenames. Uploaded images containing GPS EXIF data are rejected and must have that location metadata removed before upload. Hidden gallery entries are not displayed, but their already-uploaded media URLs are not private. Review every image and its metadata before publication; this check does not make media private or sanitize existing uploads.

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

## 🔒 License

This project is licensed under the Elastic License 2.0 (ELv2).

Commercial use, redistribution, or offering this software as a service
requires explicit permission from the author.

© 2026 **José Félix**
