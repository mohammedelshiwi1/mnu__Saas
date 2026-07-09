@echo off
chcp 65001 >nul
title MNU - نظام الإرشاد الأكاديمي SaaS

echo.
echo  ==========================================
echo   نظام الإرشاد الاكاديمي - MNU SaaS
echo   كلية الهندسة - جامعة المنصورة الاهلية
echo  ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [خطا] Python غير مثبت.
    echo حمله من: https://www.python.org/downloads/
    echo تاكد من تفعيل "Add Python to PATH"
    pause & exit /b 1
)

if not exist ".deps_ok" (
    echo [1/3] تثبيت المكتبات...
    pip install -r requirements.txt -q
    if errorlevel 1 ( echo [خطا] فشل تثبيت المكتبات & pause & exit /b 1 )
    echo installed > .deps_ok
    echo       تم تثبيت المكتبات
) else (
    echo [1/3] المكتبات موجودة
)

echo [2/3] اعداد قاعدة البيانات...
python manage.py migrate --run-syncdb >nul 2>&1

if not exist "db.sqlite3" (
    echo.
    echo  ----------------------------------------
    echo   اول تشغيل: انشئ حساب الادمن
    echo  ----------------------------------------
    python manage.py createsuperuser
    echo.
)

echo [3/3] تشغيل الموقع...
echo.
echo  الرابط: http://127.0.0.1:8000
echo  للايقاف: Ctrl+C
echo.

start /b cmd /c "timeout /t 2 >nul && start http://127.0.0.1:8000"
python manage.py runserver 127.0.0.1:8000
pause
