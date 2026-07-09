#!/bin/bash
echo ""
echo " =========================================="
echo "  نظام الإرشاد الأكاديمي - MNU SaaS"
echo "  كلية الهندسة - جامعة المنصورة الأهلية"
echo " =========================================="
echo ""

if ! command -v python3 &>/dev/null; then
    echo "[خطأ] Python3 غير مثبت."
    echo "Linux: sudo apt install python3 python3-pip"
    echo "Mac:   brew install python3"
    exit 1
fi

if [ ! -f ".deps_ok" ]; then
    echo "[1/3] تثبيت المكتبات..."
    pip3 install -r requirements.txt -q && touch .deps_ok
    echo "      تم التثبيت"
else
    echo "[1/3] المكتبات موجودة"
fi

echo "[2/3] إعداد قاعدة البيانات..."
python3 manage.py migrate --run-syncdb > /dev/null 2>&1

if [ ! -f "db.sqlite3" ]; then
    echo ""
    echo " ----------------------------------------"
    echo "  أول تشغيل: أنشئ حساب الأدمن"
    echo " ----------------------------------------"
    python3 manage.py createsuperuser
    echo ""
fi

echo "[3/3] تشغيل الموقع..."
echo ""
echo " الرابط: http://127.0.0.1:8000"
echo " للإيقاف: Ctrl+C"
echo ""

(sleep 2 && (command -v xdg-open &>/dev/null && xdg-open http://127.0.0.1:8000 || open http://127.0.0.1:8000 2>/dev/null)) &

python3 manage.py runserver 127.0.0.1:8000
