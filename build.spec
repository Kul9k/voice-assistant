import os

block_cipher = None

hidden_imports = [
    'wave',
    'audioop',
    'collections.abc',
    'http.client',
    'urllib.request',
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
    'webbrowser',
]

datas = []

main_files = [
    'core.py',
    'data_manager.py',
    'voice_engine.py',
    'system_controller.py',
    'volume_controller.py',
    'ai_client.py',
    'advanced_features.py'
]

for file in main_files:
    if os.path.exists(file):
        print(f"✅ Добавляю файл: {file}")
        datas.append((file, '.'))

resource_folders = [
    ('voice', 'voice'),
    ('data', 'data'),
    ('Deswall', 'Deswall'),
]

for src, dest in resource_folders:
    if os.path.exists(src):
        print(f"✅ Добавляю папку: {src} -> {dest}")
        datas.append((src, dest))
    else:
        print(f"⚠️  Папка не найдена: {src}")

additional_files = [
    'ai_console.py',
    'schedule_manager.py',
    'weather_client.py',
    'news_client.py',
]

for file in additional_files:
    if os.path.exists(file):
        print(f"✅ Добавляю дополнительный файл: {file}")
        datas.append((file, '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
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
        'numpy',
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
    [],
    a.binaries,
    a.datas,
    [],  # УБРАТЬ a.zipfiles отсюда
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
 coll = COLLECT(
     exe,
     a.binaries,
     a.datas,
     strip=False,
     upx=True,
     name='VoiceAssistant'
 )