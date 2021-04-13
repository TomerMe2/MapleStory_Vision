from threading import Thread
from time import sleep
from PIL import ImageGrab
import win32gui
from hp_mp_detector import get_percentages_of_hp_mp
import keyboard

PIC_INTERVAL_SEC = 0.25
POSSIBLE_BTNS = ['insert', 'delete', 'home', 'end', 'page down', 'page up']
MAPLE_WINDOW_NM = 'Beresheet 1.0'

class Snapshoter:

    def __init__(self, pipe_connection):
        self.maple_window_handler = None
        self.hp_threshold = 0.45
        self.mp_threshold = 0.3
        self.hp_pots_button = None
        self.mp_pots_button = None
        self.pipe_connection = pipe_connection

    def listen_to_pipe(self):
        """
        Interface for comms:
        TYPE$COMMAND$VAL
        For example:
        HP$VAL$50
        or
        HP$VAL$70
        or
        HP$BTN$insert
        """
        # read all the messages in the queue
        while self.pipe_connection.poll(0):
            # there's a message on the pipe!
            try:
                request = self.pipe_connection.recv()

                request_type, command, val = request.split('$')

                if command == 'VAL':
                    number = float(val)

                    if number > 0.99 or number < 0:
                        continue

                    if request_type == 'HP':
                        self.hp_threshold = number
                    elif request_type == 'MP':
                        self.mp_threshold = number

                elif command == 'BTN':
                    if request_type == 'HP' and val in POSSIBLE_BTNS:
                        self.hp_pots_button = val
                    elif request_type == 'MP' and val in POSSIBLE_BTNS:
                        self.mp_pots_button = val

            except:
                pass

    def find_maple_window(self):
        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        maple_window = None
        while maple_window is None:
            toplist, winlist = [], []
            win32gui.EnumWindows(enum_cb, toplist)

            maple_window = [(hwnd, title) for hwnd, title in winlist if title == MAPLE_WINDOW_NM]
            if len(maple_window) == 0:
                maple_window = None
                sleep(10)
                continue

            maple_window = maple_window[0]
            self.maple_window_handler = maple_window[0]

    def picture_loop(self):
        while True:
            try:
                self.listen_to_pipe()

                if self.maple_window_handler is None:
                    self.find_maple_window()

                if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == MAPLE_WINDOW_NM:

                    win32gui.SetForegroundWindow(self.maple_window_handler)
                    bbox = win32gui.GetWindowRect(self.maple_window_handler)
                    img = ImageGrab.grab(bbox)
                    percentage_hp, percentage_mp = get_percentages_of_hp_mp(img)

                    if percentage_hp < self.hp_threshold and self.hp_pots_button is not None:
                        keyboard.press_and_release(self.hp_pots_button)
                    if percentage_mp < self.mp_threshold and self.mp_pots_button is not None:
                        keyboard.press_and_release(self.mp_pots_button)

            except:
                pass

            sleep(PIC_INTERVAL_SEC)