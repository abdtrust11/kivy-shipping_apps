[app]
# اسم التطبيق الظاهر للمستخدم
title = Shipping Calculator

# اسم وحدة التشغيل الرئيسية (بدون .py)
# إذا كان ملفك main.py فدعها كما هي
package.name = ShippingApp
package.domain = alshal.sa   # غيّره لنطاقك إن أردت (org.yourname)

# إصدار التطبيق
version = 0.1.0

# ملف Python الرئيسي
source.dir = .
source.include_exts = py,kv,ttf,otf,png,jpg,jpeg,xlsx

# تضمين مجلدات وملفات مهمة داخل الـ APK
# تأكد أن لديك:
# - kv/main.kv            (لو تستخدم KV)
# - data/aramex.xlsx      (ملف الشحن)
# - assets/fonts/Cairo-Regular.ttf  (أو أي خط عربي)
source.include_patterns = \
    kv/*.kv, \
    data/*.xlsx, \
    assets/fonts/*.ttf, \
    assets/fonts/*.otf, \
    assets/images/*.png, \
    assets/images/*.jpg

# أيقونة وشاشة البداية (اختياري.. ضع ملفاتك إن وجدت)
icon.filename = assets/images/icon.png
presplash.filename = assets/images/presplash.png

# اتجاه الشاشة ووضع ملء الشاشة
orientation = portrait
fullscreen = 0

# إن كان تطبيقك يحتاج إنترنت (اختياري)
android.permissions = INTERNET

# ----- المتطلبات (PIN) -----
# لاحظ أننا ثبّتنا نسخًا متوافقة مع أندرويد وKivyMD
# أضف أي حزم أخرى تحتاجها هنا (requests, pillow, ...الخ)
requirements = python3, \
               kivy==2.3.0, \
               kivymd==1.2.0, \
               arabic_reshaper==3.0.0, \
               python-bidi==0.4.2, \
               openpyxl==3.1.5

# إذا كنت تستخدم ملفات محلية فقط (Excel داخل APK)، لا تحتاج صلاحيات تخزين

# تقليل الإذن التلقائي على أندرويد 13+
android.manifest.placeholders = \
    usesCleartextTraffic=false

# ---------- خيارات Kivy ----------
# يمكنك ضبط الحد الأدنى والنسخة إن رغبت
# kivy_version = 2.3.0

# ---------- لغات وأكواد ----------
# لدعم العربية بخطوطك المضمّنة
# احرص أن تطبيقك يسجّل خطًا عربيًا من assets/fonts في وقت التشغيل

[buildozer]
# مستوى السجل أثناء البناء (1 قليل - 2 افتراضي - 3 مفصّل)
log_level = 2

# احذف bin قبل كل بناء (ليُعاد التوليد من الصفر)
warn_on_root = 1
# (اترك الافتراضيات الأخرى)

[app:android]
# نسخة/حدود منصة أندرويد
android.api = 35
android.minapi = 21

# المعماريات المستهدفة (يدعم معظم الأجهزة)
android.archs = armeabi-v7a, arm64-v8a

# استخدم bootstrap sdl2 (الافتراضي)
# android.bootstrap = sdl2

# (اترك NDK/SDK يديرها buildozer/p4a تلقائياً)

# في حال أردت لغات واجهة إضافية:
# android.extras = android.intent.category.LAUNCHER
