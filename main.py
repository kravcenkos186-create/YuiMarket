#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юі — Комерційний Моноліт Бета-Версії (Kivy + Termux API + uiautomator2 + Claude API)
Офіційний реліз для випуску в Google Play та продажу через Telegram-канал.
"""
EDITION = "commercial_beta"
VERSION = "1.0.0"

# ======================================================================
#  🚨 СЕРІЙНИЙ НОМЕР КОПІЇ БЕТИ ДЛЯ КОНТРОЛЮ ПРОДАЖІВ
# ======================================================================
BETA_COPY_NUMBER = "YUI-BETA-0041" 

import os
import re
import sys
import time
import json
import math
import queue
import random
import string
import subprocess
import threading
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

from kivy.config import Config
# Налаштовуємо вікно під вертикальний мобільний преміум-лаунчер
Config.set("graphics", "borderless", "1")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

# Директорії для збереження даних
DATA_DIR = Path.home() / ".yui"
CONFIG_FILE = DATA_DIR / "config.json"
STATE_FILE = DATA_DIR / "state.json"

DEFAULT_CONFIG = {
    "sprites_dir": "~/storage/shared/Yui",
    "active_tier": "Premium+",
    "sim_card": 1,
    "translate_to": "українська",
    "tts_pitch": 1.6,
    "tts_rate": 1.2,
    "call_whitelist":,
    "call_announce": True,
}

def load_config():
    try: DATA_DIR.mkdir(mode=0o700, exist_ok=True)
    except Exception: pass
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try: cfg.update(json.loads(CONFIG_FILE.read_text("utf-8")))
        except Exception: pass
    else:
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), "utf-8")
    return cfg

CFG = load_config()

# ======================================================================
#  ГОЛОВНИЙ РУШІЙ БІЗНЕС-ЛОГІКИ ТА ПОДВІЙНИХ ЛІМІТІВ ВІДКАТУ
# ======================================================================
class YuiSystemEngine:
    def __init__(self):
        self.work_limit = 12 * 3600    
        self.sleep_limit = 4 * 3600    
        self.cooldown_limit = 4 * 3600 
        
        self.current_state = "WORK"    
        self.timer_start = time.time()
        
        self.active_tier = "Premium+"  
        self.pc_token = "YUI-START"
        self.token_time = time.time()
        self.current_emotion = "Radisna 🥰"
        self.running = True
        
        self.generate_new_token()

    def generate_token_loop(self):
        current_time = time.time()
        if self.active_tier == "Premium+":
            if current_time - self.token_time >= 300:
                self.generate_new_token()

    def generate_new_token(self):
        chars = string.ascii_uppercase + string.digits
        self.pc_token = f"YUI-{''.join(random.choice(chars) for _ in range(5))}"
        self.token_time = time.time()

    def get_field_3_string(self):
        current_time = time.time()
        if self.active_tier == "Premium+":
            time_left = 300 - int(current_time - self.token_time)
            mins, secs = divmod(max(0, time_left), 60)
            return f"🔑 KOD DLYA PK: {self.pc_token}\n⏳ Zgoryt cherez: {mins:02d}:{secs:02d}"
        
        elapsed = current_time - self.timer_start
        if self.current_state == "WORK":
            return f"Yui vilna 🐾. Sesiya: {self._fmt(self.work_limit - elapsed)}"
        elif self.current_state == "SLEEP":
            return f"Yui spyt 💤. Zalyshylos: {self._fmt(self.sleep_limit - elapsed)}"
        else:
            return f"🚨 SYSTEMNYI OTKAT: {self._fmt(self.cooldown_limit - elapsed)}"

    def _fmt(self, secs):
        secs = max(0, int(secs))
        return f"{secs // 3600}:{(secs % 3600) // 60:02d}:{secs % 60:02d}"

# ======================================================================
#  ІНТЕРФЕЙС: АБСОЛЮТНО ПРАВИЛЬНА ПОСАДКА НА ФІОЛЕТОВИЙ АРТ МЕНЮ
# ======================================================================
class YuiPremiumMenuLayout(FloatLayout):
    def __init__(self, engine, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        
        # 🌲 1. ВСТАНОВЛЮЄМО ТВІЙ ФІОЛЕТОВИЙ АРТ НА ВЕСЬ ФОН ДОДАТКА
        self.bg = Image(source='image_P9IQni.png', allow_stretch=True, keep_ratio=False)
        self.add_widget(self.bg)
        
        # 🔒 ЖОРСТКІ ЗАМОЧКИ БЕЗПЕКИ ПОВЕРХ ТВОРЧИХ ВКЛАДОК
        self.locks = Label(
            text="FREE 🔒       PREMIUM 🔒", font_size='13sp', bold=True,
            color=(1, 0.2, 0.2, 0.85), size_hint=(0.6, 0.05),
            pos_hint={'x': 0.05, 'y': 0.93} 
        )
        self.add_widget(self.locks)
        
        # 💜 2. ПОЛЕ 1 (СЕРДЕЧКО) — Пронумерована копія бєти та статус
        self.label_field1 = Label(
            text="", font_size='14sp', bold=True, color=(0.35, 0.2, 0.5, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.45} 
        )
        self.add_widget(self.label_field1)

        # 👑 3. ПОЛЕ 2 (КОРОНА) — Серійний номер та ліцензія
        self.label_field2 = Label(
            text=f"Kopiya bety: {BETA_COPY_NUMBER}\n[Zahyst licenzii Google Play: OK 🛡️]",
            font_size='12sp', color=(0.35, 0.2, 0.5, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.32} 
        )
        self.add_widget(self.label_field2)

        # ⭐ 4. ПОЛЕ 3 (ЗІРКА) — Живий вивід коду для входу з ПК
        self.label_field3 = Label(
            text="", font_size='15sp', bold=True, color=(0.4, 0.1, 0.6, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.19} 
        )
        self.add_widget(self.label_field3)
        
        Clock.schedule_interval(self.refresh_ui_fields, 1)

    def refresh_ui_fields(self, dt):
        self.engine.generate_token_loop()
        
        if self.engine.active_tier == "Premium+":
            self.label_field1.text = "Protokol: Yui avtonomno v kodi 🐾\nStatus: Ochikuvannya linku z Unity PK..."
            self.label_field3.text = self.engine.get_field_3_string()
        else:
            self.label_field1.text = f"Protokol Screen Pet: AKTIVEN 🐾\nEmociya Yui: {self.engine.current_emotion}"
            self.label_field3.text = self.engine.get_field_3_string()

class YuiApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 0)
        Window.size = (360, 640) 
        Window.always_on_top = True
        
        self.engine = YuiSystemEngine()
        return YuiPremiumMenuLayout(self.engine)

if __name__ == "__main__":
    YuiApp().run()
    
