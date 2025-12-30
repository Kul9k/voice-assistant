import pygame
import os
import random
import sys
from data_manager import DataManager

class VoiceEngine:
    def __init__(self):
        self.data_manager = DataManager()
        pygame.mixer.init()

        # Определяем путь к папке с голосами
        if hasattr(sys, '_MEIPASS'):
            # В exe - голоса во временной папке
            self.voice_folder = os.path.join(sys._MEIPASS, "voice")
        else:
            # В исходном коде
            self.voice_folder = "voice"

        print(f"🔊 Папка с голосами: {self.voice_folder}")

    def get_voice_file(self, base_name):
        #Возвращает путь к MP3
        voice_settings = self.data_manager.get_voice_settings()
        gender_suffix = "_woman" if voice_settings['gender'] == 'female' else ""

        voice_file = f"{base_name}{gender_suffix}.mp3"
        voice_path = os.path.join(self.voice_folder, voice_file)

        if not os.path.exists(voice_path):
            voice_file = f"{base_name}.mp3"
            voice_path = os.path.join(self.voice_folder, voice_file)

        return voice_path if os.path.exists(voice_path) else None

    def play_voice(self, voice_file):
        # Воспроизводит MP3
        if voice_file and os.path.exists(voice_file):
            try:
                pygame.mixer.music.load(voice_file)
                pygame.mixer.music.play()
                # Ждем окончания воспроизведения
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
            except Exception as e:
                print(f"Ошибка воспроизведения {voice_file}: {e}")
        else:
            print(f"Файл не найден: {voice_file}")

    def speak(self, text):
        print(f"Ассистент: {text}")

    def play_random_success(self):
        voices = []
        for base in ["CommandCompleted", "CommandCompleted1"]:
            voice_file = self.get_voice_file(base)
            if voice_file:
                voices.append(voice_file)

        if voices:
            self.play_voice(random.choice(voices))
        else:
            print("✅ Команда выполнена")

    def play_welcome(self):
        voice_file = self.get_voice_file("welcome")
        if voice_file:
            self.play_voice(voice_file)
        else:
            print("Привет! Помощник готов к работе")

    def play_command_completed(self):
        voice_file = self.get_voice_file("CommandCompleted")
        if voice_file:
            self.play_voice(voice_file)

    def play_command_completed1(self):
        voice_file = self.get_voice_file("CommandCompleted1")
        if voice_file:
            self.play_voice(voice_file)

    def play_more_details(self):
        voice_file = self.get_voice_file("MoreDetailСcommand")
        if voice_file:
            self.play_voice(voice_file)
        else:
            print("Пожалуйста, уточните команду")

    def play_applying_settings(self):
        voice_file = self.get_voice_file("Applysavedata")
        if voice_file:
            self.play_voice(voice_file)

    def play_internet_search(self):
        voice_file = self.get_voice_file("InternetSearch")
        if voice_file:
            self.play_voice(voice_file)

    def change_voice_gender(self, gender, permanent=False):
        # Меняет пол голоса
        if gender in ['male', 'female']:
            success = self.data_manager.set_voice_gender(gender, permanent)
            if success:
                self.play_random_success()
            return success
        return False