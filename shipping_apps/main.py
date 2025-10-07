"""
تطبيق حاسبة تكلفة الشحن - أرامكس
متوافق مع: Android, iOS, Desktop
"""

import os
import platform

# ⚙️ إعدادات خاصة بسطح المكتب فقط
PLATFORM = platform.system()
IS_DESKTOP = PLATFORM in ('Windows', 'Darwin', 'Linux') and 'ANDROID_ARGUMENT' not in os.environ

if IS_DESKTOP:
    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,disable_multitouch')
    Config.set('kivy', 'keyboard_mode', 'system')
    Config.set('input', 'mtdev_%(name)s', '')
    
    from kivy.core.window import Window
    Window.size = (390, 800)

# 📚 المكتبات الأساسية
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path, resource_find
from kivy.metrics import dp
from kivy.factory import Factory
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem

# 🌐 دعم العربية
try:
    from arabic_reshaper import reshape as ar_reshape, reshape
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    print("⚠️ تحذير: مكتبات العربية غير متوفرة")
    ARABIC_SUPPORT = False
    def reshape(text):
        return text
    def ar_reshape(text):
        return text
    def get_display(text, base_dir='R'):
        return text

# 📄 قراءة JSON بدلاً من Excel
import json
from math import ceil
import re
import sys

# 🔢 أوزان المنتجات (بالكيلوغرام)
PRODUCT_WEIGHTS = {
    "عباية": 0.7,
    "طرحة": 0.2,
    "نقاب": 0.1
}

# ==================== دوال مساعدة ====================

def normalize(text):
    """تطبيع النص للمقارنة"""
    return text.strip().lower() if text else ""

def safe_number(value):
    """تحويل آمن للأرقام"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0

def load_shipping_data():
    """
    تحميل بيانات الشحن من ملف JSON
    ✅ متوافق مع iOS, Android, Desktop
    """
    try:
        # 📂 المسارات المحتملة للملف
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        
        possible_paths = [
            os.path.join(base_path, "aramex.json"),
            os.path.join(base_path, "data", "aramex.json"),
            "aramex.json",
            "data/aramex.json",
            os.path.join(os.path.dirname(__file__), "aramex.json"),
            os.path.join(os.path.dirname(__file__), "data", "aramex.json"),
        ]
        
        # 🔍 البحث عن الملف
        for file_path in possible_paths:
            if os.path.exists(file_path):
                print(f"✅ وجدت الملف: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"✅ تم تحميل {len(data)} دولة")
                return data
        
        # ❌ لم يُعثر على الملف
        print("❌ لم يتم العثور على aramex.json")
        print("📂 المسارات المجربة:")
        for path in possible_paths:
            print(f"   - {path}")
        return []
        
    except json.JSONDecodeError as e:
        print(f"❌ خطأ في قراءة JSON: {e}")
        return []
    except Exception as e:
        print(f"❌ خطأ في تحميل البيانات: {e}")
        return []

def calculate_shipping_cost(data, country_input, weight):
    """حساب تكلفة الشحن بناء على الوزن"""
    country_input_norm = normalize(country_input)
    
    for row in data:
        country_en = normalize(row.get("Country_EN", ""))
        country_ar = normalize(row.get("Country_AR", ""))
        
        if country_input_norm == country_en or country_input_norm == country_ar:
            first = row.get("FirstHalfKg", 0)
            add_05_10 = row.get("Add_0_5_to_10", 0)
            add_10_to_15 = row.get("Add_10_to_15", 0)
            add_over_15 = row.get("Add_over_15", 0)

            half_kg_units = ceil(weight * 2)

            if weight <= 0.5:
                total = first
            elif weight <= 10:
                total = first + (half_kg_units - 1) * add_05_10
            elif weight <= 15:
                total = first + (19 * add_05_10) + ((half_kg_units - 20) * add_10_to_15)
            else:
                total = first + (19 * add_05_10) + (10 * add_10_to_15) + ((half_kg_units - 30) * add_over_15)
            
            return total
    
    return None

# ==================== دعم العربية ====================

_AR_RANGE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')

def is_arabic(s: str) -> bool:
    """فحص إذا كان النص عربي"""
    return bool(s and _AR_RANGE.search(s))

def ar(s: str, force=None) -> str:
    """تشكيل النص العربي"""
    if not ARABIC_SUPPORT:
        return s
    s = s or ""
    base = force or ('R' if is_arabic(s) else 'L')
    return get_display(ar_reshape(s), base_dir=base)

def halign_for(s: str) -> str:
    """تحديد اتجاه النص"""
    return "right" if is_arabic(s) else "left"

def reshape_arabic(s: str) -> str:
    """تشكيل النص العربي مع RTL"""
    if not ARABIC_SUPPORT:
        return s or ""
    return get_display(reshape(s or ""), base_dir="R")

def ar_markup(text: str) -> str:
    """تشكيل نص يحوي Markup"""
    if not ARABIC_SUPPORT:
        return text
    parts = re.split(r'(\[/?[^\]]+\])', text or '')
    return ''.join(p if p.startswith('[') else ar(p) for p in parts)

# ==================== حقل نصي عربي مخصص ====================

class ArabicTextField(MDTextField):
    """
    حقل نص يدعم الكتابة العربية بشكل صحيح
    """
    raw = StringProperty("")
    _programmatic = False

    def insert_text(self, substring, from_undo=False):
        if from_undo or self._programmatic or not ARABIC_SUPPORT:
            return super().insert_text(substring, from_undo)
        self.raw += substring
        self.text = get_display(reshape(self.raw), base_dir='R')
        self.cursor = (len(self.text), 0)

    def do_backspace(self, from_undo=False, mode='bkspc'):
        if self._programmatic or not ARABIC_SUPPORT:
            return super().do_backspace(from_undo, mode)
        if self.raw:
            self.raw = self.raw[:-1]
            self.text = get_display(reshape(self.raw), base_dir='R')
            self.cursor = (len(self.text), 0)

    def set_text_programmatically(self, value: str):
        """تعيين النص برمجياً"""
        self._programmatic = True
        try:
            self.raw = value or ""
            if ARABIC_SUPPORT:
                self.text = get_display(reshape(self.raw), base_dir='R') if self.raw else ""
            else:
                self.text = self.raw
            self.cursor = (len(self.text), 0)
        finally:
            self._programmatic = False

# ==================== تسجيل الخط العربي ====================

def register_arabic_font():
    """تسجيل خط عربي"""
    try:
        resource_add_path("assets/fonts")
        
        candidates = [
            "Amiri-Regular.ttf",
            "Cairo-Regular.ttf",
            "NotoKufiArabic-Regular.ttf",
            "NotoNaskhArabic-Regular.ttf",
        ]
        
        font_path = None
        for fname in candidates:
            p = resource_find(fname)
            if p and os.path.exists(p):
                font_path = p
                break
        
        if not font_path:
            print("⚠️ لم يتم العثور على خط عربي في assets/fonts")
            return
        
        LabelBase.register(name="Roboto", fn_regular=font_path)
        LabelBase.register(name="Default", fn_regular=font_path)
        LabelBase.register(name="ArabicFont", fn_regular=font_path)
        print(f"✅ تم تسجيل الخط: {font_path}")
        
    except Exception as e:
        print(f"⚠️ خطأ في تسجيل الخط: {e}")

# ==================== عنصر قائمة للدروبداون ====================

class MenuListItemPy(OneLineListItem):
    """عنصر قائمة يدعم العربية"""
    def __init__(self, text: str = "", **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_style = "Body1"

Factory.register("MenuListItemPy", cls=MenuListItemPy)

# ==================== شاشة الحساب الرئيسية ====================

class ShippingScreen(MDScreen):
    result_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shipping_data = load_shipping_data()
        self.countries = set()
        
        for row in self.shipping_data:
            if row.get("Country_AR"):
                self.countries.add(row["Country_AR"])
            if row.get("Country_EN"):
                self.countries.add(row["Country_EN"])
        
        self.sorted_countries = sorted(list(self.countries))
        Clock.schedule_once(self.setup_menu)

    def setup_menu(self, *args):
        self.update_dropdown_menu(self.sorted_countries)

    def update_dropdown_menu(self, countries_list):
        """تحديث قائمة الدول"""
        items = []
        for country in countries_list:
            reshaped_name = reshape_arabic(country)
            items.append({
                "viewclass": "MenuListItemPy",
                "text": reshaped_name,
                "on_release": (lambda *_, x=country: self.select_country(x)),
                "height": dp(48),
            })

        if hasattr(self, 'menu'):
            self.menu.dismiss()

        self.menu = MDDropdownMenu(
            caller=self.ids.country_field,
            items=items,
            width=dp(280),
            max_height=dp(320),
            position="auto",
        )

    def on_country_text_change(self, instance, _text):
        """البحث أثناء الكتابة"""
        typed_raw = getattr(instance, 'raw', _text) or ""
        typed = normalize(typed_raw)

        if not typed:
            self.update_dropdown_menu(self.sorted_countries)
            return

        matches = [c for c in self.sorted_countries if typed in normalize(c)]

        if matches:
            self.update_dropdown_menu(matches)
            if hasattr(self, 'menu'):
                self.menu.open()
        else:
            if hasattr(self, 'menu'):
                self.menu.dismiss()

    def open_menu(self):
        if hasattr(self, "menu"):
            self.menu.open()

    def select_country(self, country_name):
        """اختيار دولة من القائمة"""
        field = self.ids.country_field
        if hasattr(field, "set_text_programmatically"):
            field.set_text_programmatically(country_name)
        else:
            field.text = country_name

        if hasattr(self, "menu"):
            self.menu.dismiss()

        # مسح الحقول
        self.ids.qty_abaya.text = ""
        self.ids.qty_tarha.text = ""
        self.ids.qty_niqab.text = ""

    def calculate(self):
        """حساب تكلفة الشحن"""
        try:
            field = self.ids.country_field
            country_input = getattr(field, 'raw', field.text)

            if not country_input:
                self.result_text = "[color=#ff0000]❌ فضلاً اختر الدولة[/color]"
                return

            base_price_test = calculate_shipping_cost(self.shipping_data, country_input, 0.1)
            if base_price_test is None:
                self.result_text = "[color=#ff0000]❌ لم يتم العثور على الدولة[/color]"
                return

            try:
                qty_abaya = int(self.ids.qty_abaya.text or 0)
                qty_tarha = int(self.ids.qty_tarha.text or 0)
                qty_niqab = int(self.ids.qty_niqab.text or 0)
            except ValueError:
                self.result_text = "[color=#ff0000]❌ أدخل أرقام صحيحة[/color]"
                return

            if qty_abaya == 0 and qty_tarha == 0 and qty_niqab == 0:
                self.result_text = "[color=#ff0000]❌ أدخل أعداد المنتجات[/color]"
                return

            total_weight = (
                qty_abaya * PRODUCT_WEIGHTS["عباية"] +
                qty_tarha * PRODUCT_WEIGHTS["طرحة"] +
                qty_niqab * PRODUCT_WEIGHTS["نقاب"]
            )

            base_price = calculate_shipping_cost(self.shipping_data, country_input, total_weight)
            if base_price is None:
                self.result_text = "[color=#ff0000]❌ خطأ في حساب السعر[/color]"
                return

            final_price = ceil(base_price * 1.30)
            self.result_text = ar_markup(f"[b]📦 تكلفة الشحن: {final_price} ريال سعودي[/b]")

        except Exception as e:
            self.result_text = "[color=#ff0000]❌ خطأ في الحسابات[/color]"
            print(f"❌ خطأ: {e}")

# ==================== شاشة الإعدادات ====================

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.shipping_data = load_shipping_data()
        Clock.schedule_once(self.setup_menu)

    def setup_menu(self, *args):
        items = []
        countries = set()
        
        for row in self.shipping_data:
            if row.get("Country_AR"):
                countries.add(row["Country_AR"])
            if row.get("Country_EN"):
                countries.add(row["Country_EN"])

        sorted_countries = sorted(list(countries))

        for country in sorted_countries:
            reshaped_name = reshape_arabic(country)
            items.append({
                "viewclass": "MenuListItemPy",
                "text": reshaped_name,
                "on_release": (lambda *_, x=country: self.select_country(x)),
                "height": dp(48),
            })

        self.menu = MDDropdownMenu(
            caller=self.ids.set_country_field,
            items=items,
            width=dp(280),
            max_height=dp(320),
            position="auto",
        )

    def open_menu(self):
        if hasattr(self, "menu"):
            self.menu.open()

    def select_country(self, country_name):
        """اختيار دولة وعرض معلوماتها"""
        self.ids.set_country_field.text = reshape_arabic(country_name)
        if hasattr(self, "menu"):
            self.menu.dismiss()

        country_input_norm = normalize(country_name)
        for row in self.shipping_data:
            country_en = normalize(row.get("Country_EN", ""))
            country_ar = normalize(row.get("Country_AR", ""))

            if country_input_norm == country_en or country_input_norm == country_ar:
                self.ids.first_limit.text = "0.5"
                self.ids.first_rate.text = str(row.get("FirstHalfKg", 0))
                self.ids.step_rate_05_10.text = str(row.get("Add_0_5_to_10", 0))
                self.ids.step_rate_10_15.text = str(row.get("Add_10_to_15", 0))
                self.ids.step_rate_over_15.text = str(row.get("Add_over_15", 0))
                break

    def save_changes(self):
        """عرض رسالة حول الحفظ"""
        dialog = MDDialog(
            title="حفظ الإعدادات",
            text="ملاحظة: هذه النسخة تقرأ من ملف JSON فقط. لحفظ التعديلات، يجب تعديل الملف مباشرة.",
        )
        dialog.open()

# ==================== التطبيق الرئيسي ====================

class ShippingApp(MDApp):
    def ar(self, s: str) -> str:
        """تشكيل نص عربي - للاستخدام في KV"""
        return reshape_arabic(s)

    def build(self):
        """بناء التطبيق"""
        register_arabic_font()
        
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # تحديث أنماط الخطوط
        try:
            if hasattr(self.theme_cls, 'font_styles'):
                self.theme_cls.font_styles.update({
                    "H1": ["ArabicFont", 96, False, -1.5],
                    "H2": ["ArabicFont", 60, False, -0.5],
                    "H3": ["ArabicFont", 48, False, 0],
                    "H4": ["ArabicFont", 34, False, 0.25],
                    "H5": ["ArabicFont", 24, False, 0],
                    "H6": ["ArabicFont", 20, False, 0.15],
                    "Subtitle1": ["ArabicFont", 16, False, 0.15],
                    "Subtitle2": ["ArabicFont", 14, False, 0.1],
                    "Body1": ["ArabicFont", 16, False, 0.5],
                    "Body2": ["ArabicFont", 14, False, 0.25],
                    "Button": ["ArabicFont", 14, True, 1.25],
                    "Caption": ["ArabicFont", 12, False, 0.4],
                    "Overline": ["ArabicFont", 10, True, 1.5],
                })
        except Exception as e:
            print(f"⚠️ فشل تحديث أنماط الخطوط: {e}")

        return Builder.load_file("kv/main.kv")

if __name__ == "__main__":
    print("=" * 50)
    print(f"🚀 تشغيل التطبيق على: {PLATFORM}")
    print(f"📱 وضع: {'سطح المكتب' if IS_DESKTOP else 'موبايل'}")
    print("=" * 50)
    ShippingApp().run()
