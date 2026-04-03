import time

def info(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [INFO] {msg}")

def error(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [ERROR] {msg}")

def warning(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [WARNING] {msg}")

def debug(msg):
    print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} [DEBUG] {msg}")