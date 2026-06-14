from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.clipboard import Clipboard
from kivy.utils import platform
import re
import subprocess

# خوارزميات حساب الـ PIN
def generate_checksum(pin7):
    if len(pin7) != 7:
        return None
    d = [int(c) for c in pin7]
    odd = sum(d[i] for i in range(0,7,2))
    even = sum(d[i] for i in range(1,7,2))
    total = (odd * 3) + even
    return str((10 - (total % 10)) % 10)

def dlink(mac):
    last = mac[3:6]
    core = ''.join(str(b) for b in last).zfill(7)[:7]
    return core + generate_checksum(core)

def thomson(mac):
    b0,b1,b2,b3,b4,b5 = mac
    pin = (b3 ^ b5) * 256 + (b2 ^ b4)
    core = str(pin % 10000000).zfill(7)
    return core + generate_checksum(core)

def arcadyan(mac):
    b3,b4,b5 = mac[3:6]
    val = (b3 * b4 * b5) % 10000000
    core = str(val).zfill(7)
    return core + generate_checksum(core)

def pirelli(mac):
    b3,b4,b5 = mac[3:6]
    xor = b3 ^ b4 ^ b5
    pin = xor * 65536
    core = str(pin % 10000000).zfill(7)
    return core + generate_checksum(core)

class WPSGeneratorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        
        # عنوان
        self.add_widget(Label(text='مولّد WPS PIN', font_size='24sp', bold=True, color=(0.1,0.3,0.6,1)))
        
        # حقل إدخال MAC
        self.add_widget(Label(text='عنوان MAC (BSSID):'))
        self.mac_input = TextInput(text='00:11:22:33:44:55', multiline=False, font_size='18sp',
                                   halign='center', size_hint_y=None, height=50)
        self.add_widget(self.mac_input)
        
        # زر الجلب التلقائي (غير مضمون على أندرويد)
        btn_fetch = Button(text='جلب تلقائي (قد لا يعمل)', size_hint_y=None, height=50,
                           background_color=(0.4,0.6,0.9,1))
        btn_fetch.bind(on_press=self.auto_fill_mac)
        self.add_widget(btn_fetch)
        
        # خيارات الخوارزميات
        self.add_widget(Label(text='اختر الخوارزميات:', font_size='18sp', bold=True))
        algo_grid = GridLayout(cols=2, size_hint_y=None, height=120, spacing=5)
        self.checks = {}
        for name in ['D-Link', 'Thomson', 'Arcadyan', 'Pirelli']:
            ch = CheckBox(active=True)
            self.checks[name] = ch
            algo_grid.add_widget(Label(text=name, halign='right'))
            algo_grid.add_widget(ch)
        self.add_widget(algo_grid)
        
        # زر التوليد
        btn_gen = Button(text='توليد الأرقام', size_hint_y=None, height=60,
                         background_color=(0.2,0.5,0.8,1), font_size='20sp')
        btn_gen.bind(on_press=self.generate)
        self.add_widget(btn_gen)
        
        # منطقة النتائج (داخل ScrollView للشاشات الصغيرة)
        self.add_widget(Label(text='الـ PINs المحتملة:', font_size='18sp', bold=True))
        self.result_label = Label(text='', font_size='16sp', halign='left', valign='top',
                                  size_hint_y=None, height=200, text_size=(400, None))
        scroll = ScrollView(size_hint=(1, 0.4))
        scroll.add_widget(self.result_label)
        self.add_widget(scroll)
        
        # زر نسخ الكل
        btn_copy = Button(text='نسخ جميع الأرقام', size_hint_y=None, height=50,
                          background_color=(0.3,0.7,0.3,1))
        btn_copy.bind(on_press=self.copy_to_clipboard)
        self.add_widget(btn_copy)
        
        # تذييل
        self.add_widget(Label(text='للأغراض التعليمية فقط', font_size='14sp', color=(1,0,0,1)))

    def validate_mac(self, mac):
        return re.match(r'^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$', mac) is not None

    def generate(self, instance):
        mac_str = self.mac_input.text.strip()
        if not self.validate_mac(mac_str):
            self.result_label.text = "صيغة MAC غير صحيحة"
            return
        mac_bytes = [int(b,16) for b in mac_str.split(':')]
        results = []
        if self.checks['D-Link'].active:
            results.append(f"D-Link   : {dlink(mac_bytes)}")
        if self.checks['Thomson'].active:
            results.append(f"Thomson  : {thomson(mac_bytes)}")
        if self.checks['Arcadyan'].active:
            results.append(f"Arcadyan : {arcadyan(mac_bytes)}")
        if self.checks['Pirelli'].active:
            results.append(f"Pirelli  : {pirelli(mac_bytes)}")
        self.result_label.text = "\n".join(results) if results else "لم تختر أي خوارزمية"

    def copy_to_clipboard(self, instance):
        txt = self.result_label.text
        if txt and "غير صحيحة" not in txt and "لم تختر" not in txt:
            Clipboard.copy(txt)
            self.result_label.text += "\n\n✓ تم النسخ"
        else:
            self.result_label.text += "\n\nلا شيء لنسخه"

    def auto_fill_mac(self, instance):
        # محاولة جلب MAC (قد لا تنجح بدون صلاحيات)
        try:
            if platform == 'android':
                # على أندرويد يمكن استخدام أوامر shell (صلاحيات محدودة)
                # هذا غالباً لن يعمل إلا بروت
                self.result_label.text = "الجلب التلقائي غير مدعوم حالياً على أندرويد"
            elif platform == 'linux':
                res = subprocess.check_output(['iwgetid','-r','-a'], text=True).strip()
                if res:
                    self.mac_input.text = res
                    self.result_label.text = "تم الجلب"
            elif platform == 'win':
                res = subprocess.check_output('netsh wlan show interfaces', shell=True, text=True)
                match = re.search(r'BSSID\s*:\s*([0-9A-Fa-f:]{17})', res)
                if match:
                    self.mac_input.text = match.group(1)
                    self.result_label.text = "تم الجلب"
            else:
                self.result_label.text = "نظام التشغيل غير مدعوم للجلب التلقائي"
        except Exception as e:
            self.result_label.text = f"فشل الجلب: {e}"

class WPSApp(App):
    def build(self):
        return WPSGeneratorLayout()

if __name__ == '__main__':
    WPSApp().run()
