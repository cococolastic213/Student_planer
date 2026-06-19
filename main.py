"""
Точка запуска — запускать этот файл в PyCharm.
"""
import sys, os, shutil, importlib

# Удаляем старый кеш Python чтобы гарантированно загрузить свежий код
_base = os.path.dirname(os.path.abspath(__file__))
for root, dirs, files in os.walk(_base):
    for d in dirs:
        if d == "__pycache__":
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
importlib.invalidate_caches()

sys.path.insert(0, _base)
from ui.main_window import main

if __name__ == "__main__":
    main()
