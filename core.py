import self
import speech_recognition as sr
import time
import webbrowser
import shutil
import subprocess
import tempfile
import os
import sys
import re
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from data_manager import DataManager
from voice_engine import VoiceEngine
from volume_controller import VolumeController
from advanced_features import AdvancedFeatures

class VolumeController:

    def __init__(self):
        self.volume_interface = None
        self._init_volume_interface()

    def _init_volume_interface(self):
        try:
            # Устройство воспроизведения по умолчанию
            devices = AudioUtilities.GetSpeakers()

            # Активируем менюшку управления громкостью
            interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None
            )

            # Приводим к правильному типу
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            print("✅ Интерфейс громкости инициализирован")

        except Exception as e:
            print(f"⚠️ Не удалось инициализировать интерфейс громкости: {e}")
            self.volume_interface = None

    def get_current_volume(self):
        if self.volume_interface:
            try:
                current = self.volume_interface.GetMasterVolumeLevelScalar()
                return int(current * 100)
            except:
                pass
        return 50  # Предполагаем 50%

    def set_volume(self, percent):

        # Ограничиваем диапазон
        percent = max(0, min(100, percent))

        if self.volume_interface:
            try:
                # Устанавливаем громкость
                self.volume_interface.SetMasterVolumeLevelScalar(percent / 100.0, None)
                print(f"✅ Громкость установлена на {percent}%")
                return True
            except Exception as e:
                print(f"❌ Ошибка установки громкости: {e}")
                return False
        else:
            # Резервный метод
            return self._set_volume_fallback(percent)

    def increase_volume(self, amount):
        current = self.get_current_volume()
        new_volume = min(100, current + amount)
        return self.set_volume(new_volume)

    def decrease_volume(self, amount):
        current = self.get_current_volume()
        new_volume = max(0, current - amount)
        return self.set_volume(new_volume)

    def _set_volume_fallback(self, percent):
        print(f"⚠️ Использую резервный метод: {percent}%")

        try:
            # Сбрасываем к минимуму
            for _ in range(50):
                pyautogui.press('volumedown')

            # Устанавливаем приблизительно
            steps = percent // 2  # каждое нажатие ~2%
            for _ in range(steps):
                pyautogui.press('volumeup')
                pyautogui.sleep(0.01)

            print(f"✅ Приблизительно установлено: {percent}%")
            return True

        except Exception as e:
            print(f"❌ Ошибка резервного метода: {e}")
            return False

class AIAssistant:
    def __init__(self):
        print("Инициализация помощника...")
        self.data_manager = DataManager()
        self.voice_engine = VoiceEngine()
        self.volume_controller = VolumeController()
        self.advanced_features = AdvancedFeatures(self.data_manager, self.voice_engine)

        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

        self.is_listening = True
        self.is_awake = False
        self.assistant_name = self.data_manager.get_assistant_name()
        self.waiting_for_details = False
        self.current_context = None

        print(f"Помощник {self.assistant_name} готов к работе!")
        self.voice_engine.play_welcome()

    self.volume_controller = VolumeController()

    def handle_volume(self, command):
        print(f"🔊 Команда: {command}")

        # Ищем числа в команде
        numbers = re.findall(r'\d+', command.lower())
        cmd_lower = command.lower()

        # Слова для определения типа команды
        has_set = any(word in cmd_lower for word in ["сделай", "поставь", "установи", "громкость", "звук"])
        has_increase = any(word in cmd_lower for word in ["прибавь", "увеличь", "добавь", "плюс"])
        has_decrease = any(word in cmd_lower for word in ["убавь", "уменьши", "минус", "отними"])

        if numbers:
            number = int(numbers[0])

            if has_increase:
                # Прибавить на X процентов да тот самый X хоть где то пригодился
                self.voice_engine.play_random_success()
                if self.volume_controller.increase_volume(number):
                    print(f"📢 Прибавлено на {number}%")
                else:
                    self.voice_engine.play_more_details()

            elif has_decrease:
                # Убавить на X процентов
                self.voice_engine.play_random_success()
                if self.volume_controller.decrease_volume(number):
                    print(f"📢 Убавлено на {number}%")
                else:
                    self.voice_engine.play_more_details()

            elif has_set:
                # Установить на X процентов
                self.voice_engine.play_random_success()
                if self.volume_controller.set_volume(number):
                    print(f"📢 Установлено на {number}%")
                else:
                    self.voice_engine.play_more_details()

            else:
                # По умолчанию установить на X процентов
                self.voice_engine.play_random_success()
                if self.volume_controller.set_volume(number):
                    print(f"📢 Громкость {number}%")
                else:
                    self.voice_engine.play_more_details()

        else:
            # Команды без чисел
            if has_increase:
                # Прибавить по умолчанию
                self.voice_engine.play_random_success()
                if self.volume_controller.increase_volume(10):
                    print("📢 Громкость увеличена")
                else:
                    self.voice_engine.play_more_details()

            elif has_decrease:
                # Убавить по умолчанию
                self.voice_engine.play_random_success()
                if self.volume_controller.decrease_volume(10):
                    print("📢 Громкость уменьшена")
                else:
                    self.voice_engine.play_more_details()

            elif any(word in cmd_lower for word in ["максимум", "на полную", "100"]):
                # Максимальная громкость
                self.voice_engine.play_random_success()
                if self.volume_controller.set_volume(100):
                    print("📢 Максимальная громкость")
                else:
                    self.voice_engine.play_more_details()

            elif any(word in cmd_lower for word in ["минимум", "выключи звук", "0", "ноль"]):
                # Минимальная громкость
                self.voice_engine.play_random_success()
                if self.volume_controller.set_volume(0):
                    print("📢 Звук выключен")
                else:
                    self.voice_engine.play_more_details()

            elif any(word in cmd_lower for word in ["половина", "50", "средняя"]):
                # Половина громкости
                self.voice_engine.play_random_success()
                if self.volume_controller.set_volume(50):
                    print("📢 Половина громкости")
                else:
                    self.voice_engine.play_more_details()

            else:
                # Показать текущую громкость
                current = self.volume_controller.get_current_volume()
                print(f"📢 Текущая громкость: {current}%")
                self.voice_engine.play_random_success()

    def listen_for_wake_word(self):
        try:
            print("🔊 Слушаю...", end="\r")
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
            text = self.recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"🎯 Распознано: {text}")

            if self.assistant_name.lower() in text:
                if text.strip() == self.assistant_name.lower():
                    self.wake_up(greeting=True)
                else:
                    command = text.replace(self.assistant_name.lower(), "").strip()
                    self.wake_up()
                    self.process_command(command)
                return True
        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        return False

    def wake_up(self, greeting=False):
        self.is_awake = True
        if greeting:
            self.voice_engine.play_welcome()
            print("👋 Помощник приветствует")
        else:
            self.voice_engine.play_random_success()
            print("✅ Помощник активирован")

    def listen_for_command(self, extended_timeout=False):
        try:
            timeout = 10 if extended_timeout else 6
            print("🎤 Слушаю команду...")

            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=7 if extended_timeout else 5
                )

            command = self.recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"📝 Команда: {command}")
            return command

        except sr.WaitTimeoutError:
            if self.waiting_for_details:
                print("⏰ Таймаут ожидания уточнения")
                self.waiting_for_details = False
                self.current_context = None
            else:
                print("⏰ Таймаут ожидания команды")
            self.is_awake = False
        except sr.UnknownValueError:
            print("❓ Не удалось распознать команду")
            if not self.waiting_for_details:
                self.voice_engine.play_more_details()
            self.is_awake = False
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            self.is_awake = False
        return None

    def process_command(self, command):
        if not command:
            return

        print(f"🔄 Обрабатываю: {command}")

        if self.waiting_for_details and self.current_context:
            self.process_with_context(command)
            return

        # Команды с изменениями
        if any(word in command for word in ["переключи голос", "смени голос", "измени голос"]):
            if "мужск" in command:
                self.voice_engine.change_voice_gender("male", False)
            elif "женск" in command:
                self.voice_engine.change_voice_gender("female", False)
            else:
                self.ask_for_details("голос", "Укажите пол голоса: мужской или женский")

        elif any(word in command for word in ["открой", "зайди на", "открыть"]):
            self.handle_open_command(command)

        elif any(word in command for word in ["выключи пк", "выключи компьютер", "заверши работу"]):
            self.handle_shutdown(command)

        elif any(word in command for word in ["отмени выключение", "отмена выключения", "отмени завершение"]):
            self.cancel_shutdown()

        elif any(word in command for word in ["отмени перезагрузку", "отмена перезагрузки"]):
            self.cancel_shutdown()  # Та же команда отменяет и перезагрузку

        elif any(word in command for word in ["запусти", "открой программу", "запусти программу"]):
            self.handle_program_command(command)

        elif any(word in command for word in ["громкость", "звук"]):
            self.handle_volume(command)

        elif any(word in command for word in ["перезагрузи пк", "перезагрузи компьютер", "рестарт"]):
            self.handle_restart(command)

        elif any(word in command for word in ["обои", "фон рабочего стола"]):
            self.handle_wallpaper(command)

        elif any(word in command for word in ["смени имя", "измени имя", "новое имя"]):
            self.handle_change_name(command)

        elif any(word in command for word in ["режим консоли", "консоль", "текстовый режим"]):
            self.start_console_mode()

        # заменил "код" на "кот" да костыльно ну че
        elif "кот красный" in command:
            self.handle_red_code()

        elif "кот жёлтый" in command:
            self.voice_engine.play_random_success()
            self.shutdown()

        elif any(word in command for word in ["кот зеленый", "кот зелёный"]):
            self.handle_green_code()

        # заменил "режим ии" на "режим искусственный интеллект" да тоже костыль и че
        elif any(word in command for word in ["режим искусственный интеллект", "искусственный интеллект", "задай вопрос"]):
            self.handle_ai_mode(command)

        elif any(word in command for word in ["запиши идею", "сохрани идею", "запомни идею"]):
            self.handle_record_idea(command)

        elif any(word in command for word in ["запись", "запиши звук"]):
            self.voice_engine.play_random_success()
            print("🎙️ Запись звука активирована")

        elif any(word in command for word in ["найди в интернете", "поиск в интернете", "найди информацию"]):
            self.handle_internet_search(command)

        elif any(word in command for word in ["поменяй язык", "смени язык", "измени язык"]):
            if "русск" in command:
                self.data_manager.set_language("RU", False)
                self.voice_engine.play_random_success()
            elif "английск" in command:
                self.data_manager.set_language("EN", False)
                self.voice_engine.play_random_success()
            else:
                self.ask_for_details("язык", "Укажите язык: русский или английский")

        elif any(word in command for word in ["привет", "здравствуй", "добрый день", "доброе утро"]):
            self.voice_engine.play_welcome()

        elif any(word in command for word in ["спасибо", "благодарю", "молодец"]):
            self.voice_engine.play_random_success()

        elif any(word in command for word in ["пауза", "продолжи", "включи музыку", "плейлист", "играй"]):
            self.advanced_features.handle_music_command(command)

            # Добавление сайтов/программ
        elif any(word in command for word in ["добавь сайт", "добавь программу", "добавь приложение"]):
            self.advanced_features.handle_add_item(command)

            # Справка
        elif "музыка помощь" in command or "помощь музыка" in command:
            self.advanced_features.show_music_help()
        elif "добавление помощь" in command or "помощь добавление" in command:
            self.advanced_features.show_add_help()

            # Показать данные людишек
        elif "мои сайты" in command:
            self.advanced_features.list_custom_websites()
        elif "мои программы" in command:
            self.advanced_features.list_custom_programs()
        elif any(word in command for word in ["таймер", "будильник", "напомни", "осталось"]):
            self.advanced_features.handle_timer_command(command)

        # Музыкальные команды
        elif any(word in command for word in ["пауза", "продолжи", "включи музыку", "плейлист", "играй"]):
            self.advanced_features.handle_music_command(command)

        # Добавление сайтов или программ
        elif any(word in command for word in ["добавь сайт", "добавь программу", "добавь приложение"]):
            self.advanced_features.handle_add_item(command)

        # Справка
        elif "расширенная помощь" in command or "функции помощь" in command:
            self.advanced_features.show_help()


        else:
            print(f"❓ Неизвестная команда: {command}")
            self.voice_engine.play_more_details()

    def ask_for_details(self, context, message):
        self.waiting_for_details = True
        self.current_context = context
        print(f"❓ {message}")
        self.voice_engine.play_more_details()

    def process_with_context(self, details):
        context = self.current_context
        self.waiting_for_details = False
        self.current_context = None

        if context == "голос":
            if "мужск" in details:
                self.voice_engine.change_voice_gender("male", False)
            elif "женск" in details:
                self.voice_engine.change_voice_gender("female", False)
            else:
                self.voice_engine.play_more_details()

        elif context == "сайт":
            if details and self.open_website(details):
                self.voice_engine.play_random_success()
            else:
                self.voice_engine.play_more_details()

        elif context == "программа":
            if details and self.open_program(details):
                self.voice_engine.play_random_success()
            else:
                self.voice_engine.play_more_details()

        elif context == "обои":
            if details and self.change_wallpaper(details):
                self.voice_engine.play_random_success()
            else:
                self.voice_engine.play_more_details()

        elif context == "имя":
            if details:
                self.data_manager.set_assistant_name(details, False)
                self.assistant_name = details
                self.voice_engine.play_random_success()
            else:
                self.voice_engine.play_more_details()

        elif context == "язык":
            if "русск" in details:
                self.data_manager.set_language("RU", False)
                self.voice_engine.play_random_success()
            elif "английск" in details:
                self.data_manager.set_language("EN", False)
                self.voice_engine.play_random_success()
            else:
                self.voice_engine.play_more_details()

    def handle_open_command(self, command):
        sites = {
            "youtube": "https://youtube.com",
            "ютуб": "https://youtube.com",
            "google": "https://google.com",
            "гугл": "https://google.com",
            "vk": "https://vk.com",
            "вк": "https://vk.com",
            "яндекс": "https://yandex.ru",
            "yandex": "https://yandex.ru",
            "github": "https://github.com",
            "гитхаб": "https://github.com",
            "stackoverflow": "https://stackoverflow.com",
            "стек оверфлоу": "https://stackoverflow.com",
            "wikipedia": "https://wikipedia.org",
            "википедия": "https://wikipedia.org",
            "notion": "https://notion.so",
            "ноушен": "https://notion.so",
            "figma": "https://figma.com",
            "фигма": "https://figma.com",
            "drive": "https://drive.google.com",
            "гугл драйв": "https://drive.google.com",
            "chatgpt": "https://chat.openai.com",
            "чат жпт": "https://chat.openai.com",
            "deepseek": "https://chat.deepseek.com",
            "дипсик": "https://chat.deepseek.com",
            "telegram": "https://web.telegram.org",
            "телеграм": "https://web.telegram.org",
            "whatsapp": "https://web.whatsapp.com",
            "ватсап": "https://web.whatsapp.com",
            "discord": "https://discord.com",
            "дискорд": "https://discord.com",
            "reddit": "https://reddit.com",
            "реддит": "https://reddit.com",
            "spotify": "https://open.spotify.com",
            "спотифай": "https://open.spotify.com",
            "netflix": "https://netflix.com",
            "нетфликс": "https://netflix.com",
            "twitch": "https://twitch.tv",
            "твич": "https://twitch.tv",
            "amazon": "https://amazon.com",
            "амазон": "https://amazon.com",
            "aliexpress": "https://aliexpress.com",
            "алиэкспресс": "https://aliexpress.com",
            "ozon": "https://ozon.ru",
            "озон": "https://ozon.ru",
            "wildberries": "https://wildberries.ru",
            "вайлдбериз": "https://wildberries.ru",
            "avito": "https://avito.ru",
            "авито": "https://avito.ru",
            "hh": "https://hh.ru",
            "хедхантер": "https://hh.ru",
            "linkedin": "https://linkedin.com",
            "линкедин": "https://linkedin.com",
            "instagram": "https://instagram.com",
            "инстаграм": "https://instagram.com",
            "twitter": "https://x.com",
            "твиттер": "https://x.com",
            "facebook": "https://facebook.com",
            "фейсбук": "https://facebook.com",
            "tiktok": "https://tiktok.com",
            "тикток": "https://tiktok.com",
            "pinterest": "https://pinterest.com",
            "пинтерест": "https://pinterest.com",
            "medium": "https://medium.com",
            "медиум": "https://medium.com",
            "udemy": "https://udemy.com",
            "юдеми": "https://udemy.com",
            "coursera": "https://coursera.org",
            "курсера": "https://coursera.org",
            "khanacademy": "https://khanacademy.org",
            "хан академи": "https://khanacademy.org",
            "duolingo": "https://duolingo.com",
            "дуолинго": "https://duolingo.com",
            "deepl": "https://deepl.com",
            "дипл": "https://deepl.com",
            "translate": "https://translate.google.com",
            "гугл переводчик": "https://translate.google.com",
            "maps": "https://maps.google.com",
            "гугл карты": "https://maps.google.com",
            "weather": "https://weather.com",
            "погода": "https://weather.com",
            "calendar": "https://calendar.google.com",
            "гугл календарь": "https://calendar.google.com",
            "gmail": "https://mail.google.com",
            "гмейл": "https://mail.google.com",
            "outlook": "https://outlook.live.com",
            "аутлук": "https://outlook.live.com",
            "dropbox": "https://dropbox.com",
            "дропбокс": "https://dropbox.com",
            "trello": "https://trello.com",
            "трелло": "https://trello.com",
            "slack": "https://slack.com",
            "слак": "https://slack.com",
            "zoom": "https://zoom.us",
            "зум": "https://zoom.us",
            "meet": "https://meet.google.com",
            "гугл мит": "https://meet.google.com",
            "canva": "https://canva.com",
            "канва": "https://canva.com",
            "unsplash": "https://unsplash.com",
            "ансплеш": "https://unsplash.com",
            "flaticon": "https://flaticon.com",
            "флатикон": "https://flaticon.com",
            "fontawesome": "https://fontawesome.com",
            "фонт оусом": "https://fontawesome.com",
            "codepen": "https://codepen.io",
            "код пен": "https://codepen.io",
            "replit": "https://replit.com",
            "реплит": "https://replit.com",
            "leetcode": "https://leetcode.com",
            "литкод": "https://leetcode.com",
            "gitlab": "https://gitlab.com",
            "гитлаб": "https://gitlab.com",
            "bitbucket": "https://bitbucket.org",
            "битбакет": "https://bitbucket.org",
            "docker": "https://hub.docker.com",
            "докер": "https://hub.docker.com",
            "npm": "https://npmjs.com",
            "энпиэм": "https://npmjs.com",
            "pypi": "https://pypi.org",
            "пайпи": "https://pypi.org",
            "mdn": "https://developer.mozilla.org",
            "мдн": "https://developer.mozilla.org",
            "w3schools": "https://w3schools.com",
            "в три скулс": "https://w3schools.com",
            "freecodecamp": "https://freecodecamp.org",
            "фри код кэмп": "https://freecodecamp.org",
            "codecademy": "https://codecademy.com",
            "код академи": "https://codecademy.com",
            "kaggle": "https://kaggle.com",
            "кэгл": "https://kaggle.com",
            "arxiv": "https://arxiv.org",
            "арксив": "https://arxiv.org",
            "scihub": "https://sci-hub.se",
            "сай хаб": "https://sci-hub.se",
            "libgen": "https://libgen.is",
            "либген": "https://libgen.is",
            "goodreads": "https://goodreads.com",
            "гудридс": "https://goodreads.com",
            "imdb": "https://imdb.com",
            "имдб": "https://imdb.com",
            "kinopoisk": "https://kinopoisk.ru",
            "кинопоиск": "https://kinopoisk.ru",
            "booking": "https://booking.com",
            "букинг": "https://booking.com",
            "airbnb": "https://airbnb.com",
            "эир би эн би": "https://airbnb.com",
            "aviasales": "https://aviasales.ru",
            "авиасейлс": "https://aviasales.ru",
            "tripadvisor": "https://tripadvisor.com",
            "трипадвайзер": "https://tripadvisor.com",
            "banki": "https://banki.ru",
            "банки ру": "https://banki.ru",
            "investing": "https://investing.com",
            "инвестинг": "https://investing.com",
            "yahoo": "https://yahoo.com",
            "яху": "https://yahoo.com",
            "bing": "https://bing.com",
            "бинг": "https://bing.com",
            "duckduckgo": "https://duckduckgo.com",
            "дакдакго": "https://duckduckgo.com",
            "ecosia": "https://ecosia.org",
            "экозия": "https://ecosia.org"
        }
            # Я половину сайтов даже не знаю список чисто с нейронки

        for site_name, url in sites.items():
            if site_name in command:
                webbrowser.open(url)
                self.voice_engine.play_random_success()
                return

        self.ask_for_details("сайт", "Какой сайт открыть? (YouTube, Google, VK, Yandex)")

    def handle_shutdown(self, command):

        print(f"🔧 Команда: {command}")

        # Ищем число
        numbers = re.findall(r'\d+', command)

        # Определяем единицы
        cmd_lower = command.lower()

        if "секунд" in cmd_lower:
            if numbers:
                seconds = int(numbers[0])
                print(f"⏱️  {seconds} секунд")
            else:
                seconds = 60
                print(f"⏱️  секунд не указано, ставлю {seconds}")

        elif "минут" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 60
                print(f"⏱️  {numbers[0]} минут = {seconds} секунд")
            else:
                seconds = 60  # 1 минута по умолчанию
                print(f"⏱️  минут не указано, ставлю 1 минуту ({seconds}с)")

        elif "час" in cmd_lower or "часа" in cmd_lower or "часов" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 3600
                print(f"⏱️  {numbers[0]} час(ов) = {seconds} секунд")
            else:
                seconds = 3600  # 1 час по умолчанию
                print(f"⏱️  час(ов) не указано, ставлю 1 час ({seconds}с)")

        elif "день" in cmd_lower or "дня" in cmd_lower or "дней" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 86400
                print(f"⏱️  {numbers[0]} день(дней) = {seconds} секунд")
            else:
                seconds = 86400  # 1 день по умолчанию
                print(f"⏱️  дней не указано, ставлю 1 день ({seconds}с)")

        else:
            # Если нет указания единиц
            if numbers:
                seconds = int(numbers[0])  # предполагаем секунды
                print(f"⏱️  Предполагаю {seconds} секунд")
            else:
                seconds = 60
                print(f"⏱️  Время не указано, ставлю {seconds} секунд")

        # Проверка минимального времени
        if seconds < 10:
            print("⚠️  Минимум 10 секунд")
            seconds = 10

        # Проверка максимального времени (48 часов)
        if seconds > 172800:  # 48 часов
            print("⚠️  Максимум 48 часов")
            seconds = 172800

        # Выполняем
        import os
        os.system(f"shutdown -s -t {seconds}")

        self.voice_engine.play_random_success()

        # Красивый вывод времени
        if seconds >= 86400:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            print(f"✅ ПК выключится через {days} день(дней) {hours} час(ов)")
        elif seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            print(f"✅ ПК выключится через {hours} час(ов) {minutes} минут")
        elif seconds >= 60:
            minutes = seconds // 60
            secs = seconds % 60
            print(f"✅ ПК выключится через {minutes} минут {secs} секунд")
        else:
            print(f"✅ ПК выключится через {seconds} секунд")

    def handle_restart(self, command):

        print(f"🔧 Команда: {command}")

        # Ищем число
        numbers = re.findall(r'\d+', command)

        # Определяем единицы
        cmd_lower = command.lower()

        if "секунд" in cmd_lower:
            if numbers:
                seconds = int(numbers[0])
                print(f"⏱️  {seconds} секунд")
            else:
                seconds = 60
                print(f"⏱️  секунд не указано, ставлю {seconds}")

        elif "минут" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 60
                print(f"⏱️  {numbers[0]} минут = {seconds} секунд")
            else:
                seconds = 60  # 1 минута по умолчанию
                print(f"⏱️  минут не указано, ставлю 1 минуту ({seconds}с)")

        elif "час" in cmd_lower or "часа" in cmd_lower or "часов" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 3600
                print(f"⏱️  {numbers[0]} час(ов) = {seconds} секунд")
            else:
                seconds = 3600  # 1 час по умолчанию
                print(f"⏱️  час(ов) не указано, ставлю 1 час ({seconds}с)")

        elif "день" in cmd_lower or "дня" in cmd_lower or "дней" in cmd_lower:
            if numbers:
                seconds = int(numbers[0]) * 86400
                print(f"⏱️  {numbers[0]} день(дней) = {seconds} секунд")
            else:
                seconds = 86400  # 1 день по умолчанию
                print(f"⏱️  дней не указано, ставлю 1 день ({seconds}с)")

        else:
            # Если нет указания единиц
            if numbers:
                seconds = int(numbers[0])  # предполагаем секунды
                print(f"⏱️  Предполагаю {seconds} секунд")
            else:
                seconds = 60
                print(f"⏱️  Время не указано, ставлю {seconds} секунд")

        # Проверка минимального времени
        if seconds < 10:
            print("⚠️  Минимум 10 секунд")
            seconds = 10

        # Проверка максимального времени
        if seconds > 172800:
            print("⚠️  Максимум 48 часов")
            seconds = 172800

        # Выполняем
        import os
        os.system(f"shutdown /r /t {seconds}")

        self.voice_engine.play_random_success()

        # Красивый вывод времени
        if seconds >= 86400:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            print(f"✅ ПК перезагрузится через {days} день(дней) {hours} час(ов)")
        elif seconds >= 3600:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            print(f"✅ ПК перезагрузится через {hours} час(ов) {minutes} минут")
        elif seconds >= 60:
            minutes = seconds // 60
            secs = seconds % 60
            print(f"✅ ПК перезагрузится через {minutes} минут {secs} секунд")
        else:
            print(f"✅ ПК перезагрузится через {seconds} секунд")

    def cancel_shutdown(self):
        os.system("shutdown -a")
        self.voice_engine.play_random_success()
        print("✅ Выключение/перезагрузка отменена")

    def handle_program_command(self, command):
        programs = {
            "калькулятор": "calc.exe",
            "блокнот": "notepad.exe",
            "пайнт": "mspaint.exe",
            "paint": "mspaint.exe"
        }

        for prog_name, path in programs.items():
            if prog_name in command:
                subprocess.Popen(path, shell=True)
                self.voice_engine.play_random_success()
                return

        self.ask_for_details("программа", "Какую программу открыть? (калькулятор, блокнот, пэинт)")

    def handle_wallpaper(self, command):
        self.voice_engine.play_random_success()
        print("🖼️ Смена обоев (функция в разработке)")

    def handle_change_name(self, command):
        match = re.search(r'на\s+([^\s]+)', command)
        if match:
            new_name = match.group(1)
            self.data_manager.set_assistant_name(new_name, False)
            self.assistant_name = new_name
            self.voice_engine.play_random_success()
        else:
            self.ask_for_details("имя", "Какое имя установить?")

    def start_console_mode(self):
        print("💻 Активация консольного режима...")
        self.voice_engine.play_random_success()

        print("\n" + "=" * 50)
        print("КОНСОЛЬНЫЙ РЕЖИМ")
        print("=" * 50)
        print("Доступные команды:")
        print("  ии [вопрос] - задать вопрос AI")
        print("  ии-чат - открыть чат с AI")
        print("  ии-настройки - показать настройки AI")
        print("  голос [мужской/женский] - сменить голос")
        print("  сайт [название] - открыть сайт")
        print("  программа [название] - открыть программу")
        print("  выключение [секунды] - выключить ПК")
        print("  отмена - отменить выключение/перезагрузку")
        print("  перезагрузка [секунды] - перезагрузить ПК")
        print("  имя [новое_имя] - сменить имя")
        print("  кот [красный/желтый/зеленый] - специальные коды")
        print("  музыка пауза - поставить музыку на паузу")
        print("  музыка играй - продолжить музыку")
        print("  музыка включи [запрос] - найти музыку")
        print("  добавить сайт - добавить новый сайт")
        print("  добавить программу - добавить новую программу")
        print("  мои сайты - показать пользовательские сайты")
        print("  мои программы - показать пользовательские программы")
        print("  таймер на [время] - установить таймер (5 минут, 1 час)")
        print("  будильник [время] - установить будильник (07:30)")
        print("  таймеры - показать активные таймеры")
        print("  отменить таймер - отменить таймер")
        print("  музыка пауза - поставить музыку на паузу")
        print("  музыка играй - продолжить музыку")
        print("  музыка включи [запрос] - найти музыку")
        print("  добавить сайт - добавить новый сайт")
        print("  добавить программу - добавить новую программу")
        print("  помощь - показать справку")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nКонсоль> ").strip().lower()
                if user_input == 'выход':
                    print("🔙 Возврат в голосовой режим...")
                    break

                elif user_input.startswith('таймер '):
                    timer_cmd = user_input.replace('таймер ', '').strip()
                    self.advanced_features.handle_timer_command(f"установи таймер {timer_cmd}")

                elif user_input.startswith('будильник '):
                    alarm_cmd = user_input.replace('будильник ', '').strip()
                    self.advanced_features.handle_timer_command(f"поставь будильник на {alarm_cmd}")

                elif user_input == 'таймеры':
                    self.advanced_features.show_timers_status()

                elif user_input == 'отменить таймер':
                    self.advanced_features.cancel_timer("")

                elif user_input.startswith('музыка '):
                    music_cmd = user_input.replace('музыка ', '').strip()
                    self.advanced_features.handle_music_command(music_cmd)

                elif user_input == 'добавить сайт':
                    self.advanced_features.add_website_interactive()

                elif user_input == 'добавить программу':
                    self.advanced_features.add_program_interactive()

                elif user_input == 'помощь':
                    self.advanced_features.show_help() # Потом исправить

                elif user_input.startswith('музыка '):
                    music_cmd = user_input.replace('музыка ', '').strip()
                    self.advanced_features.handle_music_command(music_cmd)

                elif user_input == 'добавить сайт':
                    self.advanced_features.add_website_interactive()

                elif user_input == 'добавить программу':
                    self.advanced_features.add_program_interactive()

                elif user_input == 'мои сайты':
                    self.advanced_features.list_custom_websites()

                elif user_input == 'мои программы':
                    self.advanced_features.list_custom_programs()
                elif user_input.startswith('голос '):
                    gender = user_input.replace('голос ', '').strip()
                    if gender in ['мужской', 'male']:
                        self.voice_engine.change_voice_gender("male", False)
                    elif gender in ['женский', 'female']:
                        self.voice_engine.change_voice_gender("female", False)

                elif user_input.startswith('сайт '):
                    site = user_input.replace('сайт ', '').strip()
                    self.handle_open_command(f"открой {site}")

                elif user_input.startswith('программа '):
                    program = user_input.replace('программа ', '').strip()
                    self.handle_program_command(f"открой {program}")

                elif user_input.startswith('выключение'):
                    seconds = 60
                    if ' ' in user_input:
                        try:
                            seconds = int(user_input.split(' ')[1])
                        except:
                            pass
                    self.handle_shutdown(f"выключи пк через {seconds}")
                elif user_input == 'отмена':
                    self.cancel_shutdown()

                elif user_input.startswith('перезагрузка'):
                    seconds = 60
                    if ' ' in user_input:
                        try:
                            seconds = int(user_input.split(' ')[1])
                        except:
                            pass
                    self.handle_restart(f"перезагрузи пк через {seconds}")

                elif user_input.startswith('имя '):
                    new_name = user_input.replace('имя ', '').strip()
                    self.data_manager.set_assistant_name(new_name, False)
                    self.assistant_name = new_name
                    self.voice_engine.play_random_success()

                elif user_input.startswith('кот '):
                    code = user_input.replace('кот ', '').strip()
                    if code == 'красный':
                        print("🔴 Переход в режим безопасности...")
                        self.start_security_console()  # Используем ту же функцию
                    elif code == 'желтый':
                        self.voice_engine.play_random_success()
                        self.shutdown()
                    elif code == 'зеленый':
                        self.handle_green_code()

                    elif user_input.startswith('ии '):
                        question = user_input.replace('ии ', '').strip()
                        self.handle_ai_mode(f"задай вопрос {question}")
                    elif user_input == 'ии-чат':
                        self.launch_ai_chat()
                    elif user_input == 'ии-настройки':
                        ai_settings = self.data_manager.get_ai_settings()
                        print("\n🤖 НАСТРОЙКИ AI:")
                        print(f"  Модель: {ai_settings['model']}")
                        print(f"  API URL: {ai_settings['api_url']}")
                        print(f"  Показывать текст: {ai_settings['show_text_response']}")
                else:
                    print("❓ Неизвестная команда")

            except KeyboardInterrupt:
                print("\n🔙 Возврат в голосовой режим...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    def handle_red_code(self):
        print("🔴 Активирован КОТ КРАСНЫЙ - удаление помощника")
        print("Для подтверждения введите код в специальной консоли...")
        self.start_security_console()

    def activate_removal_procedure(self):
        print("🚨 АКТИВАЦИЯ ПРОЦЕДУРЫ УДАЛЕНИЯ")

        # Определяем путь к корневой папке
        # Если скрипт находится внутри папки поднимаемся на уровень выше
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        target_folder_name = "AIAssistant"

        # Ищем папку в текущей папке или родительской
        removal_path = None

        # Проверяем текущую папку
        if os.path.basename(current_dir) == target_folder_name:
            removal_path = current_dir
        # Проверяем родительскую папку
        elif os.path.exists(os.path.join(parent_dir, target_folder_name)):
            removal_path = os.path.join(parent_dir, target_folder_name)
        else:
            # Если не нашли, ищем меньшую
            for root, dirs, files in os.walk(parent_dir):
                if target_folder_name in dirs:
                    removal_path = os.path.join(root, target_folder_name)
                    break

        if not removal_path:
            print("❌ Папка AIAssistant не найдена")
            return

        print(f"📁 Найдена папка для удаления: {removal_path}")

        # Подтверждение удаления
        choice = input(
            "Вы уверены, что хотите удалить папку AIAssistant и ВСЕ её содержимое? (да/нет): ").strip().lower()

        if choice == 'да':
            print("🗑️ Начинается удаление файлов помощника...")

            try:
                # Дополнительное подтверждение
                confirm = input(f"Введите 'УДАЛИТЬ' для подтверждения удаления папки {removal_path}: ").strip()
                if confirm != 'УДАЛИТЬ':
                    print("❌ Отмена удаления - неправильное подтверждение")
                    return

                print("⏳ Удаление...")

                # Используем для рекурсивного удаления папки со всем содержимым
                shutil.rmtree(removal_path)

                # Проверяем, что папка удалена
                time.sleep(1)  # Небольшая задержка
                if not os.path.exists(removal_path):
                    print("✅ Папка AIAssistant успешно удалена")
                    if hasattr(self, 'voice_engine'):
                        self.voice_engine.play_random_success()
                else:
                    print("⚠️ Не удалось полностью удалить папку")

            except PermissionError as e:
                print(f"❌ Ошибка доступа: {e}")
                print("⚠️ Закройте все файлы в папке AIAssistant и попробуйте снова")
            except Exception as e:
                print(f"❌ Ошибка при удалении: {e}")

        else:
            print("❌ Отмена удаления")

    def start_security_console(self):
        print("\n" + "=" * 50)
        print("СИСТЕМА БЕЗОПАСНОСТИ")
        print("=" * 50)
        print("Доступные команды:")
        print("  красный [код] - активация красного кода")
        print("  желтый - активация желтого кода")
        print("  зеленый - активация зеленого кода")
        print("  выход - вернуться в голосовой режим")
        print("=" * 50)

        while True:
            try:
                user_input = input("\nБезопасность> ").strip().lower()

                if user_input == 'выход':
                    print("🔙 Возврат в голосовой режим...")
                    break

                elif user_input.startswith('красный'):
                    # Извлекаем код
                    parts = user_input.split(' ', 1)
                    if len(parts) > 1:
                        password = parts[1].strip()
                        if password == self.data_manager.data['security']['red_code']:
                            print("✅ Код принят! Активация процедуры удаления...")
                            self.voice_engine.play_random_success()
                            self.activate_removal_procedure()

                            break
                        else:
                            print("❌ Неверный код! Доступ запрещен.")
                            self.voice_engine.play_more_details()
                    else:
                        print("❌ Укажите код: красный [ваш_код]")

                elif user_input == 'желтый':
                    print("🟡 Активация желтого кода...")
                    self.voice_engine.play_random_success()
                    self.shutdown()
                    break

                elif user_input == 'зеленый':
                    print("🟢 Активация зеленого кода...")
                    self.handle_green_code()
                    break

                else:
                    print("❓ Неизвестная команда. Доступные: красный, желтый, зеленый, выход")

            except KeyboardInterrupt:
                print("\n🔙 Возврат в голосовой режим...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")

    def handle_green_code(self):
        print("🟢 Активирован КОТ ЗЕЛЕНЫЙ - закрытие окон")
        for _ in range(10):
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.3)
        self.voice_engine.play_random_success()

    def handle_ai_mode(self, command):
        question = command.replace("режим искусственный интеллект", "").replace("искусственный интеллект", "").replace(
            "задай вопрос", "").strip()

        if question:
            # Если есть вопрос, показываем ответ
            print(f"🤖 Вопрос к AI: {question}")
            print("⏳ AI думает...")

            response = self.ai_client.ask_question(question)
            print(f"🤖 AI: {response}")

            # Предлагаем открыть полноценный чат
            choice = input("Открыть чат с AI для продолжения? (да/нет): ").strip().lower()
            if choice in ['да', 'yes', 'y']:
                self.launch_ai_chat()
        else:
            # Если вопроса нет, открываем чат
            self.launch_ai_chat()

    def launch_ai_chat(self, question=None):
        try:

            # Получаем путь к питону
            python_exe = sys.executable
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Создаем временный пайтон скрипт для ии чата
            py_content = '''import sys
    import os
    sys.path.insert(0, r"''' + current_dir + '''")

    try:
        from data_manager import DataManager
        from ai_client import AIClient

        print("========================================")
        print("      РЕЖИМ ИСКУССТВЕННОГО ИНТЕЛЛЕКТА")
        print("========================================")
        print()

        dm = DataManager()
        ai = AIClient(dm)
    '''

            # Добавляем вопрос если есть
            if question:
                py_content += f'''
        print("Вопрос: {question}")
        print()
        response = ai.ask_question("{question}")
        print(f"🤖 AI: {{response}}")
        print()
        input("Нажмите Enter для выхода...")
    '''
            else:
                py_content += '''
        ai.chat_loop()
    '''

            py_content += '''
    except Exception as e:
        print(f"Ошибка: {e}")
        input("Нажмите Enter для выхода...")
    '''

            # Создаем временный пайтон файл
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(py_content)
                temp_py = f.name

            # Создаем простой бат без сложных команд
            bat_content = f'''@echo off
    chcp 65001
    title ИИ Помощник
    "{python_exe}" "{temp_py}"
    pause
    del "{temp_py}"
    '''

            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False, encoding='utf-8') as f:
                f.write(bat_content)
                temp_bat = f.name

            # Запускаем бат
            subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', f'"{temp_bat}"'], shell=True)

            print("🪟 Запуск отдельного окна ИИ...")
            self.voice_engine.play_random_success()

        except Exception as e:
            print(f"❌ Ошибка запуска ИИ режима: {e}")
            self.voice_engine.play_more_details()

    def handle_record_idea(self, command):
        idea = command.replace("запиши идею", "").replace("сохрани идею", "").strip()
        if idea:
            from datetime import datetime
            with open("Ideas.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime('"%Y.%m.%d""%H:%M"')
                f.write(f'{timestamp} {idea}\n')
            self.voice_engine.play_random_success()
            print(f"💡 Идея записана: {idea}")
        else:
            self.ask_for_details("идея", "Какую идею записать?")

    def handle_internet_search(self, command):
        query = command.replace("найди в интернете", "").replace("поиск в интернете", "").replace("найди информацию",
                                                                                                  "").strip()

        if query:
            self.voice_engine.play_internet_search()
            print(f"🔍 Поиск в интернете: {query}")

            browser = "chrome"  # браузер по умолчанию

            # Браузеры
            browsers = {
                "в хроме": "chrome",
                "в chrome": "chrome",
                "в яндексе": "yandex",
                "в yandex": "yandex",
                "в яху": "yahoo",
                "в yahoo": "yahoo",
                "в опере": "opera",
                "в opera": "opera",
                "в edge": "edge",
                "в майкрософт эдж": "edge"
            }

            # Ищем указание браузера в запросе
            for browser_keyword, browser_name in browsers.items():
                if browser_keyword in query.lower():
                    browser = browser_name
                    query = query.replace(browser_keyword, "").strip()
                    break

            # Выполняем поиск
            self.perform_internet_search(query, browser)
        else:
            self.ask_for_details("поиск", "Что найти в интернете?")

    def perform_internet_search(self, query, browser="chrome"):
        try:
            # Url для поиска
            search_urls = {
                "chrome": f"https://www.google.com/search?q={query}",
                "yandex": f"https://yandex.ru/search/?text={query}",
                "yahoo": f"https://search.yahoo.com/search?p={query}",
                "opera": f"https://www.google.com/search?q={query}",
                "edge": f"https://www.bing.com/search?q={query}"
            }

            url = search_urls.get(browser, search_urls["chrome"])

            # Открываем в браузере
            webbrowser.open(url)
            print(f"🌐 Открываю поиск в {browser}: {query}")
            self.voice_engine.play_random_success()

        except Exception as e:
            print(f"❌ Ошибка при поиске: {e}")
            self.voice_engine.play_more_details()

    def open_website(self, site_name): # Потом исправить
        sites = {
            "youtube": "https://youtube.com",
            "ютуб": "https://youtube.com",
            "google": "https://google.com",
            "гугл": "https://google.com",
            "vk": "https://vk.com",
            "вк": "https://vk.com",
            "yandex": "https://yandex.ru",
            "яндекс": "https://yandex.ru"
        }

        site_name = site_name.lower().strip()
        if site_name in sites:
            webbrowser.open(sites[site_name])
            return True
        return False

    def open_program(self, program_name):
        programs = {
            "калькулятор": "calc.exe",
            "блокнот": "notepad.exe",
            "пайнт": "mspaint.exe",
            "paint": "mspaint.exe"
        }

        program_name = program_name.lower().strip()
        if program_name in programs:
            subprocess.Popen(programs[program_name], shell=True)
            return True
        return False

    def change_wallpaper(self, wallpaper_name):
        return True

    def start_voice_mode(self):
        print("🎙️ Голосовой режим активирован")

        while self.is_listening:
            if not self.is_awake:
                if self.listen_for_wake_word():
                    continue
            else:
                extended_timeout = self.waiting_for_details
                command = self.listen_for_command(extended_timeout)
                if command:
                    self.process_command(command)

            time.sleep(0.1)

    def shutdown(self):
        print("👋 Выключение помощника...")
        self.is_listening = False
        sys.exit(0)

def main():
    assistant = AIAssistant()
    try:
        assistant.start_voice_mode()
    except KeyboardInterrupt:
        print("\nВыключение...")
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()