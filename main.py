import sys
import os
import tempfile
import atexit

# Принудительно импортируем проблемные модули
try:
    import wave
    import audioop
    import collections.abc

    print("✅ Встроенные модули загружены")
except ImportError as e:
    print(f"⚠️ Предупреждение: {e}")


# отчистка временных файлов
def cleanup_temp_files():
    if hasattr(sys, '_MEIPASS'):
        try:
            import shutil
            temp_dir = os.path.dirname(sys._MEIPASS)
            if temp_dir.startswith(tempfile.gettempdir()):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass


atexit.register(cleanup_temp_files)

# Определяем правильный путь к файлам
if hasattr(sys, '_MEIPASS'):
    # в собранном exe используем временную папку
    base_path = sys._MEIPASS
    # Папка где находится exe
    exe_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    # В исходном коде
    base_path = os.path.dirname(os.path.abspath(__file__))
    exe_dir = base_path

print(f"📍 Базовый путь (ресурсы): {base_path}")
print(f"📍 Папка EXE (запись): {exe_dir}")

# Добавляем пути для импорта модулей
sys.path.insert(0, base_path)
sys.path.append(exe_dir)

# Основные модули
modules_to_check = ['core.py', 'data_manager.py', 'voice_engine.py',
                    'system_controller.py', 'volume_controller.py']

print("🔍 Проверка модулей:")
for module in modules_to_check:
    module_path = os.path.join(base_path, module)
    exists = os.path.exists(module_path)
    print(f"  {module}: {'✅' if exists else '❌'}")

# Проверяем наличие папок с ресурсами
folders_to_check = ['voice', 'data', 'Deswall']
print("\n📁 Проверка ресурсов:")
for folder in folders_to_check:
    folder_path = os.path.join(base_path, folder)
    exists = os.path.exists(folder_path)
    print(f"  {folder}/: {'✅' if exists else '❌'}")

try:
    from core import main

    print("\n✅ Все модули загружены успешно!")

    # Запускаем основную программу
    main()

except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")
    print("📂 Содержимое текущей директории:")
    try:
        for file in os.listdir(base_path):
            print(f"   - {file}")
    except:
        pass
    input("\nНажмите Enter для выхода...")
    sys.exit(1)
except Exception as e:
    print(f"\n💥 Критическая ошибка: {e}")
    import traceback

    traceback.print_exc()
    input("\nНажмите Enter для выхода...")
    sys.exit(1)