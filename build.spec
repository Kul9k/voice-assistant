# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Получаем текущую директорию
base_path = os.path.dirname(os.path.abspath(sys.argv[0])) if hasattr(sys, 'frozen') else os.getcwd()
sys.path.insert(0, base_path)

hidden_imports = [
    'wave',
    'audioop',
    'collections.abc',
    'http.client',
    'urllib.request',
    'urllib.parse',
    'ssl',
    'platform',
    'threading',
    'json',
    're',
    'webbrowser',
    'subprocess',
    'pygame',
    'pygame._sdl2.audio',
    'pygame._sdl2.mixer',
    'comtypes',
    'comtypes.gen',
    'pycaw.pycaw',
    'pycaw.utils',
    'speech_recognition',
    'pyaudio',
    'engineio.async_drivers.threading',
    'numpy',
    'pyautogui',
    'requests',
    'pyperclip',
    'datetime',
    'time',
    'socket',
    'urllib',
    'speech_enhancer',
    'numpy',
]

# Добавляем наши модули
project_modules = [
    'core',
    'data_manager',
    'voice_engine',
    'system_controller',
    'volume_controller',
    'ai_client',
    'advanced_features',
    'yandex_music',
    'text_transformer',
]

hidden_imports.extend(project_modules)

datas = []

# Основные файлы проекта
main_files = [
    'core.py',
    'data_manager.py',
    'voice_engine.py',
    'system_controller.py',
    'volume_controller.py',
    'ai_client.py',
    'advanced_features.py',
    'yandex_music.py',
    'text_transformer.py',
    'main.py',
    'speech_enhancer.py',
]

for file in main_files:
    file_path = os.path.join(base_path, file)
    if os.path.exists(file_path):
        print(f"✅ Добавляю файл: {file}")
        datas.append((file_path, '.'))
    else:
        print(f"⚠️  Файл не найден: {file}")

# Папки с ресурсами
resource_folders = [
    ('voice', 'voice'),
    ('data', 'data'),
    ('Deswall', 'Deswall'),
]

for src, dest in resource_folders:
    src_path = os.path.join(base_path, src)
    if os.path.exists(src_path):
        print(f"✅ Добавляю папку: {src} -> {dest}")

        # Собираем все файлы из папки
        for root, dirs, files in os.walk(src_path):
            for file in files:
                # Пропускаем служебные файлы
                if file.startswith('.') or file.endswith(('.pyc', '.pyo')):
                    continue

                src_file_path = os.path.join(root, file)
                # Сохраняем структуру папок
                rel_path = os.path.relpath(root, base_path)
                dest_path = os.path.dirname(os.path.join(dest, os.path.relpath(src_file_path, src_path)))
                datas.append((src_file_path, dest_path))
    else:
        print(f"⚠️  Папка не найдена: {src}")

# Иконка
icon_file = None
icon_candidates = ['icon.ico', 'icon.png', 'icon.jpg', 'icon.bmp']
for icon in icon_candidates:
    icon_path = os.path.join(base_path, icon)
    if os.path.exists(icon_path):
        icon_file = icon_path
        print(f"✅ Использую иконку: {icon}")
        break

if not icon_file:
    print("⚠️  Иконка не найдена")

print(f"\n📂 Базовая папка: {base_path}")
print(f"📦 Всего файлов: {len(datas)}")
print("="*50)

a = Analysis(
    ['main.py'],
    pathex=[base_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
        'pydoc',
        'distutils',
        'matplotlib',
        'PIL',
        'numpy.testing',
        'numpy.random._examples',
        'scipy',
        'pandas',
        'torch',
        'tensorflow',
        'keras',
        'sklearn',
        'cryptography',
        'OpenGL',
        'wx',
        'PyQt5',
        'PySide2',
        'pygame.tests',
        'notebook',
        'jupyter',
        'ipython',
        'django',
        'flask',
        'bokeh',
        'plotly',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VoiceAssistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codepage='utf8',
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceAssistant'
)