import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.clock import Clock
from fractions import Fraction
import re

# --- НАСТРОЙКИ ЦВЕТОВ ---
Window.clearcolor = (0.08, 0.09, 0.1, 1) 
CARD_COLOR = (0.13, 0.15, 0.17, 1)       
ACCENT_COLOR = (0, 0.66, 1, 1)           
TEXT_COLOR = (0.95, 0.95, 0.95, 1)       
SUBTEXT_COLOR = (0.6, 0.6, 0.6, 1)       
ERROR_COLOR = (1, 0.3, 0.3, 1)

# --- ПОДКЛЮЧЕНИЕ ШРИФТА ---
try:
    from kivy.core.text import LabelBase
    LabelBase.register(name="Montserrat", fn_regular="Montserrat-Bold.ttf")
    CUSTOM_FONT = "Montserrat"
except:
    CUSTOM_FONT = "Roboto" 

# --- КАСТОМНАЯ КАРТОЧКА (Очень круглые углы) ---
class Card(BoxLayout):
    def __init__(self, bg_color, border_color=None, radius=40, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.border_color = border_color
        self.radius = radius
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            if self.border_color:
                Color(*self.border_color)
                self.line = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius), width=1.5)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.border_color:
            self.line.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], self.radius)

# --- КАСТОМНОЕ ПОЛЕ ВВОДА (Максимально круглое) ---
class RoundInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = (0, 0, 0, 0) 
        self.foreground_color = TEXT_COLOR
        self.cursor_color = ACCENT_COLOR
        self.font_name = CUSTOM_FONT
        self.font_size = '18sp' # Уменьшили шрифт
        self.halign = 'center'
        self.padding = [20, 15] # Уменьшили отступы
        
        with self.canvas.before:
            Color(0.08, 0.09, 0.1, 1) 
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[30]) # Радиус 30
            Color(0, 0.66, 1, 0.3) 
            self.line = Line(rounded_rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1], 30), width=1.2)
        
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.pos[0], self.pos[1], self.size[0], self.size[1], 30)

# --- ЭКРАН ЗАСТАВКИ ---
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        self.welcome_lbl = Label(
            text="Добро пожаловать", font_size='36sp', bold=True, font_name=CUSTOM_FONT, 
            color=ACCENT_COLOR, pos_hint={'center_x': 0.5, 'center_y': 0.7} 
        )
        made_by_lbl = Label(
            text="Сделано Zero Index Hub\nдля вас", font_size='16sp', bold=True, font_name=CUSTOM_FONT, 
            color=TEXT_COLOR, halign='center', pos_hint={'center_x': 0.5, 'center_y': 0.45} 
        )
        
        self.progress_bg = BoxLayout(size_hint=(0.6, 0.01), pos_hint={'center_x': 0.5, 'center_y': 0.2})
        with self.progress_bg.canvas.before:
            Color(*CARD_COLOR)
            self.bg_rect = RoundedRectangle(pos=self.progress_bg.pos, size=self.progress_bg.size, radius=[10])
            
        self.progress_bar = BoxLayout(size_hint=(0.0, 1.0)) 
        with self.progress_bar.canvas.before:
            Color(*ACCENT_COLOR)
            self.bar_rect = RoundedRectangle(pos=self.progress_bar.pos, size=self.progress_bar.size, radius=[10])
        
        self.progress_bg.add_widget(self.progress_bar)
        self.progress_bg.bind(pos=self.update_progress_rects, size=self.update_progress_rects)
        
        layout.add_widget(self.welcome_lbl)
        layout.add_widget(made_by_lbl)
        layout.add_widget(self.progress_bg)
        self.add_widget(layout)
        
        self.pulse_dir = 1
        self.progress_val = 0.0
        self.loading_time = 2.5
        self.fade_time = 1.5

    def update_progress_rects(self, *args):
        self.bg_rect.pos = self.progress_bg.pos
        self.bg_rect.size = self.progress_bg.size
        self.bar_rect.pos = self.progress_bar.pos
        self.bar_rect.size = self.progress_bar.size

    def on_enter(self):
        Clock.schedule_interval(self.pulse_welcome, 0.05)
        Clock.schedule_interval(self.update_progress, 1.0 / 60.0) 
        Clock.schedule_once(self.start_fade, self.loading_time)

    def pulse_welcome(self, dt):
        current_size = self.welcome_lbl.font_size
        if self.pulse_dir == 1:
            current_size += 0.2
            if current_size >= 38: self.pulse_dir = -1
        else:
            current_size -= 0.2
            if current_size <= 36: self.pulse_dir = 1
        self.welcome_lbl.font_size = current_size

    def update_progress(self, dt):
        if self.progress_val < 1.0:
            self.progress_val += (1.0 / self.loading_time) / 60.0
            if self.progress_val > 1.0: self.progress_val = 1.0
            self.progress_bar.size_hint_x = self.progress_val

    def start_fade(self, dt):
        self.manager.transition = FadeTransition(duration=self.fade_time)
        self.manager.current = 'calc'

# --- ЭКРАН КАЛЬКУЛЯТОРА ---
class CalcScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        main_layout = FloatLayout()
        
        # Уменьшили общий размер коробки (было 0.88 x 0.75, стало 0.85 x 0.65)
        self.main_box = BoxLayout(
            orientation='vertical', 
            size_hint=(0.85, 0.65), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5}, 
            spacing=20 
        )

        # Заголовок (уменьшили высоту до 0.15)
        header_box = BoxLayout(orientation='vertical', size_hint=(1, 0.15))
        title = Label(
            text="PRECISION", font_size='24sp', bold=True, font_name=CUSTOM_FONT, color=TEXT_COLOR, 
            size_hint=(1, 0.7), halign='center', valign='bottom'
        )
        subtitle = Label(
            text="CALCULATOR", font_size='14sp', font_name=CUSTOM_FONT, color=ACCENT_COLOR, 
            size_hint=(1, 0.3), halign='center', valign='top'
        )
        header_box.add_widget(title)
        header_box.add_widget(subtitle)
        self.main_box.add_widget(header_box)

        # Карточка ввода (уменьшили высоту до 0.2, радиус 40)
        input_card = Card(CARD_COLOR, border_color=None, radius=40, size_hint=(1, 0.2), padding=[0, 0])
        
        self.entry = RoundInput(
            hint_text="К примеру: 1/2 + 3/4 * 2", 
            hint_text_color=(0.4, 0.4, 0.4, 1)
        )
        
        input_card.add_widget(self.entry)
        self.main_box.add_widget(input_card)

        # Карточка кнопки (уменьшили высоту до 0.12, радиус 40)
        btn_card = Card(bg_color=ACCENT_COLOR, radius=40, size_hint=(1, 0.12))
        self.btn = Button(
            text="ВЫЧИСЛИТЬ", font_size='18sp', bold=True, font_name=CUSTOM_FONT,
            background_color=(0,0,0,0), background_normal='', background_down='',
            color=Window.clearcolor, 
        )
        self.btn.bind(on_press=self.calculate)
        btn_card.add_widget(self.btn)
        self.main_box.add_widget(btn_card)

        # Карточка результата (уменьшили высоту до 0.25, радиус 40)
        self.result_card = Card(CARD_COLOR, border_color=(0, 0.66, 1, 0.3), radius=40, size_hint=(1, 0.25), padding=[15, 15])
        
        self.result_label = Label(
            text="ГОТОВ К РАБОТЕ", font_size='24sp', bold=True, font_name=CUSTOM_FONT, color=SUBTEXT_COLOR,
            halign='center', valign='middle'
        )
        self.result_label.bind(size=self.result_label.setter('text_size'))
        self.result_card.add_widget(self.result_label)
        self.main_box.add_widget(self.result_card)

        main_layout.add_widget(self.main_box)
        self.add_widget(main_layout)

    def calculate(self, instance):
        expr = self.entry.text.strip()
        if not expr:
            self.show_error("ВВЕДИТЕ ЧИСЛА")
            return

        expr = expr.replace("×", "*").replace("÷", "/").replace(",", ".")

        try:
            tokens = re.findall(r'(\d+/\d+|\d+\.\d+|\d+)', expr)
            new_expr = expr
            for token in tokens:
                if '/' in token:
                    num, den = token.split('/')
                    new_expr = new_expr.replace(token, f"Fraction({num}, {den})")
                elif '.' in token:
                    new_expr = new_expr.replace(token, f"Fraction('{token}')")
                else:
                    new_expr = new_expr.replace(token, f"Fraction({token})")

            result = eval(new_expr)

            if result.denominator == 1:
                final_text = f"{result.numerator}"
            else:
                final_text = f"{result.numerator}/{result.denominator}\n(≈ {float(result):.3f})"

            self.result_label.text = final_text
            self.result_label.color = ACCENT_COLOR

        except ZeroDivisionError:
            self.show_error("ДЕЛЕНИЕ НА НОЛЬ")
        except Exception:
            self.show_error("ОШИБКА ВВОДА")

    def show_error(self, msg):
        self.result_label.text = msg
        self.result_label.color = ERROR_COLOR

# --- ГЛАВНОЕ ПРИЛОЖЕНИЕ ---
class CalculatorApp(App):
    def build(self):
        self.title = "Precision Calculator"
        sm = ScreenManager(transition=FadeTransition(duration=0)) 
        sm.add_widget(SplashScreen(name='splash'))
        sm.add_widget(CalcScreen(name='calc'))
        return sm

if __name__ == '__main__':
    CalculatorApp().run()
