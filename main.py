from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import urllib.request
import json
import threading

SERVER_URL = "https://yuisensei.pythonanywhere.com"

class YuiApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        layout.add_widget(Label(text="Yui AI", font_size=32))
        self.status = Label(text="Статус: перевірка...")
        layout.add_widget(self.status)

        btn = Button(text="Отримати код для ПК")
        btn.bind(on_press=self.get_code)
        layout.add_widget(btn)

        Clock.schedule_once(lambda dt: self.check_server(), 1)
        return layout

    def check_server(self):
        self.status.text = "Yui запущена"

    def get_code(self, instance):
        self.status.text = "Запит коду..."
        self.status.text = "Потрібно підключити серверний запит"

YuiApp().run()
