# نظام الإرشاد الأكاديمي - MNU SaaS
## Academic Advisor System | كلية الهندسة - جامعة المنصورة الأهلية

---

## 👥 الأدوار والصلاحيات

| الدور | الصلاحيات |
|-------|-----------|
| **admin** | كل الصلاحيات - إنشاء مستخدمين، تعيين مرشدين، تحليلات |
| **head** | رئيس وحدة الإرشاد - متابعة + تقارير (بدون تعديل) |
| **advisor** | مرشد أكاديمي - طلابه + شكاوى + شات + تقارير |
| **student** | طالب - بياناته + شات + شكاوى + إقرار البيانات |

---

## 🚀 التشغيل المحلي (للتجربة)

### Windows
```
دبل كليك على run.bat
```

### Mac / Linux
```bash
chmod +x run.sh && ./run.sh
```

**بيانات الدخول التجريبية:**
- Admin: `admin` / `admin123`
- Head:  `head` / `head123`
- Advisor 1: `advisor1` / `advisor123`
- Advisor 2: `advisor2` / `advisor123`

---

## ☁️ النشر على Railway (مجاني)

### الخطوات:
1. ارفع الملفات على GitHub repository
2. اذهب إلى [railway.app](https://railway.app) وسجّل بحساب GitHub
3. اضغط **New Project → Deploy from GitHub repo**
4. اختر الـ repository
5. اضغط **Add Variables** وأضف:

```
SECRET_KEY=your-super-secret-key-change-this-now
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=  (Railway هيضيفها تلقائياً لو أضفت PostgreSQL)
```

6. اضغط **Add Plugin → PostgreSQL** (مجاني)
7. Railway هيعمل deploy تلقائياً ✅

### بعد الـ deploy:
```bash
# في Railway terminal
python manage.py createsuperuser
```

---

## 🏛️ النشر على سيرفر الجامعة (Ubuntu/Linux)

```bash
# 1. Clone المشروع
git clone <repo-url> /var/www/mnu_advisor
cd /var/www/mnu_advisor

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Environment variables
cp .env.example .env
nano .env  # عدّل القيم

# 4. Database & static
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser

# 5. Gunicorn service
sudo nano /etc/systemd/system/mnu_advisor.service
```

**mnu_advisor.service:**
```ini
[Unit]
Description=MNU Advisor Django App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/mnu_advisor
ExecStart=/var/www/mnu_advisor/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable mnu_advisor
sudo systemctl start mnu_advisor
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /var/www/mnu_advisor/staticfiles/;
    }
    location /media/ {
        alias /var/www/mnu_advisor/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔧 متغيرات البيئة (.env)

```env
SECRET_KEY=your-very-secret-key-min-50-chars
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 📦 التقنيات المستخدمة

| التقنية | الاستخدام |
|---------|-----------|
| Django 4.2+ | Backend Framework |
| Bootstrap 5.3 | UI Framework |
| Chart.js 4 | الرسوم البيانية |
| python-docx | تصدير Word |
| openpyxl | تصدير Excel |
| WhiteNoise | Static Files |
| Gunicorn | Production Server |
| PostgreSQL / SQLite | قاعدة البيانات |

---

## 📊 الميزات الرئيسية

- ✅ **3 أدوار** - Admin / Advisor / Student
- ✅ **لوحة تحكم** ذكية لكل دور
- ✅ **شات مباشر** بين الطالب والمرشد
- ✅ **نظام شكاوى** مع تصعيد للإدارة
- ✅ **إقرار إلكتروني** بصحة البيانات
- ✅ **تحليلات متقدمة** - EWS, Heatmap, Leaderboard
- ✅ **بحث موحّد** بالطالب أو المرشد
- ✅ **تصدير Word** - استمارة لكل طالب
- ✅ **تصدير Excel** - 4 شيتات منسّقة
- ✅ **متوافق** مع Railway / Render / سيرفر الجامعة
