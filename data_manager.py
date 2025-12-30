import json
import os
import sys


class DataManager:
    def __init__(self, data_file=None):
        # Определяем правильный путь
        if data_file is None:
            if hasattr(sys, '_MEIPASS'):
                # В exe данные рядом с exe
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
                self.data_file = os.path.join(exe_dir, "data", "savedata.json")
            else:
                # В исходном коде
                self.data_file = "data/savedata.json"
        else:
            self.data_file = data_file

        # Загружаем данные сразу при запуске
        self.data = self._load_data()

        # Убедимся что структура полная
        self._ensure_data_structure()

    def _load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем папку если не существует
                os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
                default_data = self._get_default_data()
                self._save_data(default_data)
                return default_data
        except Exception as e:
            print(f"⚠️ Ошибка загрузки данных: {e}")
            # Возвращаем данные по умолчанию
            return self._get_default_data()

    def _get_default_data(self):
        return {
            "assistant": {
                "name": "Джиминитрон", # Это первое что пришло в голову
                "is_temp_name": False,
                "default_name": "Джиминитрон"
            },
            "voice": {
                "gender": "male",
                "rate": 180,
                "volume": 0.8,
                "is_temp_voice": False,
                "default_gender": "male"
            },
            "language": {
                "current": "RU",
                "default": "RU",
                "is_temp_language": False
            },
            "ai": {
                "api_key": "",
                "api_url": "https://api.openai.com/v1/chat/completions",
                "model": "gpt-3.5-turbo",
                "show_text_response": True
            },
            "websites": {
                "youtube": "https://youtube.com",
                "ютуб": "https://youtube.com",
                "google": "https://google.com",
                "гугл": "https://google.com",
                "vk": "https://vk.com",
                "вк": "https://vk.com",
                "яндекс": "https://yandex.ru",
                "yandex": "https://yandex.ru",
                "github": "https://github.com",
                "гитхаб": "https://github.com"
            },
            "programs": {
                "калькулятор": "calc.exe",
                "блокнот": "notepad.exe",
                "пайнт": "mspaint.exe"
            },
            "wallpapers": {
                "космос": "wallpaper1.png",
                "природа": "wallpaper2.png",
                "абстракция": "wallpaper3.png"
            },
            "security": {
                "red_code": "2011_03_21",
                "yellow_code": "9002"
            },
        }

    def _save_data(self, data):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения данных: {e}")
            return False

    def _ensure_data_structure(self):
        default_data = self._get_default_data()
        needs_save = False

        for section, default_values in default_data.items():
            if section not in self.data:
                self.data[section] = default_values
                needs_save = True
            else:
                # Проверяем подполя подполя аххахахах почему это смешно
                for key, value in default_values.items():
                    if key not in self.data[section]:
                        self.data[section][key] = value
                        needs_save = True

        if needs_save:
            self._save_data(self.data)

    # Разные схемы

    def get_assistant_name(self):
        return self.data.get('assistant', {}).get('name', 'Джиминитрон')

    def set_assistant_name(self, name, permanent=False):
        if 'assistant' not in self.data:
            self.data['assistant'] = {}

        self.data['assistant']['name'] = name
        self.data['assistant']['is_temp_name'] = not permanent
        if permanent:
            self.data['assistant']['default_name'] = name

        return self._save_data(self.data)

    def get_voice_settings(self):
        return self.data.get('voice', {})

    def set_voice_gender(self, gender, permanent=False):
        if 'voice' not in self.data:
            self.data['voice'] = {}

        self.data['voice']['gender'] = gender
        self.data['voice']['is_temp_voice'] = not permanent
        if permanent:
            self.data['voice']['default_gender'] = gender

        return self._save_data(self.data)

    def get_language(self):
        return self.data.get('language', {}).get('current', 'RU')

    def set_language(self, language, permanent=False):
        if language.upper() in ['RU', 'EN']:
            if 'language' not in self.data:
                self.data['language'] = {}

            self.data['language']['current'] = language.upper()
            self.data['language']['is_temp_language'] = not permanent
            if permanent:
                self.data['language']['default'] = language.upper()

            return self._save_data(self.data)
        return False

    def get_website(self, site_name):
        return self.data.get('websites', {}).get(site_name.lower())

    def get_program(self, program_name):
        return self.data.get('programs', {}).get(program_name.lower())

    def get_wallpaper(self, wallpaper_name):
        return self.data.get('wallpapers', {}).get(wallpaper_name.lower())

    def get_ai_settings(self):
        return self.data.get('ai', {
            'api_key': '',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'model': 'gpt-3.5-turbo',
            'show_text_response': True
        })

    def update_ai_settings(self, api_key=None, model=None, show_text_response=None):
        try:
            if 'ai' not in self.data:
                self.data['ai'] = self.get_ai_settings()

            if api_key is not None:
                self.data['ai']['api_key'] = api_key
            if model is not None:
                self.data['ai']['model'] = model
            if show_text_response is not None:
                self.data['ai']['show_text_response'] = show_text_response

            return self._save_data(self.data)
        except Exception as e:
            print(f"❌ Ошибка обновления настроек AI: {e}")
            return False

    def add_custom_website(self, name, url):
        if 'websites' not in self.data:
            self.data['websites'] = {}

        self.data['websites'][name.lower()] = url
        return self._save_data(self.data)

    def add_custom_program(self, name, path):
        if 'programs' not in self.data:
            self.data['programs'] = {}

        self.data['programs'][name.lower()] = path
        return self._save_data(self.data)

    def get_custom_websites(self):
        return self.data.get('websites', {})

    def get_custom_programs(self):
        return self.data.get('programs', {})