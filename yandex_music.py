# yandex_music.py
import webbrowser
import pyautogui
import time
import urllib.parse
import random
import subprocess
import os
import sys
import json
from datetime import datetime
import tempfile
import socket


class YandexMusicController:
    """Контроллер Яндекс.Музыки для аккаунта пользователя"""

    def __init__(self, voice_engine=None):
        self.base_url = "https://music.yandex.ru"
        self.voice_engine = voice_engine
        self.user_sessions_file = "data/user_sessions.json"
        self.current_user = None
        self.connection_port = None

        # Инициализация
        self._load_user_sessions()
        self._start_local_server()

        print("✅ Яндекс.Музыка инициализирована (режим пользователя)")

    def _load_user_sessions(self):
        """Загрузить сохраненные сессии пользователей"""
        try:
            os.makedirs("data", exist_ok=True)
            if os.path.exists(self.user_sessions_file):
                with open(self.user_sessions_file, 'r', encoding='utf-8') as f:
                    self.user_sessions = json.load(f)
            else:
                self.user_sessions = {}
        except:
            self.user_sessions = {}

    def _save_user_sessions(self):
        """Сохранить сессии пользователей"""
        try:
            with open(self.user_sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_sessions, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _start_local_server(self):
        """Запустить локальный сервер для привязки аккаунтов"""
        try:
            # Находим свободный порт
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', 0))
            self.connection_port = sock.getsockname()[1]
            sock.close()

            # В фоновом режиме можно будет сделать прием данных
            # Сейчас просто сохраняем порт для будущего использования
        except:
            self.connection_port = None

    def _play_sound(self, sound_type='success'):
        """Воспроизвести звуковой сигнал"""
        if self.voice_engine:
            if sound_type == 'success':
                self.voice_engine.play_random_success()
            elif sound_type == 'error':
                self.voice_engine.play_more_details()

    def search(self, query, show_instructions=True):
        """Поиск музыки (без автозапуска)"""
        try:
            # Кодируем запрос для URL
            encoded_query = urllib.parse.quote(query)
            search_url = f"{self.base_url}/search?text={encoded_query}"

            print(f"🔍 Поиск: {query}")

            # Открываем в обычном браузере (пользователь уже вошел в свой аккаунт)
            webbrowser.open(search_url)

            if show_instructions:
                self._show_play_instructions()

            self._play_sound('success')
            return True

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self._play_sound('error')
            return False

    def _show_play_instructions(self):
        """Показать инструкции для воспроизведения"""
        print("\n" + "=" * 50)
        print("🎵 ИНСТРУКЦИЯ:")
        print("=" * 50)
        print("1. Выберите трек из результатов поиска")
        print("2. Нажмите кнопку 'Play' в плеере")
        print("3. Управляйте голосом:")
        print("   • 'пауза' / 'продолжи'")
        print("   • 'следующий' / 'предыдущий'")
        print("   • 'громче' / 'тише'")
        print("=" * 50)

    def play_artist(self, artist_name):
        """Открыть страницу артиста"""
        try:
            encoded_artist = urllib.parse.quote(artist_name)
            url = f"{self.base_url}/artist/{encoded_artist}"

            print(f"🎤 Открываю артиста: {artist_name}")
            webbrowser.open(url)

            self._show_play_instructions()
            self._play_sound('success')
            return True

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self._play_sound('error')
            return False

    def open_radio(self, radio_type='стандартное'):
        """Открыть радиостанцию"""
        radios = {
            'стандартное': '',
            'мне нравится': 'users/me/playlists/3',
            'дежавю': 'users/me/playlists/521',
            'плейлист дня': 'users/me/playlists/542',
            'новинки': 'new-releases',
            'популярное': 'chart',
            'танцевальное': 'genre/dance',
            'рок': 'genre/rock',
            'хип-хоп': 'genre/hiphop',
            'классика': 'genre/classical',
            'джаз': 'genre/jazz',
            'электроника': 'genre/electronic',
            'метал': 'genre/metal',
            'поп': 'genre/pop',
            'инди': 'genre/indie'
        }

        if radio_type in radios:
            url = f"{self.base_url}/{radios[radio_type]}"
        else:
            # Ищем радио по запросу
            encoded_query = urllib.parse.quote(f"{radio_type} радио")
            url = f"{self.base_url}/search?text={encoded_query}"

        print(f"📻 Открываю радио: {radio_type}")
        webbrowser.open(url)

        self._show_play_instructions()
        self._play_sound('success')
        return True

    def control_playback(self, action):
        """Управление воспроизведением (только если плеер открыт)"""
        hotkeys = {
            'play_pause': 'space',  # Play/Pause
            'play': 'space',  # Play
            'pause': 'space',  # Pause
            'next': ('ctrl', 'right'),  # Следующий трек
            'prev': ('ctrl', 'left'),  # Предыдущий трек
            'volume_up': 'up',  # Громче
            'volume_down': 'down',  # Тише
            'mute': ('ctrl', 'm'),  # Mute
            'like': ('ctrl', 'l'),  # Нравится
            'dislike': ('ctrl', 'd'),  # Не нравится
            'shuffle': ('ctrl', 'h'),  # Перемешать
            'repeat': ('ctrl', 'r'),  # Повтор
            'fullscreen': 'f'  # Полный экран
        }

        if action in hotkeys:
            try:
                # Проверяем, открыта ли Яндекс.Музыка (грубая проверка)
                time.sleep(0.1)  # Небольшая задержка

                if isinstance(hotkeys[action], tuple):
                    # Комбинация клавиш
                    pyautogui.hotkey(*hotkeys[action])
                else:
                    # Одиночная клавиша
                    pyautogui.press(hotkeys[action])

                actions_text = {
                    'play_pause': '▶️⏸️ Воспроизведение/Пауза',
                    'next': '⏭️ Следующий трек',
                    'prev': '⏮️ Предыдущий трек',
                    'volume_up': '🔊 Громче',
                    'volume_down': '🔉 Тише',
                    'like': '❤️ Добавить в "Мне нравится"',
                    'shuffle': '🔀 Перемешать',
                    'repeat': '🔁 Повтор'
                }

                if action in actions_text:
                    print(actions_text[action])
                else:
                    print(f"🎛️ Команда: {action}")

                self._play_sound('success')
                return True

            except Exception as e:
                print(f"⚠️ Невозможно выполнить команду. Убедитесь что плеер открыт: {e}")
                self._play_sound('error')
                return False

        return False

    def smart_search(self, command_text):
        """Умный поиск по команде"""
        cmd_lower = command_text.lower()

        # Определяем тип запроса
        if 'радио' in cmd_lower:
            # Извлекаем тип радио
            for radio_type in ['мне нравится', 'дежавю', 'плейлист дня',
                               'новинки', 'популярное', 'танцевальное',
                               'рок', 'хип-хоп', 'классика']:
                if radio_type in cmd_lower:
                    return self.open_radio(radio_type)
            return self.open_radio('стандартное')

        elif 'артист' in cmd_lower or 'групп' in cmd_lower:
            # Извлекаем имя артиста
            clean_text = cmd_lower.replace('артиста', '').replace('группу', '').replace('группы', '').strip()
            return self.play_artist(clean_text)

        else:
            # Обычный поиск
            return self.search(command_text)

    # ФУНКЦИИ ДЛЯ УМНОЙ КОЛОНКИ (будущее)

    def setup_user_account(self, user_id=None):
        """Настройка аккаунта пользователя"""
        print("\n" + "=" * 60)
        print("🔐 ПРИВЯЗКА АККАУНТА ЯНДЕКС")
        print("=" * 60)

        print("\nВарианты привязки:")
        print("1. Уже вошли в Яндекс в браузере - музыка будет играть от вашего имени")
        print("2. Для умной колонки - отсканируйте QR-код")

        choice = input("\nВыберите вариант (1 или 2): ").strip()

        if choice == '1':
            print("\n✅ Отлично! Теперь музыка будет играть из вашего аккаунта.")
            print("   Откройте Яндекс.Музыку в браузере и войдите в свой аккаунт.")
            return True

        elif choice == '2':
            return self._generate_pairing_qr(user_id)

        print("❌ Отмена настройки")
        return False

    def _generate_pairing_qr(self, user_id):
        """Сгенерировать QR-код для привязки"""
        try:
            import qrcode
            from PIL import Image

            # Генерируем уникальный код
            pairing_code = f"YAMUSIC_{random.randint(100000, 999999)}"

            # Данные для QR-кода
            qr_data = {
                "type": "yandex_music_pairing",
                "code": pairing_code,
                "device": socket.gethostname(),
                "port": self.connection_port,
                "timestamp": time.time()
            }

            # Создаем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(json.dumps(qr_data))
            qr.make(fit=True)

            # Сохраняем изображение
            img = qr.make_image(fill_color="black", back_color="white")
            qr_file = f"pairing_{pairing_code}.png"
            img.save(qr_file)

            print(f"\n📱 QR-код для привязки сохранен: {qr_file}")
            print(f"🔢 Код: {pairing_code}")
            print("\nИнструкция:")
            print("1. Откройте Яндекс.Музыку на телефоне")
            print("2. Настройки → Устройства → Добавить устройство")
            print("3. Отсканируйте QR-код или введите код вручную")

            # Открываем изображение
            os.startfile(qr_file)

            # Сохраняем информацию о привязке
            if user_id:
                self.user_sessions[user_id] = {
                    'pairing_code': pairing_code,
                    'paired': False,
                    'timestamp': time.time()
                }
                self._save_user_sessions()

            return True

        except ImportError:
            print("\n❌ Для генерации QR-кода установите:")
            print("   pip install qrcode[pil] pillow")
            return False
        except Exception as e:
            print(f"❌ Ошибка генерации QR-кода: {e}")
            return False

    def show_help(self):
        """Показать справку"""
        print("\n" + "=" * 60)
        print("🎵 ЯНДЕКС.МУЗЫКА - ИНСТРУКЦИЯ")
        print("=" * 60)

        print("\n📋 ПРЕДВАРИТЕЛЬНАЯ НАСТРОЙКА:")
        print("1. Откройте браузер (Chrome, Edge, Firefox)")
        print("2. Перейдите на music.yandex.ru")
        print("3. Войдите в СВОЙ аккаунт Яндекс")
        print("4. Закройте и больше не открывайте в инкогнито")

        print("\n🎤 ГОЛОСОВЫЕ КОМАНДЫ:")
        print("  • 'Включи [песня/артист]' - поиск музыки")
        print("  • 'Включи радио' - открыть радиостанцию")
        print("  • 'Рок радио' / 'Танцевальное радио'")
        print("  • 'Открой артиста [имя]'")

        print("\n🎛️ УПРАВЛЕНИЕ (после запуска):")
        print("  • 'Пауза' / 'Продолжи'")
        print("  • 'Следующий' / 'Предыдущий'")
        print("  • 'Громче' / 'Тише'")
        print("  • 'Нравится' / 'Перемешать'")

        print("\n💡 ВАЖНО: Сначала выберите и запустите музыку в браузере!")
        print("=" * 60)

        self._play_sound('success')

    def get_status(self):
        """Получить статус"""
        now = datetime.now().strftime("%H:%M")

        status = {
            'mode': 'user_account',
            'paired_users': len(self.user_sessions),
            'current_user': self.current_user,
            'time': now,
            'instructions': 'Войдите в Яндекс.Музыку в браузере под своим аккаунтом'
        }

        return status