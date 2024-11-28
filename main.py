# main.py
import signal
import sys
from app.functions.base.settings import load_settings
from app.ui.menu_functions import handle_main_menu

def signal_handler(sig, frame):
    print('\nGracefully exiting Paneful...')
    sys.exit(0)

def main():
    # Set up signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    settings = load_settings()
    handle_main_menu(settings)

if __name__ == "__main__":
    main()