import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

class VolumeController:
    # Контроллер громкости системы

    def __init__(self):
        self.volume_interface = None
        self._init_volume_interface()

    def _init_volume_interface(self):
        try:
            # Пытаемся импортировать pycaw
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            # Получаем устройство воспроизведения по умолчанию
            devices = AudioUtilities.GetSpeakers()

            # Активируем интерфейс управления громкостью
            interface = devices.Activate(
                IAudioEndpointVolume._iid_,
                CLSCTX_ALL,
                None
            )

            # Приводим к правильному типу
            self.volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            print("✅ Интерфейс громкости инициализирован (pycaw)")

        except ImportError:
            print("⚠️ PyCAW не установлен. Установите: pip install pycaw comtypes")
            self.volume_interface = None
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
        return 50  # Предполагаем 50% если не удалось получить

    def set_volume(self, percent):
        # Ограничиваем диапазон
        percent = max(0, min(100, int(percent)))

        print(f"🎛️  Устанавливаю громкость: {percent}%")

        # Сначала пробуем через pycaw
        if self.volume_interface:
            try:
                # Устанавливаем громкость
                self.volume_interface.SetMasterVolumeLevelScalar(percent / 100.0, None)

                # Проверяем
                current = self.volume_interface.GetMasterVolumeLevelScalar()
                actual_percent = int(current * 100)
                print(f"✅ Точная установка: {actual_percent}%")
                return True

            except Exception as e:
                print(f"❌ Ошибка pycaw: {e}")

        # Если pycaw не сработал, используем резервный метод
        return self._set_volume_fallback(percent)

    def increase_volume(self, amount):
        # Увеличить громкость на указанное количество процентов
        current = self.get_current_volume()
        new_volume = min(100, current + amount)
        return self.set_volume(new_volume)

    def decrease_volume(self, amount):
        # Уменьшить громкость на указанное количество процентов
        current = self.get_current_volume()
        new_volume = max(0, current - amount)
        return self.set_volume(new_volume)

    def _set_volume_fallback(self, percent):
        # Резервный метод регулировки громкости через клавиши
        print(f"🔧 Резервный метод: {percent}%")

        try:

            # Сбрасываем к минимуму
            for _ in range(25):
                pyautogui.press('volumedown')
                pyautogui.sleep(0.01)

            # Устанавливаем нужный уровень
            steps = int(percent / 2)  # 2% за нажатие
            for _ in range(steps):
                pyautogui.press('volumeup')
                pyautogui.sleep(0.01)

            print(f"✅ Приблизительная установка: ~{percent}%")
            return True

        except Exception as e:
            print(f"❌ Ошибка резервного метода: {e}")
            return False