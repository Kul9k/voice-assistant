import os
import webbrowser
import subprocess
import pyautogui
from datetime import datetime


class SystemController:
    def __init__(self, data_manager, voice_engine):
        self.data_manager = data_manager
        self.voice_engine = voice_engine

    def open_website(self, site_name):
       # Открывает сайт
        url = self.data_manager.get_website(site_name)
        if url:
            webbrowser.open(url)
            return True
        return False

    def open_program(self, program_name):
        # Открывает программу
        program_path = self.data_manager.get_program(program_name)
        if program_path:
            try:
                subprocess.Popen(program_path, shell=True)
                return True
            except:
                return False
        return False

    def shutdown_pc(self, seconds=60):
        # Выключает пк
        try:
            os.system(f"shutdown -s -t {seconds}")
            return True
        except:
            return False

    def cancel_shutdown(self):
        # Отменяет выключение
        try:
            os.system("shutdown -a")
            return True
        except:
            return False

    def restart_pc(self, seconds=60):
        # Перезагружает пк
        try:
            os.system(f"shutdown /r /f /t {seconds}")
            return True
        except:
            return False

    def change_volume(self, direction, amount=10):
        # Изменяет громкость
        try:
            if direction == "прибавь":
                for _ in range(amount // 2):
                    pyautogui.press('volumeup')
            else:
                for _ in range(amount // 2):
                    pyautogui.press('volumedown')
            return True
        except:
            return False

    def close_all_windows(self):
        # Закрывает все окна
        try:
            for _ in range(10):
                pyautogui.hotkey('alt', 'f4')
                pyautogui.sleep(0.5)
            return True
        except:
            return False

    def record_idea(self, idea_text):
        # Записывает идею
        try:
            with open("Ideas.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime('"%Y.%m.%d""%H:%M"')
                f.write(f'{timestamp} {idea_text}\n')
            return True
        except:
            return False