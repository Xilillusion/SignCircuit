import keyboard
from multiprocessing import Process

from core.executor import load_script
from utils import log, locator

def main(filename: str):
    log.info("Bot started. Press 'esc' to exit.")
    load_script(filename)

if __name__ == "__main__":
    p_locator = Process(target=locator.display_position, daemon=True)
    p_locator.start()

    filename = input("Enter script filename: ")
    p = Process(target=main, args=[filename], daemon=True)
    p.start()

    keyboard.wait('esc')

    if p.is_alive():
        p.terminate()
    if p_locator.is_alive():
        p_locator.terminate()