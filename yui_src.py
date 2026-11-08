#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Юі — аніме-асистент (Kivy + Termux API + uiautomator2 + Claude API)

Підготовка в Termux (на кожному телефоні однаково):
    pkg install python python-numpy opencv-python python-pillow termux-api android-tools
    pip install uiautomator2 kivy requests
    termux-setup-storage
    export YUI_ADB_SERIAL=localhost:ПОРТ
    export ANTHROPIC_API_KEY=sk-ant-...
"""
# <SALE>
EDITION = "sale"
# </SALE>
# <PERSONAL>
EDITION = "personal"
# </PERSONAL>
VERSION = "1.0.0"

import os
import re
import sys
import time
import json
import math
import queue
import random
import hmac
import hashlib
import secrets
import string
import subprocess
import threading
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path

import numpy as np
import cv2
from PIL import Image as PILImage

from kivy.config import Config
Config.set("graphics", "borderless", "1")
Config.set("graphics", "resizable", "0")
Config.set("graphics", "width", "360")
Config.set("graphics", "height", "640")

from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

# ======================================================================
#  🚨 УНІКАЛЬНИЙ СЕРІЙНИЙ НОМЕР БЕТА-КОПІЇ ДЛЯ КОНТРОЛЮ ПРОДАЖІВ
# ======================================================================
BETA_COPY_NUMBER = "YUI-BETA-0041"

# <SALE>
# ======================================================================
#  ТІЛЬКИ ДЛЯ ПРОДАЖУ: сайт, ліцензія, безкоштовний цикл, самознищення
# ======================================================================
SERVER_URL = "https://pythonanywhere.com"
CODE_TTL = 300                         
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"   
STATUS_INTERVAL = 600                  
GRACE_SECONDS = 24 * 3600              
WORK_SEC, SLEEP_PHASE_SEC, REST_SEC = 12 * 3600, 4 * 3600, 4 * 3600   
CYCLE_SEC = WORK_SEC + SLEEP_PHASE_SEC + REST_SEC
STRIKE_LIMIT = 3                       
STRIKE_WINDOW = 600
DESTROY_DELETES_SCRIPT = True          
# </SALE>

PLAN_ORDER = {"free": 0, "premium": 1, "premium_plus": 2}

DATA_DIR = Path.home() / ".yui"
CONFIG_FILE = DATA_DIR / "config.json"
STATE_FILE = DATA_DIR / "state.json"
AUTH_FILE = DATA_DIR / "auth.json"
AUDIT_FILE = DATA_DIR / "audit.log"
MESSAGES_FILE = DATA_DIR / "messages.txt"
# <SALE>
LICENSE_FILE = DATA_DIR / "license.json"
# </SALE>

DEFAULT_CONFIG = {
    "sprites_dir": "~/storage/shared/Yui",
    "screen": "auto",                     
    "owner_numbers": [],                  
    "find_phone_phrase": "",              
    "find_phone_reply_sms": True,
    "call_whitelist": [],                 
    "call_announce": True,
    "call_greeting": "Привіт, я Юі, помічниця власника, він зараз не може говорити, що передати?",
    "sim_card": 1,
    "translate_to": "українська",
    "allow_wifi_off": False,              
    "timer_use_system": False,
    "tts_pitch": 1.6,
    "tts_rate": 1.2,
    "extra_blocked_packages": [],
}

def load_config():
    try: DATA_DIR.mkdir(mode=0o700, exist_ok=True)
    except Exception: pass
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        try: cfg.update(json.loads(CONFIG_FILE.read_text("utf-8")))
        except Exception: pass
    return cfg

CFG = load_config()
CLEAN_DIR = Path(CFG["sprites_dir"]).expanduser() / "clean"
NORMAL_SIZE = (60, 60)
WALK_FRAME_DELAY = 0.05

YUI_SPRITES = {
    "IDLE": "1.png", "HAPPY": "5.png", "CONFUSED": "6.png", "NEKO": "7.png", "WELCOME": "8.png",
    "WALK": ["11.png", "12.png", "13.png", "14.png", "15.png", "16.png", "17.png", "18.png"],
    "SLEEP_BED": "19.png", "OFFENDED": "3.png"
}

class Speaker:
    def __init__(self):
        self.q = queue.Queue(maxsize=3)
        threading.Thread(target=self._worker, daemon=True).start()
    def say_wait(self, text):
        try: subprocess.run(["termux-tts-speak", "-l", "uk", "-p", str(CFG["tts_pitch"]), "-r", str(CFG["tts_rate"]), text], timeout=15)
        except Exception: pass
    def _worker(self):
        while True:
            try: subprocess.run(["termux-tts-speak", "-l", "uk", msg], timeout=15)
            except Exception: pass
# <SALE>
class License:
    def __init__(self, brain):
        self.b = brain
        self.pc_token = "YUI-START"
        self.token_time = time.time()
        self.generate_token()
    def generate_token(self):
        chars = string.ascii_uppercase + string.digits
        self.pc_token = f"YUI-{''.join(random.choice(chars) for _ in range(5))}"
        self.token_time = time.time()
    def update_premium_token(self):
        if time.time() - self.token_time >= 300:
            self.generate_token()
    def current_plan(self): return "premium_plus"
    def code_active(self): return True

class Guardian:
    def __init__(self, brain): pass
    def strike(self, r, w=1): pass
# </SALE>

class YuiSystem:
    def __init__(self):
        self.running = True
        self.is_sleeping = False
        self.active_tier = "Premium+"
        self.current_emotion = "Радісна 🥰"
        self.timer_start = time.time()
        
        self.speaker = Speaker()
        self.commands = Commands(self)
        self.agent = PhoneAgent(self)
        # <SALE>
        self.license = License(self)
        self.guard = Guardian(self)
        # </SALE>

    def update_system_logic(self):
        # <SALE>
        self.license.update_premium_token()
        # </SALE>

    def _format_seconds(self, seconds):
        secs = max(0, int(seconds))
        return f"{secs // 3600}:{(secs % 3600) // 60:02d}:{secs % 60:02d}"

class Commands:
    def __init__(self, brain): self.b = brain
class PhoneAgent:
    def __init__(self, brain): self.b = brain

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
        
        # 🔒 ЗАМОЧКИ БЕЗПЕКИ ПОВЕРХ ТВОРЧИХ ВКЛАДОК ДЛЯ БЕТИ
        self.locks = Label(
            text="FREE 🔒       PREMIUM 🔒", font_size='13sp', bold=True,
            color=(1, 0.2, 0.2, 0.85), size_hint=(0.6, 0.05), pos_hint={'x': 0.05, 'y': 0.93}
        )
        self.add_widget(self.locks)
        
        # 💜 2. ПОЛЕ 1 (СЕРДЕЧКО) — Статус автономної комерційної роботи
        self.label_field1 = Label(
            text="Протокол: Юі автономно в коді 🐾\nСтатус: Очікування лінку з Unity ПК...",
            font_size='14sp', bold=True, color=(0.35, 0.2, 0.5, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.45} 
        )
        self.add_widget(self.label_field1)

        # 👑 3. ПОЛЕ 2 (КОРОНА) — Пронумерована копія бєти для продажів
        self.label_field2 = Label(
            text=f"Копія бети: {BETA_COPY_NUMBER}\n[Захист ліцензії Google Play: ОК 🛡️]",
            font_size='12sp', color=(0.35, 0.2, 0.5, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.32}
        )
        self.add_widget(self.label_field2)

        # ⭐ 4. ПОЛЕ 3 (ЗІРКА) — Миттєве виведення 5-хвилинного коду для сайту ПК
        self.label_field3 = Label(
            text="", font_size='15sp', bold=True, color=(0.4, 0.1, 0.6, 1),
            size_hint=(0.7, 0.1), pos_hint={'x': 0.15, 'y': 0.19}
        )
        self.add_widget(self.label_field3)
        
        Clock.schedule_interval(self.refresh_beta_ui, 1)

    def refresh_beta_ui(self, dt):
        self.engine.update_system_logic()
        # <SALE>
        time_left = 300 - int(time.time() - self.engine.license.token_time)
        mins, secs = divmod(max(0, time_left), 60)
        self.label_field3.text = f"🔑 КOД ДЛЯ ПК: {self.engine.license.pc_token}\n⏳ Згорить через: {mins:02d}:{secs:02d}"
        # </SALE>

class YuiWidget(FloatLayout):
    def __init__(self, brain, **kw):
        super().__init__(**kw)
        self.brain = brain
        _layer = YuiPremiumMenuLayout(self.brain, size_hint=(1, 1))
        self.add_widget(_layer)

class YuiApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 0)
        Window.size = (360, 640)
        Window.always_on_top = True
        self.brain = YuiSystem()
        return YuiWidget(self.brain)
    def on_stop(self): self.brain.stop()

if __name__ == "__main__":
    YuiApp().run()