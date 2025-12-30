import json
import os
import time
import threading
import pyautogui
import webbrowser
import re
from datetime import datetime, timedelta

class AdvancedFeatures:
    def __init__(self, data_manager, voice_engine):
        self.data_manager = data_manager
        self.voice_engine = voice_engine
        self.active_timers = {}
        self.active_alarms = {}
        self.timer_counter = 0

        # Загружаем сохраненные таймеры
        self.load_timers()

        print("✅ Расширенные функции инициализированы")

    def handle_timer_command(self, command):
        print(f"⏱️ Таймер команда: {command}")
        cmd_lower = command.lower()

        # 1. Установить таймер
        if any(word in cmd_lower for word in ["установи таймер", "поставь таймер", "таймер на"]):
            return self.set_timer(command)

        # 2. Установить будильник
        elif any(word in cmd_lower for word in ["установи будильник", "поставь будильник", "будильник на"]):
            return self.set_alarm(command)

        # 3. Проверить таймеры
        elif any(word in cmd_lower for word in ["сколько осталось", "остаток таймера", "статус таймера", "таймеры"]):
            return self.show_timers_status()

        # 4. Отменить таймер
        elif any(word in cmd_lower for word in ["останови таймер", "отмени таймер", "удали таймер"]):
            return self.cancel_timer(command)

        # 5. Отменить будильник
        elif any(word in cmd_lower for word in ["останови будильник", "отмени будильник", "удали будильник"]):
            return self.cancel_alarm(command)

        # 6. Напоминание
        elif "напомни" in cmd_lower:
            return self.set_reminder(command)

        else:
            print("❌ Не понял команду таймера")
            self.voice_engine.play_more_details()
            return False

    def parse_time(self, command):
        """Разобрать время из команды"""
        # Ищем числа
        numbers = re.findall(r'\d+', command)
        if not numbers:
            return None

        total_seconds = 0
        cmd_lower = command.lower()

        # Часы
        if "час" in cmd_lower:
            hours = int(numbers[0])
            total_seconds = hours * 3600
        # Минуты
        elif "минут" in cmd_lower:
            minutes = int(numbers[0])
            total_seconds = minutes * 60
        # Секунды
        elif "секунд" in cmd_lower:
            total_seconds = int(numbers[0])
        # По умолчанию - минуты
        else:
            total_seconds = int(numbers[0]) * 60

        return total_seconds

    def set_timer(self, command):
        try:
            # проверяем время
            seconds = self.parse_time(command)
            if not seconds:
                print("❌ Не указано время")
                self.voice_engine.play_more_details()
                return False

            # Минимальное время - 10 секунд
            if seconds < 10:
                seconds = 10

            # Создаем таймер
            timer_id = self.timer_counter
            self.timer_counter += 1

            timer_info = {
                'id': timer_id,
                'name': f"Таймер {timer_id}",
                'end_time': time.time() + seconds,
                'duration': seconds,
                'active': True,
                'type': 'timer'
            }

            self.active_timers[timer_id] = timer_info

            # Запускаем поток
            thread = threading.Thread(target=self._timer_thread, args=(timer_id,), daemon=True)
            thread.start()

            # Сохраняем
            self.save_timers()

            # Форматируем вывод
            if seconds >= 3600:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                time_str = f"{hours} час {minutes} мин"
            elif seconds >= 60:
                minutes = seconds // 60
                secs = seconds % 60
                time_str = f"{minutes} мин {secs} сек"
            else:
                time_str = f"{seconds} сек"

            print(f"✅ Таймер #{timer_id} установлен на {time_str}")
            self.voice_engine.play_random_success()
            return True

        except Exception as e:
            print(f"❌ Ошибка установки таймера: {e}")
            return False

    def _timer_thread(self, timer_id):
        """Поток для отслеживания таймера"""
        try:
            timer = self.active_timers.get(timer_id)
            if not timer or not timer['active']:
                return

            end_time = timer['end_time']

            # Ждем окончания
            while time.time() < end_time:
                time.sleep(1)
                # Проверяем, не отменили ли таймер
                if timer_id not in self.active_timers or not self.active_timers[timer_id]['active']:
                    return

            # Таймер сработал
            print(f"\n🔔 ТАЙМЕР #{timer_id} ЗАВЕРШЕН!")
            print("⏰ Время вышло!")

            # Проигрываем звук несколько раз
            for _ in range(3):
                self.voice_engine.play_random_success()
                time.sleep(1)

            # Удаляем таймер
            if timer_id in self.active_timers:
                del self.active_timers[timer_id]
                self.save_timers()

        except Exception as e:
            print(f"❌ Ошибка в потоке таймера: {e}")

    def set_alarm(self, command):
        """Установить будильник"""
        try:
            # Ищем время в формате ЧЧ:ММ
            time_match = re.search(r'(\d{1,2}):(\d{2})', command)

            if not time_match:
                print("❌ Укажите время в формате ЧЧ:ММ (например: 07:30)")
                self.voice_engine.play_more_details()
                return False

            hour = int(time_match.group(1))
            minute = int(time_match.group(2))

            # Проверяем корректность времени
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                print("❌ Неправильное время")
                self.voice_engine.play_more_details()
                return False

            # Создаем время будильника
            now = datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

            # Если время уже прошло сегодня, ставим на завтра
            if alarm_time < now:
                alarm_time += timedelta(days=1)

            # Создаем будильник
            alarm_id = self.timer_counter
            self.timer_counter += 1

            alarm_info = {
                'id': alarm_id,
                'name': f"Будильник {alarm_id}",
                'alarm_time': alarm_time.timestamp(),
                'active': True,
                'type': 'alarm'
            }

            self.active_alarms[alarm_id] = alarm_info

            # Запускаем поток
            thread = threading.Thread(target=self._alarm_thread, args=(alarm_id,), daemon=True)
            thread.start()

            # Сохраняем
            self.save_timers()

            print(f"✅ Будильник #{alarm_id} установлен на {alarm_time.strftime('%H:%M')}")
            self.voice_engine.play_random_success()
            return True

        except Exception as e:
            print(f"❌ Ошибка установки будильника: {e}")
            return False

    def _alarm_thread(self, alarm_id):
        try:
            alarm = self.active_alarms.get(alarm_id)
            if not alarm or not alarm['active']:
                return

            alarm_time = alarm['alarm_time']

            # Ждем наступления времени
            while time.time() < alarm_time:
                time.sleep(30)  # Проверяем каждые 30 секунд
                # Проверяем, не отменили ли будильник
                if alarm_id not in self.active_alarms or not self.active_alarms[alarm_id]['active']:
                    return

            # Будильник сработал
            print(f"\n🔔 БУДИЛЬНИК #{alarm_id}!")
            print("⏰ Время просыпаться!")

            # Проигрываем звук несколько раз
            for _ in range(5):
                self.voice_engine.play_random_success()
                time.sleep(2)

            # Удаляем будильник (одноразовый)
            if alarm_id in self.active_alarms:
                del self.active_alarms[alarm_id]
                self.save_timers()

        except Exception as e:
            print(f"❌ Ошибка в потоке будильника: {e}")

    def show_timers_status(self):
        """Показать статус активных таймеров и будильников"""
        print("\n" + "=" * 50)
        print("⏰ АКТИВНЫЕ ТАЙМЕРЫ И БУДИЛЬНИКИ")
        print("=" * 50)

        # Таймеры
        if self.active_timers:
            print("\n⏱️ ТАЙМЕРЫ:")
            for timer_id, timer in self.active_timers.items():
                if timer['active']:
                    remaining = timer['end_time'] - time.time()
                    if remaining > 0:
                        mins = int(remaining // 60)
                        secs = int(remaining % 60)
                        print(f"  #{timer_id}: {mins} мин {secs} сек осталось")
        else:
            print("\n⏱️ Активных таймеров нет")

        # Будильники
        if self.active_alarms:
            print("\n🔔 БУДИЛЬНИКИ:")
            for alarm_id, alarm in self.active_alarms.items():
                if alarm['active']:
                    alarm_time = datetime.fromtimestamp(alarm['alarm_time'])
                    print(f"  #{alarm_id}: на {alarm_time.strftime('%H:%M')}")
        else:
            print("\n🔔 Активных будильников нет")

        self.voice_engine.play_random_success()
        return True

    def cancel_timer(self, command):
        if not self.active_timers:
            print("⏱️ Активных таймеров нет")
            return False

        print("\n⏱️ Активные таймеры:")
        active_timers = [t for t in self.active_timers.values() if t['active']]

        if not active_timers:
            print("  Нет активных таймеров")
            return False

        for i, timer in enumerate(active_timers, 1):
            remaining = timer['end_time'] - time.time()
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            print(f"  {i}. #{timer['id']}: {mins} мин {secs} сек")

        choice = input("\nКакой таймер отменить? (номер или 'все'): ").strip()

        if choice.lower() == 'все':
            for timer in active_timers:
                self.active_timers[timer['id']]['active'] = False
            print("✅ Все таймеры отменены")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(active_timers):
                timer_id = active_timers[idx]['id']
                self.active_timers[timer_id]['active'] = False
                print(f"✅ Таймер #{timer_id} отменен")
            else:
                print("❌ Неверный номер")
                return False
        else:
            print("❌ Неверный выбор")
            return False

        self.save_timers()
        self.voice_engine.play_random_success()
        return True

    def cancel_alarm(self, command):
        if not self.active_alarms:
            print("🔔 Активных будильников нет")
            return False

        print("\n🔔 Активные будильники:")
        active_alarms = [a for a in self.active_alarms.values() if a['active']]

        if not active_alarms:
            print("  Нет активных будильников")
            return False

        for i, alarm in enumerate(active_alarms, 1):
            alarm_time = datetime.fromtimestamp(alarm['alarm_time'])
            print(f"  {i}. #{alarm['id']}: {alarm_time.strftime('%H:%M')}")

        choice = input("\nКакой будильник отменить? (номер или 'все'): ").strip()

        if choice.lower() == 'все':
            for alarm in active_alarms:
                self.active_alarms[alarm['id']]['active'] = False
            print("✅ Все будильники отменены")
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(active_alarms):
                alarm_id = active_alarms[idx]['id']
                self.active_alarms[alarm_id]['active'] = False
                print(f"✅ Будильник #{alarm_id} отменен")
            else:
                print("❌ Неверный номер")
                return False
        else:
            print("❌ Неверный выбор")
            return False

        self.save_timers()
        self.voice_engine.play_random_success()
        return True

    def set_reminder(self, command):
        print("📝 Напоминания пока в разработке")
        print("   Используйте 'таймер на X минут' для временных напоминаний")
        self.voice_engine.play_more_details()
        return False

    def load_timers(self):
        try:
            timers_file = "data/timers.json"
            if os.path.exists(timers_file):
                with open(timers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_timers = data.get('timers', {})
                    self.active_alarms = data.get('alarms', {})
                    self.timer_counter = data.get('counter', 0)
                    print(f"✅ Загружено {len(self.active_timers)} таймеров и {len(self.active_alarms)} будильников")
        except:
            self.active_timers = {}
            self.active_alarms = {}
            self.timer_counter = 0

    def save_timers(self):
        try:
            os.makedirs("data", exist_ok=True)
            timers_file = "data/timers.json"
            data = {
                'timers': self.active_timers,
                'alarms': self.active_alarms,
                'counter': self.timer_counter,
                'saved': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(timers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения таймеров: {e}")
            return False

    # Далее муз функции

    def handle_music_command(self, command):
        """Обработка музыкальных команд"""
        print(f"🎵 Музыкальная команда: {command}")
        cmd_lower = command.lower()

        # 1. Пауза
        pause_keywords = ["пауза", "поставь на паузу", "останови музыку", "стоп"]
        if any(keyword in cmd_lower for keyword in pause_keywords):
            return self.pause_music()

        # 2. Продолжить
        resume_keywords = [
            "продолжи", "продолжай", "включи музыку обратно", "продолжим",
            "поехали", "давай дальше", "воспроизведи", "играй",
            "продолжить воспроизведение", "снять с паузы", "возобновить"
        ]
        if any(keyword in cmd_lower for keyword in resume_keywords):
            return self.resume_music()

        # 3. Включить музыку/плейлист
        play_keywords = ["включи", "запусти", "открой", "воспроизведи", "поставь", "найди"]
        for keyword in play_keywords:
            if keyword in cmd_lower:
                query = cmd_lower.split(keyword)[-1].strip()

                # Проверяем на плейлист
                if "плейлист" in query:
                    playlist = query.replace("плейлист", "").strip()
                    if playlist:
                        return self.play_playlist(playlist)
                    else:
                        print("❌ Укажите название плейлиста")
                        self.voice_engine.play_more_details()
                        return False
                else:
                    # Обычный трек/автор
                    if query:
                        return self.play_music(query)
                    else:
                        print("❌ Укажите что играть")
                        self.voice_engine.play_more_details()
                        return False

        # Если команда не распознана
        print("❌ Не понял музыкальную команду")
        self.voice_engine.play_more_details()
        return False

    def pause_music(self):
        try:
            pyautogui.press('playpause')

            # Eще методы для разных плееров
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'shift', 'p')  # Для некоторых плееров

            print("⏸️ Музыка поставлена на паузу")
            self.voice_engine.play_random_success()
            return True
        except Exception as e:
            print(f"❌ Не удалось поставить на паузу: {e}")
            return False

    def resume_music(self):
        try:
            pyautogui.press('playpause')

            print("▶️ Воспроизведение продолжено")
            self.voice_engine.play_random_success()
            return True
        except Exception as e:
            print(f"❌ Не удалось продолжить: {e}")
            return False

    def play_music(self, query):
        print(f"🎶 Ищу: {query}")

        try:
            # Открываем YouTube Music с поиском
            search_url = f"https://music.youtube.com/search?q={query}"
            webbrowser.open(search_url)

            print(f"🔍 Открываю поиск на YouTube Music: {query}")
            self.voice_engine.play_random_success()
            return True
        except Exception as e:
            print(f"❌ Ошибка поиска музыки: {e}")

            # Пробуем Яндекс.Музыку ps: Не навижу яндекс
            try:
                search_url = f"https://music.yandex.ru/search?text={query}"
                webbrowser.open(search_url)
                print(f"🔍 Открываю поиск на Яндекс.Музыке")
                self.voice_engine.play_random_success()
                return True
            except:
                print("❌ Не удалось открыть поиск музыки")
                self.voice_engine.play_more_details()
                return False

    def play_playlist(self, playlist_name):
        print(f"📋 Ищу плейлист: {playlist_name}")

        try:
            # YouTube Music поиск плейлистов
            search_url = f"https://music.youtube.com/search?q={playlist_name} playlist"
            webbrowser.open(search_url)

            print(f"🔍 Открываю поиск плейлиста: {playlist_name}")
            self.voice_engine.play_random_success()
            return True
        except Exception as e:
            print(f"❌ Ошибка поиска плейлиста: {e}")
            self.voice_engine.play_more_details()
            return False

    # Далее добавление сайтов и програм

    def handle_add_item(self, command):
        print(f"➕ Команда добавления: {command}")
        cmd_lower = command.lower()

        if "сайт" in cmd_lower:
            self.add_website_interactive()
        elif any(word in cmd_lower for word in ["программу", "приложение"]):
            self.add_program_interactive()
        else:
            print("❌ Не понял, что добавить (сайт или программу?)")
            self.voice_engine.play_more_details()

    def add_website_interactive(self):
        print("\n" + "="*60)
        print("ДОБАВЛЕНИЕ НОВОГО САЙТА")
        print("="*60)
        print("ВНИМАНИЕ: ВВОДИТЕ НАЗВАНИЯ ПРАВИЛЬНО!")
        print("ЛУЧШЕ СКАЧАЙТЕ ВЕРСИЮ С КОНСОЛЬЮ И СКАЖИТЕ ТАМ НАЗВАНИЕ")
        print("="*60)

        try:
            name = input("\nНазвание сайта (например: 'youtube'): ").strip()
            if not name:
                print("❌ Название не может быть пустым")
                return

            url = input(f"URL для '{name}' (например: https://youtube.com): ").strip()
            if not url:
                print("❌ URL не может быть пустым")
                return

            # Добавляем https если нет
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Загружаем и обновляем данные
            data = self.data_manager.data

            if 'websites' not in data:
                data['websites'] = {}

            # Добавляем сайт
            data['websites'][name.lower()] = url

            # Русский вариант если есть кириллица
            if any(ord(c) > 127 for c in name):
                pass

            # Сохраняем
            if self.data_manager.add_custom_website(name, url):
                print(f"\n✅ Сайт '{name}' успешно добавлен!")
                print(f"   URL: {url}")
                print(f"\n📝 Теперь можно говорить:")
                print(f'   "{self.data_manager.get_assistant_name()} открой {name}"')
                self.voice_engine.play_random_success()
            else:
                print("❌ Ошибка сохранения")
                self.voice_engine.play_more_details()

        except KeyboardInterrupt:
            print("\n❌ Отмена добавления")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def add_program_interactive(self):
        print("\n" + "="*60)
        print("ДОБАВЛЕНИЕ НОВОЙ ПРОГРАММЫ")
        print("="*60)
        print("ВНИМАНИЕ: ВВОДИТЕ НАЗВАНИЯ ПРАВИЛЬНО!")
        print("ЛУЧШЕ СКАЧАЙТЕ ВЕРСИЮ С КОНСОЛЬЮ И СКАЖИТЕ ТАМ НАЗВАНИЕ")
        print("="*60)

        try:
            name = input("\nНазвание программы (например: 'калькулятор'): ").strip()
            if not name:
                print("❌ Название не может быть пустым")
                return

            print(f"\n📝 Путь к программе '{name}':")
            print("   Примеры:")
            print("   - calc.exe (системный калькулятор)")
            print("   - notepad.exe (блокнот)")
            print("   - mspaint.exe (Paint)")
            print("   - C:\\Program Files\\Program\\program.exe (полный путь)")

            path = input(f"\nВведите путь для '{name}': ").strip()
            if not path:
                print("❌ Путь не может быть пустым")
                return

            # Загружаем и обновляем данные
            data = self.data_manager.data

            if 'programs' not in data:
                data['programs'] = {}

            # Добавляем программу
            data['programs'][name.lower()] = path

            # Сохраняем
            if self.data_manager.add_custom_program(name, path):
                print(f"\n✅ Программа '{name}' успешно добавлена!")
                print(f"   Путь: {path}")
                print(f"\n📝 Теперь можно говорить:")
                print(f'   "{self.data_manager.get_assistant_name()} запусти {name}"')
                self.voice_engine.play_random_success()
            else:
                print("❌ Ошибка сохранения")
                self.voice_engine.play_more_details()

        except KeyboardInterrupt:
            print("\n❌ Отмена добавления")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    # Далее системные функции

    def show_music_help(self):
        print("\n" + "="*50)
        print("🎵 МУЗЫКАЛЬНЫЕ КОМАНДЫ")
        print("="*50)
        print("\n⏸️  Пауза:")
        print("   'пауза', 'поставь на паузу', 'стоп'")

        print("\n▶️  Продолжить:")
        print("   'продолжи', 'продолжай', 'играй', 'снять с паузы'")

        print("\n🎶 Включить музыку:")
        print("   'включи [название/автор]'")
        print("   'найди [песня]'")
        print("   'поставь [трек]'")

        print("\n📋 Плейлисты:")
        print("   'включи плейлист [название]'")
        print("   'найди плейлист [тема]'")
        print("   'запусти сборник [имя]'")

    def show_add_help(self):
        print("\n" + "="*50)
        print("➕ ДОБАВЛЕНИЕ САЙТОВ/ПРОГРАММ")
        print("="*50)
        print("\n🌐 Добавить сайт:")
        print("   'добавь сайт' - добавить новый сайт")
        print("   Пример: 'добавь сайт' → название: 'youtube' → URL: 'https://youtube.com'")

        print("\n💻 Добавить программу:")
        print("   'добавь программу' - добавить программу")
        print("   'добавь приложение' - то же самое")
        print("   Пример: 'добавь программу' → название: 'фотошоп' → путь: 'C:\\Photoshop\\photoshop.exe'")

    # Далее утилиты

    def list_custom_websites(self):
        websites = self.data_manager.get_custom_websites()

        if not websites:
            print("📭 Пользовательских сайтов нет")
            return

        print("\n🌐 Ваши сайты:")
        for name, url in websites.items():
            print(f"  • {name}: {url}")

    def list_custom_programs(self):
        programs = self.data_manager.get_custom_programs()

        if not programs:
            print("📭 Пользовательских программ нет")
            return

        print("\n💻 Ваши программы:")
        for name, path in programs.items():
            print(f"  • {name}: {path}")

