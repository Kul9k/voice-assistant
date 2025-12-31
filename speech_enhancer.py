import speech_recognition as sr
import numpy as np
import wave
import os
import time
from queue import Queue
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class SpeechEnhancer:
    # Улучшенная система распознавания речи

    def __init__(self, voice_engine=None):
        self.voice_engine = voice_engine
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.energy_threshold = 4000  # Начальный порог шума
        self.dynamic_threshold = True  # Динамическая подстройка порога
        self.ambient_adjust_duration = 2  # Время настройки на шум
        self.phrase_timeout = 3.0  # Таймаут фразы
        self.min_phrase_length = 0.3  # Минимальная длина фразы
        self.max_phrase_length = 7.0  # Максимальная длина фразы

        # Статистика для улучшения
        self.successful_records = 0
        self.failed_records = 0
        self.last_recognition_time = 0

        # Очередь для обработки аудио
        self.audio_queue = Queue()

        # Инициализация микрофона
        self._init_microphone()

        # Словарь для коррекции распознавания
        self.correction_dict = self._load_correction_dict()

    def _init_microphone(self):
        # Инициализация микрофона с выбором лучшего устройства
        try:
            # Получаем список всех микрофонов
            mic_list = sr.Microphone.list_microphone_names()
            print(f"🎤 Найдено микрофонов: {len(mic_list)}")

            # Ищем лучший микрофон
            preferred_keywords = ['microphone', 'mic', 'аудио', 'звук', 'record', 'ввод']
            backup_keywords = ['default', 'по умолчанию', 'stereo', 'стерео']

            selected_index = None

            # Ищем по предпочтительным ключевым словам
            for i, name in enumerate(mic_list):
                name_lower = name.lower()
                for keyword in preferred_keywords:
                    if keyword in name_lower and 'virtual' not in name_lower:
                        selected_index = i
                        print(f"✅ Выбран микрофон: {name}")
                        break
                if selected_index is not None:
                    break

            # Если не нашли, ищем по запасным
            if selected_index is None:
                for i, name in enumerate(mic_list):
                    name_lower = name.lower()
                    for keyword in backup_keywords:
                        if keyword in name_lower:
                            selected_index = i
                            print(f"⚠️  Выбран запасной микрофон: {name}")
                            break
                    if selected_index is not None:
                        break

            # Если все еще не нашли, используем первый
            if selected_index is None and mic_list:
                selected_index = 0
                print(f"⚠️  Использую первый микрофон: {mic_list[0]}")

            if selected_index is not None:
                self.microphone = sr.Microphone(device_index=selected_index)
                print(f"🎤 Микрофон #{selected_index} инициализирован")
            else:
                print("⚠️  Микрофоны не найдены, использую default")
                self.microphone = sr.Microphone()

            # Настраиваем распознаватель
            self._configure_recognizer()

        except Exception as e:
            print(f"❌ Ошибка инициализации микрофона: {e}")
            self.microphone = sr.Microphone()

    def _configure_recognizer(self):
        # Настройка параметров распознавателя
        # Устанавливаем начальный порог энергии
        self.recognizer.energy_threshold = self.energy_threshold

        # Настройка для лучшего распознавания
        self.recognizer.dynamic_energy_threshold = self.dynamic_threshold
        self.recognizer.pause_threshold = 0.8  # Пауза между словами
        self.recognizer.phrase_threshold = 0.3  # Порог начала фразы
        self.recognizer.non_speaking_duration = 0.5  # Минимальная тишина в конце

        print(f"⚙️  Настройки распознавателя:")
        print(f"   Порог энергии: {self.recognizer.energy_threshold}")
        print(f"   Динамический порог: {self.recognizer.dynamic_energy_threshold}")
        print(f"   Порог паузы: {self.recognizer.pause_threshold}")

    def _load_correction_dict(self):
        # Загружаем словарь для коррекции распознавания
        correction_dict = {
            # Частые ошибки Google Speech Recognition для русского
            'джемини': 'джимини',
            'джими': 'джимми',
            'джи ми': 'джимми',
            'джин': 'джим',
            'мини': 'ми',
            'трон': 'трон',
            'джимини трон': 'джиминитрон',

            # Команды
            'пауза музыку': 'пауза',
            'стоп музыку': 'стоп',
            'следующий трек': 'следующий',
            'предыдущий трек': 'предыдущий',
            'громче звук': 'громче',
            'тише звук': 'тише',

            # Частые опечатки
            'открыть': 'открой',
            'закрыть': 'закрой',
            'включить': 'включи',
            'выключить': 'выключи',
            'перезагрузить': 'перезагрузи',
            'остановить': 'останови',
            'найти': 'найди',
            'поискать': 'поищи',

            # Сайты
            'ютуб': 'youtube',
            'гугл': 'google',
            'вконтакте': 'vk',
            'яндекс': 'yandex',
        }
        return correction_dict

    def adjust_for_ambient_noise_enhanced(self, duration=2):
        # Улучшенная настройка на фоновый шум
        try:
            if not self.microphone:
                print("⚠️  Микрофон не инициализирован")
                return False

            print(f"🔊 Настраиваюсь на фоновый шум ({duration} сек)...")

            with self.microphone as source:
                # Делаем несколько измерений для точности
                noise_levels = []
                for _ in range(3):
                    try:
                        noise = self.recognizer.listen(
                            source,
                            timeout=1,
                            phrase_time_limit=1
                        )
                        # Примерная оценка уровня шума
                        audio_data = noise.get_raw_data()
                        if audio_data:
                            rms = np.sqrt(np.mean(np.frombuffer(audio_data, dtype=np.int16) ** 2))
                            noise_levels.append(rms)
                    except:
                        pass

                if noise_levels:
                    avg_noise = np.mean(noise_levels)
                    # Устанавливаем порог чуть выше шума
                    new_threshold = max(3000, avg_noise * 1.5)
                    self.recognizer.energy_threshold = new_threshold
                    print(f"✅ Установлен порог: {int(new_threshold)}")
                    return True

            # Если не удалось измерить шум, используем дефолтные настройки
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"✅ Использованы стандартные настройки шума")
            return True

        except Exception as e:
            print(f"❌ Ошибка настройки шума: {e}")
            return False

    def listen_for_wake_word_enhanced(self, wake_word, timeout=3):
        # Улучшенное прослушивание wake-слова
        try:
            if not self.microphone:
                return False, None

            print("🔊 Слушаю wake-слово...", end="\r")

            with self.microphone as source:
                try:
                    # Улучшенное прослушивание с лучшими параметрами
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=timeout,
                        snowboy_configuration=None  # Отключаем snowboy если используется
                    )

                    # Распознаем с несколькими попытками
                    text = self.recognize_with_retry(audio, retries=2)

                    if text:
                        print(f"🎯 Распознано: {text}")

                        # Проверяем wake-слово
                        if wake_word.lower() in text.lower():
                            # Извлекаем команду если есть
                            command = text.lower().replace(wake_word.lower(), "").strip()
                            return True, command

                    return False, None

                except sr.WaitTimeoutError:
                    return False, None
                except sr.UnknownValueError:
                    return False, None

        except Exception as e:
            print(f"❌ Ошибка прослушивания: {e}")
            return False, None

    def listen_for_command_enhanced(self, timeout=6, extended=False):
        # Улучшенное прослушивание команды
        try:
            if not self.microphone:
                return None

            print("🎤 Слушаю команду...")

            # Настраиваем таймауты
            listen_timeout = timeout + 2 if extended else timeout
            phrase_limit = 8 if extended else 6

            with self.microphone as source:
                try:
                    # Записываем аудио с улучшенными параметрами
                    audio = self.recognizer.listen(
                        source,
                        timeout=listen_timeout,
                        phrase_time_limit=phrase_limit
                    )

                    # Распознаем с несколькими попытками и коррекцией
                    text = self.recognize_with_retry(audio, retries=3)

                    if text:
                        # Корректируем распознанный текст
                        corrected = self.correct_recognition(text)

                        # Логируем статистику
                        self._log_recognition_stats(text, corrected)

                        print(f"📝 Команда: {corrected}")
                        return corrected
                    else:
                        print("❌ Не удалось распознать речь")
                        return None

                except sr.WaitTimeoutError:
                    print("⏰ Таймаут ожидания команды")
                    return None
                except sr.UnknownValueError:
                    print("🔇 Не удалось распознать речь (UnknownValueError)")
                    return None
                except Exception as e:
                    print(f"❌ Ошибка прослушивания команды: {e}")
                    return None

        except Exception as e:
            print(f"❌ Критическая ошибка микрофона: {e}")
            return None

    def recognize_with_retry(self, audio_data, retries=3, language="ru-RU"):
        # Распознавание с повторными попытками
        for attempt in range(retries):
            try:
                # Пробуем разные варианты для надежности
                if attempt == 0:
                    # Первая попытка: стандартное распознавание
                    text = self.recognizer.recognize_google(
                        audio_data,
                        language=language,
                        show_all=False
                    )
                elif attempt == 1:
                    # Вторая попытка: с альтернативами
                    result = self.recognizer.recognize_google(
                        audio_data,
                        language=language,
                        show_all=True
                    )
                    if result and 'alternative' in result:
                        text = result['alternative'][0]['transcript']
                    else:
                        continue
                else:
                    # Третья попытка: с английским fallback
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language=language
                        )
                    except:
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language="en-US"
                        )

                if text and text.strip():
                    return text.strip()

            except sr.UnknownValueError:
                if attempt == retries - 1:
                    raise
                time.sleep(0.1)
            except sr.RequestError as e:
                print(f"⚠️  Ошибка API распознавания: {e}")
                return None
            except Exception as e:
                print(f"⚠️  Ошибка распознавания (попытка {attempt + 1}): {e}")
                if attempt == retries - 1:
                    return None

        return None

    def correct_recognition(self, text):
        # Коррекция распознанного текста
        if not text:
            return text

        corrected = text.lower()

        # Применяем замены из словаря
        for wrong, correct in self.correction_dict.items():
            if wrong in corrected:
                corrected = corrected.replace(wrong, correct)

        # Удаляем лишние пробелы
        corrected = ' '.join(corrected.split())

        # Исправляем распространенные ошибки
        corrections = [
            (r'\bджим\s*ми\b', 'джимми'),
            (r'\bджи\s*мини\b', 'джимини'),
            (r'\bпау\s*за\b', 'пауза'),
            (r'\bсле\s*дую\s*щий\b', 'следующий'),
            (r'\bпреды\s*ду\s*щий\b', 'предыдущий'),
            (r'\bгром\s*че\b', 'громче'),
            (r'\bти\s*ше\b', 'тише'),
        ]

        import re
        for pattern, replacement in corrections:
            corrected = re.sub(pattern, replacement, corrected)

        return corrected

    def _log_recognition_stats(self, original, corrected):
        # Логирование статистики распознавания
        now = time.time()

        if original != corrected:
            print(f"🔧 Исправлено: '{original}' → '{corrected}'")

        # Считаем успешные/неуспешные распознавания
        if corrected and len(corrected) > 2:
            self.successful_records += 1
        else:
            self.failed_records += 1

        # Логируем время между командами
        if self.last_recognition_time > 0:
            time_diff = now - self.last_recognition_time
            if time_diff < 1.0:
                print(f"⚠️  Слишком частые команды: {time_diff:.1f} сек")

        self.last_recognition_time = now

        # Периодически показываем статистику
        total = self.successful_records + self.failed_records
        if total > 0 and total % 10 == 0:
            success_rate = (self.successful_records / total) * 100
            print(f"📊 Статистика: {success_rate:.1f}% успешных распознаваний")

    def save_audio_sample(self, audio_data, filename_prefix="debug"):
        # Сохранение аудио-сэмпла для отладки
        try:
            debug_dir = "debug_audio"
            os.makedirs(debug_dir, exist_ok=True)

            timestamp = int(time.time())
            filename = f"{debug_dir}/{filename_prefix}_{timestamp}.wav"

            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(audio_data.sample_width)
                wf.setframerate(audio_data.sample_rate)
                wf.writeframes(audio_data.get_wav_data())

            print(f"💾 Аудио сохранено: {filename}")
            return filename
        except:
            return None

    def get_microphone_info(self):
        # Получить информацию о микрофоне
        if not self.microphone:
            return "Микрофон не инициализирован"

        try:
            mic_list = sr.Microphone.list_microphone_names()
            current_index = self.microphone.device_index if hasattr(self.microphone, 'device_index') else 0

            info = f"🎤 Текущий микрофон: #{current_index}\n"
            if current_index < len(mic_list):
                info += f"   Название: {mic_list[current_index]}\n"

            info += f"⚙️  Настройки:\n"
            info += f"   Порог энергии: {self.recognizer.energy_threshold:.0f}\n"
            info += f"   Динамический порог: {self.recognizer.dynamic_energy_threshold}\n"
            info += f"   Статистика: {self.successful_records}✓ / {self.failed_records}✗"

            return info
        except:
            return "Информация о микрофоне недоступна"

    def calibrate_microphone(self):
        # Калибровка микрофона
        print("\n" + "=" * 50)
        print("🎤 КАЛИБРОВКА МИКРОФОНА")
        print("=" * 50)

        print("\n1. Убедитесь в тишине на 3 секунды...")
        time.sleep(3)

        print("2. Настраиваюсь на фоновый шум...")
        success = self.adjust_for_ambient_noise_enhanced(duration=3)

        if success:
            print("3. Произнесите фразу 'тест микрофона'...")

            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognize_with_retry(audio)

                    if text and "тест" in text.lower():
                        print(f"✅ Калибровка успешна! Распознано: {text}")
                        print(f"   Новый порог: {self.recognizer.energy_threshold:.0f}")
                        return True
                    else:
                        print("❌ Фраза не распознана")
                        return False
            except:
                print("❌ Ошибка при калибровке")
                return False
        else:
            print("❌ Не удалось настроить шум")
            return False